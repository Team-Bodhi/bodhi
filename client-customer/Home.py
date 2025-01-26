import streamlit as st

from components.book_details import render_book_details
from components.book_grid import render_main_page
from components.checkout_form import render_checkout_form
from components.shopping_cart import render_shopping_cart
from styles.custom_styles import apply_custom_styles
from utils.session import initialize_session_state

# Must be the first Streamlit command
st.set_page_config(layout="wide", page_title="Bodhi Bookstore")

# Apply custom styles
apply_custom_styles()

# Initialize session state
initialize_session_state()

# Render shopping cart sidebar (except on checkout page)
if st.session_state.page != 'checkout':
    render_shopping_cart()

# Render main content based on current page
if st.session_state.page == 'details' and st.session_state.current_book:
    render_book_details()
elif st.session_state.page == 'checkout':
    render_checkout_form()
else:
    render_main_page() 