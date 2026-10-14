# Kế hoạch & Phân công Công việc: Thành viên 2 - Data Analyst & BI Lead

> **Vai trò:** Data Analyst & Trưởng nhóm Trực quan hóa (BI / Dashboard Lead)  
> **Phạm vi trách nhiệm:** Pipeline 3 (Analytics Aggregations), Pipeline 4 (Data Marts - Gold Layer), Pipeline 6 (Visualization / Streamlit Dashboard)  
> **Công nghệ chính:** Python, PySpark / DuckDB, Streamlit, Plotly, Pandas (chỉ dùng đọc bảng Gold nhẹ)  
> **Mục tiêu then chốt:** Biến đổi dữ liệu sạch thành các bảng phân tích nghiệp vụ TMĐT sâu sắc (KPIs, Phễu chuyển đổi, RFM) và xây dựng 1 **Dashboard Streamlit tổng thể** trực quan, đẹp mắt và phản hồi tức thì.

---

## 1. Tổng quan Trách nhiệm & Luồng công việc

```text
[data/silver/events_cleaned.parquet]
        │
        ▼ (Task 1: Business Analytics & Aggregations)
[src/analytics/business_kpis.py]
[src/analytics/funnel_analysis.py]
[src/analytics/customer_rfm.py]
        │
        ▼ (Task 2: Gold Data Marts Storage)
[data/gold/kpis_daily.parquet]
[data/gold/funnel_metrics.parquet]
[data/gold/category_brand_stats.parquet]
[data/gold/customer_segments.parquet]
        │
        ▼ (Task 3: Streamlit Interactive Dashboard)
[dashboard/app.py & components/] ─── Tích hợp Tab ML của Thành viên 3
```

---

## 2. Chi tiết các Task theo Timeline

### Giai đoạn 1: Khám phá Dữ liệu Mẫu & Thiết kế Wireframe (Ngày 1 – 3)
* [x] **Task DA-01: Khám phá nghiệp vụ trên tập mẫu (EDA)**
  * Nhận file `data/bronze/sample_100k.csv` từ Thành viên 1.
  * Phân tích các loại sự kiện: Tỷ lệ `view`, `cart`, `purchase`.
  * Xác định các câu hỏi kinh doanh cốt lõi:
    * Doanh thu đỉnh điểm rơi vào ngày nào/khung giờ nào?
    * Tỷ lệ khách xem xong bỏ đi (Drop-off) là bao nhiêu?
    * Những thương hiệu và ngành hàng nào mang lại 80% doanh thu (Nguyên lý Pareto)?
* [x] **Task DA-02: Thiết kế bố cục & Wireframe cho Dashboard**
  * Phác thảo cấu trúc Dashboard trên Streamlit gồm 4–5 Tabs chính:
    * **Tab 1:** Tổng quan chỉ số điều hành (Executive Overview)
    * **Tab 2:** Phân tích Phễu chuyển đổi & Hành vi (Funnel & Behavioral Analytics)
    * **Tab 3:** Xếp hạng Sản phẩm & Thương hiệu (Product & Brand Intelligence)
    * **Tab 4:** Phân khúc khách hàng RFM (Customer Segmentation)
    * **Tab 5:** Mô phỏng dự đoán đơn hàng bằng Machine Learning (Phối hợp cùng Thành viên 3)

---

### Giai đoạn 2: Tạo các Bảng Gold / Data Marts (Ngày 4 – 7)
* [x] **Task DA-03: Tính toán chỉ số KPIs kinh doanh theo ngày**
  * **File:** `src/analytics/business_kpis.py`
  * Đọc từ `data/silver/events_cleaned.parquet` bằng PySpark/DuckDB để tính:
    * Tổng GMV (Gross Merchandise Value), tổng lượt mua (`purchase count`).
    * Số lượng khách hoạt động hàng ngày (DAU - Daily Active Users).
    * Tỷ lệ chuyển đổi tổng thể hàng ngày: $\text{Conversion Rate} = \frac{\text{Tổng lượt purchase}}{\text{Tổng lượt session}} \times 100\%$.
    * Giá trị trung bình đơn hàng (AOV - Average Order Value): $\frac{\text{Doanh thu}}{\text{Số lượt purchase}}$.
    * Lưu kết quả: `data/gold/kpis_daily.parquet`.
* [x] **Task DA-04: Phân tích Phễu chuyển đổi (Funnel Analysis)**
  * **File:** `src/analytics/funnel_analysis.py`
  * Đo lường bước chuyển đổi: `view` $\rightarrow$ `cart` $\rightarrow$ `purchase`.
  * Tính tỷ lệ rơi rụng (Drop-off rate) ở từng bước, phân tích phễu theo từng ngành hàng chính (`main_category`).
  * Lưu kết quả: `data/gold/funnel_metrics.parquet`.
