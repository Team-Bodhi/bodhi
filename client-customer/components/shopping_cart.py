import streamlit as st

from utils.cart import remove_from_cart, update_cart_quantity
from utils.helpers import navigate_to


def render_shopping_cart():
    """Render the shopping cart sidebar"""
    with st.sidebar:
        st.title("Shopping Cart 🛒")
        if not st.session_state.cart:
            st.write("Your cart is empty")
            st.write("---")
            st.write("Start shopping by browsing our collection!")
        else:
            total_items = sum(item["quantity"] for item in st.session_state.cart)
            st.write(f"**{total_items} items in cart**")
            
            for idx, item in enumerate(st.session_state.cart):
                st.markdown(f"""
                <div class="cart-item">
                    <div>{item['title']}</div>
                    <div class="price-tag">${item['price']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    new_quantity = st.number_input(
                        "Qty",
                        min_value=1,
                        value=item["quantity"],
                        key=f"qty_{idx}"
                    )
                    if new_quantity != item["quantity"]:
                        update_cart_quantity(idx, new_quantity)
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"remove_{idx}"):
                        remove_from_cart(idx)
                        st.rerun()
            
            st.write("---")
            st.markdown(f'<h3 class="price-tag">Total: ${st.session_state.total_amount:.2f}</h3>', 
                       unsafe_allow_html=True)
            
            if st.button("Proceed to Checkout →", type="primary", use_container_width=True):
                navigate_to('checkout') 