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
            # Ensure username is set from email
            registration_data = {
                "email": user_data["email"],
                "username": user_data["email"],  # Explicitly set username to email
                "password": user_data["password"],
                "firstName": user_data["firstName"],
                "lastName": user_data["lastName"],
                "phone": user_data["phone"],
                "address": user_data["address"]
            }
            
            # Add debug logging
            st.write("Debug - Sending registration data:", {**registration_data, 'password': '*****'})
            
            response = requests.post(
                f"{self.base_url}/auth/register",
                json=registration_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Add debug logging for response
            st.write("Debug - Registration response status:", response.status_code)
            
            try:
                response_data = response.json()
                st.write("Debug - Registration response:", response_data)
                
                if response.status_code == 201:
                    # Store auth token and user data in session
                    st.session_state.user = response_data["user"]
                    st.session_state.token = response_data["token"]
                    st.session_state.is_authenticated = True
                    st.session_state.auth_error = None
                    return response_data
                else:
                    # Extract detailed error message
                    error_msg = response_data.get("error", "Registration failed")
                    if "details" in response_data:
                        error_msg += f": {response_data['details']}"
                    elif "message" in response_data:
                        error_msg += f": {response_data['message']}"
                    
                    # Check for specific error cases
                    if "duplicate key" in str(response_data).lower():
                        error_msg = "An account with this email already exists"
                    elif "validation" in str(response_data).lower():
                        error_msg = "Please check your input: " + error_msg
                    
                    st.session_state.auth_error = error_msg
                    st.error(error_msg)
                    return None
            except Exception as e:
                st.write("Debug - Response parsing error:", str(e))
                st.write("Raw response text:", response.text)
                raise e
        except Exception as e:
            error_msg = f"Registration failed: {str(e)}"
            if "connection" in str(e).lower():
                error_msg = "Unable to connect to the server. Please try again later."
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
            
            # Add debug logging
            print(f"Login response status: {response.status_code}")
            print(f"Login response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if not data.get('data'):
                    st.error("Invalid server response format")
                    return False
                    
                user_data = data['data'].get('user', {})
                token = data['data'].get('token')
                
                if not user_data or not token:
                    st.error("Missing user data or token in response")
                    return False
                
                # Store user data and token
                st.session_state.token = token
                # Store both the user ID and profile ID
                user_data['_id'] = user_data.get('id')  # User ID
                user_data['profileId'] = user_data.get('profileId')  # Customer profile ID
                st.session_state.user = user_data
                st.session_state.is_authenticated = True
                st.session_state.auth_error = None
                
                # Store permissions if available
                if 'permissions' in data['data']:
                    st.session_state.permissions = data['data']['permissions']
                
                # Fetch complete profile data immediately after login
                self.get_customer_profile()
                
                return True
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Unknown error')
                    
                    # Provide more user-friendly error messages
                    if error_msg == 'Invalid credentials':
                        error_msg = "Incorrect email or password. Please try again."
                    elif 'not found' in error_msg.lower():
                        error_msg = "No account found with this email address."
                    elif 'password' in error_msg.lower():
                        error_msg = "Incorrect password. Please try again."
                    
                    st.error(error_msg)
                except:
                    st.error("Login failed. Please check your credentials and try again.")
                return False
                
        except requests.exceptions.ConnectionError:
            st.error("Unable to connect to the server. Please check your internet connection and try again.")
            return False
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
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
            # Get the profile ID (Customer ID) from the session
            profile_id = st.session_state.user.get('profileId')
            if not profile_id:
                st.error("Customer profile ID not found. Please try logging out and back in.")
                return False

            # Add debug logging
            st.write("Debug - Fetching profile with ID:", profile_id)
            
            # Fetch customer profile using the customers endpoint
            response = requests.get(
                f"{self.base_url}/customers/{profile_id}",
                headers=headers
            )
            
            st.write("Debug - Profile response status:", response.status_code)
            
            if response.status_code == 200:
                profile_data = response.json()
                st.write("Debug - Profile response:", profile_data)
                
                # Check if the response has a data wrapper
                if 'data' in profile_data:
                    profile_data = profile_data['data']
                
                # Ensure we have both user ID and profile ID set correctly
                profile_data['_id'] = st.session_state.user['_id']  # Keep the user ID
                profile_data['profileId'] = profile_id  # Keep the profile/customer ID
                
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
            # Get the profile ID (Customer ID) from the session
            profile_id = st.session_state.user.get('profileId')
            if not profile_id:
                st.error("Customer profile ID not found. Please try logging out and back in.")
                return False

            # Add debug logging
            st.write("Debug - Updating profile with ID:", profile_id)
            st.write("Debug - Update data:", profile_data)
            
            # Use the customers endpoint with the profile ID
            response = requests.put(
                f"{self.base_url}/customers/{profile_id}",
                headers=headers,
                json=profile_data
            )
            
            st.write("Debug - Update response status:", response.status_code)
            
            if response.status_code == 200:
                updated_profile = response.json()
                st.write("Debug - Update response:", updated_profile)
                
                # Check if the response has a data wrapper
                if 'data' in updated_profile:
                    updated_profile = updated_profile['data']
                
                # Ensure we maintain both IDs
                updated_profile['_id'] = st.session_state.user['_id']  # Keep the user ID
                updated_profile['profileId'] = profile_id  # Keep the profile ID
                
                # Merge profile data with existing user data
                st.session_state.user.update(updated_profile)
                return True
            else:
                error_msg = response.json().get('error', 'Unknown error occurred')
                st.error(f"Failed to update profile: {error_msg}")
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
                
            # Get the current user's profile ID (customer ID) to filter sales
            customer_id = st.session_state.user.get('profileId')
            if not customer_id:
                st.error("Customer profile ID not found")
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