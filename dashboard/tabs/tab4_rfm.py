"""
Tab 4: Customer RFM Segmentation Component (Task 2.4)
Author: Nhóm Thực Hiện (Data & AI Team)
Purpose: Phân khúc 3+ triệu khách hàng theo mô hình RFM & Đề xuất hành động kinh doanh
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dashboard.utils.data_loader import load_customer_segments_summary

def render_tab4_rfm(filters: dict):
    """Render Tab 4: Phân khúc Khách hàng RFM."""
    df_rfm = load_customer_segments_summary()
    if df_rfm.empty:
        st.warning("Chưa có dữ liệu Phân khúc RFM. Vui lòng kiểm tra data/gold/customer_segments.parquet.")
        return

    st.markdown("### 👥 Phân Khúc Khách Hàng RFM (Customer Segmentation)")
    st.markdown("Phân loại **3.021.435 người dùng** dựa trên 3 tiêu chí cốt lõi: **Recency** (Mới tương tác), **Frequency** (Tần suất), **Monetary** (Chi tiêu).")

    # Hiển thị số liệu 3 nhóm tiêu biểu
    champions = df_rfm[df_rfm['segment'] == 'Champions']
    loyal = df_rfm[df_rfm['segment'] == 'Loyal Customers']
    at_risk = df_rfm[df_rfm['segment'] == 'At Risk']

    champ_count = champions['user_count'].iloc[0] if not champions.empty else 0
    champ_avg_spend = champions['avg_monetary'].iloc[0] if not champions.empty else 0
    loyal_count = loyal['user_count'].iloc[0] if not loyal.empty else 0
    at_risk_count = at_risk['user_count'].iloc[0] if not at_risk.empty else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🏆 Khách VIP (Champions)</div>
            <div class="metric-value">{champ_count:,} <span style="font-size: 1rem; color: #94a3b8;">users</span></div>
            <div class="metric-delta delta-positive">Chi tiêu TB: ${champ_avg_spend:,.2f}/khách</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💎 Khách Trung Thành (Loyal)</div>
            <div class="metric-value">{loyal_count:,} <span style="font-size: 1rem; color: #94a3b8;">users</span></div>
            <div class="metric-delta delta-positive">Tần suất ghé thăm ổn định</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⚠️ Nguy Cơ Rời Bỏ (At Risk)</div>
            <div class="metric-value">{at_risk_count:,} <span style="font-size: 1rem; color: #94a3b8;">users</span></div>
            <div class="metric-delta delta-negative">Cần gửi Voucher tái kích hoạt</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns([5, 5])
    with col_chart1:
        # Tỷ trọng người dùng theo phân khúc
        fig_user_pie = px.pie(
            df_rfm,
            names='segment',
            values='user_count',
            title="<b>Phân Bổ Số Lượng Khách Hàng</b>",
            color='segment',
            color_discrete_map={
                'Champions': '#10b981',
                'Loyal Customers': '#3b82f6',
                'Potential Loyalists': '#60a5fa',
                'At Risk': '#f59e0b',
                'Hibernating': '#ec4899',
                'Lost / Casual Visitors': '#64748b'
            },
            template="plotly_dark",
            hole=0.4
        )
        fig_user_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=40, b=10),
            height=380
        )
        st.plotly_chart(fig_user_pie, width="stretch", key="rfm_chart_pie")

    with col_chart2:
        # Đóng góp doanh thu của từng phân khúc
        fig_rev_bar = px.bar(
            df_rfm,
            x='total_segment_revenue',
            y='segment',
            orientation='h',
            title="<b>Đóng Góp Doanh Thu Từng Phân Khúc ($)</b>",
            labels={'total_segment_revenue': 'Tổng Doanh Thu ($)', 'segment': 'Phân Khúc'},
            color='total_segment_revenue',
            color_continuous_scale='Viridis'
        )
        fig_rev_bar.update_layout(
            yaxis=dict(autorange="reversed"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            height=380
        )
        st.plotly_chart(fig_rev_bar, width="stretch", key="rfm_chart_bar")

    st.markdown("<b>Bảng Chiến Lược Hành Động Cho Từng Phân Khúc:</b>", unsafe_allow_html=True)
    st.dataframe(
        df_rfm[['segment', 'user_count', 'avg_recency', 'avg_frequency', 'avg_monetary', 'user_share_pct']].rename(
            columns={
                'segment': 'Phân Khúc',
                'user_count': 'Số Khách Hàng',
                'avg_recency': 'Ngày Kể Từ Lần Cuối',
                'avg_frequency': 'Tần Suất TB',
                'avg_monetary': 'Chi Tiêu TB ($)',
                'user_share_pct': 'Tỷ Trọng (%)'
            }
        ),
        width="stretch"
    )
