const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');

/**
 * @swagger
 * components:
 *   schemas:
 *     Users:
 *       type: object
 *       required:
 *         - username
 *         - hash
 *         - salt
 *         - firstName
 *         - lastName
 *         - role
 *         - lastLogin
 *       properties:
 *         _id:
 *           type: object
 *           description: Auto-generated MongoDB ID
 *         username:
 *           type: string
 *           description: Username
 *         hash:
 *           type: string
 *           description: Hashed password
 *         salt:
 *           type: string
 *           description: Salt
 *         firstName:
 *           type: string
 *           description: User first name
 *         lastName:
 *           type: string
 *           description: User last name
 *         role:
 *           type: string
 *           description: User role
 *         lastLogin:
 *           type: string
 *           format: date
 *           description: Timestamp of last login
 */

// User Schema
const usersSchema = new mongoose.Schema({
  _id: {
    type: Object,
    default: new mongoose.Types.ObjectId()
  },
  username: {
    type: String,
    required: true,
    unique: true
  },
  hash: {
    type: String,
    required: true
  },
  salt: {
    type: String,
    required: true
  },
  firstName: {
    type: String,
    required: true,
  },
  lastName: {
    type: String,
    required: true
  },
  role: {
    type: String,
    required: true
  },
  lastLogin: {
    type: Date,
    required: true
  }
});

// Add index for common queries

const Users = mongoose.model('Users', usersSchema);

/**
 * @swagger
 * /api/users:
 *   get:
 *     summary: Returns a list of users
 *     tags: 
 *       - Users
 *     parameters:
 *       - in: query
 *         name: username
 *         schema:
 *           type: string
 *         description: Filter by username
 *     responses:
 *       200:
 *         description: List of users
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Users'
 */
router.get('/', async (req, res) => {
  try {
    const { username } = req.query;
    let query = {};

    if (username) query.genre = genre;

    console.log('Collection name:', Users.collection.name);
    console.log('Database name:', mongoose.connection.db.databaseName);

    const users = await Users.find(query)
      .select('-__v')
      .sort({ username: 1 });
    console.log('Found users:', users.length);
    res.json(users);
  } catch (error) {
    console.error('Error in /api/users:', error);
    res.status(500).json({ error: 'Error fetching users' });
  }
});

/**
 * @swagger
 * /api/users:
 *   post:
 *     summary: Create a new user
 *     tags: 
 *       - Users
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/Users'
 *     responses:
 *       201:
 *         description: Users created successfully
 *       400:
 *         description: Invalid input or user already exists
 */
router.post('/', async (req, res) => {
  try {
    const user = new Users(req.body);
    const id = new mongoose.Types.ObjectId();
    user._id = id;
    const savedUser = await user.save();
    res.status(201).json(savedUser);
  } catch (error) {
    if (error.code === 11000) {
      return res.status(400).json({ error: 'Username already exists' });
    }
    res.status(400).json({ error: 'Error creating username', details: error.message });
  }
});

module.exports = router;
