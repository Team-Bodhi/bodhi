const express = require('express');
const router = express.Router();
const Customer = require('../models/customer');
const User = require('../models/user');

// Get all customers with their associated user data
router.get('/customers', async (req, res) => {
    try {
        const customers = await Customer.find()
            .populate('userId', 'email username role isActive')
            .select('-__v');
        res.json(customers);
    } catch (error) {
        console.error('Error fetching customers:', error);
        res.status(500).json({ error: 'Failed to fetch customers' });
    }
});

// Update customer
router.put('/customers/:id', async (req, res) => {
    try {
        const { firstName, lastName, phone, address } = req.body;
        const customer = await Customer.findByIdAndUpdate(
            req.params.id,
            { firstName, lastName, phone, address },
            { new: true }
        ).populate('userId', 'email username role isActive');
        
        if (!customer) {
            return res.status(404).json({ error: 'Customer not found' });
        }
        
        res.json(customer);
    } catch (error) {
        console.error('Error updating customer:', error);
        res.status(500).json({ error: 'Failed to update customer' });
    }
});

// Delete customer and associated user
router.delete('/customers/:id', async (req, res) => {
    try {
        const customer = await Customer.findById(req.params.id);
        if (!customer) {
            return res.status(404).json({ error: 'Customer not found' });
        }

        // Delete associated user if it exists
        if (customer.userId) {
            await User.findByIdAndDelete(customer.userId);
        }

        // Delete the customer
        await Customer.findByIdAndDelete(req.params.id);
        
        res.json({ message: 'Customer deleted successfully' });
    } catch (error) {
        console.error('Error deleting customer:', error);
        res.status(500).json({ error: 'Failed to delete customer' });
    }
});

module.exports = router; 