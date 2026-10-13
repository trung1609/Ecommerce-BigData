# Hướng Dẫn Vận Hành & Khai Thác E-Commerce Analytics Dashboard

**Dự án:** Phân Tích Dữ Liệu Lớn & Dự Đoán Mua Hàng Thương Mại Điện Tử (42.4M sự kiện)  
**Tác giả:** Nhóm Dự Án (Data & AI Team)  
**Công nghệ:** Streamlit, Plotly, DuckDB, Parquet  

---

## 1. Hướng Dẫn Khởi Chạy Nhanh (Quickstart)

### Điều kiện tiên quyết
Đảm bảo đã kích hoạt môi trường ảo Python và cài đặt đầy đủ các thư viện:
```bash
pip install -r requirements.txt
```

### Lệnh khởi chạy Web Dashboard
Mở terminal tại thư mục gốc của dự án (`d:\Big Data\Ecommerce-BigData`) và chạy:
```bash
streamlit run dashboard/app.py
```

Ứng dụng sẽ tự động mở trên trình duyệt tại: **`http://localhost:8501`**.

---

## 2. Kiến Trúc & Thiết Kế Đa Nền Tảng (Design & Aesthetics)

1. **Thích Ứng 100% Light Mode & Dark Mode**:
   - Sử dụng các biến giao diện CSS chuẩn của Streamlit (`var(--secondary-background-color)`, `var(--text-color)`).
   - Nền biểu đồ Plotly trong suốt (`rgba(0,0,0,0)`), tự động tương thích khi người dùng chuyển đổi theme trong menu cài đặt của Streamlit.
2. **Hiệu Ứng Chuyển Động Mượt Mà (Smooth Animated Transitions)**:
   - Tất cả các biểu đồ đều tích hợp `transition: { duration: 750, easing: 'cubic-in-out' }`. Khi người dùng thay đổi ngành hàng hoặc khoảng ngày, các thanh cột, đường biểu diễn và biểu đồ quạt sẽ morphing chuyển động uyển chuyển mà không bị giật trang.
   - Thanh trượt thời gian tương tác (Date Range Slider & Quick Selectors: `7D`, `14D`, `All`) trên biểu đồ doanh thu hàng ngày.
3. **Tối Ưu Hiệu Năng Tức Thì**:
   - Đọc trực tiếp các bảng tổng hợp tầng Gold (`data/gold/*.parquet`) được tối ưu hoá qua DuckDB columnar engine.
   - Tốc độ tải và chuyển tab: **< 0.1 giây**.

---

## 3. Chi Tiết 5 Tab Điều Hành & Giá Trị Kinh Doanh

### Tab 1: Tổng Quan Chỉ Số (Executive Overview)
- **Mục tiêu:** Cung cấp cái nhìn bao quát về sức khỏe tài chính và lưu lượng sàn thương mại điện tử.
- **Thành phần:**
  - 4 Thẻ KPI: Tổng GMV ($229.8M), Đơn hàng thành công (742k), Tỷ lệ chuyển đổi TB (1.75%), DAU kỷ lục (574k khách).
  - Biểu đồ xu hướng GMV theo ngày: Phát hiện các đợt đỉnh sóng mua sắm và hỗ trợ bộ lọc zoom thời gian.
  - Donut Chart cơ cấu sự kiện: Tỷ lệ phân bổ giữa View (83%), Cart (15%) và Purchase (2%).

### Tab 2: Phễu Chuyển Đổi (Conversion Funnel)
- **Mục tiêu:** Định lượng độ rơi rụng (drop-off) qua từng chặng hành vi mua sắm.
- **Thành phần:**
  - Biểu đồ phễu 3 bước: `View` (35.6M) $\rightarrow$ `Cart` (6.2M) $\rightarrow$ `Purchase` (742k).
  - Đo lường drop-off: Tỷ lệ rơi rụng từ View sang Cart là **82.6%**, từ Cart sang Purchase là **88.0%**.
  - Bảng so sánh hiệu suất chuyển đổi theo từng ngành hàng: Giúp nhận diện ngành hàng nào có tỷ lệ chốt đơn cao nhất.

