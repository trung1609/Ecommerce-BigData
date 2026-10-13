import os
import sys
import time

# Đường dẫn gốc của project (thư mục cha của scripts/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ingestion.load_data import get_spark_session, load_raw_csv
from src.etl.clean_events import clean_ecommerce_events, save_to_silver


def run_full_etl():
    input_csv = os.path.join(PROJECT_ROOT, "data", "bronze", "2019-Oct.csv")
    output_parquet = os.path.join(PROJECT_ROOT, "data", "silver", "events_cleaned.parquet")

    if not os.path.exists(input_csv):
        print(f"[LỖI] Không tìm thấy file gốc: {input_csv}")
        return

    print("=" * 70)
    print("BẮT ĐẦU CHẠY PIPELINE ETL DỮ LIỆU LỚN E-COMMERCE (5.67 GB)")
    print("=" * 70)
    print(f"[*] Input:  {input_csv}")
    print(f"[*] Output: {output_parquet}")

    start_time = time.time()

    # Khởi tạo Spark Session tối ưu bộ nhớ
    spark = get_spark_session(app_name="EcommerceETLFull", driver_memory="4g")
    spark.sparkContext.setLogLevel("WARN")

    # 1. Đọc dữ liệu lớn
    print("\n[Bước 1/3] Đang nạp dữ liệu bằng PySpark với Explicit Schema...")
    raw_df = load_raw_csv(spark, input_csv)

    # 2. Làm sạch & Chuẩn hóa
    print("\n[Bước 2/3] Đang làm sạch, chuẩn hóa kiểu dữ liệu và lọc bản ghi lỗi...")
    clean_df = clean_ecommerce_events(raw_df)

    # 3. Ghi ra tầng Silver Parquet
    print(f"\n[Bước 3/3] Đang ghi dữ liệu nén Snappy vào tầng Silver...")
    clean_df = clean_df.coalesce(16)
    save_to_silver(clean_df, output_parquet, partition_by_date=False)

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"HOÀN THÀNH TOÀN BỘ PIPELINE ETL!")
    print(f"Tổng thời gian xử lý: {elapsed:.2f} giây ({elapsed / 60:.2f} phút)")
    print(f"Dữ liệu sạch đã lưu tại: {output_parquet}")
    print("=" * 70)

    spark.stop()


if __name__ == "__main__":
    run_full_etl()
