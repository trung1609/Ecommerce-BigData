# Hướng Dẫn Demo & Báo Cáo Thay Đổi: Thành Viên 1 (Data Engineer)

> **Người thực hiện:** Thành viên 1 - Data Engineer / Pipeline Lead  
> **Phạm vi:** Pipeline 1 (Raw Data) $\rightarrow$ Pipeline 2 (Ingestion) $\rightarrow$ Pipeline 3 (ETL Core) $\rightarrow$ Pipeline 4 (Storage Silver)  
> **Mục tiêu:** Xử lý 5.67 GB dữ liệu thô (~42.4 triệu dòng) thành Parquet tầng Silver sạch sẽ, giảm 63.7% dung lượng và tăng tốc truy vấn gấp ~300 lần.

---

## 1. TỔNG HỢP NHANH CÂU LỆNH DEMO (QUICK CHEAT SHEET)

```powershell
# LỆNH 1: DEMO LIVE ETL LÀM SẠCH (Chạy trong ~13 giây, show 5 dòng sạch và số dòng rác bị loại)
python src/etl/clean_events.py

# LỆNH 2: DEMO TỐC ĐỘ QUÉT 42.3 TRIỆU DÒNG TẦNG SILVER PARQUET (Chạy trong 2.4 giây)
python scripts/preview_silver_data.py
```

---

## 🔄 2. BẢNG SO SÁNH TRỌNG TÂM: TRƯỚC VÀ SAU KHI LÀM SẠCH

### A. Về Dữ liệu & Các Cột (Data & Schema Transformation)

| Trường dữ liệu | Trước khi làm sạch (Bronze CSV) | Sau khi làm sạch (Silver Parquet) | Ý nghĩa & Lý do kỹ thuật (Trả lời Thầy) |
| :--- | :--- | :--- | :--- |
| **Thời gian (`event_time`)** | Chuỗi text có đuôi `" UTC"` (vd: `2019-10-01 00:00:00 UTC`) | Chuẩn hóa sang `Timestamp` chuẩn | Cho phép Spark dùng các hàm xử lý thời gian toán học thay vì xử lý chuỗi. |
| **Phái sinh thời gian** *(Mới)* | ❌ Chưa có | ✅ **`event_date`**: Ngày (`yyyy-MM-dd`)<br>✅ **`hour`**: Khung giờ (`0 – 23`)<br>✅ **`day_of_week`**: Thứ (`1 = CN ... 7 = T7`) | • **`event_date`**: Phục vụ phân vùng đĩa (Partitioning).<br>• **`hour` & `day_of_week`**: Giúp TV2 vẽ Heatmap khung giờ vàng; TV3 làm feature chu kỳ cho ML. |
| **Danh mục (`category_code`)** | Chuỗi dài phân cấp (vd: `electronics.smartphone`), nhiều ô rỗng `null` | ✅ Tách thành **`main_category`** (Cấp 1: `electronics`)<br>✅ Tách thành **`sub_category`** (Cấp 2: `smartphone`) | • **Tránh quét chuỗi chậm**: Thay vì `LIKE '%...%'` trên 42M dòng, Spark lọc theo cột cực nhanh.<br>• **Giảm chiều cho ML**: Giảm từ hàng ngàn mã chi tiết về mười mấy ngành hàng chính, tránh vỡ RAM khi One-Hot Encoding.<br>• **Hỗ trợ BI**: Làm bộ lọc phân cấp vĩ mô/vi mô trên Dashboard. |
| **Giá trị Null / Missing** | Ô rỗng hoặc `null` ở `brand`, `category_code`, `user_session` | Điền nhãn `"unknown"`, `"unknown_session"` | Bảo toàn dữ liệu hành vi người dùng, tránh bị drop mất dòng khi phân tích. |
| **Dữ liệu rác & Lỗi** | Tồn tại giao dịch có `price <= 0`, `user_id` rỗng, trùng lặp sự kiện | Lọc sạch 100% dòng có `price <= 0`, khử trùng lặp theo tổ hợp 5 khóa | Đảm bảo tính toàn vẹn (Data Integrity) cho báo cáo doanh thu và mô hình dự đoán. |
| **Tổng số cột** | **9 cột gốc** | **14 cột chuẩn hóa** | Đầy đủ thông tin phục vụ cả BI và ML. |

---

### B. Về Hiệu Năng & Lưu Trữ (System Benchmark trên 42.4M dòng)

| Tiêu chí | Trước xử lý (Bronze CSV) | Sau xử lý (Silver Parquet) | Mức độ cải thiện |
| :--- | :--- | :--- | :--- |
| **Định dạng file** | File văn bản phẳng `CSV` | File dạng cột `Parquet` (nén Snappy) | Tối ưu hóa đọc theo cột (Columnar I/O) |
| **Dung lượng lưu trữ** | **5.67 GB** | **2.06 GB** (16 partitions) | **Giảm 63.7%** dung lượng ổ cứng |
| **Số lượng bản ghi** | 42,448,764 dòng | **42,349,874 dòng** | Loại bỏ chính xác **98,890 dòng lỗi/rác** |
| **Thời gian quét dữ liệu** | Mất **10 - 15 phút** | **2.44 giây** | **Tăng tốc gấp ~300 lần** |

---

## 💻 3. CÔNG NGHỆ SỬ DỤNG & TRÁCH NHIỆM TRONG DỰ ÁN

