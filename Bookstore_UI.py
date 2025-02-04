# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 17:36:27 2025

@author: kaymo
"""

# functions for bookstore_ui
#
from bookstore_ui.bookstore import *
from bookstore_ui.Login_UI import *

API_BASE_URL = st.secrets["api"]["base_url"]
if not API_BASE_URL:
    raise ValueError("API_BASE_URL is not set in Streamlit secrets.")

API_USER_URL = f"{API_BASE_URL}/users"

# Streamlit UI components
# Set page configuration (must be the first Streamlit command)
st.set_page_config(page_title="Bodhi Books Management System", layout="wide")

init_session_state()
page = "Home"
login_section()

# Protected Pages
if st.session_state.logged_in:
    # Sidebar Navigation
    st.sidebar.header("Navigation")
    nav_options = ["Home", "Inventory Management", "Sales Records", "Orders"]
    
    # Add Admin option only for admin users
    if st.session_state.role == "admin":
        nav_options.append("Admin")
    
    page = st.sidebar.radio(
        "Go to",
        options=nav_options,
        format_func=lambda x: f"🏠 {x}" if x == "Home" else (
            "📦 Inventory" if x == "Inventory Management" else
            "📊 Sales" if x == "Sales Records" else
            "🛒 Orders" if x == "Orders" else
            "⚙️ Admin"
        )
    )
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
        logout()
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
                    edit_book(book)
                    #st.session_state.selected_book = book
    
                if cols[5].button("Delete", key=f"delete_{book['_id']}"):
                    delete_book(book["_id"])
                    st.success(f"Book '{book['title']}' deleted successfully.")
                    st.session_state.refresh_inventory = True
                    st.rerun()

        
    # Sales Records Page
    elif page == "Sales Records":
        st.title("📊 Sales Records")
        
        # Filters Section at the top
        st.header("🔍 Filter Sales Data")
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", key="sales_start_date")
            sale_type = st.selectbox(
                "Sale Type",
                ["All", "online", "instore"],  # Changed to match backend values
                format_func=lambda x: x.title() if x != "All" else x,
                key="sale_type_filter"
            )
        
        with col2:
            end_date = st.date_input("End Date", key="sales_end_date")
            status = st.selectbox(
                "Order Status",
                ["All", "pending", "shipped", "received", "canceled"],  # Changed to match backend values
                format_func=lambda x: x.title() if x != "All" else x,
                key="status_filter"
            )
        
        with col3:
            book_title = st.text_input("Book Title", key="book_title_filter")
            genres = st.multiselect(
                "Genres",
                ["Science", "Science Fiction", "Mystery", "Fiction", "Romance", "Comic", "Non-Fiction"],
                key="genre_filter"
            )
        
        # Build filter parameters
        filter_params = {
            "startDate": start_date.isoformat() if start_date else None,
            "endDate": end_date.isoformat() if end_date else None,
            "type": sale_type if sale_type != "All" else None,  # Removed .lower() since values already match
            "orderStatus": status if status != "All" else None,  # Removed .lower() since values already match
            "bookTitle": book_title if book_title else None,
        }
        
        # Add genres as a comma-separated list if any are selected
        if genres:
            filter_params["genre"] = ",".join(genres)
        
        # Remove None values
        filter_params = {k: v for k, v in filter_params.items() if v is not None}
        
        try:
            # Sales Overview Section
            st.header("Sales Overview")
            
            # Debug filter parameters
            with st.expander("Debug Filters"):
                st.write("Applied Filters:", filter_params)
            
            # Fetch summary statistics with filters
            summary_response = requests.get(f"{API_SALESREPORTS_URL}/summary", params=filter_params)
            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                
                # Display key metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Revenue", f"${summary_data['totalRevenue']:,.2f}")
                with col2:
                    st.metric("Total Orders", f"{summary_data['totalOrders']:,}")
                with col3:
                    st.metric("Total Items", f"{summary_data['totalItems']:,}")
                with col4:
                    st.metric("Avg Order Value", f"${summary_data['averageOrderValue']:,.2f}")
                
                # Sales by Type and Status
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Sales by Type")
                    type_data = {
                        item['_id'] if item['_id'] else 'In-Store': item['revenue'] 
                        for item in summary_data['salesByType']
                    }
                    if type_data:
                        st.bar_chart(type_data)
                    else:
                        st.info("No sales type data available for the selected filters.")
                
                with col2:
                    st.subheader("Sales by Status")
                    status_data = {
                        item['_id'] if item['_id'] else 'Completed': item['count'] 
                        for item in summary_data['salesByStatus']
                    }
                    if status_data:
                        st.bar_chart(status_data)
                    else:
                        st.info("No status data available for the selected filters.")
            
            # Sales Trends Section
            st.header("Sales Trends")
            
            # Daily Sales Chart with filters
            daily_response = requests.get(f"{API_SALESREPORTS_URL}/daily", params=filter_params)
            if daily_response.status_code == 200:
                daily_data = daily_response.json()
                
                if daily_data:
                    # Create DataFrame for better visualization
                    import pandas as pd
                    df_daily = pd.DataFrame(daily_data)
                    df_daily['_id'] = pd.to_datetime(df_daily['_id'])
                    df_daily = df_daily.set_index('_id')
                    
                    # Allow user to select metric to view
                    metric = st.selectbox(
                        "Select Metric",
                        ["Total Sales ($)", "Total Items", "Order Count"],
                        key="daily_metric"
                    )
                    
                    if metric == "Total Sales ($)":
                        st.line_chart(df_daily['totalSales'])
                    elif metric == "Total Items":
                        st.line_chart(df_daily['totalItems'])
                    else:
                        st.line_chart(df_daily['orderCount'])
                else:
                    st.info("No daily sales data available for the selected filters.")
            
            # Top Genres Chart with filters
            st.header("Top Selling Genres")
            genres_response = requests.get(f"{API_SALESREPORTS_URL}/top-genres", params=filter_params)
            if genres_response.status_code == 200:
                genres_data = genres_response.json()
                
                if genres_data:
                    # Create two columns for revenue and quantity
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("By Revenue")
                        genre_revenue = {item['_id']: item['revenue'] for item in genres_data}
                        st.bar_chart(genre_revenue)
                    
                    with col2:
                        st.subheader("By Quantity")
                        genre_quantity = {item['_id']: item['totalSales'] for item in genres_data}
                        st.bar_chart(genre_quantity)
                else:
                    st.info("No genre data available for the selected filters.")
            
            # Detailed Sales List
            st.header("Sales Details")
            
            # Fetch filtered sales data
            sales_response = requests.get(f"{API_BASE_URL}/sales", params=filter_params)
            if sales_response.status_code == 200:
                sales_data = sales_response.json()
                
                if not sales_data:
                    st.info("No sales found matching the specified criteria.")
                else:
                    # Display sales in an expandable table
                    for sale in sales_data:
                        with st.expander(
                            f"Order #{sale.get('_id')} - {sale['orderDate']} - ${sale['totalPrice']:.2f}"
                        ):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Order Details**")
                                st.write(f"Type: {sale['type'].title()}")
                                st.write(f"Status: {sale['orderStatus'].title()}")
                                st.write(f"Payment Method: {sale['paymentMethod'].title()}")
                                st.write(f"Total Items: {sale['totalItems']}")
                            
                            with col2:
                                st.write("**Shipping Details**")
                                if sale.get('shippingAddress'):
                                    addr = sale['shippingAddress']
                                    st.write(f"Street: {addr.get('street', 'N/A')}")
                                    st.write(f"City: {addr.get('city', 'N/A')}")
                                    st.write(f"State: {addr.get('state', 'N/A')}")
                                    st.write(f"ZIP: {addr.get('zipCode', 'N/A')}")
                            
                            st.write("**Ordered Items**")
                            for item in sale['orderItems']:
                                book = item['bookDetails']
                                st.markdown(f"""
                                * **{book['title']}** by {book['author']}
                                  * Quantity: {item['quantity']}
                                  * Price: ${item['price']:.2f}
                                  * Genre: {book['genre']}
                                  * ISBN: {book['isbn']}
                                """)
            
        except Exception as e:
            st.error(f"Error loading sales data: {str(e)}")

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
        if st.button("Create Order"):
            if 'booksOrdered' in st.session_state:
                del st.session_state['booksOrdered']
            create_order()

            
        cancel_button = False
        cancel_order_id = ""

        # if order details not selected, hide this state
        if "selected_order" not in st.session_state:
            st.session_state.selected_order = None

        # Section: View Existing Purchase Orders
        st.subheader("Existing Purchase Orders")

        orders = fetch_orders()
        if orders:
            header_cols = st.columns([3, 2, 3, 2, 2, 2, 2])
            header_cols[0].write("Order Number")
            header_cols[1].write("Status")
            header_cols[2].write("Supplier Name")
            header_cols[3].write("Ordered On")
            header_cols[4].write("Total Cost")
            header_cols[5].write("")
            header_cols[6].write("")
            for order in orders:
                order_id = order['_id']
                date = ""
                cols = st.columns([3, 2, 3, 2, 2, 2, 2])
                cols[0].write(order.get("orderNumber", "N/A"))
                cols[1].write(str(order.get("status", "N/A")).capitalize())
                cols[2].write(order.get("supplierName", "N/A"))
                cols[3].write(formatDate(order['orderDate']))
                cols[4].write(f"${order['totalCost']:.2f}")
                if cols[5].button("Details", key=f'order_{order_id}'):
                    order_details(order_id)
                if cols[6].button("Cancel", key=f'cancel_{order_id}'):
                    cancel_order(order_id)

    # Admin Page
    elif page == "Admin":
        st.title("⚙️ Admin Dashboard")
        
        # User Management Section
        st.header("👥 User Management")
        
        # Fetch all users
        users = fetch_users_api()
        
        # Create new user button
        if st.button("➕ Create New User"):
            create_user()
        
        if users:
            # Display users in a table
            st.subheader("Current Users")
            
            # Table headers
            cols = st.columns([2, 2, 2, 1, 1, 1])
            cols[0].write("**Name**")
            cols[1].write("**Email**")
            cols[2].write("**Role**")
            cols[3].write("**Status**")
            cols[4].write("**Actions**")
            cols[5].write("")
            
            # Display each user
            for user in users:
                cols = st.columns([2, 2, 2, 1, 1, 1])
                cols[0].write(f"{user.get('firstName', '')} {user.get('lastName', '')}")
                cols[1].write(user.get('email', 'N/A'))
                
                # Role with color
                role = user.get('role', 'N/A').title()
                role_color = {
                    'Admin': 'red',
                    'Employee': 'blue',
                    'Customer': 'green'
                }.get(role, 'grey')
                cols[2].markdown(f"<span style='color: {role_color};'>{role}</span>", unsafe_allow_html=True)
                
                # Status with color
                status = "🟢 Active" if user.get('isActive', True) else "🔴 Inactive"
                cols[3].write(status)
                
                # Edit button
                if cols[4].button("✏️", key=f"edit_user_{user['_id']}"):
                    edit_user(user)
                
                # Delete button (prevent deleting own account)
                if user.get('email') != st.session_state.user.get('email'):
                    if cols[5].button("🗑️", key=f"delete_user_{user['_id']}"):
                        success, message = delete_user_api(user['_id'])
                        if success:
                            st.success(message)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(message)
        else:
            st.info("No users found. Create a new user to get started.")

else: 
    page = "Home"

@st.dialog("Edit User")
def edit_user(user):
    with st.form("edit_user_form"):
        # User details
        email = st.text_input("Email", value=user.get('email', ''))
        first_name = st.text_input("First Name", value=user.get('firstName', ''))
        last_name = st.text_input("Last Name", value=user.get('lastName', ''))
        role = st.selectbox(
            "Role",
            options=['customer', 'employee', 'admin'],
            index=['customer', 'employee', 'admin'].index(user.get('role', 'customer'))
        )
        is_active = st.checkbox("Active", value=user.get('isActive', True))
        
        # Optional password change
        st.write("---")
        st.write("Leave password fields blank to keep current password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("Update User")
        if submitted:
            # Validate passwords if provided
            if new_password or confirm_password:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                    return
            
            # Prepare update data
            update_data = {
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "role": role,
                "isActive": is_active
            }
            
            # Add password if provided
            if new_password:
                update_data["password"] = new_password
            
            try:
                response = requests.put(
                    f"{API_USER_URL}/{user['_id']}",
                    json=update_data
                )
                
                if response.status_code == 200:
                    st.success("User updated successfully")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to update user. Please try again.")
            except Exception as e:
                st.error(f"Error updating user: {str(e)}")
