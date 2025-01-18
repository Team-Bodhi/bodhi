const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');
const Sale = require('../models/sale');

router.get('/', async (req, res) => {
  try {

    const sales = await Sale.find()
      .select('-__v')
      .sort({ title: 1 });
    console.log('Found sales:', sales.length);
    res.json(sales);
  } catch (error) {
    console.error('Error in /api/sales:', error);
    res.status(500).json({ error: 'Error fetching sales' });
  }
});

module.exports = router;