* [x] **Task DA-05: Thống kê Ngành hàng & Thương hiệu**
  * **File:** `src/analytics/category_brand_stats.py`
  * Nhóm theo `main_category`, `sub_category`, `brand` để tính: số lượt xem, số lượt mua, doanh thu, giá trung bình.
  * Lưu kết quả: `data/gold/category_brand_stats.parquet`.
* [x] **Task DA-06: Phân tích phân khúc khách hàng RFM**
  * **File:** `src/analytics/customer_rfm.py`
  * Tính toán cho từng `user_id`:
    * **R (Recency):** Số ngày từ lần tương tác cuối cùng đến hết tháng 10/2019.
    * **F (Frequency):** Tổng số phiên/sự kiện của người dùng.
    * **M (Monetary):** Tổng số tiền đã chi tiêu cho các sự kiện `purchase`.
  * Phân loại khách hàng: *Champions, Loyal Customers, Potential Loyalists, At Risk, Lost*.
  * Lưu kết quả: `data/gold/customer_segments.parquet`.

---

### Giai đoạn 3: Phát triển Dashboard Streamlit Hoàn chỉnh (Ngày 8 – 14)
* [x] **Task DA-07: Xây dựng khung ứng dụng Streamlit chuyên nghiệp**
  * **File:** `dashboard/app.py`
  * Cấu hình giao diện: Dark/Light Mode hiện đại, Sidebar bộ lọc (Filter theo ngày, ngành hàng, khoảng giá).
  * Sử dụng `@st.cache_data` để nạp các file parquet từ `data/gold/` giúp ứng dụng tải tức thì (<1 giây).
* [x] **Task DA-08: Triển khai các Biểu đồ Trực quan với Plotly**
  * Dựng thẻ Metric (KPI Cards) có so sánh delta.
  * Biểu đồ xu hướng Area Chart / Line Chart cho doanh thu theo thời gian.
  * Biểu đồ Funnel Chart hiển thị dòng chảy hành vi khách hàng.
  * Heatmap ma trận hoạt động theo 24 giờ x 7 ngày trong tuần.
  * Biểu đồ Treemap / Sunburst cho cơ cấu danh mục hàng hóa.
  * Scatter plot 2D/3D cho phân cụm khách hàng RFM.
* [x] **Task DA-09: Tích hợp Giao diện Dự đoán ML cùng Thành viên 3**
  * Dựng form người dùng tại Tab 5: Nhập số lượt xem, ngành hàng, giờ trong ngày $\rightarrow$ Gọi hàm dự đoán của Thành viên 3 $\rightarrow$ Hiển thị thanh Gauge xác suất mua hàng (%) và khuyến nghị kinh doanh.
* [x] **Task DA-10: Kiểm thử Dashboard & Chuẩn bị Demo**
  * Kiểm tra tính phản hồi mượt mà, tương thích 100% cả Light Mode & Dark Mode, hoạt ảnh biểu đồ chuyển động mượt.
  * Hoàn thiện tài liệu hướng dẫn vận hành và giải thích chi tiết các chỉ số biểu đồ tại `docs/dashboard_guide.md`.

---

## 3. Bản giao ước đầu ra (Deliverables)

| Tên đầu ra | Đường dẫn | Người tiếp nhận | Định dạng / Chi tiết |
| :--- | :--- | :--- | :--- |
| **Bảng Gold KPIs theo ngày** | `data/gold/kpis_daily.parquet` | Dashboard | File tổng hợp gọn nhẹ (~vài trăm KB) |
| **Bảng Gold Phễu hành vi** | `data/gold/funnel_metrics.parquet` | Dashboard | Tỷ lệ chuyển đổi và rơi rụng qua từng bước |
| **Bảng Gold Ngành hàng/Thương hiệu** | `data/gold/category_brand_stats.parquet` | Dashboard | Doanh thu, số lượt bán theo danh mục/brand |
| **Bảng Gold Phân khúc RFM** | `data/gold/customer_segments.parquet` | Dashboard | Điểm số R, F, M và nhóm khách hàng |
| **Ứng dụng Dashboard hoàn chỉnh** | `dashboard/app.py` | Người dùng & Giảng viên | Streamlit Web App chạy mượt mà, trực quan cao |
| **Tài liệu Hướng dẫn Dashboard** | `docs/dashboard_guide.md` | Báo cáo môn học | Hướng dẫn chạy và giải thích các chỉ số biểu đồ |
