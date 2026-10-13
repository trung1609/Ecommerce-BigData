"""
Script xem nhanh dữ liệu sạch tầng Silver (events_cleaned.parquet).
Cách dùng: Mở file này và bấm nút "Run Python File" (▶️) để xem bảng dữ liệu và thống kê.
Tự động xuất thêm file preview_1000.csv để bạn có thể mở xem trực tiếp bằng Microsoft Excel.
"""

import os
import sys
import csv
import time

# Đường dẫn gốc của project (thư mục cha của scripts/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ingestion.load_data import get_spark_session


def preview_silver():
    silver_path = os.path.join(PROJECT_ROOT, "data", "silver", "events_cleaned.parquet")
    csv_preview_path = os.path.join(PROJECT_ROOT, "data", "silver", "preview_1000.csv")

    if not os.path.exists(silver_path):
        print(f"[LỖI] Chưa tìm thấy dữ liệu: {silver_path}")
        return

    print("=" * 80)
    print("🔍 XEM DỮ LIỆU SẠCH TẦNG SILVER (events_cleaned.parquet)")
    print("=" * 80)

    spark = get_spark_session(app_name="PreviewSilver", driver_memory="2g")
    spark.sparkContext.setLogLevel("WARN")

    # Đọc dữ liệu Parquet
    df = spark.read.parquet(silver_path)

    print(f"\n1. Tổng số dòng dữ liệu sạch: {df.count():,} dòng")
    print(f"2. Danh sách 14 cột đã chuẩn hóa:")
    for idx, (col_name, col_type) in enumerate(df.dtypes, 1):
        print(f"   {idx:2d}. {col_name:<16} : {col_type}")

    print("\n" + "=" * 80)
    print("📋 10 DÒNG DỮ LIỆU MẪU ĐẦU TIÊN:")
    print("=" * 80)
    df.select(
        "event_time", "event_type", "main_category", 
        "sub_category", "brand", "price", "user_id"
    ).show(10, truncate=False)

    print("\n" + "=" * 80)
    print("📊 THỐNG KÊ NHANH CÁC LOẠI HÀNH VI (event_type):")
    print("=" * 80)
    df.groupBy("event_type").count().orderBy("count", ascending=False).show()

    # Xuất 1000 dòng ra CSV bằng module csv chuẩn của Python (để mở bằng Excel)
    print("\n" + "=" * 80)
    print("[*] Đang xuất 1,000 dòng mẫu sang file CSV để mở bằng Excel...")
    try:
        sample_rows = df.limit(1000).collect()
        columns = df.columns
        with open(csv_preview_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            for r in sample_rows:
                writer.writerow([r[c] for c in columns])

        print(f"✅ ĐÃ CẬP NHẬT FILE EXCEL: {csv_preview_path}")
    except PermissionError:
        print(f"ℹ️ File {csv_preview_path} đang được mở trong Excel, dữ liệu đã có sẵn từ trước.")

    print("👉 Bạn có thể nhấp đúp vào file preview_1000.csv trong thư mục data/silver để xem bằng Excel!")
    print("=" * 80)

    spark.stop()


if __name__ == "__main__":
    preview_silver()
