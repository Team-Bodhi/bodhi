import time

import streamlit as st

from bookstore_ui.bookstore import *

# init session state

def init_session_state():
    # Login State Management
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "name" not in st.session_state:
        st.session_state.name = ""
    if "role" not in st.session_state:
        st.session_state.role = ""

    # Initialize session state variables
    if "temp_email" not in st.session_state:
        st.session_state.temp_email = ""
    if "temp_password" not in st.session_state:
        st.session_state.temp_password = ""
    if "clear_fields" not in st.session_state:
        st.session_state.clear_fields = False

@st.dialog("Create Account")
def create_account():
    with st.form("employee_account_form", clear_on_submit=False):  # Changed to false to keep form visible until success
        # Input fields for creating a new account
        new_email = st.text_input("Email", key="new_email")
        new_password = st.text_input("Password", type="password", key="new_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        first_name = st.text_input("First Name", key="first_name")
        last_name = st.text_input("Last Name", key="last_name")
        
        submitted = st.form_submit_button("Create Account")
        if submitted:
            if not all([new_email, new_password, confirm_password, first_name, last_name]):
                st.warning("All fields are required to create an account.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                response = add_user_api(new_email, new_password, first_name, last_name, "employee")
                
                # Check if the response indicates success
                if "successfully" in response.lower():
                    st.success(response)
                    st.session_state.clear_fields = True
                    time.sleep(1)  # Give user time to read the success message
                    st.rerun()
                else:
                    # Show error message but don't close the modal
                    st.error(response)

def login_section():
    # Splash Page Content
    st.title("📚 Bodhi Books Management System")
    st.header("Preserving Literary Treasures, One Page at a Time")
    
    st.write("Welcome to the Bodhi Books Management System — your gateway to efficiently managing our exclusive collection of rare and antique books.")
    
    st.write("This app is designed to empower our employees with the tools they need to:")
    st.markdown("""
    * Manage inventory of rare books
    * Create purchase orders for restocking
    * View sales records and generate reports
    """)
    
    st.write("Use the sidebar to navigate through the different sections of the app.")
    
    if not st.session_state.logged_in:
        st.divider()
        st.subheader("🔐 Employee Login")
        # Clear fields if the flag is set
        if st.session_state.clear_fields:
            st.session_state.temp_email = ""
            st.session_state.temp_password = ""
            st.session_state.clear_fields = False  # Reset the flag
        # Temporary variables for login inputs
        email = st.text_input("Email", key="temp_email")
        password = st.text_input("Password", type="password", key="temp_password")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Login"):
                if handle_login():
                    # Check if user is employee or admin
                    if st.session_state.role not in ["employee", "admin"]:
                        st.error("Access Denied. This portal is for employees only.")
                        st.session_state.logged_in = False
                        st.session_state.role = ""
                        st.session_state.name = ""
                    else:
                        st.rerun()

        # Create account button
        if not st.session_state.logged_in:
            st.session_state.show_create_account = True
            if st.session_state.show_create_account:
                if st.button("Create Employee Account"):
                    create_account()
    
def logout():
    st.success(f"Welcome, {st.session_state.name}!")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()