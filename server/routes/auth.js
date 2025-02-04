const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const User = require('../models/user');
const Customer = require('../models/customer');
const Employee = require('../models/employee');
const auth = require('../middleware/auth');

// Helper function to generate JWT token
const generateToken = (user) => {
    return jwt.sign(
        { 
            id: user._id,
            role: user.role
        },
        process.env.JWT_SECRET,
        { expiresIn: '24h' }
    );
};

// Register new customer
router.post('/register', async (req, res) => {
    let createdUser = null;
    let createdCustomer = null;
    
    try {
        const { email, password, firstName, lastName, role } = req.body;

        // Check if user already exists
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return res.status(400).json({ error: 'Email already registered' });
        }

        // Create user account first
        createdUser = new User({
            email,
            firstName,
            lastName,
            password,
            role: role || 'customer'
        });
        await createdUser.save();

        // Create blank customer profile with user reference
        try {
            createdCustomer = new Customer({
                userId: createdUser._id
            });
            await createdCustomer.save();

            // Update user with customer reference
            createdUser.customerId = createdCustomer._id;
            await createdUser.save();

            // Generate token
            const token = generateToken(createdUser);

            res.status(201).json({
                token,
                user: {
                    id: createdUser._id,
                    email: createdUser.email,
                    firstName: createdUser.firstName,
                    lastName: createdUser.lastName,
                    role: createdUser.role,
                    customerId: createdCustomer._id
                }
            });
        } catch (customerError) {
            // If customer creation fails, clean up the user
            if (createdUser) {
                await User.findByIdAndDelete(createdUser._id);
            }
            throw customerError;
        }
    } catch (error) {
        console.error('Registration error:', error);
        
        // Cleanup any created resources if something failed
        try {
            if (createdCustomer) {
                await Customer.findByIdAndDelete(createdCustomer._id);
            }
            if (createdUser) {
                await User.findByIdAndDelete(createdUser._id);
            }
        } catch (cleanupError) {
            console.error('Cleanup error:', cleanupError);
        }

        res.status(500).json({ 
            error: 'Registration failed',
            details: error.message 
        });
    }
});

// Login
router.post('/login', async (req, res) => {
    try {
        const { email, password } = req.body;

        // Find user
        const user = await User.findOne({ email });
        if (!user) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        // Verify password
        const isValid = await user.comparePassword(password);
        if (!isValid) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        // Get profile if it exists
        const profile = await user.getProfile();

        // Update last login
        user.lastLogin = new Date();
        await user.save();

        // Generate token
        const token = generateToken(user);

        res.json({
            success: true,
            data: {
                token,
                user: {
                    id: user._id,
                    email: user.email,
                    firstName: user.firstName,
                    lastName: user.lastName,
                    role: user.role,
                    customerId: user.customerId,
                    employeeId: user.employeeId,
                    profile: profile ? profile.toObject() : null
                },
                permissions: {
                    canManageUsers: user.role === 'admin',
                    canManageInventory: ['admin', 'employee'].includes(user.role),
                    canPlaceOrders: true
                }
            },
            message: 'Login successful'
        });
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ error: 'Login failed' });
    }
});

// Get current user profile
router.get('/profile', auth, async (req, res) => {
    try {
        const user = await User.findById(req.user.id);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        const profile = await user.getProfile();
        if (!profile) {
            return res.status(404).json({ error: 'Profile not found' });
        }

        res.json({
            id: user._id,
            email: user.email,
            role: user.role,
            ...profile.toObject()
        });
    } catch (error) {
        console.error('Profile fetch error:', error);
        res.status(500).json({ error: 'Failed to fetch profile' });
    }
});

// Update user profile
router.put('/profile', auth, async (req, res) => {
    try {
        const user = await User.findById(req.user.id);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        const profile = await user.getProfile();
        if (!profile) {
            return res.status(404).json({ error: 'Profile not found' });
        }

        // Update allowed fields based on profile type
        const allowedFields = user.profileType === 'Customer' 
            ? ['firstName', 'lastName', 'phone', 'address']
            : ['firstName', 'lastName', 'phone', 'address', 'jobTitle'];

        allowedFields.forEach(field => {
            if (req.body[field] !== undefined) {
                profile[field] = req.body[field];
            }
        });

        await profile.save();

        res.json({
            id: user._id,
            email: user.email,
            role: user.role,
            ...profile.toObject()
        });
    } catch (error) {
        console.error('Profile update error:', error);
        res.status(500).json({ error: 'Failed to update profile' });
    }
});

// Create employee (admin only)
router.post('/employee', auth, async (req, res) => {
    try {
        // Check if requester is admin
        if (req.user.role !== 'admin') {
            return res.status(403).json({ error: 'Unauthorized' });
        }

        const { 
            email, password, firstName, lastName, 
            phone, address, jobTitle, role, salary 
        } = req.body;

        // Check if user already exists
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return res.status(400).json({ error: 'Email already registered' });
        }

        // Create user account first
        const user = new User({
            email,
            firstName,
            lastName,
            password,
            role: role || 'employee'
        });
        await user.save();

        // Create employee profile
        const employee = new Employee({
            phone,
            address,
            jobTitle,
            role: role || 'employee',
            salary,
            userId: user._id
        });
        await employee.save();

        // Update user with employee reference
        user.employeeId = employee._id;
        await user.save();

        res.status(201).json({
            message: 'Employee created successfully',
            employee: {
                ...employee.toObject(),
                firstName: user.firstName,
                lastName: user.lastName,
                email: user.email
            }
        });
    } catch (error) {
        console.error('Employee creation error:', error);
        res.status(500).json({ error: 'Failed to create employee' });
    }
});

module.exports = router; 