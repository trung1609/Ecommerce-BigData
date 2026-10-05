# Chức năng từng thư mục và file

Mọi đường dẫn dưới đây đều tính từ `ecommerce-bigdata/`. Thư mục Pipeline 2–6 hiện chỉ chứa tài liệu mô tả, không có chương trình thực thi.

| Thư mục | Chức năng |
| --- | --- |
| `data/` | Chứa các tầng dữ liệu cục bộ; nội dung dữ liệu không lên Git |
| `data/bronze/` | Pipeline 1: giữ nguyên CSV gốc |
| `data/silver/` | Dự phòng dữ liệu đã làm sạch, thường là Parquet |
| `data/gold/` | Dự phòng bảng tổng hợp và đặc trưng phục vụ ML/dashboard |
| `src/` | Mã nguồn xử lý của dự án trong các bước sau |
| `src/ingestion/` | Pipeline 2: mã đọc/tiếp nhận dữ liệu |
| `src/etl/` | Pipeline 3: mã làm sạch, chuẩn hóa, biến đổi |
| `src/storage/` | Pipeline 4: tổ chức đọc/ghi Parquet; kết nối PostgreSQL nếu nhóm cần sau này |
| `src/analytics/` | Tính chỉ số và phân tích hành vi từ dữ liệu đã xử lý |
| `src/ml/` | Pipeline 5: tạo tập học, huấn luyện, đánh giá với Spark MLlib |
| `dashboard/` | Pipeline 6: mã ứng dụng Streamlit |
| `models/` | Lưu mô hình đã huấn luyện và đầu ra liên quan ở bước sau |
| `notebooks/` | Notebook khám phá và thử nghiệm; chưa nạp CSV lớn tại bước này |
| `config/` | Cấu hình đường dẫn và tham số khi phát triển các bước sau; không chứa mật khẩu |
| `docs/` | Tài liệu dự án, thiết kế và hồ sơ dữ liệu |
| `tests/` | Kiểm thử logic xử lý khi có mã nguồn ở các bước sau |

| File | Chức năng |
| --- | --- |
| `README.md` | Điểm bắt đầu: phạm vi, cây thư mục, hướng dẫn, quy tắc nhóm |
| `.gitignore` | Ngăn Git theo dõi dữ liệu lớn, môi trường, cache, bí mật và đầu ra mô hình |
| `requirements.txt` | Nơi khai báo thư viện Python về sau; hiện chỉ có chú thích |
| `data/bronze/2019-Oct.csv` | Bản sao nguyên byte của dữ liệu gốc; không sửa trực tiếp |
| `data/bronze/.gitkeep` | Giữ thư mục bronze trong Git mà không đưa CSV lên Git |
| `data/silver/.gitkeep` | Giữ thư mục silver trống trong Git |
| `data/gold/.gitkeep` | Giữ thư mục gold trống trong Git |
| `docs/raw_data.md` | Thiết kế Pipeline 1, đường dẫn, header, giới hạn kiểm tra và tiêu chí hoàn thành |
| `docs/raw_data_manifest.json` | Hồ sơ kích thước, SHA-256 và nguồn dữ liệu đã biết/chưa biết |
| `docs/project_structure.md` | Tài liệu bạn đang đọc: giải thích mọi thư mục và file ban đầu |
| `src/README.md` | Giải thích khu vực mã nguồn và trạng thái chưa triển khai |
| `src/ingestion/README.md` | Mô tả vai trò Pipeline 2 và điểm dừng hiện tại |
| `src/etl/README.md` | Mô tả vai trò Pipeline 3 |
| `src/storage/README.md` | Mô tả vai trò Pipeline 4 |
| `src/analytics/README.md` | Mô tả khu vực phân tích hành vi |
| `src/ml/README.md` | Mô tả vai trò Pipeline 5 |
| `dashboard/README.md` | Mô tả khu vực Streamlit cho Pipeline 6 |
| `models/README.md` | Giải thích nơi lưu mô hình tương lai |
| `notebooks/README.md` | Giải thích nơi thử nghiệm, khám phá dữ liệu |
| `config/README.md` | Giải thích nơi đặt cấu hình tương lai |
| `tests/README.md` | Giải thích nơi đặt kiểm thử tương lai |

`.gitkeep` là file rỗng theo quy ước, không chạy chương trình và không phải một tính năng xử lý dữ liệu của Git. Chưa tạo `__init__.py`, script chạy hoặc cấu hình Spark vì chưa triển khai mã Python.