### Tab 3: Sản Phẩm & Thương Hiệu (Brand Intelligence)
- **Mục tiêu:** Phân tích mức độ tập trung thị phần và hiệu ứng Pareto (80/20).
- **Thành phần:**
  - Bảng xếp hạng Top 10 thương hiệu dẫn đầu doanh thu (Apple, Samsung áp đảo với hơn 70% GMV).
  - Cơ cấu danh mục sản phẩm (Electronics, Appliances chiếm tỷ trọng chi phối).
  - Phân tích Pareto động: Tự động tính toán tỷ trọng đóng góp của 2 thương hiệu đầu bảng theo ngành hàng được lọc.

### Tab 4: Phân Khúc Khách Hàng RFM (Customer Segmentation)
- **Mục tiêu:** Phân loại hơn 3 triệu khách hàng thành 6 nhóm hành vi để tối ưu chiến dịch Retention & Remarketing.
- **Các phân khúc:**
  1. **Champions (Khách VIP):** Vừa mua gần đây, mua thường xuyên và chi tiêu mạnh tay $\rightarrow$ Đặc quyền VIP, CSKH riêng.
  2. **Loyal Customers (Khách Thân Thiết):** Mua đều đặn, giá trị ổn định $\rightarrow$ Tích điểm, tặng quà tri ân.
  3. **Potential Loyalists (Khách Tiềm Năng):** Mua gần đây, chi tiêu khá $\rightarrow$ Upsell, gợi ý combo.
  4. **At Risk (Nguy Cơ Rời Bỏ):** Từng mua nhiều nhưng đã lâu không quay lại $\rightarrow$ Email kích hoạt, tặng voucher giảm giá lớn.
  5. **Hibernating (Ngủ Đông):** Tần suất thấp, giá trị thấp, đã lâu không ghé $\rightarrow$ Chiến dịch quét lại định kỳ.
  6. **Lost (Đã Rời Bỏ):** Không có tương tác trong thời gian dài $\rightarrow$ Không tốn chi phí retargeting trực tiếp.

### Tab 5: Dự Đoán Mua Hàng ML & Giải Thích Đặc Trưng (ML Purchase Predictor & XAI)
- **Mục tiêu:** Mô phỏng suy luận xác suất chốt đơn của một phiên duyệt web theo thời gian thực kết hợp AI Explainability.
- **Thành phần:**
  - Bộ điều khiển tham số: Ngành hàng, Giá tiền, Số lượt xem, Số lượt thêm giỏ, Khung giờ truy cập.
  - Đồng hồ đo xác suất (Gauge Chart) chuyển động mượt mà kèm phân loại khuyến nghị kinh doanh theo màu sắc (Xanh / Vàng / Đỏ).
  - **Explainable AI (XAI)**: Biểu đồ thanh ngang chỉ rõ mức độ tác động của từng đặc trưng (Hành động thêm giỏ, Lượt xem, Khung giờ, Mức giá) vào quyết định cuối cùng của mô hình.

---

## 4. Kịch Bản Demo Cho Nhóm (Presentation Pitch)
1. **Mở đầu**: Giới thiệu quy mô dữ liệu khổng lồ (42.4 triệu dòng sự kiện) được xử lý qua kiến trúc Data Lakehouse (Bronze $\rightarrow$ Silver $\rightarrow$ Gold) và thời gian truy vấn tầng Gold siêu tốc (<0.1s).
2. **Khảo sát kinh doanh (Tab 1 & 2)**: Nhấn mạnh doanh thu đỉnh điểm và điểm nghẽn rớt đơn lớn nhất tại bước `View` $\rightarrow$ `Cart`.
3. **Phân tích chiến lược (Tab 3 & 4)**: Trình diễn định luật Pareto trên thương hiệu và chỉ rõ phân khúc khách hàng VIP đem lại phần lớn dòng tiền.
4. **Trình diễn công nghệ AI (Tab 5)**: Thao tác thay đổi số lượng giỏ hàng và khung giờ để biểu đồ Gauge và XAI nhảy animation tức thì, minh chứng khả năng ứng dụng AI vào cá nhân hóa trải nghiệm người dùng theo thời gian thực.
