"""Train and compare Spark MLlib purchase classifiers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import setuptools
from pyspark.ml import Pipeline
from pyspark.ml.classification import (
    GBTClassifier,
    LogisticRegression,
    RandomForestClassifier,
)
from pyspark.ml.feature import OneHotEncoder, StandardScaler, StringIndexer, VectorAssembler
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from src.ml.evaluate import evaluate_predictions, write_evaluation_report
from src.ml.feature_engineering import (
    CATEGORY_COLUMN,
    LABEL_COLUMN,
    NUMERIC_FEATURES,
    create_spark_session,
)


def chronological_split(features: DataFrame) -> tuple[DataFrame, DataFrame, int]:
    """Split sessions at the 80th percentile of their UTC start time."""
    ordered = features.withColumn("_session_epoch", F.unix_timestamp("session_start"))
    quantiles = ordered.approxQuantile("_session_epoch", [0.8], 0.001)
    if not quantiles:
        raise ValueError("Cannot compute a temporal cutoff from an empty feature table")
    cutoff_epoch = int(quantiles[0])
    training = ordered.filter(F.col("_session_epoch") < cutoff_epoch).drop("_session_epoch")
    testing = ordered.filter(F.col("_session_epoch") >= cutoff_epoch).drop("_session_epoch")
    if training.limit(1).count() == 0 or testing.limit(1).count() == 0:
        raise ValueError("Temporal split produced an empty train or test partition")
    return training, testing, cutoff_epoch


def _class_weights(training: DataFrame) -> tuple[DataFrame, float]:
    class_counts = {
        int(row[LABEL_COLUMN]): int(row["count"])
        for row in training.groupBy(LABEL_COLUMN).count().collect()
    }
    positive_count = class_counts.get(1, 0)
    negative_count = class_counts.get(0, 0)
    if not positive_count or not negative_count:
        raise ValueError("Training data must contain both purchase and non-purchase sessions")
    positive_weight = min(negative_count / positive_count, 20.0)
    weighted = training.withColumn(
        "class_weight",
        F.when(F.col(LABEL_COLUMN) == 1, F.lit(positive_weight)).otherwise(F.lit(1.0)),
    )
    return weighted, positive_weight


def _candidate_estimators() -> dict[str, object]:
    return {
        "Logistic Regression": LogisticRegression(
            labelCol=LABEL_COLUMN,
            featuresCol="scaled_features",
            weightCol="class_weight",
            maxIter=50,
            regParam=0.03,
        ),
        "Random Forest": RandomForestClassifier(
            labelCol=LABEL_COLUMN,
            featuresCol="scaled_features",
            weightCol="class_weight",
            numTrees=60,
            maxDepth=8,
            seed=42,
        ),
        "Gradient-Boosted Trees": GBTClassifier(
            labelCol=LABEL_COLUMN,
            featuresCol="scaled_features",
            weightCol="class_weight",
            maxIter=35,
            maxDepth=5,
            seed=42,
        ),
    }


def _pipeline(classifier: object) -> Pipeline:
    return Pipeline(
        stages=[
            StringIndexer(
                inputCol=CATEGORY_COLUMN,
                outputCol="category_index",
                handleInvalid="keep",
            ),
            OneHotEncoder(
                inputCols=["category_index"],
                outputCols=["category_vector"],
                handleInvalid="keep",
                dropLast=False,
            ),
            VectorAssembler(
                inputCols=[*NUMERIC_FEATURES, "category_vector"],
                outputCol="raw_features",
                handleInvalid="keep",
            ),
            StandardScaler(
                inputCol="raw_features",
                outputCol="scaled_features",
                withMean=False,
                withStd=True,
            ),
            classifier,
        ]
    )


def train_and_evaluate(
    input_path: str,
    model_path: str,
    report_path: str,
    spark: SparkSession | None = None,
) -> dict[str, object]:
    owns_spark = spark is None
    spark = spark or create_spark_session("ecommerce-purchase-training")
    spark.conf.set("spark.sql.session.timeZone", "UTC")
    try:
        features = spark.read.parquet(input_path)
        training, testing, cutoff_epoch = chronological_split(features)
        training, positive_weight = _class_weights(training)
        training = training.cache()
        testing = testing.cache()
        train_count = training.count()
        test_count = testing.count()

        model_metrics: dict[str, dict[str, float]] = {}
        model_curves: dict[str, dict[str, list[float]]] = {}
        fitted_models = {}
        for name, estimator in _candidate_estimators().items():
            fitted = _pipeline(estimator).fit(training)
            predictions = fitted.transform(testing).cache()
            metrics, curves = evaluate_predictions(predictions)
            predictions.unpersist()
            model_metrics[name] = metrics
            model_curves[name] = curves
            fitted_models[name] = fitted
            print(f"{name}: {json.dumps(metrics, sort_keys=True)}")

        best_name = max(model_metrics, key=lambda name: model_metrics[name]["pr_auc"])
        best_model = fitted_models[best_name]
        model_directory = Path(model_path)
        model_directory.parent.mkdir(parents=True, exist_ok=True)
        best_model.write().overwrite().save(str(model_directory))
        metadata = {
            "model_name": best_name,
            "label_column": LABEL_COLUMN,
            "positive_class_weight": positive_weight,
            "temporal_cutoff_epoch_utc": cutoff_epoch,
            "train_rows": train_count,
            "test_rows": test_count,
            "metrics": model_metrics[best_name],
        }
        (model_directory / "model_metadata.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )

        best_predictions = best_model.transform(testing).cache()
        write_evaluation_report(
            report_path=report_path,
            model_metrics=model_metrics,
            model_curves=model_curves,
            best_model_name=best_name,
            best_model=best_model,
            best_predictions=best_predictions,
            train_count=train_count,
            test_count=test_count,
            cutoff_epoch=cutoff_epoch,
        )
        best_predictions.unpersist()
        training.unpersist()
        testing.unpersist()
        return metadata
    finally:
        if owns_spark:
            spark.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/gold/ml_features.parquet")
    parser.add_argument("--model", default="models/best_purchase_model")
    parser.add_argument("--report", default="docs/model_evaluation_report.md")
    args = parser.parse_args()
    train_and_evaluate(args.input, args.model, args.report)


if __name__ == "__main__":
    main()