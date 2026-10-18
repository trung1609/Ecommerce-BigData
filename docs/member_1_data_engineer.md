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
* [x] **Task DE-02: Thiết lập môi trường PySpark & Java**
  * Đã cài đặt JDK 17, Python 3.11, Hadoop winutils (`C:\hadoop\bin`), PySpark 3.5.1 và PyArrow 15.0.0.
* [x] **Task DE-03 (Phần 1): Trích xuất Sample 100k (Pipeline 2)**
  * **File:** `src/ingestion/extract_sample.py`
  * Đã trích xuất thành công `data/bronze/sample_100k.csv` (100.000 dòng dữ liệu, 12.73 MB). Sẵn sàng bàn giao cho Thành viên 2 (DA) và Thành viên 3 (MLE).
* [x] **Task DE-03 (Phần 2): Xây dựng PySpark Ingestion Engine**
  * **File:** `src/ingestion/load_data.py`
  * Định nghĩa **Explicit StructType Schema** 9 cột, khởi tạo SparkSession tối ưu và đã kiểm thử đọc dữ liệu thành công.

---

### Giai đoạn 2: Xử lý ETL & Lưu trữ Silver Parquet (Ngày 4 – 7)
* [x] **Task DE-04: Xây dựng Module Làm sạch dữ liệu (Pipeline 3)**
  * **File:** `src/etl/clean_events.py`
  * Chuẩn hóa thời gian, tách danh mục (`main_category`, `sub_category`), xử lý missing values, lọc bỏ giá âm và loại trùng lặp. Đã kiểm thử chạy thành công trên 100k dòng mẫu chỉ trong 14.88 giây.
* [x] **Task DE-05: Lưu trữ tầng Silver Parquet Hoàn chỉnh (Pipeline 4)**
  * **File:** `run_clean_full_data.py`
  * Đã xử lý toàn bộ 5.67 GB (~42.4 triệu dòng) thành công!
  * **Kết quả:** Đã xuất ra `data/silver/events_cleaned.parquet` gồm **42,349,874 dòng** dữ liệu sạch, dung lượng nén chỉ còn **2.06 GB**, quét toàn bộ chỉ mất **2.44 giây**!
  * Đã hoàn thành báo cáo kỹ thuật tại [docs/etl_report.md](file:///e:/Trung/Code/Python/Ph%C3%A2n%20t%C3%ADch%20d%E1%BB%AF%20li%E1%BB%87u%20l%E1%BB%9Bn/ecommerce-bigdata/docs/etl_report.md).

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
| **Tài liệu Hướng dẫn Demo** | `docs/demo_member_1_data_engineer.md` | Thuyết trình / Demo | Tổng hợp tất cả câu lệnh và kịch bản demo 2 phút |
