from datetime import datetime
from typing import Dict, Optional

import requests
import streamlit as st


class AuthService:
    def __init__(self):
        self.base_url = st.secrets["api"]["base_url"]
        
    def register(self, user_data: Dict) -> Optional[Dict]:
        """Register a new customer"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/register",
                json=user_data,
                headers={'Content-Type': 'application/json'}
            )
            
            try:
                response_data = response.json()
                st.write("Response Data:", response_data)
                
                if response.status_code == 201:
                    # Store auth token and user data in session
                    st.session_state.user = response_data["user"]
                    st.write("Debug - Stored User Data:", st.session_state.user)
                    st.session_state.token = response_data["token"]
                    st.session_state.is_authenticated = True
                    st.session_state.auth_error = None
                    return response_data
                else:
                    error_msg = response_data.get("error", "Registration failed")
                    st.session_state.auth_error = error_msg
                    st.error(error_msg)
                    return None
            except Exception as e:
                st.write("Response Text:", response.text)
                raise e
        except Exception as e:
            error_msg = f"Registration failed: {str(e)}"
            st.session_state.auth_error = error_msg
            st.error(error_msg)
            return None
    
    def login(self, email: str, password: str) -> bool:
        """Login user"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                headers={
                    'Content-Type': 'application/json'
                },
                json={
                    'email': email,
                    'password': password
                }
            )
            
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('data', {}).get('user', {})
                token = data.get('data', {}).get('token')
                
                # Get the complete user profile
                profile_response = requests.get(
                    f"{self.base_url}/auth/profile",
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {token}'
                    }
                )
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    # Merge profile data with user data
                    user_data.update(profile_data)
                
                st.session_state.token = token
                st.session_state.user = user_data
                st.session_state.is_authenticated = True
                st.session_state.auth_error = None
                
                # Debug stored user data
                st.write("Debug - Stored User Data:", st.session_state.user)
                return True
            else:
                error_msg = response.json().get("error", "Login failed")
                st.session_state.auth_error = error_msg
                st.error(error_msg)
                return False
        except Exception as e:
            error_msg = f"Login failed: {str(e)}"
            st.session_state.auth_error = error_msg
            st.error(error_msg)
            return False
    
    def logout(self):
        """Logout the current user"""
        st.session_state.user = None
        st.session_state.token = None
        st.session_state.is_authenticated = False
        st.session_state.permissions = None
        st.session_state.auth_error = None
        st.session_state.cart = []
        st.session_state.total_amount = 0.0
    
    def get_headers(self):
        """Get the headers for API requests"""
        headers = {
            'Content-Type': 'application/json'
        }
        if st.session_state.is_authenticated and st.session_state.token:
            headers['Authorization'] = f'Bearer {st.session_state.token}'
        return headers

    def get_customer_profile(self):
        """Fetch the complete customer profile data"""
        if not st.session_state.is_authenticated:
            return None
        
        headers = self.get_headers()
        try:
            
            # Get the profile ID from the session - use _id since this is the customer's profile ID
            profile_id = st.session_state.user.get('_id')
            if not profile_id:
                st.error("Customer profile not found. Please try logging out and back in.")
                return False

            # Fetch customer profile using the customers endpoint
            response = requests.get(
                f"{self.base_url}/customers/{profile_id}",
                headers=headers
            )
            
            
            if response.status_code == 200:
                profile_data = response.json()
                # Check if the response has a data wrapper
                if 'data' in profile_data:
                    profile_data = profile_data['data']
                # Merge profile data with existing user data
                st.session_state.user.update(profile_data)
                return True
            else:
                error_msg = response.json().get('error', 'Unknown error occurred')
                st.error(f"Failed to fetch profile data: {error_msg}")
                return False
                
        except Exception as e:
            st.error(f"Error fetching profile: {str(e)}")
            return False

    def update_profile(self, profile_data):
        """Update the customer profile"""
        if not st.session_state.is_authenticated:
            return False
            
        headers = self.get_headers()
        try:
            response = requests.put(
                f"{self.base_url}/customers/{st.session_state.user.get('_id')}",
                headers=headers,
                json=profile_data
            )
            
            if response.status_code == 200:
                updated_profile = response.json()
                # Update session state with new profile data
                st.session_state.user.update(updated_profile)
                return True
            else:
                st.error("Failed to update profile")
                return False
                
        except Exception as e:
            st.error(f"Error updating profile: {str(e)}")
            return False

    def get_orders(self) -> Optional[list]:
        """Get customer's order history"""
        try:
            if not st.session_state.is_authenticated:
                st.error("Please login to view your orders")
                return None
                
            # Get the current user's ID to filter sales
            customer_id = st.session_state.user.get('_id')
            if not customer_id:
                st.error("Customer ID not found")
                return None
                
            response = requests.get(
                f"{self.base_url}/sales",
                headers=self.get_headers(),
                params={
                    'customerId': customer_id
                }
            )
            
            if response.status_code == 200:
                st.session_state.auth_error = None
                return response.json()
            else:
                error_msg = response.json().get("error", "Failed to fetch orders")
                st.session_state.auth_error = error_msg
                st.error(error_msg)
                return None
        except Exception as e:
            error_msg = f"Failed to fetch orders: {str(e)}"
            st.session_state.auth_error = error_msg
            st.error(error_msg)
            return None

    def submit_order(self, order_data: Dict) -> Optional[Dict]:
        """Submit a new order"""
        if not st.session_state.is_authenticated:
            st.error("Please login to place an order")
            return None

        try:
            # Transform the order data to match server expectations
            formatted_order = {
                "customerId": st.session_state.user.get("_id"),  # Use the customer profile ID
                "orderItems": [
                    {
                        "bookId": item["bookId"],
                        "quantity": item["quantity"]
                    }
                    for item in order_data["items"]
                ],
                "shippingAddress": order_data["shipping"],
                "paymentMethod": order_data["payment_method"],  # Match the exact field name
                "totalPrice": float(order_data["total"]),  # Ensure it's a number
                "orderStatus": "pending",
                "type": "online",
                "orderDate": datetime.now().isoformat()
            }

            # Debug the formatted order
            st.write("Debug - Formatted Order:", formatted_order)

            response = requests.post(
                f"{self.base_url}/sales",
                headers=self.get_headers(),
                json=formatted_order
            )

            # Debug the response
            st.write("Debug - Order Response:", response.json())

            if response.status_code == 201:
                return response.json()
            else:
                error_msg = response.json().get("error", "Failed to create order")
                if "details" in response.json():
                    error_msg += f": {response.json()['details']}"
                st.error(f"Order submission failed: {error_msg}")
                return None

        except Exception as e:
            st.error(f"Error submitting order: {str(e)}")
            return None

auth_service = AuthService() 