"""Interactive dashboard tab backed by the saved Member 3 purchase model."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st


@st.cache_resource
def _load_purchase_model():
    from src.ml.predict import load_purchase_model

    return load_purchase_model()


def _session_features(
    view_count: int,
    cart_count: int,
    distinct_products: int,
    distinct_categories: int,
    average_price: float,
    hour: int,
    is_weekend: bool,
    category: str,
) -> dict[str, int | float | str]:
    return {
        "view_count": view_count,
        "cart_count": cart_count,
        "distinct_products": distinct_products,
        "distinct_categories": distinct_categories,
        "avg_price": average_price,
        "max_price": average_price,
        "hour_of_day": hour,
        "is_weekend": int(is_weekend),
        "top_category_viewed": category,
    }


def render_tab5_ml_prediction() -> None:
    """Render the real-model purchase prediction and a no-cart what-if."""
    st.markdown("### Dự đoán khả năng mua hàng")
    st.caption("Xác suất được tính bởi mô hình Spark MLlib đã huấn luyện.")

    input_column, result_column = st.columns([1, 1])
    with input_column:
        category = st.selectbox(
            "Danh mục được xem nhiều nhất",
            options=[
                "electronics.smartphone",
                "electronics.clocks",
                "computers.notebook",
                "appliances.kitchen.washer",
                "appliances.environment.air_heater",
                "__unknown__",
            ],
        )
        average_price = st.number_input(
            "Giá trung bình sản phẩm",
            min_value=0.0,
            max_value=3000.0,
            value=299.0,
            step=10.0,
        )
        view_count = st.slider("Lượt xem", min_value=1, max_value=25, value=4)
        distinct_products = st.slider(
            "Sản phẩm khác nhau đã xem",
            min_value=1,
            max_value=view_count,
            value=min(3, view_count),
        )
        distinct_categories = st.slider(
            "Danh mục khác nhau đã xem", min_value=1, max_value=10, value=2
        )
        cart_count = st.slider("Lượt thêm giỏ", min_value=0, max_value=10, value=1)
        hour = st.slider("Giờ bắt đầu phiên", min_value=0, max_value=23, value=14)
        is_weekend = st.checkbox("Phiên diễn ra vào cuối tuần")
        predict_clicked = st.button(
            "Chạy dự đoán", type="primary", width="stretch"
        )

    if not predict_clicked:
        with result_column:
            st.info("Nhập đặc trưng phiên rồi chạy dự đoán.")
        return

    features = _session_features(
        view_count=view_count,
        cart_count=cart_count,
        distinct_products=distinct_products,
        distinct_categories=distinct_categories,
        average_price=average_price,
        hour=hour,
        is_weekend=is_weekend,
        category=category,
    )
    baseline_features = {**features, "cart_count": 0}

    try:
        from src.ml.predict import predict_purchase_probability

        model = _load_purchase_model()
        probability = predict_purchase_probability(features, model=model)
        baseline_probability = predict_purchase_probability(
            baseline_features, model=model
        )
    except FileNotFoundError:
        with result_column:
            st.error(
                "Chưa tìm thấy model. Hãy chạy `python -m src.ml.train` "
                "sau khi tạo Gold features."
            )
        return
    except Exception as error:
        with result_column:
            st.error(f"Không thể chạy inference: {error}")
        return

    with result_column:
        st.metric(
            "Xác suất mua hàng",
            f"{probability:.1%}",
            delta=f"{(probability - baseline_probability) * 100:+.1f} điểm % so với phiên không thêm giỏ",
        )
        figure = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=probability * 100,
                number={"suffix": "%"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#168c80"},
                    "steps": [
                        {"range": [0, 30], "color": "#f4d9d5"},
                        {"range": [30, 70], "color": "#f5e7bd"},
                        {"range": [70, 100], "color": "#cce8df"},
                    ],
                },
            )
        )
        figure.update_layout(height=250, margin={"l": 20, "r": 20, "t": 25, "b": 10})
        st.plotly_chart(figure, width="stretch", key="ml_model_probability")

        if probability >= 0.7:
            st.success("Tín hiệu mua cao: cân nhắc hiển thị ưu đãi hoặc thanh toán nhanh.")
        elif probability >= 0.4:
            st.warning("Tín hiệu mua trung bình: có thể gợi ý sản phẩm liên quan.")
        else:
            st.info("Tín hiệu mua thấp: tiếp tục tối ưu trải nghiệm duyệt sản phẩm.")

        with st.expander("So sánh kịch bản"):
            st.write(f"Có {cart_count} lượt thêm giỏ: **{probability:.1%}**")
            st.write(f"Không có lượt thêm giỏ: **{baseline_probability:.1%}**")
