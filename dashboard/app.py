"""
E-Commerce Big Data Intelligence Dashboard (Main Application Entry Point)
Author: Nhóm Thực Hiện (Data & AI Team)
Technology Stack: Streamlit, Plotly, DuckDB, Parquet (Gold Layer)
Usage:
    streamlit run dashboard/app.py
"""

import sys
from pathlib import Path
import streamlit as st

# Thêm root workspace vào sys.path để import các module nội bộ
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import các components & tabs
from dashboard.components.styles import apply_custom_css
from dashboard.components.sidebar import render_sidebar
from dashboard.tabs.tab1_overview import render_tab1_overview
from dashboard.tabs.tab2_funnel import render_tab2_funnel
from dashboard.tabs.tab3_products import render_tab3_products
from dashboard.tabs.tab4_rfm import render_tab4_rfm
from dashboard.tabs.tab5_ml_prediction import render_tab5_ml_prediction

def main():
    # Cấu hình giao diện toàn cục
    st.set_page_config(
        page_title="E-Commerce Big Data Intelligence",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Nạp Custom CSS Glassmorphism & Dark Mode
    apply_custom_css()

    # Render Header Banner
    st.markdown("""
    <div class="dashboard-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="dashboard-title">E-Commerce Big Data Intelligence</h1>
                <p class="dashboard-subtitle">
                    Phân tích Hành vi Khách hàng & Dự đoán Khả năng Mua hàng trên Dữ liệu Lớn Thương mại Điện tử
                </p>
            </div>
            <div>
                <span class="badge badge-gold">TẦNG GOLD</span>
                <span class="badge badge-fast">DUCKDB ENGINE</span>
                <span class="badge badge-live">LIVE ANALYTICS</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Render Sidebar điều khiển & nhận bộ lọc
    filters = render_sidebar()

    # Tạo 5 Tabs điều hành chính
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 1. Tổng Quan Chỉ Số",
        "🌪️ 2. Phễu Chuyển Đổi",
        "🏷️ 3. Sản Phẩm & Thương Hiệu",
        "👥 4. Phân Khúc RFM",
        "🔮 5. Dự Đoán Mua Hàng ML"
    ])

    with tab1:
        render_tab1_overview(filters)

    with tab2:
        render_tab2_funnel(filters)

    with tab3:
        render_tab3_products(filters)

    with tab4:
        render_tab4_rfm(filters)

    with tab5:
        render_tab5_ml_prediction()

    # Footer
    st.markdown("""
    <div style="margin-top: 50px; text-align: center; color: #475569; font-size: 0.8rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px;">
        Dự án môn Phân tích và Tích hợp Dữ liệu lớn | Nhóm 3 người | Báo cáo Phân tích Hành vi & Dự đoán Mua hàng TMĐT
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
