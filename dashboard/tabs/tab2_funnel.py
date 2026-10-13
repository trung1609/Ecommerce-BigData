"""
Tab 2: Funnel Analytics Component (Task 2.4)
Author: Nhóm Thực Hiện (Data & AI Team)
Purpose: Phân tích phễu chuyển đổi (Funnel Chart, Tỷ lệ rơi rụng theo bước & theo ngành hàng)
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from dashboard.utils.data_loader import load_funnel_metrics

def render_tab2_funnel(filters: dict):
    """Render Tab 2: Phân tích Phễu Chuyển Đổi."""
    df_funnel = load_funnel_metrics()
    if df_funnel.empty:
        st.warning("Chưa có dữ liệu Phễu chuyển đổi. Vui lòng kiểm tra data/gold/funnel_metrics.parquet.")
        return

    selected_cat = filters.get("selected_category", "ALL")

    # Lấy dòng dữ liệu tương ứng với category được chọn
    cat_row = df_funnel[df_funnel['main_category'] == selected_cat]
    if cat_row.empty:
        cat_row = df_funnel[df_funnel['main_category'] == 'ALL']

    row = cat_row.iloc[0]

    st.markdown("### 🌪️ Phân Tích Phễu Chuyển Đổi & Hành Vi (Conversion Funnel)")
    st.markdown(f"Đo lường hành trình người dùng: **Xem sản phẩm (View)** ➡️ **Thêm giỏ hàng (Cart)** ➡️ **Chốt đơn (Purchase)** *(Đang xem: `{selected_cat}`)*.")

    # 3 Thẻ chỉ số chuyển đổi phễu
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">👁️ Bước 1: Lượt Xem (Views)</div>
            <div class="metric-value">{int(row['view_sessions']):,} <span style="font-size: 1rem; color: #94a3b8;">phiên</span></div>
            <div class="metric-delta delta-positive">100% Lưu Lượng Ban Đầu</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🛒 Bước 2: Thêm Giỏ (Cart)</div>
            <div class="metric-value">{int(row['cart_sessions']):,} <span style="font-size: 1rem; color: #94a3b8;">phiên</span></div>
            <div class="metric-delta delta-positive">Tỷ lệ thêm giỏ: {row['view_to_cart_rate_pct']}% (Rơi rụng: {row['view_to_cart_drop_pct']}%)</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💳 Bước 3: Mua Hàng (Purchase)</div>
            <div class="metric-value">{int(row['purchase_sessions']):,} <span style="font-size: 1rem; color: #94a3b8;">phiên</span></div>
            <div class="metric-delta delta-positive">Chuyển đổi tổng thể: {row['overall_conversion_rate_pct']}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

    col_chart, col_table = st.columns([6, 4])
    with col_chart:
        # Biểu đồ Phễu Funnel Chart bằng Plotly
        stages = ['1. Xem Hàng (View)', '2. Thêm Giỏ (Cart)', '3. Mua Hàng (Purchase)']
        values = [row['view_sessions'], row['cart_sessions'], row['purchase_sessions']]
        
        fig_funnel = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            opacity=0.9,
            marker={"color": ["#3b82f6", "#f59e0b", "#10b981"]}
        ))
        fig_funnel.update_layout(
            title=f"<b>Mô Hình Phễu Khách Hàng ({selected_cat})</b>",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            height=380
        )
        st.plotly_chart(fig_funnel, width="stretch", key="funnel_chart_main")

    with col_table:
        st.markdown("<b>Bảng So Sánh Tỷ Lệ Chuyển Đổi Các Ngành Hàng</b>", unsafe_allow_html=True)
        display_df = df_funnel[df_funnel['main_category'] != 'ALL'][
            ['main_category', 'view_sessions', 'purchase_sessions', 'overall_conversion_rate_pct']
        ].copy()
        display_df.columns = ['Ngành Hàng', 'Lượt Xem', 'Lượt Mua', 'Tỷ Lệ Mua (%)']
        st.dataframe(
            display_df.sort_values(by='Tỷ Lệ Mua (%)', ascending=False),
            width="stretch",
            height=340
        )
