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


# Functions for creating orders
# Add books to order
def add_book_to_order(booksInOrder):
    # Select book titles from the inventory
    books = fetch_books()
    book_titles = [book['title'] for book in books]
    book_title = st.selectbox("Select Book", book_titles if books else [], key=f'book_{booksInOrder}')
                
    # Input other fields
    quantity_to_order = st.number_input("Quantity to Order", key=f'book_{booksInOrder}_qty', min_value=1, value=1)


# Create orders 
#FIXME requires testing
@st.dialog("Create Order")
def create_order():
    st.subheader("Create Purchase Order")
    booksInOrder = 0
    with st.form("purchase_order_form", clear_on_submit=True):
        order_number = st.text_input("Order Number", placeholder="e.g., ORD123")
        supplier_name = st.text_input("Supplier Name", placeholder="e.g., Book Supplier Inc.")
        #  status = st.selectbox("Status", ["Pending", "Shipped", "Received"])
        total_cost = st.number_input("Total Cost", min_value=0.0, step=0.01)
        order_date = st.date_input("Order Date")
        expected_delivery_date = st.date_input("Expected Delivery Date")

        # Select book titles from the inventory
        books = fetch_books()
        book_titles = [book['title'] for book in books]
        book_title = st.selectbox("Select Book", book_titles if books else [], key=f'book_{booksInOrder}')
                
        # Input other fields
        quantity_to_order = st.number_input("Quantity to Order", key=f'book_{booksInOrder}_qty', min_value=1, value=1)

        # FIXME always init to pending?
        submitted = st.form_submit_button("Save Purchase Order")
        if submitted:
            book_id = fetch_books(title=book_title)[0].get('_id')
            new_order = {
                "orderNumber": order_number,
                "supplierName": supplier_name,
                "booksOrdered": [{"bookId": book_id, "quantity": quantity_to_order}],
                "totalCost": total_cost,
                "status": "pending",
                "orderDate": str(order_date),
                "expectedDeliveryDate": str(expected_delivery_date)
            }
            response = requests.post(API_MFRORDER_URL, json=new_order)
                    
            # Handle the response
            if response.status_code == 201:
                st.success(f"Order '{order_number}' created successfully.")
            elif response.status_code == 400:
                st.error(" Invalid input or order already exists")
            else:
                st.error(f"Failed to create the order {order_number}. Please try again.")
                
            if new_order:
                st.info(f"Order for {quantity_to_order} units of '{book_title}' created successfully!")
            else:
                st.error("Failed to match the selected book.")
        else:
            st.error("Please fill out all required fields.")
  
    
# Function to fetch mfr order by id
def fetch_order_by_id(order_id):
    response = requests.get(API_MFRORDER_URL + f'/{order_id}')
    if response.status_code == 200:
        return response.json()  # Returns list of orders as JSON
    else:
        st.error("Failed to fetch orders. Please try again.")
        return []
    
 
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
    
# Function to handle login
def handle_login():
    role = validate_login_api(st.session_state.temp_username, st.session_state.temp_password)
    if role:
        # update the session state for successful login
        st.session_state.logged_in = True
        st.session_state.username = st.session_state.temp_username
        st.session_state.role = role
        # Set a flag to clear fields on rerun
        st.session_state.clear_fields = True
        st.rerun()
    else:
        st.error("Invalid username or password. Please try again.")