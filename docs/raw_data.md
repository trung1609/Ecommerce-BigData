# Pipeline 1 – Raw Data

## Mục tiêu và giới hạn

Đầu vào: file `2019-Oct.csv` có sẵn, được người dùng xác định là REES46 Multi-category Behavior Events. Đầu ra: bản sao nguyên vẹn trong `data/bronze/` và hồ sơ mô tả file. Đây là quản lý dữ liệu gốc; chưa đọc thành DataFrame, chưa nhập vào Spark/cơ sở dữ liệu và chưa thực hiện Pipeline 2.

Luồng công việc: xác định file → ghi nhận dung lượng → sao chép nguyên byte → so sánh SHA-256 → ghi hồ sơ → dừng.

Trong dự án này, **bronze là nơi giữ CSV gốc bất biến theo quy ước nhóm**. Silver dành cho dữ liệu đã làm sạch và gold dành cho bảng tổng hợp/đặc trưng ở các bước sau. Tên các tầng mô tả trạng thái dữ liệu, không phải ba hệ thống cần cài đặt.

## Đường dẫn chính xác

```text
E:\Trung\Code\Python\Phân tích dữ liệu lớn\ecommerce-bigdata\data\bronze\2019-Oct.csv
```

File ban đầu tại `E:\Trung\Code\Python\Phân tích dữ liệu lớn\2019-Oct.csv` được giữ nguyên. Sao chép tiêu tốn thêm khoảng 5,67 GB. Không dùng thao tác Save trong trình sửa bảng tính để ghi lại CSV.

Nếu thành viên khác nhận dự án từ Git: tự lấy cùng file từ nguồn đã được nhóm thống nhất, đặt đúng đường dẫn tương đối `data/bronze/2019-Oct.csv` và đối chiếu hash với manifest. Không tự thay manifest để che đi sự khác biệt. Nếu hash khác, xác minh lại file với người quản lý dữ liệu trước khi tiếp tục.

## Hồ sơ dữ liệu

`raw_data_manifest.json` ghi tên bộ dữ liệu do người dùng cung cấp, đường dẫn tương đối, số byte, SHA-256, ngày ghi nhận và trạng thái kiểm tra bản sao. URL tải, giấy phép và thời điểm tải thực tế chưa được cung cấp nên để `null`; nhóm cần bổ sung từ nguồn tải thực tế, không phỏng đoán.

Header quan sát trực tiếp từ dòng đầu của CSV:

```text
event_time,event_type,product_id,category_id,category_code,brand,price,user_id,user_session
```

| Cột | Ý nghĩa dự kiến theo tên cột, cần đối chiếu tài liệu nguồn |
| --- | --- |
| event_time | Thời điểm sự kiện |
| event_type | Loại hành vi/sự kiện |
| product_id | Mã sản phẩm |
| category_id | Mã danh mục |
| category_code | Mã phân loại danh mục |
| brand | Thương hiệu |
| price | Giá ghi trong sự kiện; chưa xác minh đơn vị tiền |
| user_id | Mã người dùng |
| user_session | Mã phiên truy cập |

Chưa xác minh kiểu dữ liệu, múi giờ, số dòng, giá trị thiếu, trùng lặp, khoảng ngày thực tế hoặc các giá trị của `event_type`. Chưa chọn nhãn dự đoán hay khẳng định chất lượng dữ liệu. Việc đọc một dòng header và tính hash chỉ là kiểm tra file; không làm sạch hay biến đổi nội dung.

## Điều kiện hoàn thành

- File tồn tại đúng đường dẫn và không rỗng.
- Kích thước bản sao bằng bản gốc.
- SHA-256 của bản sao khớp bản gốc. Điều này xác nhận bản sao giống file hiện có, không chứng minh tính xác thực của nguồn tải.
- Manifest có thông tin kiểm tra; những thông tin nguồn chưa biết được để rõ là chưa biết.
- CSV bị loại khỏi Git và nhóm hiểu quy tắc không sửa dữ liệu gốc.

Không áp đặt quyền chỉ đọc ở hệ điều hành; sự bất biến hiện được bảo vệ bằng quy ước và mã hash. Các chương trình tương lai phải ghi đầu ra sang silver/gold, không ghi vào bronze.

**Điểm dừng:** sau các kiểm tra trên, chờ người dùng xác nhận mới thiết kế và triển khai Pipeline 2.
