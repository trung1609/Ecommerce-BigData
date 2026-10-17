"""Evaluation and reporting helpers for Spark purchase models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
import setuptools

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.functions import vector_to_array
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from sklearn.metrics import precision_recall_curve, roc_curve

from src.ml.feature_engineering import CATEGORY_COLUMN, LABEL_COLUMN, NUMERIC_FEATURES


def evaluate_predictions(
    predictions: DataFrame, curve_sample_size: int = 100_000
) -> tuple[dict[str, float], dict[str, list[float]]]:
    """Calculate Spark metrics and bounded curve points for report plots."""
    evaluator = BinaryClassificationEvaluator(
        labelCol=LABEL_COLUMN, rawPredictionCol="rawPrediction"
    )
    pr_auc = evaluator.setMetricName("areaUnderPR").evaluate(predictions)
    roc_auc = evaluator.setMetricName("areaUnderROC").evaluate(predictions)

    counts = predictions.agg(
        F.sum(F.when((F.col(LABEL_COLUMN) == 1) & (F.col("prediction") == 1), 1).otherwise(0)).alias("tp"),
        F.sum(F.when((F.col(LABEL_COLUMN) == 0) & (F.col("prediction") == 1), 1).otherwise(0)).alias("fp"),
        F.sum(F.when((F.col(LABEL_COLUMN) == 1) & (F.col("prediction") == 0), 1).otherwise(0)).alias("fn"),
    ).first()
    true_positive = int(counts["tp"] or 0)
    false_positive = int(counts["fp"] or 0)
    false_negative = int(counts["fn"] or 0)
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    total_rows = predictions.count()
    sample_fraction = min(1.0, curve_sample_size / max(total_rows, 1))
    sample = (
        predictions.select(LABEL_COLUMN, vector_to_array("probability")[1].alias("score"))
        .sample(withReplacement=False, fraction=sample_fraction, seed=42)
        .limit(curve_sample_size)
        .collect()
    )
    labels = [int(row[LABEL_COLUMN]) for row in sample]
    scores = [float(row["score"]) for row in sample]
    if len(set(labels)) < 2:
        raise ValueError("Curve evaluation requires both purchase and non-purchase labels in test data")

    curve_precision, curve_recall, _ = precision_recall_curve(labels, scores)
    false_positive_rate, true_positive_rate, _ = roc_curve(labels, scores)
    metrics = {
        "pr_auc": float(pr_auc),
        "roc_auc": float(roc_auc),
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }
    curves = {
        "precision": curve_precision.tolist(),
        "recall": curve_recall.tolist(),
        "false_positive_rate": false_positive_rate.tolist(),
        "true_positive_rate": true_positive_rate.tolist(),
    }
    return metrics, curves


def _feature_importances(model: Any) -> list[tuple[str, float]]:
    estimator = model.stages[-1]
    if hasattr(estimator, "featureImportances"):
        values = estimator.featureImportances.toArray().tolist()
    elif hasattr(estimator, "coefficients"):
        values = [abs(value) for value in estimator.coefficients.toArray().tolist()]
    else:
        return []

    labels: list[str] = []
    for stage in model.stages:
        if stage.__class__.__name__ == "StringIndexerModel":
            labels = list(stage.labels)
            break
    names = list(NUMERIC_FEATURES) + [f"{CATEGORY_COLUMN}={label}" for label in labels]
    names.extend(
        f"{CATEGORY_COLUMN}=__unseen_{index}__"
        for index in range(len(names), len(values))
    )
    names = names[: len(values)]
    if len(names) < len(values):
        names.extend(f"feature_{index}" for index in range(len(names), len(values)))
    return sorted(zip(names, values), key=lambda item: item[1], reverse=True)


def _error_rows(predictions: DataFrame, limit: int = 10) -> tuple[list[Any], list[Any]]:
    scored = predictions.withColumn(
        "purchase_probability", vector_to_array("probability")[1]
    )
    columns = ["user_id", "user_session", LABEL_COLUMN, "purchase_probability"]
    false_positives = (
        scored.filter((F.col(LABEL_COLUMN) == 0) & (F.col("prediction") == 1))
        .select(*columns)
        .orderBy(F.desc("purchase_probability"))
        .limit(limit)
        .collect()
    )
    false_negatives = (
        scored.filter((F.col(LABEL_COLUMN) == 1) & (F.col("prediction") == 0))
        .select(*columns)
        .orderBy(F.asc("purchase_probability"))
        .limit(limit)
        .collect()
    )
    return false_positives, false_negatives


def write_evaluation_report(
    report_path: str,
    model_metrics: dict[str, dict[str, float]],
    model_curves: dict[str, dict[str, list[float]]],
    best_model_name: str,
    best_model: Any,
    best_predictions: DataFrame,
    train_count: int,
    test_count: int,
    cutoff_epoch: int,
) -> None:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pr_path = path.parent / "model_pr_curve.png"
    roc_path = path.parent / "model_roc_curve.png"

    figure, axis = plt.subplots(figsize=(8, 6))
    for name, curve in model_curves.items():
        area = model_metrics[name]["pr_auc"]
        axis.plot(curve["recall"], curve["precision"], label=f"{name} (PR-AUC {area:.3f})")
    axis.set(xlabel="Recall", ylabel="Precision", title="Precision-Recall curves")
    axis.legend(loc="best")
    axis.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(pr_path, dpi=150)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(8, 6))
    for name, curve in model_curves.items():
        area = model_metrics[name]["roc_auc"]
        axis.plot(
            curve["false_positive_rate"],
            curve["true_positive_rate"],
            label=f"{name} (ROC-AUC {area:.3f})",
        )
    axis.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Chance")
    axis.set(xlabel="False positive rate", ylabel="True positive rate", title="ROC curves")
    axis.legend(loc="best")
    axis.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(roc_path, dpi=150)
    plt.close(figure)

    importance_rows = _feature_importances(best_model)[:15]
    false_positives, false_negatives = _error_rows(best_predictions)
    lines = [
        "# Báo cáo đánh giá mô hình dự đoán mua hàng",
        "",
        f"Mô hình được chọn theo PR-AUC trên tập test: **{best_model_name}**.",
        f"Tập train có {train_count:,} phiên; tập test có {test_count:,} phiên. "
        f"Mốc chia thời gian Unix UTC: `{cutoff_epoch}`.",
        "",
        "## So sánh mô hình",
        "",
        "| Mô hình | PR-AUC | ROC-AUC | Precision | Recall | F1 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, metrics in model_metrics.items():
        lines.append(
            f"| {name} | {metrics['pr_auc']:.4f} | {metrics['roc_auc']:.4f} "
            f"| {metrics['precision']:.4f} | {metrics['recall']:.4f} | {metrics['f1']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Đường cong",
            "",
            "![Precision-Recall curves](model_pr_curve.png)",
            "",
            "![ROC curves](model_roc_curve.png)",
            "",
            "## Đặc trưng quan trọng nhất",
            "",
        ]
    )
    if importance_rows:
        lines.extend(["| Đặc trưng | Importance / |coefficient| |", "|---|---:|"])
        lines.extend(f"| {name} | {value:.6f} |" for name, value in importance_rows)
    else:
        lines.append("Mô hình không cung cấp feature importance hoặc hệ số tuyến tính.")
    lines.extend(["", "## Phân tích lỗi", "", "### False positives", ""])
    lines.extend(_format_error_table(false_positives))
    lines.extend(["", "### False negatives", ""])
    lines.extend(_format_error_table(false_negatives))
    lines.extend(
        [
            "",
            "## Giới hạn diễn giải",
            "",
            "Báo cáo này được sinh từ dữ liệu đầu vào của lần chạy. Đặc trưng phiên dương "
            "chỉ dùng view/cart trước purchase đầu tiên; các encoder và scaler được fit "
            "trên train. Nếu đầu vào là sample 100k theo thứ tự thời gian, đây chỉ là "
            "smoke-test: các phiên sát cuối sample có thể bị right-censoring và không "
            "đại diện cho đánh giá cuối trên Silver đầy đủ.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _format_error_table(rows: list[Any]) -> list[str]:
    if not rows:
        return ["Không có trường hợp trong nhóm này ở ngưỡng phân loại hiện tại."]
    lines = [
        "| user_id | user_session | label | P(purchase) |",
        "|---:|---|---:|---:|",
    ]
    lines.extend(
        f"| {row['user_id']} | {row['user_session']} | {row[LABEL_COLUMN]} "
        f"| {float(row['purchase_probability']):.4f} |"
        for row in rows
    )
    return lines