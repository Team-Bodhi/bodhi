import requests
import streamlit as st
from utils.api import API_BASE_URL


def render_admin_customers():
    st.title("Customer Management")
    
    # Fetch customers from API
    try:
        response = requests.get(f"{API_BASE_URL}/api/admin/customers")
        customers = response.json()
        
        # Create a table of customers
        for customer in customers:
            with st.expander(f"{customer['firstName']} {customer['lastName']}"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                # Customer details
                with col1:
                    st.write("**Contact Info:**")
                    st.write(f"Email: {customer['userId']['email']}")
                    st.write(f"Phone: {customer['phone']}")
                    st.write(f"Address: {customer['address']}")
                
                # Edit form
                with col2:
                    with st.form(key=f"edit_customer_{customer['_id']}"):
                        st.write("**Edit Customer:**")
                        new_first_name = st.text_input("First Name", value=customer['firstName'])
                        new_last_name = st.text_input("Last Name", value=customer['lastName'])
                        new_phone = st.text_input("Phone", value=customer['phone'])
                        new_address = st.text_input("Address", value=customer['address'])
                        
                        if st.form_submit_button("Update"):
                            update_data = {
                                'firstName': new_first_name,
                                'lastName': new_last_name,
                                'phone': new_phone,
                                'address': new_address
                            }
                            
                            response = requests.put(
                                f"{API_BASE_URL}/api/admin/customers/{customer['_id']}", 
                                json=update_data
                            )
                            
                            if response.status_code == 200:
                                st.success("Customer updated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update customer")
                
                # Delete button
                with col3:
                    if st.button("Delete", key=f"delete_{customer['_id']}"):
                        if st.warning("Are you sure you want to delete this customer?"):
                            response = requests.delete(
                                f"{API_BASE_URL}/api/admin/customers/{customer['_id']}"
                            )
                            
                            if response.status_code == 200:
                                st.success("Customer deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete customer")
                
    except Exception as e:
        st.error(f"Error loading customers: {str(e)}")

def render_admin_page():
    st.title("Admin Dashboard")
    
    # Simple tab navigation
    tab1, tab2 = st.tabs(["Customers", "Other"])
    
    with tab1:
        render_admin_customers()
    
    with tab2:
        st.write("Other admin features coming soon...") 