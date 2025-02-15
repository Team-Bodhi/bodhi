import streamlit as st
from services.auth import auth_service


def render_login_form():
    """Render the login form"""
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back", key="login_back_home"):
            st.session_state.page = 'main'
            st.rerun()
    with col2:
        st.title("Login")
    
    with st.form("login_form"):
        email = st.text_input(
            "Email",
            key="login_email",
            help="Enter your email address",
            kwargs={
                "autocomplete": "username email",
                "type": "email"
            }
        )
        password = st.text_input(
            "Password",
            type="password",
            key="login_password",
            help="Enter your password",
            kwargs={
                "autocomplete": "current-password"
            }
        )
        
        submit = st.form_submit_button("Login")
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
                return
                
            if auth_service.login(email=email, password=password):
                st.session_state.page = 'main'
                st.rerun()
    
    # Registration link
    st.write("Don't have an account?")
    if st.button("Register", key="login_to_register"):
        st.session_state.page = 'register'
        st.rerun()


def render_registration_form():
    """Render the registration form"""
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back", key="register_back_home"):
            st.session_state.page = 'main'
            st.rerun()
    with col2:
        st.title("Create Account")

    with st.form("registration_form"):
        # Personal Information
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input(
                "First Name",
                help="Enter your first name"
            )
        with col2:
            last_name = st.text_input(
                "Last Name",
                help="Enter your last name"
            )

        # Account Information
        st.subheader("Account Information")
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input(
                "Email",
                help="Enter a valid email address",
                kwargs={
                    "type": "email",
                    "autocomplete": "email"
                }
            )
            phone = st.text_input("Phone", help="Enter your phone number")
        with col2:
            password = st.text_input(
                "Password",
                type="password",
                help="Password must be at least 8 characters long",
                kwargs={
                    "autocomplete": "new-password",
                    "minlength": "8"
                }
            )
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                help="Re-enter your password",
                kwargs={
                    "autocomplete": "new-password"
                }
            )

        # Shipping Address
        st.subheader("Shipping Address")
        col1, col2 = st.columns(2)
        with col1:
            street = st.text_input(
                "Street Address",
                help="Enter your street address"
            )
            city = st.text_input(
                "City",
                help="Enter your city"
            )
        with col2:
            state = st.text_input(
                "State",
                help="Enter your state (e.g., CA)"
            )
            zip_code = st.text_input(
                "ZIP Code",
                help="Enter your 5-digit ZIP code"
            )

        submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)

        if submit:
            # Validate all fields are filled
            if not all([first_name, last_name, email, password, confirm_password,
                       phone, street, city, state, zip_code]):
                st.error("Please fill in all fields")
                return

            # Validate email format
            if not '@' in email or not '.' in email:
                st.error("Please enter a valid email address")
                return

            # Validate password length
            if len(password) < 8:
                st.error("Password must be at least 8 characters long")
                return

            # Validate passwords match
            if password != confirm_password:
                st.error("Passwords do not match")
                return

            # Validate ZIP code format
            if not zip_code.isdigit() or len(zip_code) != 5:
                st.error("Please enter a valid 5-digit ZIP code")
                return

            # Validate phone number (basic check)
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) < 10:
                st.error("Please enter a valid phone number")
                return

            user_data = {
                "firstName": first_name,
                "lastName": last_name,
                "email": email.lower().strip(),  # Normalize email
                "username": email.lower().strip(),  # Use email as username
                "password": password,
                "phone": phone,
                "address": {
                    "street": street,
                    "city": city,
                    "state": state.upper(),  # Normalize state
                    "zip": zip_code
                }
            }

            with st.spinner("Creating your account..."):
                if auth_service.register(user_data):
                    st.success("Registration successful! Welcome to Bodhi Books.")
                    st.session_state.page = 'main'
                    st.rerun()

    # Login link
    st.write("Already have an account?")
    if st.button("Login", key="register_to_login"):
        st.session_state.page = 'login'
        st.rerun()


