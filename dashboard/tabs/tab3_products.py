"""
Tab 3: Product & Brand Intelligence Component (Task 2.4)
Author: Nhóm Thực Hiện (Data & AI Team)
Purpose: Xếp hạng ngành hàng, thương hiệu và phân tích Pareto 80/20
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dashboard.utils.data_loader import load_category_brand_stats

def render_tab3_products(filters: dict):
    """Render Tab 3: Xếp hạng Thương hiệu & Ngành hàng."""
    df_brand = load_category_brand_stats()
    if df_brand.empty:
        st.warning("Chưa có dữ liệu Thương hiệu. Vui lòng kiểm tra data/gold/category_brand_stats.parquet.")
        return

    selected_cat = filters.get("selected_category", "ALL")
    if selected_cat != "ALL":
        df_display = df_brand[df_brand['main_category'] == selected_cat]
    else:
        df_display = df_brand

    st.markdown("### Xếp Hạng Sản Phẩm & Thương Hiệu (Brand & Product Intelligence)")
    st.markdown("Phân tích cơ cấu doanh thu và tìm ra các đầu tàu kinh doanh theo nguyên lý Pareto 80/20.")

    # Top 10 Thương hiệu theo Doanh thu
    top_brands = df_display[df_display['brand'] != 'unknown'].groupby('brand', as_index=False).agg({
        'total_revenue': 'sum',
        'purchase_count': 'sum',
        'avg_price': 'mean'
    }).sort_values(by='total_revenue', ascending=False).head(10)

    col_chart1, col_chart2 = st.columns([6, 4])
    with col_chart1:
        # Đảo thứ tự để thương hiệu doanh thu cao nhất nằm trên cùng
        top_brands_sorted = top_brands.iloc[::-1]

        fig_brand = go.Figure(go.Bar(
            x=top_brands_sorted['total_revenue'],
            y=top_brands_sorted['brand'],
            orientation='h',
            marker=dict(
                color=top_brands_sorted['total_revenue'],
                colorscale='Blues'
            ),
            text=[f"${v:,.0f}" for v in top_brands_sorted['total_revenue']],
            textposition='auto'
        ))

        cat_title = "Toàn Sàn" if selected_cat == "ALL" else selected_cat.title()
        fig_brand.update_layout(
            title=f"<b>Top 10 Thương Hiệu Doanh Thu Lớn Nhất ({cat_title})</b>",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Doanh Thu ($)",
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        st.plotly_chart(fig_brand, width="stretch", key="products_chart_brand")

    with col_chart2:
        # Cơ cấu doanh thu theo Sub-category
        top_subs = df_display.groupby('sub_category', as_index=False)['total_revenue'].sum().sort_values(by='total_revenue', ascending=False).head(8)
        fig_pie = px.pie(
            top_subs,
            names='sub_category',
            values='total_revenue',
            title="<b>Cơ Cấu Doanh Thu Theo Nhóm Mặt Hàng</b>",
            hole=0.45
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=40, b=10),
            height=400
        )
        st.plotly_chart(fig_pie, width="stretch", key="products_chart_pie")

    # Thẻ thông tin Pareto phân tích động theo ngành hàng
    cat_label = "Toàn Sàn" if selected_cat == "ALL" else f"Ngành {selected_cat.title()}"
    valid_brands = top_brands[top_brands['brand'] != 'unknown'].reset_index(drop=True)
    
    if len(valid_brands) >= 2:
        top1_name = valid_brands.iloc[0]['brand'].upper()
        top1_rev = valid_brands.iloc[0]['total_revenue']
        top2_name = valid_brands.iloc[1]['brand'].upper()
        top2_rev = valid_brands.iloc[1]['total_revenue']
        total_cat_rev = df_display['total_revenue'].sum()
        share_pct = ((top1_rev + top2_rev) / total_cat_rev * 100) if total_cat_rev > 0 else 0

        st.markdown(f"""
        <div style="background: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.2); border-left: 4px solid #0ea5e9; color: var(--text-color); border-radius: 8px; padding: 14px 18px; margin-top: 15px;">
            <b>Góc Nhìn Kinh Doanh (Pareto Insight - {cat_label}):</b> 
            Hai thương hiệu dẫn đầu phân khúc là <b>{top1_name}</b> (${top1_rev:,.0f}) và <b>{top2_name}</b> (${top2_rev:,.0f}) 
            chiếm tới <b>{share_pct:.1f}%</b> tổng doanh số của {cat_label}. 
            Chiến lược tồn kho và ngân sách marketing nên ưu tiên tập trung vào 2 thương hiệu đầu tàu này để tối ưu hóa biên lợi nhuận.
        </div>
        """, unsafe_allow_html=True)
    elif len(valid_brands) == 1:
        top1_name = valid_brands.iloc[0]['brand'].upper()
        top1_rev = valid_brands.iloc[0]['total_revenue']
        st.markdown(f"""
        <div style="background: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.2); border-left: 4px solid #0ea5e9; color: var(--text-color); border-radius: 8px; padding: 14px 18px; margin-top: 15px;">
            <b>Góc Nhìn Kinh Doanh (Pareto Insight - {cat_label}):</b> 
            Thương hiệu áp đảo là <b>{top1_name}</b> với doanh thu <b>${top1_rev:,.0f}</b>.
        </div>
        """, unsafe_allow_html=True)