| Công nghệ | Phiên bản / Vị trí | Trách nhiệm & Vai trò kỹ thuật trong Task | Hậu quả nếu KHÔNG sử dụng |
| :--- | :--- | :--- | :--- |
| **Apache Spark / PySpark** | `3.5.1` (Core Engine) | **Động cơ tính toán phân tán:** Xử lý song song 42.4 triệu dòng trên RAM bằng DataFrame API; thực hiện toàn bộ logic bóc tách, lọc lỗi và khử trùng lặp. | Nếu dùng Pandas thông thường sẽ bị **tràn RAM (Out-Of-Memory)** và treo máy ngay lập tức. |
| **Java JDK** | `17 LTS` (Runtime) | **Môi trường máy ảo (JVM):** Cung cấp nền tảng chạy ngầm cho Apache Spark (vốn được viết bằng Scala chạy trên JVM). | Lệnh Python gọi Spark sẽ báo lỗi `JAVA_HOME is not set` và không khởi tạo được SparkSession. |
| **Hadoop Winutils** | `3.3.x` (`C:\hadoop\bin`) | **Cầu nối hệ thống tập tin Windows:** Cung cấp các thư viện native (`winutils.exe`, `hadoop.dll`) để phân quyền file POSIX trên Windows NTFS. | Spark đọc được file nhưng đến bước `df.write.parquet()` sẽ bị crash lỗi phân quyền hệ thống tập tin. |
| **Apache Parquet** | Định dạng tầng Silver | **Lưu trữ dạng cột (Columnar Storage):** Lưu trữ nhị phân tối ưu cho Big Data; chỉ đọc đúng các cột cần phân tích thay vì quét toàn bộ dòng. | Truy vấn chậm (mất 10-15 phút) vì phải quét toàn bộ 5.67 GB file CSV thô. |
| **Snappy Compression** | Thuật toán nén Parquet | **Nén dữ liệu tốc độ cao:** Nén dung lượng từ 5.67 GB xuống 2.06 GB (giảm 63.7%) với tốc độ giải nén cực nhanh hàng trăm MB/s. | Dung lượng đĩa tăng gấp 3 lần; tốc độ giải nén các thuật toán khác (như Gzip) rất tốn CPU. |
| **Coalesce (16 Partitions)** | `clean_df.coalesce(16)` | **Tối ưu hóa phân vùng & I/O:** Gom thành 16 file (~130 MB/file khớp chuẩn vàng 128MB Block Size của Big Data); tận dụng tối đa 16 luồng CPU song song. | Tránh lỗi **Small Files Problem** (hàng trăm file nhỏ làm nghẽn ổ đĩa) hoặc 1 file duy nhất (không đọc song song được). |
| **Explicit StructType Schema** | `src/ingestion/load_data.py` | **Định nghĩa Schema tường minh:** Khai báo sẵn 9 trường dữ liệu (Long, Double, String) ngay khi đọc CSV. | Tránh việc Spark phải quét qua 42.4 triệu dòng 2 lần để đoán kiểu dữ liệu (`inferSchema`), tiết kiệm 50% thời gian nạp. |

---

## 🛠️ 4. CHI TIẾT CÁC BƯỚC VÀ CÂU LỆNH THỰC HIỆN

### Bước 1: Kiểm tra môi trường (Chạy trước khi thuyết trình)
```powershell
python -c "import pyspark; print('PySpark version:', pyspark.__version__)"
java -version
```

### Bước 2: Demo Ingestion & Data Contract (Pipeline 1 & 2)
```powershell
python src/ingestion/extract_sample.py

# Đọc CSV với Explicit StructType Schema 9 cột (không dùng inferSchema chậm)
python src/ingestion/load_data.py
```

### Bước 3: Demo Live ETL Làm sạch (Pipeline 3 - Điểm nhấn chính)
```powershell
# Chạy live làm sạch trên 100k dòng mẫu (chỉ mất ~13 giây)
python src/etl/clean_events.py
```
* **Kết quả in ra Terminal:** Loại bỏ 136 dòng rác, lưu vào `sample_cleaned_100k.parquet`, hiển thị 5 dòng mẫu có đủ 14 cột.
---

### Bước 4: Lệnh quét toàn bộ dữ liệu sạch tầng Silver
```powershell
python scripts/preview_silver_data.py
```
## 5. GỢI Ý KỊCH BẢN NÓI TRỌNG TÂM KHI THUYẾT TRÌNH (2 PHÚT)

1. **Mở đầu & Demo Live ETL (Gõ `python src/etl/clean_events.py`):**
   > *"Thưa Thầy/Cô, ở vai trò Data Engineer, nhiệm vụ của em là chuẩn hóa tập dữ liệu 5.67 GB. Em xin demo trực tiếp script làm sạch [`src/etl/clean_events.py`]. Trong 13 giây thực thi, PySpark đã loại bỏ các dòng rác có giá âm, khử trùng lặp và chuyển hóa 9 cột thô thành **14 cột sạch**.*
   > * *Em tách thời gian thành `event_date`, `hour`, `day_of_week` để phục vụ phân vùng đĩa và vẽ Heatmap.*
   > * *Em tách danh mục thành `main_category` và `sub_category` để tối ưu truy vấn theo cột và giảm chiều cho mô hình ML."*

2. **Demo Tốc độ Silver Parquet (Gõ `python scripts/preview_silver_data.py`):**
   > *"Khi áp dụng pipeline lên toàn bộ tập dữ liệu, em lưu trữ dưới dạng Parquet nén Snappy gồm 16 partitions. Như Thầy/Cô thấy, lệnh quét toàn bộ **42,349,874 dòng** chỉ mất đúng **2.44 giây**, dung lượng giảm từ **5.67 GB xuống 2.06 GB** (tiết kiệm 63.7%). Dữ liệu chuẩn mực này đã sẵn sàng để chuyển giao cho **Thành viên 2** trình bày phần Dashboard."*
