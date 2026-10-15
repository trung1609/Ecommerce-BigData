"""
Tab 5: ML Purchase Prediction Component (Task 2.4 & DA-09)
Author: Nhóm Thực Hiện (Data & AI Team)
Purpose: Giao diện mô phỏng dự đoán xác suất mua hàng của khách bằng Machine Learning & Explainable AI
"""

import streamlit as st
import plotly.graph_objects as go
import time

def render_tab5_ml_prediction():
    """Render Tab 5: Mô Phỏng Dự Đoán Mua Hàng Bằng Machine Learning."""
    st.markdown("### Mô Phỏng Dự Đoán Khả Năng Mua Hàng (ML Purchase Predictor)")
    st.markdown("""
    Mô hình dự đoán hành vi chốt đơn của khách hàng dựa trên dữ liệu các phiên duyệt web thương mại điện tử. 
    Nhập các thông số hành vi của phiên duyệt web để ước lượng xác suất khách hàng sẽ thực hiện hành vi **`purchase`**.
    """)

    col_input, col_result = st.columns([5, 5])

    with col_input:
        st.markdown("<b>Tham Số Hành Vi Phiên Duyệt:</b>", unsafe_allow_html=True)
        
        main_cat = st.selectbox(
            "Ngành hàng sản phẩm",
            options=["electronics", "appliances", "computers", "apparel", "auto", "furniture"],
            index=0
        )
        
        price = st.number_input(
            "Giá sản phẩm ($)",
            min_value=1.0,
            max_value=3000.0,
            value=299.0,
            step=10.0
        )
        
        view_count = st.slider(
            "Số lượt xem sản phẩm trong phiên",
            min_value=1,
            max_value=25,
            value=4
        )
        
        cart_count = st.slider(
            "Số lượt thêm giỏ hàng trong phiên",
            min_value=0,
            max_value=10,
            value=1
        )
        
        hour = st.slider(
            "Khung giờ truy cập (0h - 23h)",
            min_value=0,
            max_value=23,
            value=14
        )

        predict_btn = st.button("Chạy Mô Hình Dự Đoán", type="primary", width="stretch")

    # Tính toán đặc trưng và đóng góp vào xác suất
    base_prob = 5.0
    impact_cart = cart_count * 25.0
    impact_view = view_count * 3.5 if view_count >= 3 else 2.0
    impact_price = 10.0 if price < 200 else (-12.0 if price > 1000 else 0.0)
    impact_hour = 8.0 if 18 <= hour <= 22 else (3.0 if 12 <= hour <= 14 else 0.0)

    calculated_prob = base_prob + impact_cart + impact_view + impact_price + impact_hour
    prob = min(max(calculated_prob, 2.0), 96.0)

    with col_result:
        st.markdown("<b>Kết Quả Suy Luận Của Mô Hình:</b>", unsafe_allow_html=True)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Xác Suất Chốt Đơn (%)", 'font': {'size': 18}},
            number={'suffix': "%", 'font': {'color': '#0ea5e9', 'size': 36}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#0ea5e9"},
                'bgcolor': "rgba(128, 128, 128, 0.1)",
                'borderwidth': 1,
                'bordercolor': "rgba(128, 128, 128, 0.2)",
                'steps': [
                    {'range': [0, 30], 'color': 'rgba(239, 68, 68, 0.2)'},
                    {'range': [30, 70], 'color': 'rgba(245, 158, 11, 0.2)'},
                    {'range': [70, 100], 'color': 'rgba(16, 185, 129, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': "#10b981", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=45, b=10),
            height=250
        )
        st.plotly_chart(fig_gauge, width="stretch", key="ml_chart_gauge")

        # Khuyến nghị kinh doanh dựa theo xác suất
        if prob >= 70:
            rec_text = "<b>Khả Năng Chốt Đơn Rất Cao:</b> Khách hàng đang có ý định mua rõ rệt. Đề xuất: Hiển thị ưu đãi Flash Sale đếm ngược hoặc Miễn phí vận chuyển để chốt đơn ngay!"
            border_col = "#10b981"
        elif prob >= 40:
            rec_text = "<b>Khách Hàng Đang Đắn Đo:</b> Khách đã thêm giỏ hoặc xem nhiều lần. Đề xuất: Gợi ý sản phẩm tương tự hoặc đánh giá tích cực của người mua trước."
            border_col = "#f59e0b"
        else:
            rec_text = "<b>Khách Vãng Lai:</b> Chưa có dấu hiệu mua hàng cao. Đề xuất: Không làm phiền bằng quá nhiều pop-up, tập trung tối ưu tốc độ duyệt trang."
            border_col = "#ef4444"

        st.markdown(f"""
        <div style="background: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.2); border-left: 4px solid {border_col}; color: var(--text-color); border-radius: 8px; padding: 12px 16px; margin-bottom: 16px;">
            {rec_text}
        </div>
        """, unsafe_allow_html=True)

    # Feature Importance / Explainability (XAI)
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    with st.expander("Giải Thích Đóng Góp Của Các Đặc Trưng (Explainable AI - XAI)", expanded=True):
        feature_names = ["Hành Động Thêm Giỏ", "Lượt Xem Sản Phẩm", "Khung Giờ Mua Sắm", "Tác Động Mức Giá"]
        feature_weights = [impact_cart, impact_view, impact_hour, impact_price]
        colors = ['#10b981' if w >= 0 else '#ef4444' for w in feature_weights]

        fig_xai = go.Figure(go.Bar(
            x=feature_weights,
            y=feature_names,
            orientation='h',
            marker_color=colors,
            text=[f"{w:+.1f}%" for w in feature_weights],
            textposition='auto',
        ))
        fig_xai.update_layout(
            title="<b>Mức Độ Tác Động Lên Xác Suất Chốt Đơn</b>",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Đóng Góp Tương Đối (%)",
            margin=dict(l=20, r=20, t=35, b=20),
            height=200
        )
        st.plotly_chart(fig_xai, width="stretch", key="ml_chart_xai")
