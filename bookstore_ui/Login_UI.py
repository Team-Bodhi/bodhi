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
    if "temp_username" not in st.session_state:
        st.session_state.temp_username = ""
    if "temp_password" not in st.session_state:
        st.session_state.temp_password = ""
    if "clear_fields" not in st.session_state:
        st.session_state.clear_fields = False

@st.dialog("Create Account")
def create_account():
    with st.form("purchase_order_form", clear_on_submit=True):
        # Input fields for creating a new account
        new_username = st.text_input("New Username", key="new_username")
        new_password = st.text_input("New Password", type="password", key="new_password")
        first_name = st.text_input("First Name", key="first_name")
        last_name = st.text_input("Last Name", key="last_name")
        role = st.selectbox("Role", ["staff", "manager"], key="role")
        
        submitted = st.form_submit_button("Create Account")
        if submitted:
            if new_username and new_password and first_name and last_name:
                response = add_user_api(new_username, new_password, first_name, last_name, role)
                st.info(response)
                st.rerun()
            else:
                st.warning("All fields are required to create an account.")

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
    # FIXME add way to restrict people from creating accounts? (by role)
    if not st.session_state.logged_in:
        #if "show_create_account" not in st.session_state:
            #st.session_state.show_create_account = True  # will change in future
        st.session_state.show_create_account = True
        if st.session_state.show_create_account:
            if st.button("Create Account"):
                create_account()
            
        # Initialize session state for role
        if 'role' not in st.session_state or st.session_state.role not in ["staff", "manager"]:
            st.session_state.role = "staff"  # Default to 'staff'
        
        
        # Only show the expander if "show_create_account" is True
        #if st.session_state.show_create_account:
            #with st.expander("Create a New Account", expanded=True):
                
    
def logout():
    st.success(f"Welcome, {st.session_state.username}!")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()