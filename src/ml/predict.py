"""Load the saved Spark pipeline and score one session feature record."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import setuptools
from pyspark.ml import PipelineModel
from pyspark.ml.functions import vector_to_array
from pyspark.sql import DataFrame, SparkSession, functions as F

from src.ml.feature_engineering import CATEGORY_COLUMN, NUMERIC_FEATURES, create_spark_session


DEFAULT_MODEL_PATH = "models/best_purchase_model"


def load_purchase_model(model_path: str = DEFAULT_MODEL_PATH) -> PipelineModel:
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Purchase model not found: {path}")
    if SparkSession.getActiveSession() is None:
        create_spark_session("ecommerce-purchase-model-loading")
    return PipelineModel.load(str(path))


def _feature_frame(
    spark: SparkSession, session_features: Mapping[str, Any]
) -> DataFrame:
    required = {*NUMERIC_FEATURES, CATEGORY_COLUMN}
    missing = required.difference(session_features)
    if missing:
        raise ValueError(f"Missing session features: {sorted(missing)}")
    values = [
        F.lit(float(session_features[name])).cast("double").alias(name)
        for name in NUMERIC_FEATURES
    ]
    values.append(F.lit(str(session_features[CATEGORY_COLUMN])).alias(CATEGORY_COLUMN))
    return spark.range(1).select(*values)


def predict_purchase_probability(
    session_features: Mapping[str, Any],
    model: PipelineModel | None = None,
    model_path: str = DEFAULT_MODEL_PATH,
    spark: SparkSession | None = None,
) -> float:
    """Return the estimated purchase probability for one feature record."""
    spark = spark or SparkSession.getActiveSession() or create_spark_session(
        "ecommerce-purchase-inference"
    )
    spark.conf.set("spark.sql.session.timeZone", "UTC")
    model = model or load_purchase_model(model_path)
    scored = model.transform(_feature_frame(spark, session_features))
    return float(
        scored.select(vector_to_array("probability")[1].alias("probability")).first()[0]
    )