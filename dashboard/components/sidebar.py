"""
Sidebar Controls Component (Task 2.3)
Author: Data & BI Team
Purpose: Thanh điều khiển Sidebar tối giản, tinh tế, thích ứng hoàn hảo cả Light & Dark mode
"""

from datetime import date
import streamlit as st
from dashboard.utils.data_loader import get_available_categories

def render_sidebar() -> dict:
    """Render Sidebar tối giản và trả về từ điển các bộ lọc người dùng đã chọn."""
    with st.sidebar:
        # 1. Thẻ Brand Header thích ứng đa theme
        st.markdown("""
        <div class="sidebar-brand-card">
            <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: var(--text-color); letter-spacing: -0.01em;">E-Commerce Analytics</h3>
            <p style="margin: 3px 0 0 0; font-size: 0.78rem; opacity: 0.7; color: var(--text-color);">Big Data BI Platform</p>
        </div>
        """, unsafe_allow_html=True)

        # 2. Bộ lọc điều hành
        st.markdown('<div class="sidebar-section-title">BỘ LỌC DỮ LIỆU</div>', unsafe_allow_html=True)

        # Bộ lọc khoảng ngày
        date_range = st.date_input(
            "Khoảng thời gian",
            value=(date(2019, 10, 1), date(2019, 10, 31)),
            min_value=date(2019, 10, 1),
            max_value=date(2019, 10, 31),
            help="Chọn phạm vi ngày phân tích trong tháng 10/2019"
        )

        # Bộ lọc ngành hàng chính
        available_cats = get_available_categories()
        selected_cat = st.selectbox(
            "Ngành hàng chính",
            options=available_cats,
            index=0,
            help="Chọn 'ALL' để xem toàn sàn hoặc chọn cụ thể từng ngành hàng"
        )

        # 3. Thẻ Thông Số Hệ Thống
        st.markdown('<div class="sidebar-section-title">THÔNG SỐ HỆ THỐNG</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="sidebar-meta-box">
            <div class="sidebar-meta-row">
                <span class="sidebar-meta-label">Dữ liệu nguồn:</span>
                <span class="sidebar-meta-val">42.4M dòng</span>
            </div>
            <div class="sidebar-meta-row">
                <span class="sidebar-meta-label">Định dạng lưu:</span>
                <span class="sidebar-meta-val">Gold Parquet</span>
            </div>
            <div class="sidebar-meta-row">
                <span class="sidebar-meta-label">Engine:</span>
                <span class="sidebar-meta-val">DuckDB In-Memory</span>
            </div>
            <div class="sidebar-meta-row">
                <span class="sidebar-meta-label">Độ trễ:</span>
                <span class="sidebar-meta-val">&lt; 0.05s</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 4. Thẻ Đơn Vị Thực Hiện
        st.markdown("""
        <div class="sidebar-author-card">
            <div style="font-size: 0.88rem; color: var(--text-color); font-weight: 600;">Nhóm Thực Hiện</div>
            <div style="color: var(--text-color); opacity: 0.7; font-size: 0.78rem;">Phân Tích Dữ Liệu Lớn & AI</div>
        </div>
        """, unsafe_allow_html=True)

    return {
        "date_range": date_range,
        "selected_category": selected_cat
    }
