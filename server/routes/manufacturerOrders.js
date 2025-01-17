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

// book subschema
const bookOrderedSchema = new mongoose.Schema({
  bookId: {
    type: mongoose.Types.ObjectId,
    ref: 'books', 
    required: true,
  },
  quantity: {
    type: Number,
    required: true,
    min: 1,
  },
});

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
  booksOrdered: [ bookOrderedSchema ],
  status: {
    type: String,
    default: 'pending',
    required: true,
    enum: ['pending', 'shipped', 'received', 'canceled']
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
  },
},
{
  timestamps: true
}
);

const MfrOrder = mongoose.model('MfrOrder', mfrOrderSchema);

/**
 * @swagger
 * /api/manufacturerOrders:
 *   get:
 *     summary: Returns a list of vendor orders
 *     tags:
 *       - Manufacturer Orders
 *     parameters:
 *       - in: path
 *         name: supplierName
 *         schema:
 *           type: string
 *         description: Supplier Name
 *       - in: path
 *         name: status
 *         schema:
 *           type: string
 *         description: Order Status
 *       - in: path
 *         name: orderDate
 *         schema:
 *           type: string
 *         description: Order date 
 *     responses:
 *       200:
 *         description: List of vendor orders
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/MfrOrder'
 */
router.get('/', async (req, res) => {
  try {
    const { supplierName, status, orderDate } = req.query;
    let query = {};

    if (supplierName) query.supplierName = supplierName;
    if (status) query.status = status;
    if (orderDate) query.orderDate = orderDate;

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
 *     summary: Create a new order
 *     tags: 
 *       - Manufacturer Orders
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/MfrOrder'
 *     responses:
 *       201:
 *         description: Order created successfully
 *       400:
 *         description: Invalid input or order already exists
 */

router.post('/', async (req, res) => {
  try{ 
    const order = new MfrOrder(req.body);
    const savedOrder = await order.save();
    res.status(201).json(savedOrder);
  } catch {
    if (error.code === 11000) {
      return res.status(400).json({ error: 'User already exists' });
    }
    res.status(400).json({ error: 'Error creating user', details: error.message });
  }
})

/**
 * @swagger
 * /api/manufacturerOrders/{id}:
 *   put:
 *     summary: Update an order
 *     tags: 
 *       - Manufacturer Orders
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: Book ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/MfrOrder'
 *     responses:
 *       200:
 *         description: Order updated successfully
 *       404:
 *         description: Order not found
 */
router.put('/:id', async (req, res) => {
  try {
    const updates = {
      ...req.body,
      updatedAt: Date.now()
    };

    const order = await MfrOrder.findByIdAndUpdate(
      new mongoose.Types.ObjectId(req.params.id),
      updates,
      {
        new: true,
        runValidators: true
      }
    ).select('-__v');

    if (!order) {
      return res.status(404).json({ error: 'Book not found' });
    }

    res.json(order);
  } catch (error) {
    if (error.code === 11000) {
      return res.status(400).json({ error: 'Order number already exists' });
    }
    res.status(400).json({ error: 'Order updating book', details: error.message });
  }
});

module.exports = router;
