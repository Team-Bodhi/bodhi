from datetime import datetime

import streamlit as st


def format_date(date_str):
    """Format a date string to a readable format"""
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime("%B %d, %Y")
    except:
        return "Date unavailable"

def show_toast(message, is_error=False):
    """Show a temporary notification"""
    if is_error:
        st.error(message)
    else:
        st.success(message)
    # Clear the message after 3 seconds
    st.session_state.last_action = None

def navigate_to(page, book=None):
    """Navigate to a different page in the app"""
    if page == 'details':
        st.session_state.current_book = book
    st.session_state.page = page
    st.rerun() 