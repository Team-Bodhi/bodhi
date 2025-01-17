# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 17:36:27 2025

@author: kaymo
"""
#latest changes


import streamlit as st
import requests


API_BOOKS_URL = "https://bodhi-23sn.onrender.com/api/books"

# API helper functions

# function to fetch all books from the books endpoint
def fetch_books(genre=None, language=None, in_stock=None):
    params = {}
    if genre:
        params['genre'] = genre
    if language:
        params['language'] = language
    if in_stock is not None:
        params['inStock'] = in_stock

    response = requests.get(API_BOOKS_URL, params=params)
    
    if response.status_code == 200:
        return response.json()  #
    else:
        st.error("Failed to fetch books. Please try again.")
        return []

# Function to add a new book 
def add_book(title, author, genre, quantity, price, isbn, summary, publisher, publicationDate, page_count, language, coverImageUrl, lowStockThreshold):
    new_book = {
        "title": title,
        "author": author,
        "genre": genre,
        "quantity": quantity,
        "price": price,
        "isbn": isbn,
        "summary": summary,
        "publisher": publisher,
        "publicationDate": publicationDate,
        "pageCount": page_count,
        "language": language,
        "coverImageUrl": coverImageUrl,
        "lowStockThreshold": lowStockThreshold
    }

    response = requests.post(API_BOOKS_URL, json=new_book)
    if response.status_code == 201:
        st.success(f"Book '{title}' added successfully.")
    else:
        st.error("Failed to add the book. Please check the input and try again.")

# Function to update an existing book 
def update_book(book_id, title, author, genre, quantity, price):
    updated_book = {
        "title": title,
        "author": author,
        "genre": genre,
        "quantity": quantity,
        "price": price
    }
    response = requests.put(f"{API_BOOKS_URL}/{id}", json=updated_book)
    if response.status_code == 200:
        st.success(f"Book '{title}' updated successfully.")
    else:
        st.error("Failed to update the book. Please try again.")

# Function to delete a book 
def delete_book(book_id):
    response = requests.delete(f"{API_BOOKS_URL}/{id}")
    if response.status_code == 200:
        st.success("Book deleted successfully.")
    else:
        st.error("Failed to delete the book. Please try again.")

# API functions for manufacturer orders
# 
API_MFRORDER_URL = "https://bodhi-23sn.onrender.com/api/manufacturerOrders"

# Function to fetch orders
def fetch_orders(supplier_name=None, status=None):
    params = {}
    if supplier_name:
         params['supplierName'] = supplier_name
    if status:
         params['status'] = status
        
    response = requests.get(API_MFRORDER_URL, params=params)
    if response.status_code == 200:
        return response.json()  # Returns list of orders as JSON
    else:
        st.error("Failed to fetch orders. Please try again.")
        return []

# Function for creating orders (future POST endpoint)
# FIXME uncomment once POST is available
# def create_order(order_number, supplier_name, book_orders, status, total_cost, order_date, expected_delivery_date):
#     new_order = {
#         "orderNumber": order_number,
#         "supplierName": supplier_name,
#         "bookOrders": book_orders,
#         "status": status,
#         "totalCost": total_cost,
#         "orderDate": order_date,
#         "expectedDeliveryDate": expected_delivery_date,
#     }
    
    #FIXME uncomment when POST is available
    # response = requests.post(API_MFRORDER_URL, json=new_order)
    # if response.status_code == 201:
    #     st.success(f"Order '{order_number}' created successfully.")
    # else:
    #     st.error("Failed to create the order. Please try again.")
 
    
# API Fuctions for user authentication

API_USER_URL = "https://bodhi-23sn.onrender.com/api/users"

# Function for adding a new user
def add_user_api(username, password, first_name, last_name, role):
    new_user = {
        "username": username,
        "password": password,
        "firstName": first_name,
        "lastName": last_name,
        "role": role
    }
    response = requests.post(f"{API_USER_URL}", json=new_user)
    if response.status_code == 201:
        return "Account created successfully! You can now log in."
    elif response.status_code == 400:
        return "Username already exists. Please choose a different one."
    else:
        return "Failed to create account. Please try again."

# Function to validate login
def validate_login_api(username, password):
    credentials = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{API_USER_URL}/login", json=credentials)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            return data.get("role")  # Return role if login is successful
    return None



# Streamlit UI components
# Set page configuration (must be the first Streamlit command)
st.set_page_config(page_title="Bodhi Books Management System", layout="wide")


# Sidebar Navigation
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

# Login Section
if not st.session_state.logged_in:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        role = validate_login_api(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.success(f"Welcome, {username}! You are logged in as a {role}.")
        else:
            st.error("Invalid username or password. Please try again.")

# Create Account Section
with st.expander("Create a New Account"):
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    role = st.selectbox("Role", ["Manager", "Clerk", "Admin"])
    
    if st.button("Create Account"):
        response = add_user_api(new_username, new_password, first_name, last_name, role)
        st.info(response)

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
        

        # Filters for the search
        # FIXME: see if these text boxes can be side by side with a radio button
        st.subheader("Filter Inventory")
        genre_filter = st.text_input("Filter by Genre")
        language_filter = st.text_input("Filter by Language")
        in_stock_filter = st.checkbox("Only show books in stock")

        # Fetch and display the books using the API
        books = fetch_books(genre=genre_filter, language=language_filter, in_stock=in_stock_filter)

        # FIXME: need to have headers for each column and need a table view; there are no lines
        if books:
            for book in books:
                col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 1, 1, 1])
                col1.write(book.get('title', 'N/A'))
                col2.write(book.get('author', 'N/A'))
                col3.write(book.get('genre', 'N/A'))
                quantity = book.get('quantity', 0)
                col4.write(f"Stock: {quantity}")
                # Check for low stock and display a warning if below 20
                if quantity < 20:
                    col4.markdown("<span style='color: red;'>Low Stock!</span>", unsafe_allow_html=True)
                
                col5.write(f"${book.get('price', 0.0):.2f}")
                update_button = col6.button("Update", key=f"update_{book['_id']}")
                delete_button = col6.button("Delete", key=f"delete_{book['_id']}")

                            
                if update_button:
                    with st.form(f"update_form_{book['_id']}"):
                        new_title = st.text_input("Book Title", value=book['title'])
                        new_author = st.text_input("Author", value=book['author'])
                        new_genre = st.text_input("Genre", value=book['genre'])
                        new_quantity = st.number_input("Quantity", min_value=0, value=book['quantity'])
                        new_price = st.number_input("Price", min_value=0.0, value=book['price'])
                        update_submitted = st.form_submit_button("Submit Update")
                        if update_submitted:
                            update_book(book['_id'], new_title, new_author, new_genre, new_quantity, new_price)

                if delete_button:
                    delete_book(book['_id'])

        else:
            st.write("No books found.")
              
        # Add New Book Button and Form 
        # FIX- need to move this up, it's at the bottom of the inventory list
        with st.expander("➕ Add New Book"):
            with st.form("add_book_form", clear_on_submit=True):
                new_title = st.text_input("Book Title")
                new_author = st.text_input("Author")
                new_genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Biography"])
                new_quantity = st.number_input("Quantity", min_value=1, value=1)
                new_price = st.number_input("Price", min_value=0.0, value=1.0)
                new_isbn = st.text_input("ISBN")
                new_summary = st.text_area("Summary")
                new_publisher = st.text_input("Publisher")
                new_publication_date = st.date_input("Publication Date")
                new_page_count = st.number_input("Page Count", min_value=1, value=1)
                new_language = st.text_input("Language")
                new_cover_image_url = st.text_input("Cover Image URL")
                new_low_stock_threshold = st.number_input("Low Stock Threshold", min_value=1, value=5)
                
                add_submitted = st.form_submit_button("Add Book")
                if add_submitted:
                    add_book(new_title, new_author, new_genre, new_quantity, new_price, new_isbn, new_summary, new_publisher, new_publication_date, new_page_count, new_language, new_cover_image_url, new_low_stock_threshold)
                  
        
              
        
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
        # order submission goes nowhere until we have an API endpoint for saving orders
        st.subheader("Create Purchase Order")
        with st.form("purchase_order_form"):
            book_title = st.selectbox("Select Book", [book['title'] for book in fetch_books()])
            quantity_to_order = st.number_input("Quantity to Order", min_value=1, value=1)
            submitted = st.form_submit_button("Save Purchase Order")
            if submitted:
                st.info(f"Order functionality is not yet connected to the backend. Order for {quantity_to_order} units of '{book_title}' was simulated.")
                # FIXME uncomment when endpoint is ready
                #selected_book = next(book for book in fetch_books() if book['title'] == book_title)
                #submit_order(selected_book['_id'], quantity_to_order)

        # Section: View Existing Purchase Orders
        st.subheader("Existing Purchase Orders")
        st.write("Table of existing purchase orders will be displayed here.")
