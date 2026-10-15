# Kế hoạch & Phân công Công việc: Thành viên 3 - Machine Learning Engineer (Kỹ sư Học máy)

> **Vai trò:** Machine Learning Engineer (MLE)  
> **Phạm vi trách nhiệm:** Pipeline 5 (Machine Learning: Trích xuất đặc trưng, Huấn luyện, Đánh giá, Lưu trữ) & Pipeline 6 (Tích hợp module suy luận lên Dashboard)  
> **Công nghệ chính:** Python, PySpark MLlib (`pyspark.ml`), Scikit-learn (phụ trợ đánh giá), Joblib / Spark Model Persistence  
> **Mục tiêu then chốt:** Xây dựng mô hình phân loại dự đoán khả năng mua hàng (`purchase`) của phiên/người dùng trên dữ liệu lớn, xử lý tốt bài toán mất cân bằng lớp và cung cấp hàm dự đoán thời gian thực cho Dashboard.

---

## 1. Tổng quan Trách nhiệm & Luồng công việc

```text
[data/silver/events_cleaned.parquet]
        │
        ▼ (Task 1: Feature Engineering & Labeling trên PySpark)
[src/ml/feature_engineering.py] ──> [data/gold/ml_features.parquet]
        │
        ▼ (Task 2: Model Training & Hyperparameter Tuning)
[src/ml/train.py] ──> [models/best_purchase_model/]
        │
        ▼ (Task 3: Evaluation & Model Serialization)
[src/ml/evaluate.py] ──> [docs/model_evaluation_report.md]
        │
        ▼ (Task 4: Inference Engine & Dashboard Integration)
[src/ml/predict.py] ──> Tích hợp vào [dashboard/app.py]
```

---

## 2. Chi tiết các Task theo Timeline

### Giai đoạn 1: Định hình Bài toán & Thử nghiệm trên Dữ liệu Mẫu (Ngày 1 – 3)
* [x] **Task MLE-01: Định hình bài toán & Tránh Data Leakage**
  * Nhận file `data/bronze/sample_100k.csv` từ Thành viên 1 để làm quen và viết thử mã nguồn.
  * Xác định bài toán: **Dự đoán phiên truy cập (Session) có phát sinh hành vi mua hàng (`purchase`) hay không?**
  * Thiết kế nhãn (Target Label):
    * `label = 1`: Phiên có ít nhất 1 sự kiện `purchase`.
    * `label = 0`: Phiên không có sự kiện `purchase` (chỉ có `view` hoặc `cart`).
  * **Nguyên tắc cốt lõi:** Tuyệt đối không để rò rỉ dữ liệu (Data Leakage) – các đặc trưng đầu vào chỉ được tính từ các sự kiện trước thời điểm mua hoặc từ lịch sử quá khứ của người dùng.
* [x] **Task MLE-02: Thiết kế danh mục đặc trưng (Feature Catalog)**
  * Xác định các đặc trưng quan trọng cần trích xuất:
    1. **Đặc trưng hành vi phiên:**
       * `view_count`: Số lượt xem sản phẩm trong phiên.
       * `cart_count`: Số lượt thêm vào giỏ hàng trong phiên.
       * `distinct_products`: Số lượng mã sản phẩm khác nhau đã xem.
       * `distinct_categories`: Số lượng danh mục khác nhau đã xem.
    2. **Đặc trưng giá cả:**
       * `avg_price`: Giá trung bình của các sản phẩm đã tương tác.
       * `max_price`: Giá cao nhất của sản phẩm trong phiên.
    3. **Đặc trưng ngữ cảnh & thời gian:**
       * `hour_of_day`: Giờ thực hiện phiên (0–23).
       * `is_weekend`: Cờ đánh dấu ngày cuối tuần (1: Thứ 7/CN, 0: Ngày thường).
    4. **Đặc trưng danh mục quan tâm nhất:**
       * `top_category_viewed`: Danh mục chính được xem nhiều nhất (mã hóa One-Hot Encoding hoặc StringIndexer).

---

### Giai đoạn 2: Feature Engineering & Huấn luyện Mô hình với PySpark MLlib (Ngày 4 – 7)
* [x] **Task MLE-03: Trích xuất đặc trưng quy mô lớn trên PySpark**
  * **File:** `src/ml/feature_engineering.py`
  * Đọc `data/silver/events_cleaned.parquet`.
  * Gom nhóm theo `user_session` (và `user_id`) để tính toán các đặc trưng trên.
  * Xây dựng `Pipeline` của PySpark ML:
    * `StringIndexer` cho các cột phân loại (Category).
    * `OneHotEncoder` chuyển đổi biến phân loại.
    * `VectorAssembler` gộp tất cả đặc trưng thành một vector `features`.
    * `StandardScaler` chuẩn hóa thang đo các biến số.
  * Lưu bảng đặc trưng vào `data/gold/ml_features.parquet` để tái sử dụng mà không phải tính lại.
