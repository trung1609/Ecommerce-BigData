# src/ml

Pipeline 5: tạo đặc trưng, huấn luyện và đánh giá bằng Spark MLlib.

## Chạy pipeline

Tạo môi trường riêng và cài các thư viện ML:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Trên Windows, Spark 3.5 cần Java 8+ và bộ Hadoop native Windows (`winutils.exe` cùng `hadoop.dll`) trong `HADOOP_HOME\bin` để đọc/ghi Parquet và lưu mô hình. `winutils.exe` không được đưa vào repository.

Tạo bảng Gold từ Silver:

```powershell
.\.venv\Scripts\python.exe -m src.ml.feature_engineering --input data/silver/events_cleaned.parquet --output data/gold/ml_features.parquet
```

Có thể dùng sample CSV để kiểm tra feature engineering:

```powershell
.\.venv\Scripts\python.exe -m src.ml.feature_engineering --input D:/sample_100k.csv --output data/gold/ml_features.parquet
```

Huấn luyện, so sánh theo PR-AUC và lưu pipeline tốt nhất:

```powershell
.\.venv\Scripts\python.exe -m src.ml.train --input data/gold/ml_features.parquet --model models/best_purchase_model --report docs/model_evaluation_report.md
```

Encoder và scaler được fit bên trong pipeline chỉ trên tập train. Gold lưu đặc trưng phiên thô để giữ đúng ranh giới này. Phiên dương chỉ dùng `view`/`cart` trước purchase đầu tiên; phiên âm dùng toàn bộ hành vi phiên quan sát được.
