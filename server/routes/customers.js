const express = require('express');
const router = express.Router();
const Customer = require('../models/customer');
const mongoose = require('mongoose');

/**
 * @swagger
 * components:
 *   schemas:
 *     Customer:
 *       type: object
 *       required:
 *         - name
 *         - email
 *         - phone
 *         - address
 *       properties:
 *         _id:
 *           type: string
 *           description: Auto-generated MongoDB ID
 *         name:
 *           type: string
 *           description: Customer's full name
 *         email:
 *           type: string
 *           description: Customer's email address
 *         phone:
 *           type: string
 *           description: Customer's phone number
 *         address:
 *           type: string
 *           description: Customer's shipping address
 *         createdAt:
 *           type: string
 *           format: date-time
 *         updatedAt:
 *           type: string
 *           format: date-time
 */

/**
 * @swagger
 * /api/customers:
 *   get:
 *     summary: Returns a list of customers
 *     tags:
 *       - Customers
 *     responses:
 *       200:
 *         description: List of customers
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Customer'
 */
router.get('/', async (req, res) => {
  try {
    const customers = await Customer.find()
      .select('-__v')
      .sort({ name: 1 });
    res.json(customers);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching customers' });
  }
});

/**
 * @swagger
 * /api/customers/{id}:
 *   get:
 *     summary: Get a customer by id
 *     tags:
 *       - Customers
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Customer details
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Customer'
 */
router.get('/:id', async (req, res) => {
  try {
    const objectId = new mongoose.Types.ObjectId(req.params.id);
    const customer = await Customer.findOne({ _id: objectId }).select('-__v');
    if (!customer) {
      return res.status(404).json({ error: 'Customer not found' });
    }
    res.json(customer);
  } catch (error) {
    if (error.name === 'CastError') {
      return res.status(400).json({ error: 'Invalid customer ID format' });
    }
    res.status(500).json({ error: 'Error fetching customer' });
  }
});

/**
 * @swagger
 * /api/customers:
 *   post:
 *     summary: Create a new customer
 *     tags:
 *       - Customers
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/Customer'
 *     responses:
 *       201:
 *         description: Customer created successfully
 */
router.post('/', async (req, res) => {
  try {
    const customer = new Customer(req.body);
    const savedCustomer = await customer.save();
    res.status(201).json(savedCustomer);
  } catch (error) {
    if (error.code === 11000) {
      return res.status(400).json({ error: 'Email already exists' });
    }
    res.status(400).json({ error: 'Error creating customer', details: error.message });
  }
});

/**
 * @swagger
 * /api/customers/{id}:
 *   put:
 *     summary: Update a customer
 *     tags:
 *       - Customers
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/Customer'
 *     responses:
 *       200:
 *         description: Customer updated successfully
 */
router.put('/:id', async (req, res) => {
  try {
    const customer = await Customer.findByIdAndUpdate(
      new mongoose.Types.ObjectId(req.params.id),
      req.body,
      { new: true, runValidators: true }
    ).select('-__v');

    if (!customer) {
      return res.status(404).json({ error: 'Customer not found' });
    }
    res.json(customer);
  } catch (error) {
    if (error.name === 'CastError') {
      return res.status(400).json({ error: 'Invalid customer ID format' });
    }
    if (error.code === 11000) {
      return res.status(400).json({ error: 'Email already exists' });
    }
    res.status(400).json({ error: 'Error updating customer', details: error.message });
  }
});

/**
 * @swagger
 * /api/customers/{id}:
 *   delete:
 *     summary: Delete a customer
 *     tags:
 *       - Customers
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Customer deleted successfully
 */
router.delete('/:id', async (req, res) => {
  try {
    const customer = await Customer.findByIdAndDelete(
      new mongoose.Types.ObjectId(req.params.id)
    );
    if (!customer) {
      return res.status(404).json({ error: 'Customer not found' });
    }
    res.json({ message: 'Customer deleted successfully' });
  } catch (error) {
    if (error.name === 'CastError') {
      return res.status(400).json({ error: 'Invalid customer ID format' });
    }
    res.status(500).json({ error: 'Error deleting customer' });
  }
});

module.exports = router; 