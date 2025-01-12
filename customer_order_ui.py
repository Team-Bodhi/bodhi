# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 13:12:13 2025

@author: kaymo
"""
import streamlit as st
import pandas as pd

# Sample Inventory Data (to simulate database)
inventory_data = [
    {"title": "Book A", "author": "Author A", "category": "Fiction", "stock": 10},
    {"title": "Book B", "author": "Author B", "category": "Non-Fiction", "stock": 5},
    {"title": "Book C", "author": "Author C", "category": "Fiction", "stock": 0},
]
inventory_df = pd.DataFrame(inventory_data)

# App Title
st.title("Customer Book Ordering System")

# Search Section
st.subheader("Search for a Book")
search_query = st.text_input("Enter book title or author")

if search_query:
    # Filter inventory based on search query
    filtered_books = inventory_df[inventory_df.apply(lambda row: search_query.lower() in row['title'].lower() or search_query.lower() in row['author'].lower(), axis=1)]
    
    if not filtered_books.empty:
        st.write("Search Results:")
        st.dataframe(filtered_books)
        
        # Book Selection Section
        selected_book = st.selectbox("Select a book to order", filtered_books['title'].tolist())
        book_details = filtered_books[filtered_books['title'] == selected_book].iloc[0]
        
        st.write(f"**Author**: {book_details['author']}")
        st.write(f"**Category**: {book_details['category']}")
        st.write(f"**Available Stock**: {book_details['stock']}")
        
        # Quantity Input Section
        quantity = st.number_input("Enter quantity to order", min_value=1, max_value=book_details['stock'], value=1)
        
        # Place Order Button
        if st.button("Place Order"):
            if quantity <= book_details['stock']:
                st.success(f"Order placed successfully for {quantity} units of '{selected_book}'.")
            else:
                st.error("Insufficient stock to place the order.")
    else:
        st.warning("No books found matching your search query.")

else:
    st.write("Please enter a search query to find a book.")

