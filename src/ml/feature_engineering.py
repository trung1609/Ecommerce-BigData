"""Build leakage-safe session features for purchase prediction."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)


SESSION_KEYS = ["user_id", "user_session"]
NUMERIC_FEATURES = [
    "view_count",
    "cart_count",
    "distinct_products",
    "distinct_categories",
    "avg_price",
    "max_price",
    "hour_of_day",
    "is_weekend",
]
LABEL_COLUMN = "label"
CATEGORY_COLUMN = "top_category_viewed"
EVENT_SCHEMA = StructType(
    [
        StructField("event_time", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("product_id", LongType(), True),
        StructField("category_id", LongType(), True),
        StructField("category_code", StringType(), True),
        StructField("brand", StringType(), True),
        StructField("price", DoubleType(), True),
        StructField("user_id", LongType(), True),
        StructField("user_session", StringType(), True),
    ]
)


def build_session_features(events: DataFrame) -> DataFrame:
    """Return one labeled row per user session without post-purchase signals."""
    events.sparkSession.conf.set("spark.sql.session.timeZone", "UTC")
    required_columns = {
        *SESSION_KEYS,
        "event_time",
        "event_type",
        "product_id",
        "category_code",
        "price",
    }
    missing_columns = required_columns.difference(events.columns)
    if missing_columns:
        raise ValueError(f"Input is missing required columns: {sorted(missing_columns)}")

    event_time_type = events.schema["event_time"].dataType
    if isinstance(event_time_type, TimestampType):
        timestamp = F.col("event_time")
    else:
        timestamp = F.to_timestamp(
            F.regexp_replace(F.col("event_time"), r"\s+UTC$", ""),
            "yyyy-MM-dd HH:mm:ss",
        )

    prepared = (
        events.withColumn("_event_timestamp", timestamp)
        .withColumn("_event_type", F.lower(F.trim(F.col("event_type"))))
        .filter(
            F.col("_event_timestamp").isNotNull()
            & F.col("user_id").isNotNull()
            & F.col("user_session").isNotNull()
        )
    )

    sessions = prepared.groupBy(*SESSION_KEYS).agg(
        F.min("_event_timestamp").alias("session_start"),
        F.min(
            F.when(F.col("_event_type") == "purchase", F.col("_event_timestamp"))
        ).alias("_first_purchase_time"),
        F.max(F.when(F.col("_event_type") == "purchase", 1).otherwise(0))
        .cast("int")
        .alias(LABEL_COLUMN),
    )

    behavior = prepared.filter(F.col("_event_type").isin("view", "cart")).join(
        sessions.select(*SESSION_KEYS, "_first_purchase_time"),
        on=SESSION_KEYS,
        how="inner",
    )
    behavior = behavior.filter(
        F.col("_first_purchase_time").isNull()
        | (F.col("_event_timestamp") < F.col("_first_purchase_time"))
    )

    aggregates = behavior.groupBy(*SESSION_KEYS).agg(
        F.sum(F.when(F.col("_event_type") == "view", 1).otherwise(0))
        .cast("long")
        .alias("view_count"),
        F.sum(F.when(F.col("_event_type") == "cart", 1).otherwise(0))
        .cast("long")
        .alias("cart_count"),
        F.countDistinct(
            F.when(F.col("_event_type") == "view", F.col("product_id"))
        )
        .cast("long")
        .alias("distinct_products"),
        F.countDistinct(
            F.when(F.col("_event_type") == "view", F.col("category_code"))
        )
        .cast("long")
        .alias("distinct_categories"),
        F.avg("price").alias("avg_price"),
        F.max("price").alias("max_price"),
    )

    category_counts = (
        behavior.filter(F.col("_event_type") == "view")
        .withColumn(
            "_category",
            F.coalesce(F.col("category_code"), F.lit("__unknown__")),
        )
        .groupBy(*SESSION_KEYS, "_category")
        .agg(F.count(F.lit(1)).alias("_category_views"))
    )
    category_window = Window.partitionBy(*SESSION_KEYS).orderBy(
        F.desc("_category_views"), F.asc("_category")
    )
    top_categories = (
        category_counts.withColumn("_rank", F.row_number().over(category_window))
        .filter(F.col("_rank") == 1)
        .select(*SESSION_KEYS, F.col("_category").alias(CATEGORY_COLUMN))
    )

    result = (
        sessions.join(aggregates, on=SESSION_KEYS, how="left")
        .join(top_categories, on=SESSION_KEYS, how="left")
        .withColumn("event_date", F.to_date("session_start"))
        .withColumn("hour_of_day", F.hour("session_start").cast("int"))
        .withColumn(
            "is_weekend",
            F.when(F.dayofweek("session_start").isin(1, 7), 1)
            .otherwise(0)
            .cast("int"),
        )
        .fillna(
            {
                "view_count": 0,
                "cart_count": 0,
                "distinct_products": 0,
                "distinct_categories": 0,
                "avg_price": 0.0,
                "max_price": 0.0,
                CATEGORY_COLUMN: "__unknown__",
            }
        )
    )
    return result.select(
        *SESSION_KEYS,
        "session_start",
        "event_date",
        *NUMERIC_FEATURES,
        CATEGORY_COLUMN,
        LABEL_COLUMN,
    )


def create_spark_session(app_name: str = "ecommerce-ml-features") -> SparkSession:
    if os.name == "nt":
        hadoop_home = Path(os.environ.get("HADOOP_HOME", ""))
        native_files = (hadoop_home / "bin" / "winutils.exe", hadoop_home / "bin" / "hadoop.dll")
        if not all(path.is_file() for path in native_files):
            hadoop_home = Path(__file__).resolve().parents[2] / "hadoop"
            native_files = (hadoop_home / "bin" / "winutils.exe", hadoop_home / "bin" / "hadoop.dll")
        if all(path.is_file() for path in native_files):
            os.environ["HADOOP_HOME"] = str(hadoop_home)
            hadoop_bin = str(hadoop_home / "bin")
            path_entries = os.environ.get("PATH", "").split(os.pathsep)
            if not any(os.path.normcase(os.path.abspath(entry)) == os.path.normcase(os.path.abspath(hadoop_bin)) for entry in path_entries if entry):
                os.environ["PATH"] = os.pathsep.join([hadoop_bin, *filter(None, path_entries)])

    worker_python = os.environ.get("PYSPARK_PYTHON")
    if not worker_python or not Path(worker_python).is_file():
        os.environ["PYSPARK_PYTHON"] = sys.executable
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.shuffle.partitions", "16")
        .getOrCreate()
    )


def run_feature_engineering(input_path: str, output_path: str) -> None:
    spark = create_spark_session()
    try:
        source = Path(input_path)
        events = (
            spark.read.option("header", "true").schema(EVENT_SCHEMA).csv(input_path)
            if source.suffix.lower() == ".csv"
            else spark.read.parquet(input_path)
        )
        features = build_session_features(events)
        features.write.mode("overwrite").parquet(output_path)
        print(f"Wrote session features to {output_path}")
    finally:
        spark.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", default="data/silver/events_cleaned.parquet", help="Silver Parquet or event CSV"
    )
    parser.add_argument("--output", default="data/gold/ml_features.parquet")
    args = parser.parse_args()
    run_feature_engineering(args.input, args.output)


if __name__ == "__main__":
    main()