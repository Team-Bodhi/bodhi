import requests
import streamlit as st

# For streamlit cloud deployment uncomment this sesction, comment out local section
API_BASE_URL = st.secrets["api"]["base_url"]
if not API_BASE_URL:
    raise ValueError("API_BASE_URL is not set in Streamlit secrets.")

API_BOOKS_URL = API_BOOKS_URL = f"{API_BASE_URL}/books"
API_USER_URL = f"{API_BASE_URL}/users"
API_AUTH_URL = f"{API_BASE_URL}/auth"
API_MFRORDER_URL = f"{API_BASE_URL}/manufacturerOrders"
API_SALESREPORTS_URL = f"{API_BASE_URL}/reports/sales"

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
    if response.status_code == 200:
        return response.json()  # Returns list of orders as JSON
    else:
        st.error("Failed to fetch orders. Please try again.")
        return []

# Function to update an existing book 
def update_mfr_order(order_id, orderNumber, supplierName, status, booksOrdered, totalCost, orderedDate, expectedDate):
    updated_order = {
        "orderNumber": orderNumber,
        "supplierName": supplierName,
        "status": status,
        "booksOrdered": booksOrdered,
        "totalCost": totalCost,
        "orderedDate": orderedDate,
        "expectedDate": expectedDate,
    }

    # if order status is received, add qty to stock
    if status == 'received':
        for book in booksOrdered:
            bookDetails = fetch_book_by_id(book['bookId'])
            update_book(
                book_id=book['bookId'], 
                title=bookDetails['title'], 
                author=bookDetails['author'], 
                genre=bookDetails['genre'], 
                quantity=(int(bookDetails['quantity']) + int(book['quantity'])), 
                price=bookDetails['price']
            )
        
    response = requests.put(f"{API_MFRORDER_URL}/{order_id}", json=updated_order)
    if response.status_code == 200:
        st.success(f"Book '{orderNumber}' updated successfully!")
        return True
    else:
        st.error(f"Failed to update order: {response.text}")
        return False

# cancel an order

def cancel_order(order_id):
    orderIdFormatted = str(order_id)
    response = requests.put(f"{API_MFRORDER_URL}/cancel/{orderIdFormatted}")
    if response.status_code == 200:
        st.success(f"Order canceled successfully!")
        st.rerun()
        return True
    else:
        st.error(f"Failed to cancel order: {response.text}")
        return False

# Function for adding a new user
def add_user_api(email, password, first_name, last_name, role):
    new_user = {
        "email": email,
        "password": password,
        "firstName": first_name,
        "lastName": last_name,
        "role": role
    }
    try:
        response = requests.post(f"{API_AUTH_URL}/register", json=new_user)
        response_data = response.json()
        
        if response.status_code == 201:
            return "Employee account created successfully! You can now log in."
        elif response.status_code == 400:
            return response_data.get("error", "Invalid input or email already exists.")
        else:
            return response_data.get("error", "Failed to create account. Please try again.")
    except Exception as e:
        return f"Error creating account: {str(e)}"

# Function to handle login
def handle_login():
    try:
        credentials = {
            "email": st.session_state.temp_email,
            "password": st.session_state.temp_password
        }
        response = requests.post(f"{API_AUTH_URL}/login", json=credentials)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get("success"):
            user_data = response_data.get("data", {}).get("user", {})
            
            # Update session state with user info
            st.session_state.logged_in = True
            st.session_state.role = user_data.get("role")
            st.session_state.name = f"{user_data.get('firstName', '')} {user_data.get('lastName', '')}"
            st.session_state.clear_fields = True
            
            return True
        else:
            error_msg = response_data.get("error", "Login failed. Please try again.")
            st.error(error_msg)
            return False
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return False


#########################################################################
#                            Modals                                     #
#########################################################################

@st.dialog("Edit Book")
def edit_book(book):
    with st.form("update_book_form",clear_on_submit=True):
        new_title = st.text_input("Book Title", value=book["title"])
        new_author = st.text_input("Author", value=book["author"])
        new_genre = st.text_input("Genre", value=book["genre"])
        new_quantity = st.number_input("Quantity", min_value=0, value=book["quantity"])
        new_price = st.number_input("Price", min_value=0.0, value=float(book["price"]))
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
        order_date = st.date_input("Order Date", format="MM/DD/YYYY")
        expected_delivery_date = st.date_input("Expected Delivery Date", format="MM/DD/YYYY")

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
                st.rerun()
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

# open dialog for order details
@st.dialog("Order Details")
def order_details(order_id):
    order = fetch_order_by_id(order_id)

    if order:
        if order['status'] == 'pending':
            # update functionality
            with st.form("update_mfr_order_form",clear_on_submit=True):
                new_orderNum = st.text_input("Order Number", value=order["orderNumber"])
                new_supplier = st.text_input("Supplier Name", value=order["supplierName"])
                new_status = st.selectbox("Status", ["Pending", "Shipped", "Received"])
                new_totalCost = st.number_input("Total Cost", min_value=0.0, value=float(order["totalCost"]))
                new_orderDate = st.date_input("Order Date", format="MM/DD/YYYY", value=order["orderDate"])
                new_expected = st.date_input("Expected Date", format="MM/DD/YYYY", value=order["expectedDeliveryDate"])

                st.subheader("Books Ordered:")
                # Display table headers with Streamlit columns 
                header_cols = st.columns([3, 3, 3, 2])
                header_cols[0].write("Title")
                header_cols[1].write("Author")
                header_cols[2].write("Genre")
                header_cols[3].write("Order Quantity")
                for book in order['booksOrdered']:

                    book_details = fetch_book_by_id(str(book['bookId']))
                            
                    cols = st.columns([2, 2, 2, 1])
                    cols[0].write(book_details["title"])
                    cols[1].write(book_details["author"])
                    cols[2].write(book_details["genre"])
                    cols[3].write(book['quantity'])

                update_submitted = st.form_submit_button("Update Order")
                if update_submitted:
                    success = update_mfr_order(
                        order["_id"],
                        new_orderNum,
                        new_supplier,
                        new_status.lower(),
                        order['booksOrdered'],
                        float(new_totalCost),
                        str(new_orderDate),
                        str(new_expected),
                    )
                    if success:
                        st.success(f"Order #{new_orderNum} updated successfully!")
                        # Clear the selected order and refresh the orders
                        st.rerun()   
        else:
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
            try:
                for book in order['booksOrdered']:
                    book_details = fetch_book_by_id(str(book['bookId']))
                    cols = st.columns([2, 2, 2, 1])
                    cols[0].write(book_details['title'])
                    cols[1].write(book_details['author'])
                    cols[2].write(book_details['genre'])
                    cols[3].write(book['quantity'])
            except:
                st.write("One or more books from the order has been deleted from the system.")

            # in case a book from the order is deleted^^

            # if the status is shipped, give the user the ability to receive it
            if order['status'] == 'shipped':
                if st.button("Receive"):
                    update_mfr_order(
                        order_id=order["_id"],
                        orderNumber=order['orderNumber'],
                        supplierName=order['supplierName'],
                        status='received',
                        booksOrdered=order['booksOrdered'],
                        totalCost=order['totalCost'],
                        orderedDate=order['orderDate'],
                        expectedDate=order['expectedDeliveryDate']
                    )
                    st.rerun()

    else:
        st.subheader("No order found")