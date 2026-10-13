
import sys
import os
import argparse
from typing import Optional

# Đảm bảo in tiếng Việt trên console Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    LongType,
    DoubleType
)


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Cấu hình bắt buộc Java 17 (Java 22+ trên máy không tương thích với Spark 3.5 và gây lỗi Subject.getSubject)
jdk17_path = "C:\\Program Files\\Java\\jdk-17"
if os.path.exists(jdk17_path):
    os.environ["JAVA_HOME"] = jdk17_path
    os.environ["PATH"] = os.path.join(jdk17_path, "bin") + os.path.pathsep + os.environ.get("PATH", "")

# Cấu hình tự động HADOOP_HOME cho Windows để Spark ghi file (Parquet/CSV) không bị lỗi
if os.path.exists("C:\\hadoop\\bin\\winutils.exe"):
    hadoop_dir = "C:\\hadoop"
elif os.path.exists(os.path.join(PROJECT_ROOT, "hadoop", "bin", "winutils.exe")):
    hadoop_dir = os.path.join(PROJECT_ROOT, "hadoop")
else:
    hadoop_dir = None

if hadoop_dir:
    os.environ["HADOOP_HOME"] = hadoop_dir
    os.environ["hadoop.home.dir"] = hadoop_dir
    os.environ["PATH"] = os.path.join(hadoop_dir, "bin") + os.path.pathsep + os.environ.get("PATH", "")

# Khắc phục triệt để lỗi đường dẫn Windows có dấu cách/tiếng Việt
if os.path.exists("C:\\pyspark"):
    os.environ["SPARK_HOME"] = "C:/pyspark"
elif os.path.exists("X:\\.venv\\Lib\\site-packages\\pyspark"):
    os.environ["SPARK_HOME"] = "X:/.venv/Lib/site-packages/pyspark"

if os.path.exists("C:\\pyenv\\Scripts\\python.exe"):
    os.environ["PYSPARK_PYTHON"] = "C:/pyenv/Scripts/python.exe"
    os.environ["PYSPARK_DRIVER_PYTHON"] = "C:/pyenv/Scripts/python.exe"
elif os.path.exists("X:\\.venv\\Scripts\\python.exe"):
    os.environ["PYSPARK_PYTHON"] = "X:/.venv/Scripts/python.exe"
    os.environ["PYSPARK_DRIVER_PYTHON"] = "X:/.venv/Scripts/python.exe"
else:
    os.environ["PYSPARK_PYTHON"] = "python"
    os.environ["PYSPARK_DRIVER_PYTHON"] = "python"


def get_spark_session(app_name: str = "EcommerceIngestion", driver_memory: str = "4g") -> SparkSession:
    """
    Khởi tạo hoặc lấy SparkSession hiện có, cấu hình tối ưu cho máy cá nhân.
    """
    builder = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.driver.memory", driver_memory)
        .config("spark.executor.memory", driver_memory)
        .config("spark.sql.shuffle.partitions", "16")
        .config("spark.default.parallelism", "8")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
    )
    return builder.getOrCreate()


def get_raw_schema() -> StructType:
    """
    Định nghĩa cấu trúc schema 9 cột cho tập dữ liệu REES46 eCommerce.
    Dùng StringType cho event_time để đọc raw an toàn (tránh parse lỗi timezone 'UTC' lúc nạp thô).
    """
    return StructType([
        StructField("event_time", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("product_id", LongType(), True),
        StructField("category_id", LongType(), True),
        StructField("category_code", StringType(), True),
        StructField("brand", StringType(), True),
        StructField("price", DoubleType(), True),
        StructField("user_id", LongType(), True),
        StructField("user_session", StringType(), True)
    ])


def load_raw_csv(
    spark: SparkSession,
    file_path: str,
    schema: Optional[StructType] = None
) -> DataFrame:
    """
    Đọc file CSV vào PySpark DataFrame với schema định sẵn.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    if schema is None:
        schema = get_raw_schema()

    df = (
        spark.read
        .format("csv")
        .option("header", "true")
        .option("mode", "PERMISSIVE")
        .schema(schema)
        .load(file_path)
    )
    return df


def main():
    parser = argparse.ArgumentParser(description="PySpark Data Ingestion")
    parser.add_argument(
        "--path",
        type=str,
        default="data/bronze/sample_100k.csv",
        help="Đường dẫn tới file CSV (mặc định là data/bronze/sample_100k.csv)"
    )
    args = parser.parse_args()

    print(f"[*] Đang khởi tạo SparkSession...")
    spark = get_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    print(f"[*] Bắt đầu đọc dữ liệu từ: {args.path}")
    df = load_raw_csv(spark, args.path)

    print("\n--- SCHEMA DỮ LIỆU ĐÃ NẠP ---")
    df.printSchema()

    row_count = df.count()
    print(f"\n[+] Tổng số bản ghi đã nạp: {row_count:,} dòng")

    print("\n--- 5 DÒNG DỮ LIỆU ĐẦU TIÊN ---")
    df.show(5, truncate=False)

    spark.stop()
    print("[THÀNH CÔNG] Pipeline 2 (Ingestion) hoàn tất!")


if __name__ == "__main__":
    main()
