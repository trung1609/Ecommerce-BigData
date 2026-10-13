import csv
import tempfile
import unittest
from pathlib import Path

from pyspark.sql import SparkSession

from src.ml.feature_engineering import build_session_features


class SessionFeatureEngineeringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = (
            SparkSession.builder.master("local[2]")
            .appName("feature-engineering-tests")
            .config("spark.ui.enabled", "false")
            .config("spark.sql.shuffle.partitions", "2")
            .getOrCreate()
        )

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_features_stop_at_first_purchase_and_keep_purchase_only_session(self):
        rows = [
                ("2026-10-10 08:00:00 UTC", "view", 11, "phones", 10.0, 7, "positive"),
                ("2026-10-10 08:01:00 UTC", "cart", 12, "audio", 20.0, 7, "positive"),
                ("2026-10-10 08:02:00 UTC", "purchase", 99, "secret", 999.0, 7, "positive"),
                ("2026-10-10 08:03:00 UTC", "view", 100, "after", 1000.0, 7, "positive"),
                ("2026-10-11 09:00:00 UTC", "view", 21, "home", 5.0, 8, "negative"),
                ("2026-10-11 09:01:00 UTC", "view", 21, "home", 15.0, 8, "negative"),
                ("2026-10-11 10:00:00 UTC", "purchase", 31, "only", 30.0, 9, "purchase-only"),
        ]
        columns = [
                "event_time",
                "event_type",
                "product_id",
                "category_code",
                "price",
                "user_id",
                "user_session",
        ]
        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "events.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream)
                writer.writerow(columns)
                writer.writerows(rows)
            events = (
                self.spark.read.option("header", "true")
                .option("inferSchema", "true")
                .csv(str(csv_path))
            )
            result = {
                row.user_session: row.asDict()
                for row in build_session_features(events).collect()
            }

        positive = result["positive"]
        self.assertEqual(positive["label"], 1)
        self.assertEqual(positive["view_count"], 1)
        self.assertEqual(positive["cart_count"], 1)
        self.assertEqual(positive["distinct_products"], 1)
        self.assertEqual(positive["distinct_categories"], 1)
        self.assertEqual(positive["avg_price"], 15.0)
        self.assertEqual(positive["max_price"], 20.0)
        self.assertEqual(positive["top_category_viewed"], "phones")

        negative = result["negative"]
        self.assertEqual(negative["label"], 0)
        self.assertEqual(negative["view_count"], 2)
        self.assertEqual(negative["distinct_products"], 1)
        self.assertEqual(negative["hour_of_day"], 9)

        purchase_only = result["purchase-only"]
        self.assertEqual(purchase_only["label"], 1)
        self.assertEqual(purchase_only["view_count"], 0)
        self.assertEqual(purchase_only["avg_price"], 0.0)


if __name__ == "__main__":
    unittest.main()