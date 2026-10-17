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

    # =========================================================================
    # PHẦN MỚI: GỢI Ý SẢN PHẨM LIÊN QUAN (TWO-STAGE RECOMMENDATION SYSTEM)
    # =========================================================================
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("### Gợi Ý Sản Phẩm Liên Quan (Two-Stage Recommendation Engine)")
    st.markdown("""
    Hệ thống khai phá luật liên kết giỏ hàng (Market Basket Association) kết hợp bộ lọc ngữ nghĩa đa tiêu chí 
    (Độ tương thích thương hiệu, phân khúc giá và mức độ tín nhiệm của sản phẩm).
    """)

    try:
        from src.analytics.market_basket import (
            get_recommendations_for_product, 
            get_featured_source_products,
            search_catalog_products,
            format_product_name
        )

        col_search, col_select = st.columns([5, 5])
        with col_search:
            search_kw = st.text_input(
                "Tìm kiếm sản phẩm (tên, ngành hàng, hãng hoặc ID):",
                value="",
                placeholder="Ví dụ: bàn phím, tai nghe, laptop, apple, samsung, 5800808...",
                key="rec_search_kw"
            )

        # Danh sách lựa chọn mặc định từ các sản phẩm tiêu biểu
        featured_items = get_featured_source_products()
        default_map = {item['name']: item['id'] for item in featured_items}

        if search_kw.strip():
            matched_items = search_catalog_products(search_kw, limit=10)
            if matched_items:
                options_map = {item['display_name']: int(item['product_id']) for item in matched_items}
            else:
                st.caption(f"Không tìm thấy sản phẩm khớp với '{search_kw}'. Đang hiển thị sản phẩm mẫu tiêu biểu:")
                options_map = default_map
        else:
            options_map = default_map

        with col_select:
            selected_label = st.selectbox(
                "Chọn sản phẩm để xem gợi ý liên quan:",
                options=list(options_map.keys()),
                index=0,
                key="rec_src_select"
            )

        chosen_id = options_map[selected_label]
        recs_df, meta = get_recommendations_for_product(chosen_id, top_k=3)

        if "error" in meta:
            st.info(f"Thông báo: {meta['error']}. Vui lòng thử một sản phẩm khác.")
            return

        # Thẻ thông tin sản phẩm nguồn
        badge_type = (
            f'<span class="badge badge-live">GỢI Ý MUA KÈM (CROSS-SELL BUNDLE)</span>'
            if meta['badge_class'] == "badge-live"
            else f'<span class="badge badge-gold">SẢN PHẨM THAY THẾ (SUBSTITUTE)</span>'
        )

        src_title = format_product_name(meta['src_product_id'], meta['src_category'], meta['src_brand'], meta['src_price'])

        st.markdown(f"""
        <div style="background: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 8px; padding: 12px 18px; margin-top: 10px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <span style="font-size: 0.85rem; opacity: 0.8;">Sản phẩm đang xem:</span>
                    <b style="font-size: 1.05rem; margin-left: 6px;">{src_title}</b> 
                </div>
                <div>
                    {badge_type}
                </div>
            </div>
            <div style="font-size: 0.85rem; margin-top: 6px; opacity: 0.85;">
                Ngành hàng: <code>{meta['src_category']}</code> | Chiến lược: <b>{meta['recommendation_type']}</b> | Độ tương quan luật kết hợp (Lift): <b>{meta['rule_lift']:.2f}x</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not recs_df.empty:
            st.markdown("<b>Top 3 Sản Phẩm Được Đề Xuất Nhiều Nhất:</b>", unsafe_allow_html=True)
            cols = st.columns(len(recs_df))
            for idx, (_, row) in enumerate(recs_df.iterrows()):
                with cols[idx]:
                    match_pct = row['rank_score'] * 100
                    brand_match = "Cùng Hãng" if row['brand'] == meta['src_brand'].lower() and row['brand'] != 'unknown' else "Khác Hãng"
                    price_diff_pct = ((row['price'] - meta['src_price']) / meta['src_price']) * 100
                    rec_title = format_product_name(int(row['product_id']), row['category_code'], row['brand'], row['price'])

                    st.markdown(f"""
                    <div style="background: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.2); border-left: 4px solid #0ea5e9; border-radius: 8px; padding: 14px; min-height: 200px;">
                        <div style="font-size: 0.8rem; opacity: 0.7; text-transform: uppercase;">Top #{idx+1} Gợi Ý</div>
                        <div style="font-weight: 700; font-size: 0.95rem; margin-top: 4px; color: var(--text-color);">{rec_title}</div>
                        <div style="font-size: 0.85rem; color: #0ea5e9; margin-top: 2px;">{row['category_code']}</div>
                        <div style="font-size: 1.2rem; font-weight: 700; color: #10b981; margin-top: 6px;">${row['price']:.2f}</div>
                        <div style="font-size: 0.8rem; opacity: 0.8; margin-top: 2px;">
                            Thương hiệu: <b>{str(row['brand']).upper()}</b> ({brand_match})
                        </div>
                        <div style="font-size: 0.8rem; opacity: 0.8; margin-top: 2px;">
                            Độ lệch giá: <b>{price_diff_pct:+.1f}%</b> so với sản phẩm xem
                        </div>
                        <div style="margin-top: 12px;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
                                <span>Độ phù hợp:</span>
                                <b>{match_pct:.1f}%</b>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(min(max(row['rank_score'], 0.0), 1.0))
    except Exception as e:
        st.warning(f"Tính năng gợi ý đang được cập nhật dữ liệu: {e}")
