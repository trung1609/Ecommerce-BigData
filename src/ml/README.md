# src/ml

## Tổng quan

Pipeline 5 của dự án thuộc trách nhiệm của Member 3: xử lý feature engineering, huấn luyện mô hình, đánh giá, lưu mô hình và phục vụ suy luận thời gian thực.

Mục tiêu chính là dự đoán xác suất một phiên người dùng sẽ có `purchase` dựa trên hành vi xem, thêm vào giỏ và dữ liệu thời gian/ngữ cảnh.

## Nội dung chính

- `feature_engineering.py`: gom session, tạo label, loại bỏ data leakage, lưu `data/gold/ml_features.parquet`
- `train.py`: chia train/test theo thời gian, xử lý mất cân bằng lớp, so sánh Logistic Regression / Random Forest / GBT, lưu mô hình tốt nhất
- `evaluate.py`: tính PR-AUC, ROC-AUC, precision, recall, F1 và sinh báo cáo
- `predict.py`: hàm `predict_purchase_probability()` để suy luận từ một session feature mới
- `tests/test_feature_engineering.py`: kiểm tra logic leak-safe và label session

## Yêu cầu môi trường

- Python 3.11 (đã kiểm tra end-to-end với PySpark 3.5.8); không dùng Python 3.14 cho model loading với PySpark 3.5.x
- Java 8+ để Spark chạy
- Trên Windows, cần Hadoop native binaries trong `HADOOP_HOME\bin`:
  - `winutils.exe`
  - `hadoop.dll`
- Cài đặt dependency:

```powershell
uv venv --python 3.11 .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
```

## Quy trình chạy

### 1) Tạo bộ gold features từ Silver parquet

```powershell
.\.venv\Scripts\python.exe -m src.ml.feature_engineering --input data/silver/events_cleaned.parquet --output data/gold/ml_features.parquet
```

### 2) Hoặc kiểm tra trực tiếp với sample CSV do Member 1 bàn giao

```powershell
.\.venv\Scripts\python.exe -m src.ml.feature_engineering --input D:/sample_100k.csv --output data/gold/ml_features.parquet
```

### 3) Huấn luyện mô hình và lưu mô hình tốt nhất

```powershell
.\.venv\Scripts\python.exe -m src.ml.train --input data/gold/ml_features.parquet --model models/best_purchase_model --report docs/model_evaluation_report.md
```

### 4) Chạy suy luận trên một phiên mới

```powershell
.\.venv\Scripts\python.exe -c "from src.ml.predict import predict_purchase_probability; print(predict_purchase_probability({'view_count': 4, 'cart_count': 1, 'distinct_products': 3, 'distinct_categories': 2, 'avg_price': 120.0, 'max_price': 240.0, 'hour_of_day': 15, 'is_weekend': 0, 'top_category_viewed': 'electronics.smartphone'}))"
```

## Quy tắc dữ liệu và tránh leakage

- Mỗi `user_session` tương ứng với một hàng trong bảng features.
- `label = 1` nếu session có ít nhất một sự kiện `purchase`.
- Chỉ tính các sự kiện trước thời điểm `purchase` đầu tiên; các event sau purchase bị loại bỏ khỏi feature tính toán.
- Encoder và scaler được fit chỉ trên tập train để tránh rò rỉ thông tin từ test set.
- Chia train/test theo thời gian để mô hình đánh giá đúng theo thực tế.

## Output đã tạo

Các tài sản đã được tạo từ chạy thực tế trên sample 100k:

- `data/gold/ml_features.parquet`
- `models/best_purchase_model/`
- `docs/model_evaluation_report.md`
- `docs/model_pr_curve.png`
- `docs/model_roc_curve.png`

## Kết quả đánh giá hiện tại

Mô hình tốt nhất theo PR-AUC ở lần chạy thực tế là `Gradient-Boosted Trees` với các chỉ số:

- PR-AUC: 0.3210
- ROC-AUC: 0.7342
- Precision: 0.1739
- Recall: 0.4494
- F1: 0.2508

## Ghi chú

- `sample_100k.csv` là dữ liệu mẫu do Member 1 bàn giao, dùng cho phát triển và smoke test.
- Khi triển khai trên dữ liệu Silver đầy đủ, nên chạy lại pipeline trên dữ liệu đầy đủ để cập nhật lại metrics cuối cùng.
- Không đưa `winutils.exe` / `hadoop.dll` vào repository; chỉ cần cấu hình `HADOOP_HOME` phù hợp ở máy local.
- `create_spark_session()` cấu hình Python worker dùng đúng interpreter hiện tại qua `PYSPARK_PYTHON`, cần thiết khi chạy từ một executable venv không được activate trong `PATH`.
