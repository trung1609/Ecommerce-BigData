# src

## Tổng quan

Thư mục `src/` chứa toàn bộ mã nguồn nghiệp vụ và pipeline dữ liệu của dự án. Trong phiên bản hiện tại, phần ML đã được triển khai hoàn chỉnh cho Pipeline 5 theo yêu cầu của Member 3.

## Pipeline đã hoàn thiện

- `src/ml/feature_engineering.py`: xây dựng session-level features và label từ dữ liệu sự kiện
- `src/ml/train.py`: chia train/test theo thời gian, xử lý mất cân bằng lớp, huấn luyện nhiều mô hình và lưu mô hình tốt nhất
- `src/ml/evaluate.py`: tính toán các chỉ số chính và xuất báo cáo đánh giá mô hình
- `src/ml/predict.py`: hàm suy luận xác suất mua hàng phục vụ dashboard và kiểm thử

## Tài liệu hướng dẫn

Xem chi tiết trong [src/ml/README.md](ml/README.md).

## Đầu ra chính

- `data/gold/ml_features.parquet`
- `models/best_purchase_model/`
- `docs/model_evaluation_report.md`

## Lưu ý

- Mô hình được phát triển với PySpark MLlib, sử dụng `user_session` làm đơn vị dự đoán.
- Để chạy trên Windows, cần cấu hình `HADOOP_HOME` với Hadoop native binaries phù hợp.
- Các đầu ra mô hình và report đã được sinh từ dữ liệu sample của Member 1 và đã sẵn sàng cho việc đánh giá tiếp theo.
