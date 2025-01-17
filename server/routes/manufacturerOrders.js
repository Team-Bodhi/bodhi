const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');

/**
 * @swagger
 * components:
 *   schemas:
 *     MfrOrder:
 *       type: object
 *       required:
 *         - orderNumber
 *         - supplierName
 *         - booksOrdered
 *         - status
 *         - totalCost
 *         - orderDate
 *         - expectedDeliveryDate
 *         - createdAt
 *         - updatedAt
 *       properties:
 *         _id:
 *           type: string
 *           description: Auto-generated MongoDB ID
 *         orderNumber:
 *           type: string
 *           description: Order number (will this be an input or auto)
 *         supplierName:
 *           type: string
 *           description: Supplier the order is sent to
 *         booksOrdered:
 *           type: array
 *           description: list of books ordered
 *           items:
 *             type: object
 *             properties:
 *               bookId: 
 *                 type: string
 *                 description: ObjectId of book ordered
 *               quantity: 
 *                 type: number
 *                 description: quantity ordered of specific book
 *         status:
 *           type: string
 *           description: Status of the order (init pending)
 *         totalCost:
 *           type: number
 *           description: Total cost of the order
 *         orderDate:
 *           type: string
 *           format: date
 *           description: Date the order is placed
 *         expectedDeliveryDate:
 *           type: string
 *           format: date
 *           description: Date the order is expected to deliver (orderDate+week?)
 *         createdAt:
 *           type: string
 *           format: date
 *           description: Date the order was created (same as orderdate)
 *         updatedAt:
 *           type: string
 *           format: date
 *           description: Any updates to the order will change this value
 */

// Mfr Order Schema
const mfrOrderSchema = new mongoose.Schema({
  orderNumber: {
    type: String,
    required: true,
    trim: true
  },
  supplierName: {
    type: String,
    required: true,
    trim: true
  },
  booksOrdered: [{
    bookId: {
      type: String,
      required: true
    },
    quantity: {
      type: Number,
      min: 0 
    }  
  }],
  status: {
    type: String,
    required: true
  },
  totalCost: {
    type: Number,
    min: 0.0
  },
  orderDate: {
    type: Date,
    default: Date.now
  },
  expectedDeliveryDate: {
    type: Date,
    default: Date.now
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

mfrOrderSchema.index({ orderNumber: 1 });
const MfrOrder = mongoose.model('MfrOrder', mfrOrderSchema);

/**
 * @swagger
 * /api/manufacturerOrders:
 *   get:
 *     summary: Returns a list of vendor orders
 *     tags:
 *       - Manufacturer Orders
 *     parameters:
 *       - in: query
 *         name: supplierName
 *         schema:
 *           type: string
 *         description: Filter by supplier
 *       - in: query
 *         name: status
 *         schema:
 *           type: string
 *         description: Filter by status
 *     responses:
 *       200:
 *         description: List of vendor orders
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/MfrOrders'
 */
router.get('/', async (req, res) => {
  try {
    const { supplierName, status } = req.query;
    let query = {};

    if (supplierName) query.supplierName = supplierName;
    if (status) query.status = status;

    console.log('Collection name:', MfrOrder.collection.name);
    console.log('Database name:', mongoose.connection.db.databaseName);

    const mfrOrders = await MfrOrder.find(query)
      .select('-__v');
    console.log('Found orders:', mfrOrders.length);
    res.json(mfrOrders);
  } catch (error) {
    console.error('Error in /api/manufacturerOrders:', error);
    res.status(500).json({ error: 'Error fetching orders' });
  }
});

/**
 * @swagger
 * /api/manufacturerOrders:
 *   post:
 *     summary: Create a new mfr order
 *     tags: 
 *       - Manufacturer Orders
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/MfrOrders'
 *     responses:
 *       201:
 *         description: Mfr order created successfully
 *       400:
 *         description: Invalid input or order already exists
 */
router.post('/', async (req, res) => {
  try {
    const mfrOrder = new MfrOrder(req.body);
    const id = new mongoose.Types.ObjectId;
    mfrOrder._id = id;
    const savedMfrOrder = await mfrOrder.save();
    res.status(201).json(savedMfrOrder);
  } catch (error) {
    if (error.code === 11000) {
      return res.status(400).json({ error: 'Order already exists' });
    }
    res.status(400).json({ error: 'Error creating order', details: error.message });
  }
});

module.exports = router;
