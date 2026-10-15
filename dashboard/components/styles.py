"""
Custom CSS & Styling Component (Task 2.2)
Author: Data & BI Team
Purpose: Thiết kế giao diện đa theme (thích ứng 100% hoàn hảo cả Dark Mode & Light Mode)
"""

import streamlit as st

def apply_custom_css():
    """Chèn CSS tùy chỉnh nâng tầm thẩm mỹ giao diện Dashboard thích ứng cả Light & Dark."""
    custom_css = """
    <style>
        /* Khử khoảng trống thừa phía trên cùng của Streamlit */
        header[data-testid="stHeader"] {
            height: 2.2rem !important;
            background: transparent !important;
        }
        .main .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 96%;
        }

        /* Keyframe Entrance Animation (chỉ áp dụng nhẹ cho header lần đầu) */
        @keyframes subtleFadeUp {
            from {
                opacity: 0.9;
                transform: translateY(2px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .dashboard-header {
            animation: subtleFadeUp 0.15s ease-out forwards;
        }

        /* Banner tiêu đề chính - Tự động đồng bộ theo theme */
        .dashboard-header {
            background: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 22px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
        }
        .dashboard-title {
            font-size: 1.85rem;
            font-weight: 700;
            color: var(--text-color);
            margin: 0;
            padding: 0;
            letter-spacing: -0.02em;
        }
        .dashboard-subtitle {
            opacity: 0.75;
            font-size: 0.95rem;
            margin-top: 5px;
            margin-bottom: 0;
        }

        /* Thẻ Metric Card tự động theo theme */
        .metric-card {
            background: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 10px;
            padding: 16px 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
            transition: transform 0.15s ease, border-color 0.15s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            border-color: rgba(56, 189, 248, 0.5);
        }
        .metric-label {
            font-size: 0.8rem;
            font-weight: 600;
            opacity: 0.7;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .metric-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-color);
            margin-top: 4px;
            margin-bottom: 4px;
            letter-spacing: -0.02em;
        }
        .metric-delta {
            font-size: 0.8rem;
            font-weight: 500;
        }
        .delta-positive {
            color: #10b981;
        }
        .delta-negative {
            color: #ef4444;
        }

        /* Huy hiệu trạng thái (Badges) */
        .badge {
            display: inline-block;
            padding: 3px 9px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 600;
            margin-right: 6px;
        }
        .badge-gold {
            background: rgba(234, 179, 8, 0.15);
            color: #eab308;
            border: 1px solid rgba(234, 179, 8, 0.3);
        }
        .badge-fast {
            background: rgba(14, 165, 233, 0.15);
            color: #0ea5e9;
            border: 1px solid rgba(14, 165, 233, 0.3);
        }
        .badge-live {
            background: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        /* Tùy chỉnh thanh tab */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
            margin-bottom: 18px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 9px 18px;
            font-weight: 600;
            font-size: 0.88rem;
            border: 1px solid rgba(128, 128, 128, 0.2);
            background-color: var(--secondary-background-color);
            color: var(--text-color);
            opacity: 0.85;
        }
        .stTabs [aria-selected="true"] {
            opacity: 1 !important;
            border-color: #0ea5e9 !important;
            color: #0ea5e9 !important;
        }

        /* Sidebar thích ứng đa theme */
        .sidebar-brand-card {
            background: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 10px;
            padding: 16px 14px;
            text-align: center;
            margin-bottom: 16px;
        }
        .sidebar-section-title {
            font-size: 0.78rem;
            font-weight: 700;
            opacity: 0.7;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 14px;
            margin-bottom: 8px;
        }
        .sidebar-meta-box {
            background: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 8px;
            padding: 10px 12px;
            margin-top: 6px;
            margin-bottom: 14px;
        }
        .sidebar-meta-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 0;
            font-size: 0.8rem;
            border-bottom: 1px solid rgba(128, 128, 128, 0.1);
        }
        .sidebar-meta-row:last-child {
            border-bottom: none;
        }
        .sidebar-meta-label {
            opacity: 0.7;
        }
        .sidebar-meta-val {
            color: var(--text-color);
            font-weight: 600;
        }
        .sidebar-author-card {
            background: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            margin-top: 14px;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
