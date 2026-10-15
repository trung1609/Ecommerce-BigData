# dashboard/ — E-Commerce Big Data Intelligence Dashboard

Phụ trách bởi: **Nhóm Dự án (Data & AI Team)**  
Công nghệ: **Streamlit, Plotly, DuckDB, Parquet (Gold Layer)**

---

## 1. Tổng quan
Dashboard cung cấp giao diện trực quan hóa dữ liệu toàn diện cho 42.4 triệu sự kiện thương mại điện tử (tháng 10/2019), đọc từ các Data Marts tầng Gold (`data/gold/*.parquet`).

Ứng dụng được thiết kế theo kiến trúc Modular Component-based hiện đại với **5 Tabs điều hành**:
1. **Tổng Quan Chỉ Số (Executive Overview):** Thẻ KPIs điều hành (GMV, đơn hàng, tỷ lệ chuyển đổi, DAU đỉnh điểm) & xu hướng doanh thu hàng ngày.
2. **Phễu Chuyển Đổi (Conversion Funnel):** Mô hình phễu 3 bước (`view` $\rightarrow$ `cart` $\rightarrow$ `purchase`), đo lường tỷ lệ rơi rụng (drop-off) toàn sàn và theo từng ngành hàng.
3. **Sản Phẩm & Thương Hiệu (Brand Intelligence):** Top 10 thương hiệu doanh thu lớn nhất (Apple, Samsung...), cơ cấu mặt hàng và phân tích Pareto 80/20.
4. **Phân Khúc Khách Hàng RFM (Customer Segmentation):** Phân loại hơn 3 triệu khách hàng thành 6 nhóm (*Champions, Loyal, Potential, At Risk, Hibernating, Lost*) cùng khuyến nghị kinh doanh.
5. **Dự Đoán Mua Hàng ML (Purchase Predictor):** Gọi mô hình Spark MLlib đã lưu để ước lượng xác suất mua hàng và so sánh với kịch bản không có lượt thêm giỏ.

---

## 2. Hướng Dẫn Khởi Chạy

Chạy lệnh sau tại thư mục gốc của dự án:
```bash
streamlit run dashboard/app.py
```

Trình duyệt sẽ tự động mở tại địa chỉ: **`http://localhost:8501`**.
Tốc độ nạp dữ liệu và phản hồi thao tác: **< 0.1 giây** (nhờ cơ chế `@st.cache_data`).

Tab 5 cần mô hình đã được huấn luyện tại `models/best_purchase_model/`. Xem [hướng dẫn ML](../src/ml/README.md) để tạo features và train model. Nếu model chưa tồn tại, tab sẽ hiển thị thông báo thay vì dùng xác suất giả lập.
