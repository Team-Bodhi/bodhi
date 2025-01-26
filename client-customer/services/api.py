from datetime import datetime

import requests
import streamlit as st

API_BASE_URL = st.secrets["api"]["base_url"]

def fetch_books():
    """Fetch all books from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/books")
        return response.json()
    except:
        st.error("Unable to connect to the server. Using sample data.")
        return [
            {
                "_id": "1", 
                "title": "Sample Book", 
                "author": "Sample Author", 
                "genre": "Fiction", 
                "price": 29.99, 
                "quantity": 10, 
                "summary": "A sample book description", 
                "isbn": "123-456-789",
                "publisher": "Sample Publisher", 
                "pages": 300,
                "language": "English", 
                "publicationDate": "2024-01-01T00:00:00.000Z",
                "coverImageUrl": "http://dummyimage.com/180x100.png/dddddd/000000"
            }
        ]

def submit_order(cart_items, shipping_info, payment_method, total_amount):
    """Submit an order to the API"""
    order_data = {
        "type": "online",
        "bookOrdered": [
            {
                "bookId": item["bookId"],
                "quantity": item["quantity"],
                "price": item["price"]
            } for item in cart_items
        ],
        "status": "pending",
        "saleDate": datetime.now().isoformat(),
        "totalPrice": total_amount,
        "paymentMethod": payment_method,
        "shippingAddress": shipping_info
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/sales", json=order_data)
        return response.status_code in [200, 201], response
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False, None 