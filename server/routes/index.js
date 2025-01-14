const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bodhi Bookstore Management System API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            .api-link {
                display: inline-block;
                background: #3498db;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }
            .api-link:hover {
                background: #2980b9;
            }
        </style>
    </head>
    <body>
        <h1>Welcome to Bodhi Bookstore Management System API</h1>
        <p>This is the API server for the Bodhi Bookstore Management System. The API provides endpoints for managing books, inventory, orders, and sales records.</p>
        <h2>Available Endpoints:</h2>
        <ul>
            <li><code>/api/books</code> - Book management endpoints</li>
            <li><code>/health</code> - Server health check</li>
        </ul>
        <p>For detailed API documentation and testing interface, visit:</p>
        <a href="/api-docs" class="api-link">API Documentation</a>
    </body>
    </html>
  `);
});

module.exports = router; 