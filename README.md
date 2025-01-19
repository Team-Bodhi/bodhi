# 📚 Bodhi Bookstore Management System

Welcome to the **Bodhi Bookstore Management System** repository! This project is a Streamlit-based web application designed to manage the inventory, sales, and orders for a rare books bookstore.

## 🎯 Project Overview

The Bodhi Bookstore Management System is designed to streamline bookstore operations, providing features for managing inventory, creating purchase orders, tracking sales, and managing user access securely through an API. It integrates with a backend API for seamless interaction with the database.

## 🚀 Features

- **Inventory Management**:
  - View and filter books by genre, language, and stock status.
  - Add, update, and delete books in the inventory.
  - Highlight low-stock items (stock level below 20) for easy restocking.

- **Order Management**: still in progress
  - Create purchase orders for books running low on stock.
  - View existing purchase orders (coming soon with API integration).

- **User Authentication**:
  - Secure login and account creation using API endpoints.
  - Supports role-based access for "Manager," "Clerk," and "Admin."

- **Sales Records**: still in progress
  - View and analyze sales data (feature in progress).

📌 **Future Enhancements**
Full integration of the purchase order system with the backend API.
Detailed sales reporting and analytics.

  **Local Setup**: (assumes you already cloned the repo)
  
- **Installation Requirements**:
  - Python Version: 3.12.8 
  - Streamlit Version: 1.41.1 
  - IDE (Optional): Spyder

- **Environment setup**:
  - Create a Virtual Environment: Using conda ([recommended](https://docs.conda.io/en/latest/)): 
  - conda create --name bodhi_books python=3.12.8
  - conda activate bodhi_books

- **Install dependencies**: (if using conda follow below)
  - conda install -r requirements.txt 

- **Setup environment variables**:
  - Create a .streamlit/secrets.toml file in the root of the project. 
  - Add the following lines to the file:
```json
[api]
base_url = "https://bodhi-23sn.onrender.com/api"
```

- **Running the Application**:
  - Navigate to the directory where the main app file is located (e.g., Bookstore_UI.py). 
  - Run the following command: streamlit run Bookstore_UI.py
  - Open the app in your browser using the URL provided in the terminal (usually http://localhost:8501). 
  


