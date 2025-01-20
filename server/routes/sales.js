const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');
const Sale = require('../models/sale');

/**
 * @swagger
 * /api/sales:
 *   get:
 *     summary: Get all sales
 *     tags:
 *       - Sales
 *     responses:
 *       200:
 *         description: A list of sales
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Sale'
 *       500:
 *         description: Error fetching sales
 */
router.get('/', async (req, res) => {
  try {
    const sales = await Sale.find()
      .select('-__v')
      .sort({ saleDate: -1 }); // Sort by saleDate in descending order
    console.log('Found sales:', sales.length);
    res.json(sales);
  } catch (error) {
    console.error('Error in /api/sales:', error);
    res.status(500).json({ error: 'Error fetching sales' });
  }
});

/**
 * @swagger
 * /api/sales:
 *   post:
 *     summary: Create a new sale
 *     tags:
 *       - Sales
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/Sale'
 *     responses:
 *       201:
 *         description: Sale created successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Sale'
 *       400:
 *         description: Invalid input
 *       500:
 *         description: Error creating sale
 */
router.post('/', async (req, res) => {
  try {
    const newSale = new Sale(req.body);
    const savedSale = await newSale.save();
    res.status(201).json(savedSale);
  } catch (error) {
    res.status(400).json({ error: 'Error creating sale', details: error.message });
  }
});

/**
 * @swagger
 * /api/sales/{id}:
 *   put:
 *     summary: Update a sale by id
 *     tags:
 *       - Sales
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
 *             $ref: '#/components/schemas/Sale'
 *     responses:
 *       200:
 *         description: Sale updated successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Sale'
 *       400:
 *         description: Invalid input
 *       404:
 *         description: Sale not found
 *       500:
 *         description: Error updating sale
 */
router.put('/:id', async (req, res) => {
  try {
    const updatedSale = await Sale.findByIdAndUpdate(req.params.id, req.body, { new: true, runValidators: true });
    if (!updatedSale) {
      return res.status(404).json({ error: 'Sale not found' });
    }
    res.json(updatedSale);
  } catch (error) {
    res.status(400).json({ error: 'Error updating sale', details: error.message });
  }
});

/**
 * @swagger
 * /api/sales/{id}:
 *   delete:
 *     summary: Delete a sale by id
 *     tags:
 *       - Sales
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Sale deleted successfully
 *       404:
 *         description: Sale not found
 *       500:
 *         description: Error deleting sale
 */
router.delete('/:id', async (req, res) => {
  try {
    const deletedSale = await Sale.findByIdAndDelete(req.params.id);
    if (!deletedSale) {
      return res.status(404).json({ error: 'Sale not found' });
    }
    res.json({ message: 'Sale deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Error deleting sale' });
  }
});

module.exports = router;