
import sys
import os
import argparse
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col,
    to_timestamp,
    to_date,
    hour,
    dayofweek,
    split,
    coalesce,
    lit,
    regexp_replace
)

# Import module Ingestion đã viết
from src.ingestion.load_data import get_spark_session, load_raw_csv


def clean_ecommerce_events(df: DataFrame) -> DataFrame:
    """
    Áp dụng các quy tắc làm sạch và chuẩn hóa dữ liệu TMĐT.
    """
    print("[*] Đang thực hiện làm sạch và chuẩn hóa dữ liệu...")

    cleaned_df = df.withColumn(
        "clean_time_str",
        regexp_replace(col("event_time"), " UTC", "")
    ).withColumn(
        "event_time",
        to_timestamp(col("clean_time_str"), "yyyy-MM-dd HH:mm:ss")
    ).drop("clean_time_str")

    cleaned_df = (
        cleaned_df
        .withColumn("event_date", to_date(col("event_time")))
        .withColumn("hour", hour(col("event_time")))
        .withColumn("day_of_week", dayofweek(col("event_time")))
    )

    cat_split = split(col("category_code"), "\\.")
    cleaned_df = (
        cleaned_df
        .withColumn("main_category", coalesce(cat_split.getItem(0), lit("unknown")))
        .withColumn("sub_category", coalesce(cat_split.getItem(1), lit("unknown")))
    )

    cleaned_df = (
        cleaned_df
        .withColumn("category_code", coalesce(col("category_code"), lit("unknown.unknown")))
        .withColumn("brand", coalesce(col("brand"), lit("unknown")))
        .withColumn("user_session", coalesce(col("user_session"), lit("unknown_session")))
    )

    cleaned_df = cleaned_df.filter(
        (col("price") > 0) & 
        (col("event_type").isin(["view", "cart", "purchase"])) &
        (col("user_id").isNotNull())
    )

    cleaned_df = cleaned_df.dropDuplicates([
        "event_time", "event_type", "product_id", "user_id", "user_session"
    ])

    return cleaned_df


def save_to_silver(
    df: DataFrame,
    output_path: str,
    partition_by_date: bool = False
):
    """
    Lưu DataFrame ra định dạng Parquet (chuẩn nén Snappy).
    """
    print(f"[*] Đang ghi dữ liệu vào tầng Silver: {output_path}")
    writer = df.write.mode("overwrite").format("parquet").option("compression", "snappy")

    if partition_by_date:
        print(" - Bật chế độ phân vùng (partition) theo: event_date")
        writer = writer.partitionBy("event_date")

    writer.save(output_path)
    print(f"[THÀNH CÔNG] Đã lưu Parquet thành công vào: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="PySpark ETL Clean Events")
    parser.add_argument(
        "--input",
        type=str,
        default="data/bronze/sample_100k.csv",
        help="Đường dẫn file đầu vào"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/silver/sample_cleaned_100k.parquet",
        help="Đường dẫn lưu file Parquet tầng Silver"
    )
    parser.add_argument(
        "--partition",
        action="store_true",
        help="Phân vùng theo event_date"
    )
    args = parser.parse_args()

    start_time = time.time()
    spark = get_spark_session(app_name="EcommerceETLClean")
    spark.sparkContext.setLogLevel("WARN")

    print(f"[*] Đọc dữ liệu từ: {args.input}")
    raw_df = load_raw_csv(spark, args.input)
    raw_count = raw_df.count()
    print(f" - Số dòng dữ liệu gốc: {raw_count:,}")

    # Thực hiện làm sạch
    clean_df = clean_ecommerce_events(raw_df)
    clean_count = clean_df.count()
    print(f" - Số dòng sau khi làm sạch: {clean_count:,} (Loại bỏ {raw_count - clean_count:,} dòng rác/trùng)")

    # Lưu ra Silver
    save_to_silver(clean_df, args.output, partition_by_date=args.partition)

    print("\n--- 5 DÒNG DỮ LIỆU SẠCH MẪU ---")
    clean_df.select(
        "event_time", "event_date", "hour", "event_type", 
        "main_category", "sub_category", "brand", "price", "user_id"
    ).show(5, truncate=False)

    elapsed = time.time() - start_time
    print(f"[HOÀN THÀNH] Thời gian xử lý ETL: {elapsed:.2f} giây")

    spark.stop()


if __name__ == "__main__":
    main()
