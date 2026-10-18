# Phân Tích Dữ Liệu Lớn Thương Mại Điện Tử và Dự Đoán Hành Vi Mua Hàng

## 1. Tổng Quan Dữ Liệu và Hiện Trạng

- Tập dữ liệu nguồn: REES46 eCommerce Behavior Events (Tháng 10/2019).
- Quy mô dữ liệu thô: 5.67 GB, 42,448,764 bản ghi sự kiện.
- Trạng thái dự án: Đã hoàn thành trọn vẹn 6 pipeline từ dữ liệu thô đến giao diện trực quan hóa và mô hình học máy.

Kết quả tối ưu hóa lưu trữ:
- Định dạng: Chuyển từ CSV sang Apache Parquet nén Snappy.
- Dung lượng: Giảm từ 5.67 GB xuống 2.06 GB (tiết kiệm 63.7% dung lượng đĩa).
- Số bản ghi sạch: 42,349,874 dòng (loại bỏ 98,890 dòng rác, lỗi, trùng lặp).
- Số cột: Từ 9 cột gốc lên 14 cột chuẩn hóa.
- Tốc độ đọc: Rút ngắn từ 10-15 phút xuống 2.44 giây nhờ 16 phân vùng tối ưu.

## 2. Kiến Trúc Pipeline

Dự án được thiết kế theo mô hình 6 pipeline khép kín:

1. Pipeline 1 (Raw Data): Quản lý file gốc `data/bronze/2019-Oct.csv` và kiểm tra hash SHA-256.
2. Pipeline 2 (Ingestion): Trích xuất mẫu `sample_100k.csv` (12.7 MB) và nạp dữ liệu bằng PySpark với Explicit StructType Schema.
3. Pipeline 3 (ETL Core): Chuẩn hóa thời gian UTC, tách danh mục thành `main_category` và `sub_category`, điền nhãn unknown cho null, lọc `price > 0`, khử trùng lặp 5 khóa.
4. Pipeline 4 (Storage): Lưu trữ tầng Silver Parquet 16 phân vùng và tạo 4 bảng Data Mart tầng Gold (`kpis_daily`, `funnel_metrics`, `category_brand_stats`, `customer_segments`).
5. Pipeline 5 (Machine Learning): Tạo tập đặc trưng `ml_features.parquet`, huấn luyện và đánh giá mô hình Spark ML (Logistic Regression, Random Forest, GBT) dự đoán `is_purchased`, lưu pipeline tại `models/best_purchase_model/`.
6. Pipeline 6 (Visualization & Inference): Dashboard Streamlit phân tích phễu chuyển đổi, doanh thu, heatmap khung giờ vàng và tính năng dự đoán mua hàng trực tiếp.

## 3. Cấu Trúc Thư Mục

```text
ecommerce-bigdata/
├── data/
│   ├── bronze/            Dữ liệu thô CSV và mẫu 100k dòng
│   ├── silver/            Dữ liệu sạch Parquet và file preview CSV
│   └── gold/              Các bảng Data Mart và tập đặc trưng ML
├── src/
│   ├── ingestion/         Mã nguồn đọc CSV và nạp Spark Session
│   ├── etl/               Mã nguồn làm sạch và chuẩn hóa dữ liệu
│   ├── storage/           Mã nguồn quản lý đọc/ghi Parquet
│   ├── analytics/         Mã nguồn tổng hợp các bảng Gold
│   └── ml/                Mã nguồn feature engineering, train, predict
├── dashboard/             Ứng dụng giao diện Streamlit và các component
├── models/                Lưu trữ mô hình Spark ML đã huấn luyện
├── scripts/               Các script chạy pipeline full và preview
├── docs/                  Tài liệu kỹ thuật, báo cáo ETL, slide và demo
├── requirements.txt       Danh sách thư viện phụ thuộc
└── README.md              Hướng dẫn tổng quan dự án
```

## 4. Yêu Cầu Hệ Thống

- Hệ điều hành: Windows 10/11 hoặc Linux.
- Python: Phiên bản 3.10 hoặc 3.11.
- Java: OpenJDK / Oracle JDK 17 LTS (yêu cầu cho PySpark 3.5.1).
- Hadoop Winutils: `winutils.exe` và `hadoop.dll` tại `C:\hadoop\bin` (nếu chạy trên Windows).

Cài đặt thư viện:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 5. Hướng Dẫn Chạy Các Thành Phần

### Chạy Ingestion và Trích xuất mẫu
```powershell
python src/ingestion/extract_sample.py
python src/ingestion/load_data.py
```

### Chạy ETL làm sạch dữ liệu
```powershell
# Chạy trên tập mẫu 100k dòng (mất ~13 giây)
python src/etl/clean_events.py

# Chạy trên toàn bộ 5.67 GB dữ liệu thô
python scripts/run_clean_full_data.py
```

### Kiểm tra tốc độ đọc dữ liệu Silver Parquet
```powershell
python scripts/preview_silver_data.py
```

### Huấn luyện mô hình Machine Learning
```powershell
# Tạo đặc trưng học máy
python -m src.ml.features --input data/silver/events_cleaned.parquet --output data/gold/ml_features.parquet

# Huấn luyện mô hình và xuất báo cáo
python -m src.ml.train --input data/gold/ml_features.parquet --model models/best_purchase_model --report docs/model_evaluation_report.md
```

### Khởi chạy Dashboard trực quan hóa
```powershell
streamlit run dashboard/app.py
```

## 6. Phân Công Trách Nhiệm

- Thành viên 1 (Data Engineer): Phụ trách Pipeline 1 đến 4. Xây dựng cơ chế Ingestion, xử lý ETL làm sạch dữ liệu lớn bằng PySpark và tối ưu hóa lưu trữ tầng Silver Parquet.
- Thành viên 2 (Data Analyst): Phụ trách Pipeline 4 và 6. Tổng hợp các bảng Data Mart tầng Gold và phát triển các biểu đồ trực quan hóa trên Streamlit Dashboard.
- Thành viên 3 (Machine Learning Engineer): Phụ trách Pipeline 5 và 6. Trích xuất đặc trưng, huấn luyện mô hình Spark MLlib, đánh giá chỉ số ROC-AUC/PR-AUC và tích hợp module suy luận dự đoán vào Dashboard.