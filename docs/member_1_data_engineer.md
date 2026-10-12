# Kế hoạch & Phân công Công việc: Thành viên 1 - Data Engineer (Kỹ sư Dữ liệu)

> **Vai trò:** Data Engineer (Pipeline Lead)  
> **Phạm vi trách nhiệm:** Pipeline 1 (Raw Data), Pipeline 2 (Ingestion), Pipeline 3 (ETL Core), Pipeline 4 (Storage - Silver Layer)  
> **Công nghệ chính:** Python, PySpark, Parquet, OS File System, Logging  
> **Mục tiêu then chốt:** Xử lý file thô 5.67 GB (~42.4 triệu dòng) thành dữ liệu Parquet tầng Silver sạch sẽ, tối ưu hiệu năng và chia sẻ file mẫu (Sample) sớm cho các thành viên khác.

---

## 1. Tổng quan Trách nhiệm & Luồng công việc

```text
[data/bronze/2019-Oct.csv (5.67 GB)]
        │
        ▼ (Task 1: Ingestion & Schema Definition)
[src/ingestion/load_data.py] ──> [data/bronze/sample_100k.csv (Bàn giao cho DA & MLE)]
        │
        ▼ (Task 2: Cleaning & Transformation)
[src/etl/clean_events.py]
        │
        ▼ (Task 3: Partitioning & Storage)
[data/silver/events_cleaned.parquet (~1.2 GB)]
```

---

## 2. Chi tiết các Task theo Timeline

