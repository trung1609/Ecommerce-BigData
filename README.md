# Phân tích hành vi khách hàng thương mại điện tử

Dự án môn **Phân tích và Tích hợp Dữ liệu lớn**, nhóm 3 người, thời gian 2 tuần.

**Phạm vi hiện tại: Pipeline 1 – Raw Data.** Chưa triển khai ingestion, Spark, ETL, mô hình hay dashboard. Các thư mục còn lại chỉ dành sẵn cho bước sau.

## 1. Hiểu dự án từ đầu

Big Data là làm việc với dữ liệu có quy mô hoặc đặc điểm khiến cách xử lý thông thường trở nên khó khăn. File CSV của dự án khoảng 5,67 GB; không cần mở toàn bộ bằng Excel hoặc nạp hết vào bộ nhớ để bắt đầu. Spark sẽ được xem xét ở pipeline sau để xử lý dữ liệu theo các phần nhỏ và có thể phân tán.

Một pipeline là một giai đoạn trong luồng làm việc:

| Pipeline | Mục đích | Trạng thái |
| --- | --- | --- |
| 1. Raw Data | Giữ bản gốc, ghi nhận nguồn và kiểm tra tính toàn vẹn | Đã chuẩn bị |
| 2. Ingestion | Đọc dữ liệu vào hệ thống xử lý | Chưa triển khai |
| 3. ETL/ELT Processing | Làm sạch, chuẩn hóa và biến đổi | Chưa triển khai |
| 4. Storage | Tổ chức dữ liệu để sử dụng lại | Chưa triển khai |
| 5. Machine Learning | Tạo đặc trưng, huấn luyện và đánh giá dự đoán mua hàng | Chưa triển khai |
| 6. Visualization | Trình bày kết quả bằng dashboard | Chưa triển khai |

ETL nghĩa là trích xuất → biến đổi → lưu; ELT nghĩa là trích xuất → lưu → biến đổi. Chưa cần quyết định chi tiết cách xử lý ở bước 1.

## 2. Cấu trúc dự án

```text
ecommerce-bigdata/
├── data/
│   ├── bronze/                 # CSV gốc
│   │   └── 2019-Oct.csv
│   ├── silver/                 # Dữ liệu làm sạch về sau
│   └── gold/                   # Dữ liệu tổng hợp/đặc trưng về sau
├── src/
│   ├── ingestion/              # Pipeline 2
│   ├── etl/                    # Pipeline 3
│   ├── storage/                # Pipeline 4
│   ├── analytics/              # Phân tích hành vi, bảng tổng hợp
│   └── ml/                     # Pipeline 5
├── dashboard/                 # Pipeline 6
├── models/                    # Mô hình đã huấn luyện về sau
├── notebooks/                 # Notebook khám phá về sau
├── config/                    # Cấu hình dùng chung về sau
├── docs/
│   ├── project_structure.md   # Giải thích mọi thư mục/file
│   ├── raw_data.md            # Thiết kế và thao tác Pipeline 1
│   └── raw_data_manifest.json # Thông tin file và mã kiểm tra
├── tests/                     # Kiểm thử ở các bước sau
├── requirements.txt
├── .gitignore
└── README.md
```

Các thư mục dữ liệu trống có `.gitkeep`; các thư mục chức năng có `README.md` mô tả mục đích. Xem giải thích đầy đủ trong [docs/project_structure.md](docs/project_structure.md).

## 3. Bắt đầu từng bước trên Windows

1. Mở thư mục `ecommerce-bigdata` trong VS Code hoặc File Explorer.
2. File cần dùng nằm tại **`data/bronze/2019-Oct.csv`** tính từ thư mục dự án. Bản sao được tạo từ file đã có ở thư mục cha; file ở thư mục cha vẫn được giữ nguyên.
3. Đọc [docs/raw_data.md](docs/raw_data.md) để hiểu quy tắc giữ dữ liệu gốc.
4. Đọc `docs/raw_data_manifest.json`: đối chiếu tên file, dung lượng và SHA-256. Mã SHA-256 là dấu vân tay của nội dung file, giúp phát hiện file bị thay đổi.
5. Nếu muốn tự kiểm tra lại, mở PowerShell **tại `ecommerce-bigdata`** và chạy từng lệnh:

   ```powershell
   Get-Item -LiteralPath '.\data\bronze\2019-Oct.csv' | Select-Object Name, Length
   Get-FileHash -LiteralPath '.\data\bronze\2019-Oct.csv' -Algorithm SHA256
   ```

   Tính hash có thể mất vài phút vì phải đọc toàn bộ file; thao tác này không sửa dữ liệu. So sánh kết quả với manifest, không so sánh theo chữ hoa/chữ thường.
6. Chưa cần cài Java, Spark hay thư viện Python. `requirements.txt` hiện chỉ chứa chú thích vì Pipeline 1 không cần thư viện ngoài.
7. Dừng tại đây. Chỉ chuyển sang Pipeline 2 sau khi bạn xác nhận.

## 4. Quy tắc nhóm

- Không sửa, đổi định dạng, xóa dòng, điền giá trị thiếu hoặc ghi đè file trong `data/bronze/`.
- CSV lớn không đưa lên Git. `.gitignore` đã bỏ qua dữ liệu, mô hình sinh ra và thông tin bí mật cục bộ.
- Git chỉ lưu mã nguồn và tài liệu; nó không sao lưu CSV. Giữ thêm bản gốc ở nơi an toàn. Hai bản trên cùng ổ đĩa không bảo vệ khỏi hỏng ổ đĩa.
- CSV là văn bản dạng bảng; Parquet là định dạng lưu theo cột sẽ dùng ở bước sau. Hiện chưa chuyển đổi sang Parquet.
- Dùng Python, PySpark/Spark MLlib và Streamlit khi tới đúng giai đoạn. Chốt phiên bản tương thích khi thiết lập môi trường ở bước sau.
- PostgreSQL là lựa chọn bổ sung; chưa cần với phạm vi ban đầu. Không dùng Kafka, Airflow hoặc Kubernetes.

Phân công gợi ý cho bước 1: người 1 quản lý bản gốc và manifest; người 2 kiểm tra đường dẫn, dung lượng và hash; người 3 đọc hướng dẫn và ghi phần mô tả dữ liệu cho báo cáo.
