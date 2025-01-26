import streamlit as st


def apply_custom_styles():
    st.markdown("""
    <style>
        .book-card {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            margin-bottom: 1rem;
        }
        .cart-item {
            padding: 0.5rem;
            border-bottom: 1px solid #eee;
        }
        .price-tag {
            color: #2e7d32;
            font-weight: bold;
        }
        .stock-warning {
            color: #d32f2f;
            font-size: 0.9rem;
        }
        .success-msg {
            color: #2e7d32;
            padding: 0.5rem;
            border-radius: 0.25rem;
            background-color: #e8f5e9;
        }
        .error-msg {
            color: #d32f2f;
            padding: 0.5rem;
            border-radius: 0.25rem;
            background-color: #ffebee;
        }
    </style>
    """, unsafe_allow_html=True) 