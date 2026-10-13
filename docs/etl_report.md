# Báo cáo Kỹ thuật ETL & Tầng Dữ liệu Silver (Pipeline 1 - 4)

> **Môn học:** Phân tích và Tích hợp Dữ liệu Lớn  
> **Người thực hiện:** Thành viên 1 - Data Engineer  
> **Ngày hoàn thành:** 13/10/2026  
> **Tập dữ liệu nguồn:** REES46 eCommerce Behavior Events (`2019-Oct.csv`)

---

## 1. Tổng quan Kết quả Xử lý Big Data

| Tiêu chí | Trước khi xử lý (Bronze) | Sau khi xử lý (Silver) | Tỷ lệ tối ưu / Thay đổi |
| :--- | :--- | :--- | :--- |
| **Định dạng lưu trữ** | File văn bản `CSV` | File dạng cột `Parquet` (Snappy) | Nén cột tối ưu, tốc độ đọc nhanh gấp 15 lần |
| **Dung lượng lưu trữ** | **5.67 GB** (5,668,612,855 byte) | **2.06 GB** (16 files partitioned) | **Giảm 63.7%** dung lượng đĩa |
| **Tổng số bản ghi** | ~42,448,764 dòng | **42,349,874 dòng** | Loại bỏ **98,890 dòng** lỗi/giá âm/trùng lặp |
| **Số lượng cột** | 9 cột gốc | **14 cột chuẩn hóa** | Bổ sung 5 cột phái sinh phân tích |
| **Thời gian quét dữ liệu** | ~10 - 15 phút (trên CSV) | **2.44 giây** (trên Parquet) | **Tăng tốc độ gấp ~300 lần** |

---

## 2. Cấu trúc Schema tầng Silver (`data/silver/events_cleaned.parquet`)

| STT | Tên cột | Kiểu dữ liệu | Ý nghĩa & Quy tắc chuẩn hóa |
| :---: | :--- | :--- | :--- |
| 1 | `event_time` | `Timestamp` | Thời điểm sự kiện (UTC), chuẩn hóa từ dạng String chuỗi |
| 2 | `event_date` | `Date` | Ngày phát sinh sự kiện (`yyyy-MM-dd`), dùng để lọc nhanh |
| 3 | `hour` | `Integer` | Khung giờ trong ngày (0 – 23), phục vụ Heatmap hành vi |
| 4 | `day_of_week` | `Integer` | Thứ trong tuần (1 = Chủ Nhật, 2 = Thứ Hai, ... 7 = Thứ Bảy) |
| 5 | `event_type` | `String` | Loại hành vi: `view` (xem), `cart` (thêm giỏ), `purchase` (mua) |
| 6 | `product_id` | `Long` | Định danh duy nhất của sản phẩm |
| 7 | `category_id` | `Long` | Mã phân loại danh mục gốc |
| 8 | `category_code`| `String` | Chuỗi danh mục đầy đủ (Điền `unknown.unknown` nếu rỗng) |
| 9 | `main_category`| `String` | Ngành hàng cấp 1 (Tách chuỗi: vd `electronics`, `appliances`) |
| 10 | `sub_category` | `String` | Ngành hàng cấp 2 (Tách chuỗi: vd `smartphone`, `audio`) |
| 11 | `brand` | `String` | Thương hiệu sản phẩm (Điền `unknown` nếu rỗng) |
| 12 | `price` | `Double` | Giá bán sản phẩm (Đã lọc sạch các giá trị âm hoặc bằng 0) |
| 13 | `user_id` | `Long` | Mã định danh khách hàng |
| 14 | `user_session` | `String` | Mã phiên truy cập của khách hàng |

---

## 3. Các quy tắc ETL đã áp dụng (`src/etl/clean_events.py`)
1. **Làm sạch chuỗi thời gian:** Cắt bỏ hậu tố `" UTC"`, chuyển sang định dạng thời gian chuẩn `TimestampType` để thực hiện được các hàm thời gian trong Spark.
2. **Xử lý Null & Chuẩn hóa Text:** Các trường văn bản quan trọng không bị loại bỏ hoàn toàn mà được gán nhãn `"unknown"` để không làm mất thông tin hành vi mua sắm.
3. **Lọc dữ liệu rác (Data Integrity):** Loại bỏ triệt để các giao dịch có `price <= 0` hoặc `user_id` rỗng.
4. **Khử trùng lặp (Deduplication):** Loại bỏ các sự kiện trùng khớp hoàn toàn trên bộ định danh `[event_time, event_type, product_id, user_id, user_session]`.
5. **Tối ưu hóa ghi phân vùng:** Coalesce thành 16 partitions cân bằng để tối ưu hóa I/O cho ổ cứng máy tính cá nhân.
