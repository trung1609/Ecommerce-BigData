"""
Tab 1: Executive Overview Component (Task 2.4)
Author: Nhóm Thực Hiện (Data & AI Team)
Purpose: Tổng quan chỉ số điều hành (KPI Cards & Biểu đồ doanh thu hàng ngày)
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dashboard.utils.data_loader import load_kpis_daily

def render_tab1_overview(filters: dict):
    """Render Tab 1: Tổng quan chỉ số kinh doanh."""
    df_kpi = load_kpis_daily()
    if df_kpi.empty:
        st.warning("Chưa có dữ liệu KPIs. Vui lòng kiểm tra file data/gold/kpis_daily.parquet.")
        return

    # Áp dụng bộ lọc khoảng ngày nếu có
    date_range = filters.get("date_range")
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df_filtered = df_kpi[(df_kpi['event_date'] >= start_date) & (df_kpi['event_date'] <= end_date)]
    else:
        df_filtered = df_kpi

    # Áp dụng bộ lọc ngành hàng
    selected_cat = filters.get("selected_category", "ALL")
    if 'main_category' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['main_category'] == selected_cat]

    if df_filtered.empty:
        st.info(f"Không có dữ liệu trong khoảng thời gian đã chọn cho ngành hàng '{selected_cat}'.")
        return

    # Tính các chỉ số tổng hợp
    total_gmv = df_filtered['gmv'].sum()
    total_orders = df_filtered['purchase_count'].sum()
    total_views = df_filtered['view_count'].sum()
    total_carts = df_filtered['cart_count'].sum()
    avg_conv_rate = df_filtered['conversion_rate_pct'].mean()
    peak_dau = df_filtered['dau'].max()
    overall_aov = total_gmv / total_orders if total_orders > 0 else 0

    cat_label = "Toàn Sàn (ALL)" if selected_cat == "ALL" else f"Ngành Hàng: {selected_cat.title()}"
    st.markdown(f"### Tổng Quan Chỉ Số Điều Hành — {cat_label}")
    st.markdown("Các thước đo cốt lõi phản ánh hiệu suất kinh doanh trong tháng 10/2019.")

    # Render 4 Thẻ KPI chính
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Tổng Doanh Thu (GMV)</div>
            <div class="metric-value">${total_gmv:,.0f}</div>
            <div class="metric-delta delta-positive">31 Ngày Phân Tích</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Tổng Đơn Hàng Thành Công</div>
            <div class="metric-value">{int(total_orders):,}</div>
            <div class="metric-delta delta-positive">AOV: ${overall_aov:.2f}/đơn</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Tỷ Lệ Chuyển Đổi Trung Bình</div>
            <div class="metric-value">{avg_conv_rate:.2f}%</div>
            <div class="metric-delta delta-positive">Purchase / Session</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Khách Hoạt Động Cao Điểm</div>
            <div class="metric-value">{int(peak_dau):,}</div>
            <div class="metric-delta delta-positive">DAU Kỷ Lục</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

    # Biểu đồ xu hướng Doanh thu & Đơn hàng theo ngày
    col_chart1, col_chart2 = st.columns([7, 3])
    with col_chart1:
        fig_revenue = go.Figure()
        fig_revenue.add_trace(go.Scatter(
            x=df_filtered['event_date'],
            y=df_filtered['gmv'],
            mode='lines+markers',
            name='Doanh Thu ($)',
            line=dict(color='#3b82f6', width=3),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.12)'
        ))

        fig_revenue.update_layout(
            title=dict(
                text=f"<b>Xu Hướng Doanh Thu Hàng Ngày — {cat_label}</b>",
                x=0.0,
                y=0.98,
                xanchor='left',
                yanchor='top'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                title=dict(text="Ngày", standoff=10),
                rangeselector=dict(
                    buttons=list([
                        dict(count=7, label="7D", step="day", stepmode="backward"),
                        dict(count=14, label="14D", step="day", stepmode="backward"),
                        dict(step="all", label="All")
                    ]),
                    x=1.0,
                    xanchor="right",
                    y=1.05,
                    yanchor="bottom",
                    bgcolor="rgba(128, 128, 128, 0.15)",
                    activecolor="#0ea5e9"
                ),
                rangeslider=dict(visible=True, thickness=0.06, bgcolor="rgba(128, 128, 128, 0.08)")
            ),
            yaxis_title="Doanh Thu ($)",
            hovermode="x unified",
            margin=dict(l=20, r=20, t=65, b=55),
            height=410
        )
        st.plotly_chart(fig_revenue, width="stretch", key="overview_chart_revenue")

    with col_chart2:
        # Cơ cấu hành vi: View vs Cart vs Purchase
        event_types = ['Lượt Xem (Views)', 'Thêm Giỏ (Carts)', 'Mua Hàng (Purchases)']
        event_counts = [total_views, total_carts, total_orders]
        fig_donut = go.Figure(data=[go.Pie(
            labels=event_types,
            values=event_counts,
            hole=.55,
            marker_colors=['#38bdf8', '#f59e0b', '#10b981']
        )])
        fig_donut.update_layout(
            title="<b>Cơ Cấu Sự Kiện</b>",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=40, b=10),
            height=390
        )
        st.plotly_chart(fig_donut, width="stretch", key="overview_chart_donut")