* [x] **Task MLE-04: Xử lý mất cân bằng lớp (Imbalanced Data)**
  * Phân tích tỷ lệ nhãn: Trong thương mại điện tử, tỷ lệ phiên mua hàng thường chỉ chiếm 2–5% (nhãn 0 áp đảo nhãn 1).
  * Áp dụng kỹ thuật:
    * Gán trọng số mẫu (`weightCol`) cho nhãn hiếm trong hàm mất mát (Cost-sensitive Learning).
    * Hoặc thực hiện Undersampling lớp đa số trên tập huấn luyện để cân bằng tỷ lệ 1:3 hoặc 1:4.
* [x] **Task MLE-05: Huấn luyện các mô hình phân loại (Pipeline 5 - ML)**
  * **File:** `src/ml/train.py`
  * Phân chia tập dữ liệu theo thời gian (Time-based Splitting):
    * 80% thời gian đầu (ví dụ 01/10 – 24/10) dùng cho **Training Set**.
    * 20% thời gian sau (25/10 – 31/10) dùng cho **Test Set**.
  * Huấn luyện 2–3 mô hình để so sánh:
    1. **Baseline Model:** `LogisticRegression` (Nhanh, dễ giải thích, chuẩn mốc cơ sở).
    2. **Challenger Model 1:** `RandomForestClassifier` (Giảm thiểu overfitting, xử lý phi tuyến tốt).
    3. **Challenger Model 2:** `GBTClassifier` (Gradient-Boosted Trees - thường đạt độ chính xác cao nhất trên dữ liệu dạng bảng).

---

### Giai đoạn 3: Đánh giá, Lưu trữ & Tích hợp Suy luận (Ngày 8 – 14)
* [x] **Task MLE-06: Đánh giá mô hình toàn diện (Pipeline 5 - Evaluation)**
  * **File:** `src/ml/evaluate.py`
  * Sử dụng `BinaryClassificationEvaluator` và `MulticlassClassificationEvaluator`:
    * **PR-AUC (Area under Precision-Recall Curve):** Chỉ số quan trọng nhất cho dữ liệu mất cân bằng.
    * **ROC-AUC:** Đo lường khả năng phân tách của mô hình.
    * **Precision, Recall, F1-Score:** Đánh giá số ca mua hàng thực tế bắt được và tỷ lệ báo động giả.
  * Trích xuất **Feature Importance** (Độ quan trọng của các đặc trưng) để giải thích yếu tố nào thúc đẩy khách chốt đơn nhiều nhất.
* [x] **Task MLE-07: Lưu trữ mô hình (Model Persistence)**
  * Lưu mô hình tốt nhất vào `models/best_purchase_model/` bằng `model.save()` / `model.write().overwrite().save()`.
  * Viết module suy luận nhanh `src/ml/predict.py`: nhận vào thông số của một phiên mới và trả về xác suất mua hàng (`probability`).
* [x] **Task MLE-08: Tích hợp Module Dự đoán vào Dashboard**
  * Phối hợp cùng Thành viên 2 (DA) đưa chức năng dự đoán tương tác lên Tab 5 của Streamlit.
  * Tạo kịch bản mô phỏng What-If:
    * Khách xem 2 sản phẩm giá 100$ vào buổi sáng $\rightarrow$ Xác suất mua: 15%.
    * Khách thêm 1 sản phẩm vào giỏ hàng và xem thêm 3 phụ kiện cùng loại $\rightarrow$ Xác suất mua tăng lên 72% $\rightarrow$ Đề xuất hệ thống tự động hiển thị nút thanh toán nhanh hoặc mã giảm giá 5%.
* [x] **Task MLE-09: Viết Báo cáo Đánh giá Mô hình**
  * **File:** `docs/model_evaluation_report.md`
  * Trình bày bảng so sánh hiệu năng các mô hình, biểu đồ PR/ROC curve, giải thích Feature Importance và phân tích các trường hợp dự đoán sai (Error Analysis).

---

## 3. Bản giao ước đầu ra (Deliverables)

| Tên đầu ra | Đường dẫn | Người tiếp nhận | Định dạng / Chi tiết |
| :--- | :--- | :--- | :--- |
| **Pipeline Trích xuất Đặc trưng** | `src/ml/feature_engineering.py` | Toàn nhóm | PySpark script xử lý vector đặc trưng |
| **Bảng Gold ML Features** | `data/gold/ml_features.parquet` | MLE | Tập dữ liệu đặc trưng đã xử lý để train |
| **Script Huấn luyện Mô hình** | `src/ml/train.py` | Toàn nhóm | Script chạy PySpark MLlib, ghi log chỉ số |
| **Mô hình Huấn luyện tốt nhất** | `models/best_purchase_model/` | MLE & Dashboard | Mô hình Spark MLlib đã lưu |
| **Module Dự đoán thời gian thực** | `src/ml/predict.py` | Thành viên 2 | Hàm `predict_purchase_probability()` |
| **Báo cáo Đánh giá Mô hình** | `docs/model_evaluation_report.md` | Báo cáo môn học | So sánh mô hình, chỉ số PR-AUC, Feature Importance |
