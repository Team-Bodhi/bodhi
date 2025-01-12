# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 17:36:27 2025

@author: kaymo
"""

import streamlit as st
import pandas as pd

# Sample Inventory Data (to simulate database)
inventory_data = [
    {"title": "Book A", "author": "Author A", "genre": "Fiction", "stock": 10},
    {"title": "Book B", "author": "Author B", "genre": "Non-Fiction", "stock": 5},
    {"title": "Book C", "author": "Author C", "genre": "Fiction", "stock": 25}
]

if 'inventory_df' not in st.session_state:
    st.session_state.inventory_df = pd.DataFrame(inventory_data)

# App Title
st.set_page_config(page_title="Bookstore Management System", layout="wide")
st.title("Bookstore Management System")

# Sidebar Navigation
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Go to", [
    "Home",
    "Inventory Management",
    "Sales Records",
    "Orders"
])

# Login State Management
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'name' not in st.session_state:
    st.session_state.name = ""

if 'role' not in st.session_state:
    st.session_state.role = ""

# Logout Functionality
if st.session_state.logged_in:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.name = ""
        st.session_state.role = ""
        st.session_state['refresh'] = not st.session_state.get('refresh', False)

# Home Page (Always Accessible)
if page == "Home":
    st.header("Welcome to the Bookstore Management System")
    st.write("This is the home page. Use the sidebar to navigate.")
    
    # Login Section on Home Page
    if not st.session_state.logged_in:
        st.subheader("Login")
        name = st.text_input("Name")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Manager", "Clerk", "Admin"])
        if st.button("Login"):
            if password == "TEST":
                st.session_state.logged_in = True
                st.session_state.name = name
                st.session_state.role = role
                st.success(f"Welcome, {name}! You are logged in as a {role}.")
                st.session_state['refresh'] = not st.session_state.get('refresh', False)
            else:
                st.error("Invalid password. Please try again.")

# Protected Pages
if st.session_state.logged_in:
    if page == "Inventory Management":
        st.header("Inventory Management")

        # Function to add a new book
        def add_book(title, author, genre, stock):
            new_entry = {"title": title, "author": author, "genre": genre, "stock": stock}
            st.session_state.inventory_df = st.session_state.inventory_df.append(new_entry, ignore_index=True)

        # Function to update a book
        def update_book(index, title, author, genre, stock):
            st.session_state.inventory_df.at[index, 'title'] = title
            st.session_state.inventory_df.at[index, 'author'] = author
            st.session_state.inventory_df.at[index, 'genre'] = genre
            st.session_state.inventory_df.at[index, 'stock'] = stock

        # Function to delete a book
        def delete_book(index):
            st.session_state.inventory_df = st.session_state.inventory_df.drop(index).reset_index(drop=True)

        # Search Bar
        search_query = st.text_input("Search Inventory by Title, Author, or Genre", placeholder="Enter book title, author, or genre")

        # Filtered Inventory Display
        if search_query:
            filtered_inventory = st.session_state.inventory_df[st.session_state.inventory_df.apply(lambda row: search_query.lower() in row['title'].lower() or search_query.lower() in row['author'].lower() or search_query.lower() in row['genre'].lower(), axis=1)]
        else:
            filtered_inventory = st.session_state.inventory_df

        # Display Inventory with Update and Delete Options
        for index, row in filtered_inventory.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 1, 1, 1])
            col1.write(row['title'])
            col2.write(row['author'])
            col3.write(row['genre'])
            col4.write(row['stock'])
            update_button = col5.button("Update", key=f"update_{index}")
            delete_button = col6.button("Delete", key=f"delete_{index}")

            if update_button:
                with st.form(f"update_form_{index}"):
                    new_title = st.text_input("Book Title", value=row['title'])
                    new_author = st.text_input("Author", value=row['author'])
                    new_genre = st.text_input("Genre", value=row['genre'])
                    new_stock = st.number_input("Stock", min_value=0, value=row['stock'])
                    update_submitted = st.form_submit_button("Submit Update")
                    if update_submitted:
                        update_book(index, new_title, new_author, new_genre, new_stock)
                        st.success(f"Book '{new_title}' updated successfully.")
                        st.session_state['refresh'] = not st.session_state.get('refresh', False)

            if delete_button:
                delete_book(index)
                st.success(f"Book '{row['title']}' deleted successfully.")
                st.session_state['refresh'] = not st.session_state.get('refresh', False)

        # Add New Book Button
        if st.button("Add New Book"):
            with st.form("add_book_form", clear_on_submit=True):
                new_title = st.text_input("Book Title")
                new_author = st.text_input("Author")
                new_genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Biography"])
                new_stock = st.number_input("Stock", min_value=1, value=1)
                add_submitted = st.form_submit_button("Add Book")
                add_submitted = st.form_submit_button("Add Book")
            if add_submitted:
                    add_book(new_title, new_author, new_genre, new_stock)
                    st.success(f"Book '{new_title}' added successfully.")
                    st.session_state['refresh'] = not st.session_state.get('refresh', False)

    elif page == "Sales Records":
        st.header("Sales Records")
        st.write("Placeholder for sales records and reports")
        st.button("Generate Sales Report")
        st.write("Sales data will be displayed here.")

    elif page == "Orders":
        st.header("Order Management")

        # Section: Low-Stock Alerts
        st.subheader("Low-Stock Alerts")
        st.write("List of low-stock books will be displayed here.")
        st.button("Create Purchase Order")

        # Section: Create Purchase Order Form
        st.subheader("Create Purchase Order")
        with st.form("purchase_order_form"):
            book_title = st.selectbox("Select Book", st.session_state.inventory_df['title'].tolist())
            current_stock = st.session_state.inventory_df[st.session_state.inventory_df['title'] == book_title]['stock'].values[0]
            st.write(f"Current Stock: {current_stock}")
            quantity_to_order = st.number_input("Quantity to Order", min_value=1, value=1)
            submitted = st.form_submit_button("Save Purchase Order")
            if submitted:
                st.success(f"Purchase order for {quantity_to_order} units of '{book_title}' created successfully.")

        # Section: View Existing Purchase Orders
        st.subheader("Existing Purchase Orders")
        st.write("Table of existing purchase orders will be displayed here.")
