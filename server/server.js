const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const mongoose = require('mongoose');
const swaggerUi = require('swagger-ui-express');
const swaggerJsdoc = require('swagger-jsdoc');
require('dotenv').config();

const app = express();

// Swagger definition
const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Bodhi API',
      version: '1.0.0',
      description: 'API for the Bodhi Bookstore Management System',
      contact: {
        name: 'API Support',
        // email: 'your.email@example.com'  // Optional: Add your contact email
      },
    },
    servers: [
      {
        url: 'http://localhost:3000',
        description: 'Development server',
      },
    ],
  },
  apis: ['./routes/*.js'], // Path to the API routes
};

const swaggerSpec = swaggerJsdoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// Middleware
app.use(cors());
app.use(morgan('dev'));
app.use(express.json());

// MongoDB connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/Bodhi';
mongoose.connect(MONGODB_URI, {
  dbName: 'Bodhi'
})
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('MongoDB connection error:', err));

// Routes
const indexRoute = require('./routes/index');
const bookRoutes = require('./routes/books.js');

app.use('/', indexRoute);
app.use('/api/books', bookRoutes);

// TODO
// Customer order routes
// const customerOrderRoutes = require('./routes/customerOrders');
// app.use('/api/customer-orders', customerOrderRoutes);

// TODO
// Manufacturer order routes
// const manufacturerOrderRoutes = require('./routes/manufacturerOrders');
// app.use('/api/manufacturer-orders', manufacturerOrderRoutes);

// Basic health check route
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not Found' });
});



const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