### Giai đoạn 1: Khởi động & Chuẩn bị Môi trường (Ngày 1 – 3)
* [ ] **Task DE-01: Kiểm tra tính toàn vẹn dữ liệu gốc (Pipeline 1)**
  * Kiểm tra vị trí `data/bronze/2019-Oct.csv` và hash SHA-256 theo [docs/raw_data_manifest.json](file:///e:/Trung/Code/Python/Ph%C3%A2n%20t%C3%ADch%20d%E1%BB%AF%20li%E1%BB%87u%20l%E1%BB%9Bn/ecommerce-bigdata/docs/raw_data_manifest.json).
  * Đảm bảo `.gitignore` đã bỏ qua các file CSV lớn, không vô tình đẩy dữ liệu nặng lên Git repository.
* [ ] **Task DE-02: Thiết lập môi trường PySpark & Java**
  * Hướng dẫn cài đặt JDK (khuyến nghị Java 8 hoặc 11 64-bit), biến môi trường `JAVA_HOME`.
  * Cấu hình Hadoop `winutils.exe` cho môi trường Windows.
  * Cập nhật phiên bản tương thích vào [requirements.txt](file:///e:/Trung/Code/Python/Ph%C3%A2n%20t%C3%ADch%20d%E1%BB%AF%20li%E1%BB%87u%20l%E1%BB%9Bn/ecommerce-bigdata/requirements.txt) (`pyspark>=3.4.0`, `pyarrow>=12.0.0`).
* [ ] **Task DE-03: Xây dựng Ingestion Engine & Trích xuất Sample 100k (Pipeline 2)**
  * **File:** `src/ingestion/load_data.py`
  * Định nghĩa **Explicit StructType Schema** cho 9 cột đầu vào (tuyệt đối không dùng `inferSchema=True` để tránh quét toàn bộ 5.67 GB gây nghẽn máy):
    * `event_time`: StringType (hoặc TimestampType)
    * `event_type`: StringType
    * `product_id`: LongType
    * `category_id`: LongType
    * `category_code`: StringType
    * `brand`: StringType
    * `price`: DoubleType / FloatType
    * `user_id`: LongType
    * `user_session`: StringType
  * Tạo hàm trích xuất 100.000 dòng đầu tiên lưu ra `data/bronze/sample_100k.csv` và bàn giao ngay cho **Thành viên 2 (DA)** và **Thành viên 3 (MLE)** làm mock data.

---

### Giai đoạn 2: Xử lý ETL & Lưu trữ Silver Parquet (Ngày 4 – 7)
* [ ] **Task DE-04: Xây dựng Module Làm sạch dữ liệu (Pipeline 3)**
  * **File:** `src/etl/clean_events.py`
  * Chuẩn hóa thời gian: chuyển `event_time` sang `TimestampType` theo chuẩn UTC, trích xuất thêm các cột phái sinh: `event_date` (DateType), `hour` (IntegerType), `day_of_week` (IntegerType).
  * Chuẩn hóa danh mục: Tách chuỗi `category_code` (ví dụ `electronics.smartphone` -> `main_category`: `electronics`, `sub_category`: `smartphone`).
  * Xử lý dữ liệu khuyết thiếu:
    * `category_code`: điền `"unknown.unknown"`.
    * `brand`: điền `"unknown"`.
    * `user_session`: nếu null, có thể gắn mã phiên tạm thời hoặc lọc nếu không phục vụ phân tích phiên.
  * Lọc dữ liệu lỗi: loại bỏ các bản ghi có `price <= 0`.
  * Khử trùng lặp (Deduplication): loại bỏ các sự kiện trùng lặp hoàn toàn trên toàn bộ các cột.
* [ ] **Task DE-05: Lưu trữ tầng Silver & Phân vùng (Pipeline 4)**
  * **File:** `src/storage/write_silver.py`
  * Ghi dữ liệu sạch ra định dạng `Parquet` tại `data/silver/events_cleaned.parquet` với chuẩn nén Snappy.
  * Thử nghiệm phân vùng (Partitioning) theo `event_date` để tối ưu các câu truy vấn lọc theo ngày.
  * Ghi nhận thống kê trước & sau xử lý: Số bản ghi gốc, số bản ghi sau làm sạch, dung lượng file giảm từ 5.67 GB xuống còn bao nhiêu GB.

---

### Giai đoạn 3: Tối ưu hóa, Giám sát & Hỗ trợ tích hợp (Ngày 8 – 14)
* [ ] **Task DE-06: Tối ưu hiệu năng Spark & Memory Management**
  * Tinh chỉnh cấu hình Spark Session (`spark.driver.memory="4g"`, `spark.sql.shuffle.partitions=16-32`).
  * Đảm bảo script có thể chạy độc lập dưới dạng CLI: `python src/etl/clean_events.py`.
* [ ] **Task DE-07: Viết tài liệu Kỹ thuật dữ liệu (Documentation)**
  * Viết tài liệu báo cáo ETL: tỷ lệ missing values, số lượng dòng đã loại bỏ, cấu trúc dữ liệu tầng Silver.
  * Hỗ trợ Thành viên 2 và Thành viên 3 trong việc tối ưu hóa truy vấn Spark khi tạo bảng Gold và trích xuất đặc trưng.

---

## 3. Bản giao ước đầu ra (Deliverables & Data Contract)

| Tên đầu ra | Đường dẫn | Người tiếp nhận | Định dạng / Chi tiết |
| :--- | :--- | :--- | :--- |
| **Dữ liệu mẫu 100k** | `data/bronze/sample_100k.csv` | Thành viên 2 & 3 | CSV nhẹ (~15MB), dùng để dev song song |
| **Mã nguồn Ingestion** | `src/ingestion/load_data.py` | Toàn nhóm | Đọc file CSV bằng PySpark với Explicit Schema |
| **Mã nguồn ETL Core** | `src/etl/clean_events.py` | Toàn nhóm | Chuẩn hóa ngày giờ, lọc lỗi, bổ sung cột phái sinh |
| **Dữ liệu tầng Silver** | `data/silver/events_cleaned.parquet` | Thành viên 2 & 3 | Định dạng Parquet sạch, phân vùng tối ưu |
| **Tài liệu Báo cáo ETL** | `docs/etl_report.md` | Báo cáo môn học | Bảng thống kê số dòng trước/sau, cấu trúc schema |
