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
            role: user.role,
            profileType: user.profileType
        },
        process.env.JWT_SECRET,
        { expiresIn: '24h' }
    );
};

// Register new customer
router.post('/register', async (req, res) => {
    try {
        const { email, username, password, firstName, lastName, phone, address } = req.body;

        // Check if user already exists
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return res.status(400).json({ error: 'Email already registered' });
        }

        // Create user account first
        const user = new User({
            email,
            username,
            password,
            role: 'customer',
            profileType: 'Customer'
        });
        await user.save();

        // Create customer profile with user reference
        const customer = new Customer({
            firstName,
            lastName,
            phone,
            address,
            userId: user._id  // Set the userId from the created user
        });
        await customer.save();

        // Update user with customer reference
        user.profileId = customer._id;
        await user.save();

        // Generate token
        const token = generateToken(user);

        // Get the complete customer profile
        const customerProfile = await customer.populate('userId');

        res.status(201).json({
            token,
            user: {
                id: user._id,
                email: user.email,
                role: user.role,
                ...customer.toObject()
            }
        });
    } catch (error) {
        console.error('Registration error:', error);
        // If we failed after creating the user but before creating the customer,
        // we should clean up the user
        if (error.errors?.userId) {
            try {
                await User.findOneAndDelete({ email: req.body.email });
            } catch (cleanupError) {
                console.error('Cleanup error:', cleanupError);
            }
        }
        res.status(500).json({ error: 'Registration failed' });
    }
});

// Login (both customer and employee)
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

        // Get profile
        const profile = await user.getProfile();
        if (!profile) {
            return res.status(404).json({ error: 'Profile not found' });
        }

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
                    role: user.role,
                    firstName: profile.firstName,
                    lastName: profile.lastName,
                    profileType: user.profileType,
                    profileId: user.profileId
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

        // Create employee profile
        const employee = new Employee({
            firstName,
            lastName,
            email,
            phone,
            address,
            jobTitle,
            role,
            salary
        });
        await employee.save();

        // Create user account
        const user = new User({
            email,
            password,
            role: role || 'employee',
            profileType: 'Employee',
            profileId: employee._id
        });
        await user.save();

        // Update employee with user reference
        employee.userId = user._id;
        await employee.save();

        res.status(201).json({
            message: 'Employee created successfully',
            employee: employee.toObject()
        });
    } catch (error) {
        console.error('Employee creation error:', error);
        res.status(500).json({ error: 'Failed to create employee' });
    }
});

module.exports = router; 