def render_profile():
    """Render the user profile page"""
    if not st.session_state.is_authenticated:
        st.warning("Please login to view your profile")
        st.session_state.page = 'login'
        st.rerun()
        return

    # Add back button and title in columns
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back", key="profile_back_home"):
            st.session_state.page = 'main'
            st.rerun()
    with col2:
        st.title("My Account")
    
    # Initialize profile_updated in session state if it doesn't exist
    if 'profile_updated' not in st.session_state:
        st.session_state.profile_updated = False
    
    # Show success message if profile was just updated
    if st.session_state.profile_updated:
        st.success("Profile updated successfully!")
        # Reset the flag
        st.session_state.profile_updated = False
    
    # Fetch complete profile data when loading the page
    auth_service.get_customer_profile()
    user = st.session_state.user
    
    # Profile Information Section
    with st.expander("Personal Information", expanded=True):
        with st.form("profile_form"):
            # Personal Information
            st.subheader("Personal Information")
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name", value=user.get("firstName", ""))
            with col2:
                last_name = st.text_input("Last Name", value=user.get("lastName", ""))

            # Account Information
            st.subheader("Account Information")
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("Email", value=user.get("email", ""), disabled=True)
            with col2:
                phone = st.text_input("Phone", value=user.get("phone", ""))

            # Shipping Address
            st.subheader("Shipping Address")
            col1, col2 = st.columns(2)
            with col1:
                street = st.text_input("Street Address", value=user.get("address", {}).get("street", ""))
                city = st.text_input("City", value=user.get("address", {}).get("city", ""))
            with col2:
                state = st.text_input("State", value=user.get("address", {}).get("state", ""))
                zip_code = st.text_input("ZIP Code", value=user.get("address", {}).get("zip", ""))
                
            save_changes = st.form_submit_button("Save Changes", type="primary", use_container_width=True)
            
            if save_changes:
                updated_data = {
                    "firstName": first_name,
                    "lastName": last_name,
                    "phone": phone,
                    "address": {
                        "street": street,
                        "city": city,
                        "state": state,
                        "zip": zip_code
                    }
                }
                
                if auth_service.update_profile(updated_data):
                    # Set the success flag instead of showing the message directly
                    st.session_state.profile_updated = True
                    st.rerun()
    
    # Order History Section
    st.header("Order History")
    orders = auth_service.get_orders()
    
    if not orders:
        st.info("No orders found")
        return
        
    for order in orders:
        with st.expander(f"Order #{order['_id']} - {order['orderDate']}", expanded=False):
            st.write(f"Status: {order['orderStatus']}")
            st.write(f"Total Amount: ${order['totalPrice']:.2f}")
            
            st.subheader("Items:")
            for item in order["orderItems"]:
                book_details = item.get('bookDetails', {})
                title = book_details.get('title', 'Unknown Book')
                st.write(f"- {title} (Qty: {item['quantity']}) - ${item['price']:.2f}")
                
            if order.get('shippingAddress'):
                st.write("Shipping Address:")
                address = order["shippingAddress"]
                st.write(f"{address['street']}")
                st.write(f"{address['city']}, {address['state']} {address['zipCode']}")


def render_auth_menu():
    """Render the authentication menu in the sidebar"""
    with st.sidebar:
        if st.session_state.is_authenticated:
            
            # Get the name from the correct location in the user object
            name = st.session_state.user.get('firstName', 'User')
            st.write(f"Welcome, {name}!")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("My Account", key="sidebar_account"):
                    st.session_state.page = 'profile'
                    st.rerun()
            with col2:
                if st.button("Logout", key="sidebar_logout"):
                    auth_service.logout()
                    st.session_state.page = 'main'
                    st.rerun()
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Login", key="sidebar_login"):
                    st.session_state.page = 'login'
                    st.rerun()
            with col2:
                if st.button("Register", key="sidebar_register"):
                    st.session_state.page = 'register'
                    st.rerun() 
