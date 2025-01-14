# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 17:36:27 2025

@author: kaymo
"""
#latest changes

import streamlit as st
import pandas as pd
from pymongo import MongoClient
from bson.objectid import ObjectId

# Set page configuration (must be the first Streamlit command)
st.set_page_config(page_title="Bodhi Books Management System", layout="wide")


# Database connection function
@st.cache_resource
def get_database():
    client = MongoClient("mongodb+srv://kay:jcFfMbK0I7EkjPoA@bodhi.unctm.mongodb.net/?retryWrites=true&w=majority&appName=Bodhi")
    db = client["Bodhi"]
    return db

# Access the inventory collection
db = get_database()
inventory_collection = db["books"]

# Fetch data from MongoDB
def fetch_inventory():
    inventory = list(inventory_collection.find({}, {"_id": 1, "title": 1, "author": 1, "genre": 1, "quantity_in_stock": 1, "price": 1}))
    return inventory

if 'inventory_df' not in st.session_state:
    st.session_state.inventory_df = pd.DataFrame(fetch_inventory())
    st.session_state.inventory_df["_id"] = st.session_state.inventory_df["_id"].astype(str)

# Add, Update, and Delete functions interacting with MongoDB
def add_book(title, author, genre, quantity, price):
    new_entry = {
        "title": title,
        "author": author,
        "genre": genre,
        "quantity_in_stock": quantity,
        "price": price
    }
    inventory_collection.insert_one(new_entry)
    st.session_state.inventory_df = pd.DataFrame(fetch_inventory())
    st.session_state.inventory_df["_id"] = st.session_state.inventory_df["_id"].astype(str)

def update_book(book_id, title, author, genre, quantity, price):
    inventory_collection.update_one(
        {"_id": ObjectId(book_id)},
        {"$set": {"title": title, "author": author, "genre": genre, "quantity": quantity, "price": price}}
    )
    st.session_state.inventory_df = pd.DataFrame(fetch_inventory())
    st.session_state.inventory_df["_id"] = st.session_state.inventory_df["_id"].astype(str)

def delete_book(book_id):
    inventory_collection.delete_one({"_id": ObjectId(book_id)})
    st.session_state.inventory_df = pd.DataFrame(fetch_inventory())
    st.session_state.inventory_df["_id"] = st.session_state.inventory_df["_id"].astype(str)


# Sidebar Navigation with visible options and icons
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Go to",
    options=["Home", "Inventory Management", "Sales Records", "Orders"],
    format_func=lambda x: f"🏠 {x}" if x == "Home" else (
        "📦 Inventory" if x == "Inventory Management" else
        "📊 Sales" if x == "Sales Records" else
        "🛒 Orders"
    )
)

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
    st.title("📚 Bodhi Books Management System")
    st.subheader("Preserving Literary Treasures, One Page at a Time")
    st.write("""
    Welcome to the **Bodhi Books Management System** — your gateway to efficiently managing our exclusive collection of rare and antique books.

    This app is designed to empower our employees with the tools they need to:
    - **Manage inventory** of rare books
    - **Create purchase orders** for restocking
    - **View sales records** and generate reports

    Use the sidebar to navigate through the different sections of the app.
    """)
    
    # Login Section on Home Page
if not st.session_state.logged_in:
        st.info("📝 Ready to get started? Log in to begin managing the world of rare books.")
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
    
    # Inventory Management Page
    if page == "Inventory Management":
        st.title("📦 Inventory Management")
        st.subheader("Manage Your Rare Book Collection")
        st.write("""
        Welcome to the **Inventory Management** section. Here you can:
        - View and search our current inventory of rare books.
        - Add new books to the collection.
        - Update book information, including stock levels and prices.
        - Remove books that are no longer available.
        """)
        

         # Search Bar
        search_query = st.text_input(
            "Search Inventory by Title, Author, or Genre",
            placeholder="Enter book title, author, or genre",
            key="search_bar"
        )
        st.button("🔍", key="search_button")

        
        # Add New Book Button and Form 
        with st.expander("➕ Add New Book"):
            with st.form("add_book_form", clear_on_submit=True):
                new_title = st.text_input("Book Title")
                new_author = st.text_input("Author")
                new_genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Biography"])
                new_quantity = st.number_input("Quantity", min_value=1, value=1)
                new_price = st.number_input("Price", min_value=0.0, value=1.0)
                add_submitted = st.form_submit_button("Add Book")
                if add_submitted:
                    add_book(new_title, new_author, new_genre, new_quantity, new_price)
                    st.success(f"Book '{new_title}' added successfully.")
                    st.session_state['refresh'] = not st.session_state.get('refresh', False)

        
        # Filtered Inventory Display with Error Handling for Missing Fields
        filtered_inventory = st.session_state.inventory_df
        if search_query:
            filtered_inventory = filtered_inventory[filtered_inventory.apply(
                lambda row: search_query.lower() in str(row['title']).lower()
                or search_query.lower() in str(row['author']).lower()
                or search_query.lower() in str(row['genre']).lower(), axis=1)]

        # Display Inventory with Update and Delete Options
        for index, row in filtered_inventory.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 1, 1, 1])
            col1.write(row.get('title', 'N/A'))
            col2.write(row.get('author', 'N/A'))
            col3.write(row.get('genre', 'N/A'))
            col4.write(row.get('quantity_in_stock', 'N/A'))
            col5.write(f"${row.get('price', 0.0):.2f}")
            update_button = col6.button("Update", key=f"update_{row['_id']}")
            delete_button = col6.button("Delete", key=f"delete_{row['_id']}")

            if update_button:
                with st.form(f"update_form_{row['_id']}"):
                    new_title = st.text_input("Book Title", value=row['title'])
                    new_author = st.text_input("Author", value=row['author'])
                    new_genre = st.text_input("Genre", value=row['genre'])
                    new_quantity = st.number_input("Quantity", min_value=0, value=row['quantity'])
                    new_price = st.number_input("Price", min_value=0.0, value=row['price'])
                    update_submitted = st.form_submit_button("Submit Update")
                    if update_submitted:
                        update_book(row['_id'], new_title, new_author, new_genre, new_quantity, new_price)
                        st.success(f"Book '{new_title}' updated successfully.")
                        st.session_state['refresh'] = not st.session_state.get('refresh', False)

            if delete_button:
                delete_book(row['_id'])
                st.success(f"Book '{row['title']}' deleted successfully.")
                st.session_state['refresh'] = not st.session_state.get('refresh', False)

        
    # Sales Records Page
    elif page == "Sales Records":
        st.title("📊 Sales Records")
        st.subheader("View and Analyze Sales Data")
        st.write("""
        Welcome to the **Sales Records** section. Here you can:
        - View detailed sales records of rare books.
        - Generate sales reports.
        - Analyze trends and performance over time.
        """)
   
    # Orders Page
    elif page == "Orders":
        st.title("🛒 Orders")
        st.subheader("Manage Purchase Orders")
        st.write("""
        Welcome to the **Orders** section. Here you can:
        - View and manage existing purchase orders.
        - Create new orders for books running low on stock.
        - Ensure a steady supply of rare books for our customers.
        """)

        # Section: Create Purchase Order Form
        st.subheader("Create Purchase Order")
        with st.form("purchase_order_form"):
            book_title = st.selectbox("Select Book", st.session_state.inventory_df['title'].tolist())
            current_stock = st.session_state.inventory_df[st.session_state.inventory_df['title'] == book_title]['quantity'].values[0]
            st.write(f"Current Stock: {current_stock}")
            quantity_to_order = st.number_input("Quantity to Order", min_value=1, value=1)
            submitted = st.form_submit_button("Save Purchase Order")
            if submitted:
                st.success(f"Purchase order for {quantity_to_order} units of '{book_title}' created successfully.")

        # Section: View Existing Purchase Orders
        st.subheader("Existing Purchase Orders")
        st.write("Table of existing purchase orders will be displayed here.")
