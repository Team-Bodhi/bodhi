import streamlit as st
from services.api import submit_order
from utils.cart import clear_cart
from utils.helpers import navigate_to


def render_order_success(order_details):
    """Render the order success screen"""
    st.balloons()
    st.title("🎉 Order Placed Successfully!")
    st.success("You will receive a confirmation email shortly.")
    
    st.subheader("Order Summary")
    for item in order_details['items']:
        st.markdown(f"""
        <div class="cart-item">
            <div>{item['title']}</div>
            <div class="price-tag">${item['price']:.2f} x {item['quantity']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("---")
    st.markdown(f'<h3 class="price-tag">Total: ${order_details["total"]:.2f}</h3>', 
               unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("📦 Shipping To")
    address = order_details['shipping']
    st.write(f"{address['street']}")
    st.write(f"{address['city']}, {address['state']} {address['zipCode']}")
    
    if st.button("Continue Shopping →", type="primary", use_container_width=True):
        clear_cart()
        navigate_to('main')

def render_checkout_form():
    """Render the checkout form"""
    # Check if we're in success state
    if 'order_success' in st.session_state and st.session_state.order_success:
        render_order_success(st.session_state.order_details)
        return
    
    # Back button at the top
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            navigate_to('main')
    with col2:
        st.title("Checkout")
    
    # Create two columns for the form
    form_col, summary_col = st.columns([3, 2])
    
    with form_col:
        # Shipping Information
        with st.container():
            st.subheader("📦 Shipping Address")
            col1, col2 = st.columns(2)
            with col1:
                street = st.text_input("Street Address", placeholder="123 Main St")
                city = st.text_input("City", placeholder="Anytown")
            with col2:
                state = st.text_input("State", placeholder="CA")
                zip_code = st.text_input("ZIP Code", placeholder="12345")
        
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
                
                success, response = submit_order(
                    st.session_state.cart,
                    shipping_info,
                    payment_method,
                    st.session_state.total_amount
                )
                
                if success:
                    # Store order details for success screen
                    st.session_state.order_success = True
                    st.session_state.order_details = {
                        'items': st.session_state.cart,
                        'total': st.session_state.total_amount,
                        'shipping': shipping_info
                    }
                    st.rerun()
                else:
                    error_msg = "Failed to place order. Please try again or contact support."
                    if response:
                        error_details = response.json().get('details', '')
                        error_msg = f"{error_msg}\nDetails: {error_details}"
                    st.error(error_msg) 