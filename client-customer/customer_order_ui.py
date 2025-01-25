# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 13:12:13 2025

@author: kaymo
"""
import json
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

# Must be the first Streamlit command
st.set_page_config(layout="wide", page_title="Bodhi Bookstore")

# Custom CSS for better styling
st.markdown("""
<style>
    .book-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        margin-bottom: 1rem;
    }
    .cart-item {
        padding: 0.5rem;
        border-bottom: 1px solid #eee;
    }
    .price-tag {
        color: #2e7d32;
        font-weight: bold;
    }
    .stock-warning {
        color: #d32f2f;
        font-size: 0.9rem;
    }
    .success-msg {
        color: #2e7d32;
        padding: 0.5rem;
        border-radius: 0.25rem;
        background-color: #e8f5e9;
    }
    .error-msg {
        color: #d32f2f;
        padding: 0.5rem;
        border-radius: 0.25rem;
        background-color: #ffebee;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'total_amount' not in st.session_state:
    st.session_state.total_amount = 0.0
if 'current_book' not in st.session_state:
    st.session_state.current_book = None
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'checkout_stage' not in st.session_state:
    st.session_state.checkout_stage = 'cart'
if 'last_action' not in st.session_state:
    st.session_state.last_action = None

# API endpoints
API_BASE_URL = st.secrets["api"]["base_url"]

def fetch_books():
    try:
        response = requests.get(f"{API_BASE_URL}/books")
        return response.json()
    except:
        st.error("Unable to connect to the server. Using sample data.")
        return [
            {"_id": "1", "title": "Sample Book", "author": "Sample Author", 
             "genre": "Fiction", "price": 29.99, "quantity": 10, 
             "summary": "A sample book description", "isbn": "123-456-789",
             "publisher": "Sample Publisher", "pages": 300,
             "language": "English", "publicationDate": "2024-01-01T00:00:00.000Z",
             "coverImageUrl": "http://dummyimage.com/180x100.png/dddddd/000000"}
        ]

def show_toast(message, is_error=False):
    """Show a temporary notification"""
    if is_error:
        st.error(message)
    else:
        st.success(message)
    # Clear the message after 3 seconds
    st.session_state.last_action = None

def add_to_cart(book, quantity=1):
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
    removed_item = st.session_state.cart.pop(index)
    st.session_state.total_amount -= removed_item["price"] * removed_item["quantity"]

def submit_order(shipping_info, payment_method):
    # Format the order data according to the sale schema
    order_data = {
        "type": "online",
        "bookOrdered": [
            {
                "bookId": item["bookId"],
                "quantity": item["quantity"],
                "price": item["price"]
            } for item in st.session_state.cart
        ],
        "status": "pending",
        "saleDate": datetime.now().isoformat(),
        "totalPrice": st.session_state.total_amount,
        "paymentMethod": payment_method,
        "shippingAddress": {
            "street": shipping_info["street"],
            "city": shipping_info["city"],
            "state": shipping_info["state"],
            "zipCode": shipping_info["zipCode"]
        }
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/sales", json=order_data)
        if response.status_code in [200, 201]:
            st.session_state.cart = []
            st.session_state.total_amount = 0.0
            st.session_state.checkout_stage = 'cart'
            return True
        else:
            print(f"Error: {response.status_code}", response.json())
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def format_date(date_str):
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime("%B %d, %Y")
    except:
        return "Date unavailable"

def show_book_details(book):
    st.session_state.current_book = book
    st.session_state.page = 'details'
    st.rerun()

def show_book_grid():
    st.session_state.page = 'main'
    st.rerun()

def render_checkout_form():
    # Back button at the top
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.page = 'main'
            st.rerun()
    with col2:
        st.title("Checkout")
    
    # Create three columns for the form
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
        st.markdown(f'<h3 class="price-tag">Total: ${st.session_state.total_amount:.2f}</h3>', unsafe_allow_html=True)
        
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
                
                if submit_order(shipping_info, payment_method):
                    st.balloons()
                    st.success("Order placed successfully! You will receive a confirmation email shortly.")
                    st.session_state.page = 'main'
                else:
                    st.error("Failed to place order. Please try again or contact support.")

def render_shopping_cart():
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
            st.markdown(f'<h3 class="price-tag">Total: ${st.session_state.total_amount:.2f}</h3>', unsafe_allow_html=True)
            
            st.button("Proceed to Checkout →", type="primary", use_container_width=True,
                     on_click=lambda: setattr(st.session_state, 'page', 'checkout'))

def render_book_details():
    book = st.session_state.current_book
    
    # Back button and title in same row
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            show_book_grid()
    with col2:
        st.title(book.get('title', 'Untitled'))
    
    # Main content columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(book.get('coverImageUrl', 'http://dummyimage.com/180x100.png/dddddd/000000'),
                use_container_width=True)
        
        if book.get('quantity', 0) > 0:
            quantity = st.number_input("Quantity", min_value=1, max_value=book.get('quantity'), value=1)
            if st.button("Add to Cart 🛒", type="primary", use_container_width=True):
                add_to_cart(book, quantity)
                st.rerun()
            
            if book.get('quantity') < 10:
                st.markdown(f'<div class="stock-warning">Only {book.get("quantity")} left in stock!</div>', 
                          unsafe_allow_html=True)
        else:
            st.error("Out of Stock")
    
    with col2:
        st.subheader(f"By {book.get('author', 'Unknown Author')}")
        st.markdown(f'<h2 class="price-tag">${book.get("price", 0):.2f}</h2>', unsafe_allow_html=True)
        
        # Book details in a clean grid
        details = {
            "Genre": book.get('genre', 'Uncategorized'),
            "Publisher": book.get('publisher', 'Unknown'),
            "Language": book.get('language', 'Unknown'),
            "Pages": book.get('pages', 'Unknown'),
            "ISBN": book.get('isbn', 'Unknown'),
            "Publication Date": format_date(book.get('publicationDate', '')),
            "Stock": f"{book.get('quantity', 0)} copies available"
        }
        
        col1, col2 = st.columns(2)
        for i, (key, value) in enumerate(details.items()):
            with col1 if i % 2 == 0 else col2:
                st.write(f"**{key}:** {value}")
    
    st.write("---")
    st.subheader("Summary")
    st.write(book.get('summary', 'No summary available.'))

def render_main_page():
    st.title("Welcome to Bodhi Bookstore 📚")
    
    # Search and Filter Section
    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input("Search books by title or author")
    with col2:
        genre_filter = st.selectbox("Filter by genre", 
                                  ["All", "Fiction", "Non-Fiction", "Science", "History"])
    
    # Display Books
    books = fetch_books()
    filtered_books = books
    
    if search_query:
        filtered_books = [book for book in filtered_books 
                         if search_query.lower() in book.get('title', '').lower() 
                         or search_query.lower() in book.get('author', '').lower()]
    
    if genre_filter != "All":
        filtered_books = [book for book in filtered_books 
                         if book.get('genre') == genre_filter]
    
    # Display books in a grid
    cols = st.columns(3)
    for idx, book in enumerate(filtered_books):
        with cols[idx % 3]:
            st.write("---")
            with st.container():
                st.image(book.get('coverImageUrl', 'http://dummyimage.com/180x100.png/dddddd/000000'),
                        use_container_width=True)
                st.subheader(book.get('title', 'Untitled'))
                st.write(f"By {book.get('author', 'Unknown Author')}")
                st.write(f"**${book.get('price', 0):.2f}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("View Details 📖", key=f"details_{idx}"):
                        show_book_details(book)
                with col2:
                    if book.get('quantity', 0) > 0:
                        if st.button("Add to Cart 🛒", key=f"add_{idx}"):
                            add_to_cart(book)
                            st.rerun()
                    else:
                        st.write("Out of Stock")

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

