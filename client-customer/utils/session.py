import streamlit as st


def initialize_session_state():
    """Initialize all session state variables"""
    # Cart state
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    if 'total_amount' not in st.session_state:
        st.session_state.total_amount = 0.0
        
    # Navigation state
    if 'current_book' not in st.session_state:
        st.session_state.current_book = None
    if 'page' not in st.session_state:
        st.session_state.page = 'main'
    if 'checkout_stage' not in st.session_state:
        st.session_state.checkout_stage = 'cart'
    if 'last_action' not in st.session_state:
        st.session_state.last_action = None
        
    # Authentication state
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'permissions' not in st.session_state:
        st.session_state.permissions = None
    if 'auth_error' not in st.session_state:
        st.session_state.auth_error = None 