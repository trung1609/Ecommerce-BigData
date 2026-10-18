"""
Dashboard Data Loader Utility (Task 2.1)
Author: Nhóm Thực Hiện (Data & AI Team)
Purpose: Loader đọc dữ liệu từ các file Gold Parquet, tự động nhận diện file mới nhất
"""

from pathlib import Path
import pandas as pd
import duckdb
import streamlit as st

# Đường dẫn thư mục gold
BASE_DIR = Path(__file__).resolve().parents[2]
GOLD_DIR = BASE_DIR / "data" / "gold"

def load_kpis_daily() -> pd.DataFrame:
    """Nạp bảng kpis_daily.parquet (GMV, DAU, Orders, Conversion Rate theo ngày và theo ngành hàng)."""
    file_path = GOLD_DIR / "kpis_daily.parquet"
    if not file_path.exists():
        st.error(f"Không tìm thấy file: {file_path}. Vui lòng chạy run_all_gold_pipelines.py trước!")
        return pd.DataFrame()
    # Đọc trực tiếp bằng pandas pyarrow để luôn lấy dữ liệu mới nhất trên đĩa
    df = pd.read_parquet(file_path)
    df['event_date'] = pd.to_datetime(df['event_date'])
    return df

def load_funnel_metrics() -> pd.DataFrame:
    """Nạp bảng funnel_metrics.parquet (Phễu chuyển đổi & drop-off)."""
    file_path = GOLD_DIR / "funnel_metrics.parquet"
    if not file_path.exists():
        return pd.DataFrame()
    return pd.read_parquet(file_path)

def load_category_brand_stats() -> pd.DataFrame:
    """Nạp bảng category_brand_stats.parquet (Thống kê ngành hàng & thương hiệu)."""
    file_path = GOLD_DIR / "category_brand_stats.parquet"
    if not file_path.exists():
        return pd.DataFrame()
    return pd.read_parquet(file_path)

def load_customer_segments_summary() -> pd.DataFrame:
    """Nạp tổng hợp phân khúc khách hàng từ customer_segments.parquet."""
    file_path = GOLD_DIR / "customer_segments.parquet"
    if not file_path.exists():
        return pd.DataFrame()
    con = duckdb.connect(database=':memory:')
    summary_query = f"""
    SELECT
        segment,
        COUNT(*) AS user_count,
        ROUND(AVG(recency_days), 1) AS avg_recency,
        ROUND(AVG(frequency), 1) AS avg_frequency,
        ROUND(AVG(monetary), 2) AS avg_monetary,
        ROUND(SUM(monetary), 2) AS total_segment_revenue,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS user_share_pct
    FROM read_parquet('{file_path.as_posix()}')
    GROUP BY segment
    ORDER BY total_segment_revenue DESC
    """
    return con.execute(summary_query).fetchdf()

def get_available_categories() -> list:
    """Lấy danh sách các ngành hàng chính có sẵn."""
    funnel_df = load_funnel_metrics()
    if funnel_df.empty:
        return ["ALL"]
    cats = funnel_df[funnel_df['main_category'] != 'ALL']['main_category'].dropna().tolist()
    return ["ALL"] + sorted(cats)

def load_cross_sell_rules() -> pd.DataFrame:
    """Nạp bảng luật liên kết cross_sell_rules.parquet."""
    file_path = GOLD_DIR / "cross_sell_rules.parquet"
    if not file_path.exists():
        return pd.DataFrame()
    return pd.read_parquet(file_path)
