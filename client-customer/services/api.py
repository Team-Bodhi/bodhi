from datetime import datetime
from typing import Dict, Optional, Tuple

import requests
import streamlit as st


class ApiService:
    def __init__(self):
        self.base_url = st.secrets["api"]["base_url"]
    
    def get_headers(self):
        """Get the headers for API requests"""
        headers = {
            'Content-Type': 'application/json'
        }
        if st.session_state.is_authenticated and st.session_state.token:
            headers['Authorization'] = f'Bearer {st.session_state.token}'
        return headers

    def submit_order(self, order_data: Dict) -> Tuple[bool, Optional[Dict]]:
        """Submit a new order"""
        if not st.session_state.is_authenticated:
            st.error("Please login to place an order")
            return False, None

        try:
            # Add order status and type to the order data
            order_data.update({
                "orderStatus": "pending",
                "type": "online",
                "orderDate": datetime.now().isoformat()
            })

            response = requests.post(
                f"{self.base_url}/sales",
                headers=self.get_headers(),
                json=order_data
            )

            if response.status_code == 201:
                return True, response.json()
            else:
                error_msg = response.json().get("error", "Failed to create order")
                if "details" in response.json():
                    error_msg += f": {response.json()['details']}"
                st.error(f"Order submission failed: {error_msg}")
                return False, response

        except Exception as e:
            st.error(f"Error submitting order: {str(e)}")
            return False, None


api_service = ApiService()

def get_auth_headers():
    """Get headers with auth token if available"""
    headers = {
        'Content-Type': 'application/json'
    }
    if st.session_state.is_authenticated and st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    return headers

def fetch_books():
    """Fetch all books from the API"""
    try:
        response = requests.get(
            f"{st.secrets['api']['base_url']}/books",
            headers=get_auth_headers()
        )
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