# scripts/

Thư mục chứa các script thực thi nhanh (Automation & Utility Scripts) phục vụ quy trình phân tích dữ liệu lớn:

1. **`run_clean_full_data.py`**
   * **Chức năng:** Chạy toàn bộ pipeline ETL từ `data/bronze/2019-Oct.csv` (5.67 GB) ra tầng `data/silver/events_cleaned.parquet`.
   * **Cách dùng:** Mở file và bấm nút "Run Python File" (▶️).

2. **`preview_silver_data.py`**
   * **Chức năng:** Xem nhanh cấu trúc 14 cột, số dòng và thống kê hành vi của dữ liệu sạch tầng Silver; tự động xuất 1.000 dòng sang `data/silver/preview_1000.csv` để mở bằng Microsoft Excel.
   * **Cách dùng:** Mở file và bấm nút "Run Python File" (▶️).
