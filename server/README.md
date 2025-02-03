# 📚 Bodhi Bookstore Management System - Server

Welcome to the Bodhi Bookstore Management System! This is the backend server for our comprehensive bookstore management platform. We've built it to handle everything from inventory and sales to customer management and user authentication. 🚀

## ✨ Features

### 📦 Inventory Management

- 📋 Complete CRUD operations for book inventory
- 📊 Smart stock level tracking and alerts
- 📝 ISBN validation and uniqueness checks
- 🔍 Flexible book search and filtering
- ⏱️ Automatic timestamps for inventory changes

### 💰 Sales Management

- 🏪 Support for both in-store and online sales
- ⚡ Real-time inventory updates
- 🔒 Transaction support to ensure data integrity
- 📄 Detailed sales records with book information
- 💳 Multiple payment method support
- 🤝 Optional customer association
- 🚚 Shipping address tracking for online orders

### 👥 Customer Management

- 👤 Customer profile creation and management
- 📞 Contact information tracking
- 📋 Order history association
- 📍 Address management for shipping

### 🔐 User System

- 👮 Role-based user management (customer, admin, staff, manager)
- 🔑 Secure password hashing
- 🎫 User authentication
- 👤 Profile management

### ⚙️ System Features

- 🗄️ MongoDB Integration with proper ObjectID handling
- ⚠️ Comprehensive error handling
- 📝 Detailed activity logging
- 🔄 Automatic log rotation (7-day retention)
- 📚 OpenAPI/Swagger Documentation
- 💓 Health monitoring endpoint

## 🚀 Getting Started

### Prerequisites

- Node.js >= 18.0.0
- MongoDB
- npm or yarn

### 🛠️ Installation

1. Clone the repository:

```bash
git clone https://github.com/Team-Bodhi/bodhi.git
cd bodhi/server
```

2. Install dependencies:

```bash
npm install
```

3. Create a .env file with your configuration:

```env
MONGODB_URI=your_mongodb_uri
PORT=3000
JWT_SECRET=your_jwt_secret (Ask Team Bodhi for the secret)
```

### 🏃‍♂️ Running the Server

Development mode with hot reload:

```bash
npm run dev
```

Production mode:

```bash
npm start
```

## 📖 API Documentation

Browse our interactive API documentation at:

```
http://localhost:3000/api-docs
```

## 🛣️ API Endpoints

### 📚 Books

- `GET /api/books` - Get all books (with optional filters)
- `GET /api/books/:id` - Get a specific book
- `POST /api/books` - Create a new book
- `PUT /api/books/:id` - Update a book
- `DELETE /api/books/:id` - Delete a book

### 👥 Customers

- `GET /api/customers` - Get all customers
- `GET /api/customers/:id` - Get a specific customer
- `POST /api/customers` - Create a new customer
- `PUT /api/customers/:id` - Update a customer
- `DELETE /api/customers/:id` - Delete a customer

### 💰 Sales

- `GET /api/sales` - Get all sales (with optional filters)
- `GET /api/sales/:id` - Get a specific sale
- `POST /api/sales` - Create a new sale

### 🔐 Users

- `POST /api/users` - Create a new user
- `POST /api/users/login` - User login

### 🏥 System

- `GET /health` - Server health check endpoint

## 📁 Project Structure

```
bodhi-server/
├── models/           📦 Data models
│   ├── book.js
│   ├── customer.js
│   ├── sale.js
│   ├── user.js
│   └── log.js
├── routes/           🛣️ API routes
│   ├── books.js
│   ├── customers.js
│   ├── sales.js
│   ├── users.js
│   └── index.js
├── middleware/       🔄 Middleware
│   └── logger.js
├── server.js         🚀 Main application
├── package.json      📦 Dependencies
└── .env              🔒 Environment variables
```

## 🚀 Future Implementations

- 📦 Manufacturer Order Management
- 📊 Advanced Analytics Dashboard
- 📧 Email Notifications
- 💳 Payment Gateway Integration
- 🔍 Advanced Search Capabilities
- 📥 Batch Import/Export
- 📈 Report Generation

## 🤝 Contributing

We love contributions! Here's how you can help:

1. 🍴 Fork the repository
2. 🌿 Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🎉 Open a Pull Request

## 📄 License

ISC

---

Built with ❤️ by Team Bodhi
