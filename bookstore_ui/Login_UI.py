import streamlit as st

from bookstore_ui.bookstore import *


def login_section():
    # Login Section
    if not st.session_state.logged_in:
        st.divider()
        st.subheader("🔐 Login")
        # Clear fields if the flag is set
        if st.session_state.clear_fields:
            st.session_state.temp_username = ""
            st.session_state.temp_password = ""
            st.session_state.clear_fields = False  # Reset the flag
        # Temporary variables for login inputs
        username = st.text_input("Username", key="temp_username")
        password = st.text_input("Password", type="password", key="temp_password")
        if st.button("Login"):
            handle_login()

    # Create account

    # Initialize session state for the expander
    if not st.session_state.logged_in:
        if "show_create_account" not in st.session_state:
            st.session_state.show_create_account = False  # Expander starts collapsed
        
        # Toggle function for the expander
        def toggle_expander():
            st.session_state.show_create_account = not st.session_state.show_create_account
        
        # Main "Create a New Account" toggle button
        if not st.session_state.show_create_account:
            st.button("Create a New Account", on_click=toggle_expander)
            
        # Initialize session state for role
        if 'role' not in st.session_state or st.session_state.role not in ["staff", "manager"]:
            st.session_state.role = "staff"  # Default to 'staff'
        
        
        # Only show the expander if "show_create_account" is True
        if st.session_state.show_create_account:
            with st.expander("Create a New Account", expanded=True):
                # Input fields for creating a new account
                new_username = st.text_input("New Username", key="new_username")
                new_password = st.text_input("New Password", type="password", key="new_password")
                first_name = st.text_input("First Name", key="first_name")
                last_name = st.text_input("Last Name", key="last_name")
                role = st.selectbox("Role", ["staff", "manager"], key="role")
        
                if st.button("Create Account"):
                    if new_username and new_password and first_name and last_name:
                        response = add_user_api(new_username, new_password, first_name, last_name, role)
                        st.info(response)
        
                        # Reset form fields and collapse after success
                        st.session_state.new_username = ""
                        st.session_state.new_password = ""
                        st.session_state.first_name = ""
                        st.session_state.last_name = ""
                        st.session_state.role = "staff"  # Reset to default
                        st.session_state.show_create_account = False
                    else:
                        st.warning("All fields are required to create an account.")
    
def logout():
    st.success(f"Welcome, {st.session_state.username}!")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()