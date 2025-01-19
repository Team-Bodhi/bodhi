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

# Initialize session state
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'total_amount' not in st.session_state:
    st.session_state.total_amount = 0.0
if 'current_book' not in st.session_state:
    st.session_state.current_book = None
if 'page' not in st.session_state:
    st.session_state.page = 'main'

# API endpoints
API_BASE_URL = "http://localhost:3000/api"

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

def add_to_cart(book):
    cart_item = {
        "book_id": book["_id"],
        "title": book["title"],
        "price": book.get("price", 0),
        "quantity": 1
    }
    st.session_state.cart.append(cart_item)
    st.session_state.total_amount += cart_item["price"]

def remove_from_cart(index):
    removed_item = st.session_state.cart.pop(index)
    st.session_state.total_amount -= removed_item["price"] * removed_item["quantity"]

def submit_order():
    order_data = {
        "items": st.session_state.cart,
        "total_amount": st.session_state.total_amount,
        "order_date": datetime.now().isoformat(),
        "status": "pending"
    }
    try:
        response = requests.post(f"{API_BASE_URL}/sales", json=order_data)
        if response.status_code == 200:
            st.session_state.cart = []
            st.session_state.total_amount = 0.0
            return True
    except:
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

def render_shopping_cart():
    with st.sidebar:
        st.title("Shopping Cart 🛒")
        if not st.session_state.cart:
            st.write("Your cart is empty")
        else:
            for idx, item in enumerate(st.session_state.cart):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"{item['title']}")
                with col2:
                    st.write(f"${item['price']:.2f}")
                with col3:
                    if st.button("🗑️", key=f"remove_{idx}"):
                        remove_from_cart(idx)
                        st.rerun()
            
            st.write("---")
            st.write(f"Total: ${st.session_state.total_amount:.2f}")
            
            if st.button("Checkout"):
                if submit_order():
                    st.success("Order placed successfully!")
                else:
                    st.error("Failed to place order. Please try again.")

def render_book_details():
    book = st.session_state.current_book
    
    # Back button
    if st.button("← Back to Books"):
        show_book_grid()
    
    st.title(book.get('title', 'Untitled'))
    
    # Main content columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(book.get('coverImageUrl', 'http://dummyimage.com/180x100.png/dddddd/000000'),
                use_container_width=True)
        
        if book.get('quantity', 0) > 0:
            if st.button("Add to Cart 🛒", key=f"details_add_{book['_id']}"):
                add_to_cart(book)
                st.rerun()
        else:
            st.error("Out of Stock")
    
    with col2:
        st.subheader(f"By {book.get('author', 'Unknown Author')}")
        st.write(f"**Price:** ${book.get('price', 0):.2f}")
        st.write(f"**Genre:** {book.get('genre', 'Uncategorized')}")
        st.write(f"**Publisher:** {book.get('publisher', 'Unknown')}")
        st.write(f"**Language:** {book.get('language', 'Unknown')}")
        st.write(f"**Pages:** {book.get('pages', 'Unknown')}")
        st.write(f"**ISBN:** {book.get('isbn', 'Unknown')}")
        st.write(f"**Publication Date:** {format_date(book.get('publicationDate', ''))}")
        st.write(f"**Stock:** {book.get('quantity', 0)} copies available")
    
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

# App Layout
st.set_page_config(layout="wide", page_title="Bodhi Bookstore")

# Render shopping cart sidebar
render_shopping_cart()

# Render main content based on current page
if st.session_state.page == 'details' and st.session_state.current_book:
    render_book_details()
else:
    render_main_page()

