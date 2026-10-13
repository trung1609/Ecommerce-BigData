# src/analytics — Data Marts & Business Aggregations (Tầng Gold)

Phụ trách bởi: **Nhóm Dự Án (Data & AI Team)**  
Công nghệ: **Python, DuckDB, PyArrow**

---

## 1. Mục tiêu
Chuyển đổi dữ liệu sạch `data/silver/events_cleaned.parquet` (16 partitions, ~42.4 triệu dòng) thành 4 bảng tổng hợp nghiệp vụ gọn nhẹ trong `data/gold/`, phục vụ trực tiếp cho Web Dashboard Streamlit và báo cáo phân tích.

---

## 2. Cấu trúc Modules

| File Script | Đầu ra (Data Mart) | Mục đích nghiệp vụ |
| :--- | :--- | :--- |
| `business_kpis.py` | `data/gold/kpis_daily.parquet` | GMV, DAU, tổng đơn hàng, tỷ lệ chuyển đổi và giá trị đơn hàng trung bình (AOV) theo 31 ngày. |
| `funnel_analysis.py` | `data/gold/funnel_metrics.parquet` | Phễu hành vi (`view` $\rightarrow$ `cart` $\rightarrow$ `purchase`), tỷ lệ chuyển tiếp và tỷ lệ rơi rụng tổng thể & theo ngành hàng. |
| `category_brand_stats.py` | `data/gold/category_brand_stats.parquet` | Doanh thu, số lượt xem/mua, khoảng giá và thị phần của top thương hiệu và ngành hàng. |
| `customer_rfm.py` | `data/gold/customer_segments.parquet` | Chấm điểm Recency, Frequency, Monetary và phân loại 3+ triệu khách hàng (*Champions, Loyal, At Risk...*). |
| `run_all_gold_pipelines.py` | Cả 4 bảng trên | Master Runner chạy tự động toàn bộ 4 pipeline tuần tự với log chi tiết. |

---

## 3. Hướng dẫn Chạy Pipeline

### Chạy nhanh trên dữ liệu mẫu (100k dòng):
```bash
python src/analytics/run_all_gold_pipelines.py --sample
```

### Chạy toàn bộ dữ liệu Silver (~42.4 triệu dòng):
```bash
python src/analytics/run_all_gold_pipelines.py --full
```

Thời gian thực thi toàn bộ: **~64 giây** trên máy tính cá nhân.
