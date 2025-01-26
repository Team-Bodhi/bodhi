import streamlit as st


def add_to_cart(book, quantity=1):
    """Add a book to the cart"""
    # Check if book already in cart
    for item in st.session_state.cart:
        if item["bookId"] == book["_id"]:
            item["quantity"] += quantity
            st.session_state.total_amount += item["price"] * quantity
            st.session_state.last_action = f"Added {quantity} more {book['title']} to cart"
            return
    
    cart_item = {
        "bookId": book["_id"],
        "title": book["title"],
        "price": book.get("price", 0),
        "quantity": quantity
    }
    st.session_state.cart.append(cart_item)
    st.session_state.total_amount += cart_item["price"] * quantity
    st.session_state.last_action = f"Added {book['title']} to cart"

def update_cart_quantity(index, new_quantity):
    """Update quantity of an item in cart"""
    item = st.session_state.cart[index]
    old_quantity = item["quantity"]
    item["quantity"] = new_quantity
    st.session_state.total_amount += item["price"] * (new_quantity - old_quantity)

def remove_from_cart(index):
    """Remove an item from the cart"""
    removed_item = st.session_state.cart.pop(index)
    st.session_state.total_amount -= removed_item["price"] * removed_item["quantity"]

def clear_cart():
    """Clear the entire cart"""
    st.session_state.cart = []
    st.session_state.total_amount = 0.0 