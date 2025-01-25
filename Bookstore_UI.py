# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 17:36:27 2025

@author: kaymo
"""

import requests
import streamlit as st


# For streamlit cloud deployment uncomment this sesction, comment out local section
API_BASE_URL = st.secrets["api"]["base_url"]
if not API_BASE_URL:
    raise ValueError("API_BASE_URL is not set in Streamlit secrets.")

API_BOOKS_URL = API_BOOKS_URL = f"{API_BASE_URL}/books"
API_USER_URL = f"{API_BASE_URL}/users"
API_MFRORDER_URL = f"{API_BASE_URL}/manufacturerOrders"


# Define all functions

# datetime formatters
def formatDate(datetime):
    date = datetime.split("T")
    formatDate = date[0].split("-")
    
    day = formatDate[2]
    month = formatDate[1]
    year = formatDate[0]
    
    if month[0] == "0":
        month = month[1]
    if day[0] == "0":
        day = day[1]
        
    return (f"{month}/{day}/{year}")

def formatTime(datetime):
    time = datetime.split("T")
    formatTime = time[1].split(":")
    
    hour = formatTime[2]
    minute = formatTime[1]
    
    if hour[0] == "0":
        hour = hour[1]
        
    return (f"{hour}:{minute}")

def formatDatetime(datetime):
    date = formatDate(datetime)
    time = formatTime(datetime)
        
    return (f"{date} {time}")

# function to fetch all books- Passed testing

def fetch_books(genre=None, title=None, author=None):
    params = {}
    if genre:
        params['genre'] = genre
    if title:
        params['title'] = title
    if author:
        params['author'] = author
   

    response = requests.get(API_BOOKS_URL, params=params)
    
    if response.status_code == 200:
        return response.json()  
    else:
        st.error("Failed to fetch books. Please try again.")
        return []

# function to get one book by id
def fetch_book_by_id(book_id):

    response = requests.get(API_BOOKS_URL + f'/{book_id}')
    
    if response.status_code == 200:
        return response.json()  
    else:
        st.error("Failed to fetch book. Please try again.")
        return []

# Function to add a book- Passed testing
def add_book(title, author, genre, quantity, price, language, isbn):
    new_book = {
        "title": title,
        "author": author,
        "genre": genre,
        "quantity": quantity,
        "price": price,
        "language": language,
        "isbn": isbn

    }

    # Send the data to the API
    response = requests.post(API_BOOKS_URL, json=new_book)
    
    # Handle the response
    if response.status_code == 201:
        st.success("Book added successfully!")
    else:
        st.error(f"Failed to add book: {response.text}")
        
# Function to update an existing book 
def update_book(book_id, title, author, genre, quantity, price, language=None, isbn=None):
    updated_book = {
        "title": title,
        "author": author,
        "genre": genre,
        "quantity": quantity,
        "price": price,
    }
    # Optionally include additional fields if provided
    if language:
        updated_book["language"] = language
    if isbn:
        updated_book["isbn"] = isbn
        
    response = requests.put(f"{API_BOOKS_URL}/{book_id}", json=updated_book)
    if response.status_code == 200:
        st.success(f"Book '{title}' updated successfully!")
        return True
    else:
        st.error(f"Failed to update book: {response.text}")
        return False
 
    
# Function to delete a book
def delete_book(book_id):
    response = requests.delete(f"{API_BOOKS_URL}/{book_id}")
    if response.status_code == 200:
        st.success("Book deleted successfully.")
    else:
        st.error(f"Failed to delete the book: {response.text}")


#Function for creating orders 
#FIXME requires testing
def create_order(order_number, supplier_name, books_ordered, status, total_cost, order_date, expected_delivery_date):
    new_order = {
        "orderNumber": order_number,
        "supplierName": supplier_name,
        "booksOrdered": books_ordered,
        "status": status,
        "totalCost": total_cost,
        "orderDate": order_date,
        "expectedDeliveryDate": expected_delivery_date,
    }
    
    
    response = requests.post(API_MFRORDER_URL, json=new_order)
    
    # Handle the response
    if response.status_code == 201:
        st.success(f"Order '{order_number}' created successfully.")
        return response.json() # Return the created order for further use
    elif response.status_code == 400:
        st.error(" Invalid input or order already exists")
        return None
    else:
        st.error(f"Failed to create the order {order_date}. Please try again.")
        return None
  
 
# Function to fetch manufacturer orders
def fetch_orders(supplier_name=None, status=None):
    params = {}
    if supplier_name:
         params['supplierName'] = supplier_name
    if status:
         params['status'] = status
        
    response = requests.get(API_MFRORDER_URL, params=params)
    print(response)
    if response.status_code == 200:
        return response.json()  # Returns list of orders as JSON
    else:
        st.error("Failed to fetch orders. Please try again.")
        return []
    
# Function to fetch mfr order by id
def fetch_order_by_id(order_id):
    response = requests.get(API_MFRORDER_URL + f'/{order_id}')
    if response.status_code == 200:
        return response.json()  # Returns list of orders as JSON
    else:
        st.error("Failed to fetch orders. Please try again.")
        return []

def cancel_order(order_id):
    response = requests.put(f"{API_BASE_URL}/cancel/{order_id}")
    if response.status_code == 200:
        st.success(f"Order canceled successfully!")
        return True
    else:
        st.error(f"Failed to cancel order: {response.text}")
        return False

# open dialog for order details
@st.dialog("Order Details")
def order_details(order_id):
    order = fetch_order_by_id(order_id)

    if order:
        st.write(f"**Supplier Name**: {order['supplierName']}")
        st.write(f"**Status**: {order['status']}")
        st.write(f"**Total Cost**: ${order['totalCost']:.2f}")
        date = formatDatetime(order['orderDate'])
        st.write(f"**Order Date**: {date}")
        date = formatDatetime(order['expectedDeliveryDate'])
        st.write(f"**Expected Delivery Date**: {date}")    
                
        st.subheader("Books Ordered:")
        # Display table headers with Streamlit columns 
        header_cols = st.columns([3, 3, 3, 2])
        header_cols[0].write("Title")
        header_cols[1].write("Author")
        header_cols[2].write("Genre")
        header_cols[3].write(" Order Quantity")
        for book in order['booksOrdered']:
            book_details = fetch_book_by_id(str(book['bookId']))
                    
            cols = st.columns([2, 2, 2, 1])
            cols[0].write(book_details.get("title", "N/A"))
            cols[1].write(book_details.get("author", "N/A"))
            cols[2].write(book_details.get("genre", "N/A"))
            cols[3].write(str(book.get('quantity')))
    
# API Fuctions for user authentication

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
        return "User created successfully."
    elif response.status_code == 400:
        return "Invalid input or username already exists."
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
        if data.get("message") == "Login successful":
            user_info = data.get("user", {})
            st.session_state.role = user_info.get("role")
            st.session_state.username = user_info.get("username")
            return True #login successful
        elif response.status_code == 401:
            st.error("Invalid username or password.")
        elif response.status_code == 400:
            st.error("Missing username or password.")
        else:
            st.error("failed to log in. Please try again.")
        return False # Login failed
            
    

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

#Login State Management
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
    
# Login Section
if not st.session_state.logged_in:
    st.divider()
    st.subheader("🔐 Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        # call the validate login function
        role = validate_login_api(username, password)
        if role:
            # update the session state for successful login
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            # display a welcome message
            st.success(f"Welcome, {username}!")
            # Reset the login fields
            st.session_state.login_username = ""
            st.session_state.login_password = ""
        else:
            st.error("Invalid username or password. Please try again.")

         
            
# Create account section

# Initialize session state for the expander
if not st.session_state.logged_in and page == "Home":
    if "show_create_account" not in st.session_state:
        st.session_state.show_create_account = False  # Expander starts collapsed
    
    # Toggle function for the expander
    def toggle_expander():
        st.session_state.show_create_account = not st.session_state.show_create_account
    
    # Main "Create a New Account" toggle button
    if not st.session_state.show_create_account:
        st.button("Create a New Account", on_click=toggle_expander)
        
    # Initialize session state for role
    if 'role' not in st.session_state or st.session_state.role not in ["staff", "manager"]:
        st.session_state.role = "staff"  # Default to 'staff'
    
    
    # Only show the expander if "show_create_account" is True
    if st.session_state.show_create_account:
        with st.expander("Create a New Account", expanded=True):
            # Input fields for creating a new account
            new_username = st.text_input("New Username", key="new_username")
            new_password = st.text_input("New Password", type="password", key="new_password")
            first_name = st.text_input("First Name", key="first_name")
            last_name = st.text_input("Last Name", key="last_name")
            role = st.selectbox("Role", ["staff", "manager"], key="role")
    
            if st.button("Create Account"):
                if new_username and new_password and first_name and last_name:
                    response = add_user_api(new_username, new_password, first_name, last_name, role)
                    st.info(response)
    
                    # Reset form fields and collapse after success
                    st.session_state.new_username = ""
                    st.session_state.new_password = ""
                    st.session_state.first_name = ""
                    st.session_state.last_name = ""
                    st.session_state.role = "staff"  # Reset to default
                    st.session_state.show_create_account = False
                else:
                    st.warning("All fields are required to create an account.")
    

        
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
    
        # Track the selected book for editing
        if "selected_book" not in st.session_state:
            st.session_state.selected_book = None
            
        # Add New Book Button and Form
        with st.expander("➕ Add New Book"):
            with st.form("add_book_form", clear_on_submit=True):
                new_title = st.text_input("Book Title")
                new_author = st.text_input("Author")
                new_genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Biography"])
                new_quantity = st.number_input("Quantity", min_value=1, value=1)
                new_price = st.number_input("Price", min_value=0.0, value=1.0)
                new_language = st.text_input("Language")
                new_isbn = st.text_input("ISBN")
                add_submitted = st.form_submit_button("Add Book")
                if add_submitted:
                    add_book(new_title, new_author, new_genre, new_quantity, new_price, new_language, new_isbn)
        
        # Filters for the search
        st.subheader("Filter Inventory")
        col1, col2, col3 = st.columns(3)
    
        with col1:
            filter_by_genre = st.checkbox("Filter by Genre")
            selected_genre = st.text_input("Genre") if filter_by_genre else None
    
        with col2:
            filter_by_author = st.checkbox("Filter by Author")
            selected_author = st.text_input("Author") if filter_by_author else None
    
        with col3:
            filter_by_title = st.checkbox("Filter by Title")
            selected_title = st.text_input("Title") if filter_by_title else None
    
        # Update fetch_books function based on selected filters
        filters = {
            "genre": selected_genre if filter_by_genre else None,
            "author": selected_author if filter_by_author else None,
            "title": selected_title if filter_by_title else None,
        }

        # Fetch and display the books using the API
        books = fetch_books(**{k: v for k, v in filters.items() if v is not None})
        st.subheader("Inventory List")

        if books:
            # Display table headers with Streamlit columns
            header_cols = st.columns([2, 2, 2, 1, 1, 2])
            header_cols[0].write("Title")
            header_cols[1].write("Author")
            header_cols[2].write("Genre")
            header_cols[3].write("Stock")
            header_cols[4].write("Price")
            header_cols[5].write("Actions")


            # Display inventory with "Edit" and "Delete" actions
            for book in books:
                cols = st.columns([2, 2, 2, 1, 1, 2])
                cols[0].write(book.get("title", "N/A"))
                cols[1].write(book.get("author", "N/A"))
                cols[2].write(book.get("genre", "N/A"))
    
                quantity = book.get("quantity", 0)
                # Highlight stock if it's low
                if quantity < 20:
                    cols[3].markdown(f"<span style='color: red;'>{quantity}</span>", unsafe_allow_html=True)
                else:
                    cols[3].write(quantity)
    
                cols[4].write(f"${book.get('price', 0):.2f}")
    
                # Add "Edit" and "Delete" buttons
                if cols[5].button("Edit", key=f"edit_{book['_id']}"):
                    st.session_state.selected_book = book
    
                if cols[5].button("Delete", key=f"delete_{book['_id']}"):
                    delete_book(book["_id"])
                    st.success(f"Book '{book['title']}' deleted successfully.")
                    st.session_state.refresh_inventory = True
                    st.rerun()


        
                # Display the edit form in the sidebar if a book is selected
                if st.session_state.selected_book:
                    book = st.session_state.selected_book
                    with st.sidebar:
                        st.subheader("Edit Book")
                        with st.form("update_book_form", clear_on_submit=True):
                            new_title = st.text_input("Book Title", value=book["title"])
                            new_author = st.text_input("Author", value=book["author"])
                            new_genre = st.text_input("Genre", value=book["genre"])
                            new_quantity = st.number_input("Quantity", min_value=0, value=book["quantity"])
                            new_price = st.number_input("Price", min_value=0.0, value=book["price"])
                            new_language = st.text_input("Language", value=book.get("language", ""))
                            new_isbn = st.text_input("ISBN", value=book.get("isbn", ""))
                        
                            update_submitted = st.form_submit_button("Update Book")
                            if update_submitted:
                                success = update_book(
                                    book["_id"],
                                    new_title,
                                    new_author,
                                    new_genre,
                                    int(new_quantity),
                                    float(new_price),
                                    new_language,
                                    new_isbn,
                                )
                                if success:
                                    st.success(f"Book '{new_title}' updated successfully!")
                                    # Clear the selected book and refresh the books
                                    st.session_state.selected_book = None
                                    st.session_state.refresh_inventory = True
                                    st.rerun()
        
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
        
        # Generate Sales Report
        st.subheader("Generate Sales Report")
        with st.form("sales_report_form"):
            # Input fields for sales report parameters
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            book_title = st.text_input("Book Title (optional)")
            genre = st.text_input("Genre (optional)")
            status = st.selectbox("Sale Status (optional)", ["", "pending", "shipped", "received", "canceled"])
            sale_type = st.selectbox("Sale Type (optional)", ["", "instore", "online"])
            report_type = st.selectbox("Report Type", ["Summary", "Detailed"])
    
            # Submit button
            submitted = st.form_submit_button("Generate Report")

            if submitted:
                try:
                    # Construct query parameters based on user input
                    report_params = {
                        "startDate": str(start_date) if start_date else None,
                        "endDate": str(end_date) if end_date else None,
                        "bookTitle": book_title if book_title else None,
                        "genre": genre if genre else None,
                        "status": status if status else None,
                        "type": sale_type if sale_type else None,
                    }
                    # Filter out None values
                    report_params = {k: v for k, v in report_params.items() if v}

                    # Send request to API
                    response = requests.get(f"{API_BASE_URL}/sales", params=report_params)
            
                    # Check the API response
                    if response.status_code == 200:
                        report_data = response.json()
                        st.write("### Sales Report")
                        st.dataframe(report_data)  # Display the report data in a table
                    else:
                        st.error(f"Failed to generate report: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error generating sales report: {e}")


        # Fetch and Display All Sales Records
#        st.subheader("All Sales Records")
#        try:
#            response = requests.get(f"{API_BASE_URL}/sales")  # Replace with the correct endpoint
#            if response.status_code == 200:
#                sales_data = response.json()
#                st.dataframe(sales_data)  # Display sales records in a tabular format
#            else:
#                st.write("No sales records found or failed to fetch data.")
#        except requests.exceptions.RequestException as e:
#            st.error(f"Error fetching sales data: {e}")

        
        # Sales Trends Analysis
        st.subheader("Sales Trends and Analysis")
        trend_options = ["Sales Over Time", "Top Selling Books", "Revenue by Genre"]
        selected_trend = st.selectbox("Select Trend to Analyze", trend_options)

        try:
            if selected_trend == "Sales Over Time":
                trend_data = requests.get(f"{API_BASE_URL}/sales/trends/time").json()
                if trend_data:
                    st.line_chart(trend_data)
                else:
                    st.write("No data available for this trend.")

            elif selected_trend == "Top Selling Books":
                top_books_data = requests.get(f"{API_BASE_URL}/sales/trends/top-books").json()
                if top_books_data:
                    st.bar_chart(top_books_data)
                else:
                    st.write("No data available for this trend.")

            elif selected_trend == "Revenue by Genre":
                revenue_data = requests.get(f"{API_BASE_URL}/sales/trends/revenue-by-genre").json()
                if revenue_data:
                    st.bar_chart(revenue_data)
                else:
                    st.write("No data available for this trend.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching trend data: {e}")




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

            # Section: Create Purchase Order Form (needs to be its own section to accommodate multiple books)
                
            
            # st.subheader("Create Purchase Order")
            # with st.form("purchase_order_form", clear_on_submit=True):
            #     # Select book titles from the inventory
            #     books = fetch_books()
            #     book_titles = [book['title'] for book in books]
            #     book_title = st.selectbox("Select Book", book_titles if books else [])
                
            #     # Input other fields
            #     quantity_to_order = st.number_input("Quantity to Order", min_value=1, value=1)
            #     order_number = st.text_input("Order Number", placeholder="e.g., ORD123")
            #     supplier_name = st.text_input("Supplier Name", placeholder="e.g., Book Supplier Inc.")
            #     status = st.selectbox("Status", ["Pending", "Shipped", "Received"])
            #     total_cost = st.number_input("Total Cost", min_value=0.0, step=0.01)
            #     order_date = st.date_input("Order Date")
            #     expected_delivery_date = st.date_input("Expected Delivery Date")

            #     submitted = st.form_submit_button("Save Purchase Order")
            #     if submitted:
            #         if book_title and order_number and supplier_name:
            #             # Match the selected book with its details
            #             selected_book = next((book for book in books if book['title'] == book_title), None)
            #             if selected_book:
            #                 # Create the new order
            #                 books_ordered = [{"title": book_title, "quantity": quantity_to_order}]
            #                 new_order = create_order(
            #                     order_number=order_number,
            #                     supplier_name=supplier_name,
            #                     books_ordered=books_ordered,
            #                     status=status.lower(),
            #                     total_cost=total_cost,
            #                     order_date=str(order_date),  # Convert date to string for API
            #                     expected_delivery_date=str(expected_delivery_date),  # Convert date to string for API
            #                 )
            #                 if new_order:
            #                     st.info(f"Order for {quantity_to_order} units of '{book_title}' created successfully!")
            #             else:
            #                 st.error("Failed to match the selected book.")
            #         else:
            #             st.error("Please fill out all required fields.")
            
        cancel_button = False
        cancel_order_id = ""

        # if order details not selected, hide this state
        if "selected_order" not in st.session_state:
            st.session_state.selected_order = None

        # Section: View Existing Purchase Orders
        st.subheader("Existing Purchase Orders")
        orders = fetch_orders()
        if orders:
            for order in orders:
                order_id = order['_id']
                date = ""
                with st.expander(f"Order: {order['orderNumber']} ({order['status']})"):
                    st.write(f"**Supplier Name**: {order['supplierName']}")
                    st.write(f"**Status**: {order['status']}")
                    st.write(f"**Total Cost**: ${order['totalCost']:.2f}")
                    date = formatDatetime(order['orderDate'])
                    st.write(f"**Order Date**: {date}")
                    date = formatDatetime(order['expectedDeliveryDate'])
                    st.write(f"**Expected Delivery Date**: {date}")
    #               if st.button(f"Receive Order", order['_id']):
    #                  receive_order(order_id)
                    if st.button("Details", order['_id']):
                        order_details(order['_id'])
    #               if st.button(f"Cancel Order", order['_id']):
    #                   cancel_order(order_id)