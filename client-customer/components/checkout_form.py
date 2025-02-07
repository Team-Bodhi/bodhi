import streamlit as st
from services.api import api_service
from utils.cart import clear_cart
from utils.helpers import navigate_to


def render_order_success(order_details):
    """Render the order success screen"""
    # st.write("Debug - Rendering success screen with details:", order_details)
    
    st.balloons()
    st.title("🎉 Order Placed Successfully!")
    st.success("You will receive a confirmation email shortly.")
    
    st.subheader("Order Summary")
    for item in order_details['orderItems']:
        st.markdown(f"""
        <div class="cart-item">
            <div>{item['title']}</div>
            <div class="price-tag">${item['price']:.2f} x {item['quantity']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("---")
    st.markdown(f'<h3 class="price-tag">Total: ${order_details["totalPrice"]:.2f}</h3>', 
               unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("📦 Shipping To")
    address = order_details['shippingAddress']
    st.write(f"{address['street']}")
    st.write(f"{address['city']}, {address['state']} {address['zipCode']}")
    
    if st.button("Continue Shopping →", type="primary", use_container_width=True):
        # Clear success state and navigate to main
        st.session_state.order_success = False
        st.session_state.order_details = None
        navigate_to('main')


def render_checkout_form():
    """Render the checkout form"""
    # Back button at the top
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.current_page = 'main'
            st.rerun()
    with col2:
        st.title("Checkout")
    
    # Check if we're in success state FIRST
    if st.session_state.get('order_success', False):
        render_order_success(st.session_state.order_details)
        return
    
    # Then check if cart is empty
    if not st.session_state.cart:
        st.warning("Your cart is empty.")
        if st.button("Continue Shopping"):
            st.session_state.current_page = 'main'
            st.rerun()
        return
    
    # Create two columns for the form
    form_col, summary_col = st.columns([3, 2])
    
    with form_col:
        # Shipping Information
        with st.container():
            st.subheader("📦 Shipping Address")
        
            # Get user data if authenticated
            user = st.session_state.user if st.session_state.is_authenticated else None
            # Get address from user data if available
            user_address = user.get('address', {}) if user else {}
        
            col1, col2 = st.columns(2)
            with col1:
                street = st.text_input(
                    "Street Address",
                    value=user_address.get('street', ''),
                    placeholder="123 Main St"
                )
                city = st.text_input(
                    "City",
                    value=user_address.get('city', ''),
                    placeholder="Anytown"
                )
            with col2:
                state = st.text_input(
                    "State",
                    value=user_address.get('state', ''),
                    placeholder="CA"
                )
                zip_code = st.text_input(
                    "ZIP Code",
                    value=user_address.get('zip', ''),
                    placeholder="12345"
                )
        
        # Payment Method
        st.write("---")
        st.subheader("💳 Payment Method")
        payment_method = st.selectbox(
            "Select Payment Method",
            ["credit", "debit"],
            format_func=lambda x: x.title() + " Card"
        )
        
    with summary_col:
        st.subheader("Order Summary")
        total_items = sum(item["quantity"] for item in st.session_state.cart)
        st.write(f"**Items:** {total_items}")
        
        # Display cart items in a clean format
        for item in st.session_state.cart:
            st.markdown(f"""
            <div class="cart-item">
                <div>{item['title']}</div>
                <div class="price-tag">${item['price']:.2f} x {item['quantity']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.write("---")
        st.markdown(f'<h3 class="price-tag">Total: ${st.session_state.total_amount:.2f}</h3>', 
                   unsafe_allow_html=True)
        
        # Submit Order
        if st.button("Place Order", type="primary", use_container_width=True):
            if not all([street, city, state, zip_code]):
                st.error("Please fill in all shipping information.")
                return
            
            with st.spinner("Processing your order..."):
                shipping_info = {
                    "street": street,
                    "city": city,
                    "state": state,
                    "zipCode": zip_code
                }
                
                # Include user ID if authenticated
                order_data = {
                    "orderItems": [
                        {
                            "bookId": item["bookId"],
                            "quantity": item["quantity"]
                        }
                        for item in st.session_state.cart
                    ],
                    "shippingAddress": shipping_info,
                    "paymentMethod": payment_method,
                    "totalPrice": float(st.session_state.total_amount),
                    "customerId": st.session_state.user.get("_id") if st.session_state.is_authenticated else None
                }
            
                # st.write("Debug - Submitting order:", order_data)
                success, response = api_service.submit_order(order_data)
                # st.write("Debug - Order submission result:", success, response)
                
                if success:
                    # Store order details for success screen
                    st.session_state.order_success = True
                    st.session_state.order_details = {
                        'orderItems': [{
                            'title': item['title'],
                            'price': item['price'],
                            'quantity': item['quantity']
                        } for item in st.session_state.cart],
                        'totalPrice': st.session_state.total_amount,
                        'shippingAddress': shipping_info,
                        'paymentMethod': payment_method
                    }
                    # Clear cart after storing details
                    st.session_state.cart = []
                    st.session_state.total_amount = 0.0
                    st.rerun()
                else:
                    error_msg = "Failed to place order. Please try again or contact support."
                    if response and hasattr(response, 'json'):
                        error_details = response.json().get('details', '')
                        error_msg = f"{error_msg}\nDetails: {error_details}"
                    st.error(error_msg) 
