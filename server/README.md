# Bodhi Bookstore Management System - Server

This is the backend server for the Bodhi Bookstore Management System, a comprehensive platform designed to manage bookstore operations including inventory management, sales tracking, and order processing.

## Features

- **Inventory Management**: Complete CRUD operations for book inventory
- **OpenAPI Documentation**: Swagger UI for API exploration and testing
- **Data Validation**: Built-in validation for all book-related operations
- **MongoDB Integration**: Robust data persistence with MongoDB
- **Error Handling**: Comprehensive error handling and logging
- **Stock Alerts**: Automatic low stock detection and alerts

## Prerequisites

- Node.js >= 18.0.0
- MongoDB
- npm or yarn

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Team-Bodhi/bodhi.git
cd bodhi
```

2. Install dependencies:

```bash
npm install
```

## Running the Server

Development mode with hot reload:

```bash
npm run dev
```

Production mode:

```bash
npm start
```

## API Documentation

The API documentation is available through Swagger UI at:

```
http://localhost:3000/api-docs
```

## API Endpoints

### Books

- `GET /api/books` - Get all books (with optional filters)
- `GET /api/books/:id` - Get a specific book
- `POST /api/books` - Create a new book
- `PUT /api/books/:id` - Update a book
- `DELETE /api/books/:id` - Delete a book

### Health Check

- `GET /health` - Server health check endpoint

## Project Structure

```
bodhi-server/
├── routes/
│   └── books.js         # Book-related routes and schema
├── server.js            # Main application file
├── package.json         # Project dependencies and scripts
└── .env                 # Environment variables (create this)
```

## Future Implementations

- Customer Order Management
- Manufacturer Order Management
- Sales Record Tracking
- User Authentication and Authorization
- Role-Based Access Control

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
