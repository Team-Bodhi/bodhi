const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');

/**
 * @swagger
 * components:
 *   schemas:
 *     Book:
 *       type: object
 *       required:
 *         - title
 *         - author
 *         - genre
 *         - isbn
 *         - summary
 *         - publisher
 *         - publicationDate
 *         - pageCount
 *         - language
 *         - coverImageUrl
 *         - price
 *       properties:
 *         _id:
 *           type: string
 *           description: Auto-generated MongoDB ID
 *         title:
 *           type: string
 *           description: Book title
 *         author:
 *           type: string
 *           description: Author's name
 *         genre:
 *           type: string
 *           description: Book genre
 *         isbn:
 *           type: string
 *           description: ISBN number
 *         summary:
 *           type: string
 *           description: Book summary
 *         publisher:
 *           type: string
 *           description: Publisher's name
 *         publicationDate:
 *           type: string
 *           format: date
 *           description: Publication date
 *         pageCount:
 *           type: integer
 *           description: Number of pages
 *         language:
 *           type: string
 *           description: Book language
 *         coverImageUrl:
 *           type: string
 *           description: URL to book cover image
 *         quantity:
 *           type: integer
 *           description: Current stock quantity
 *         price:
 *           type: number
 *           description: Book price
 *         lowStockThreshold:
 *           type: integer
 *           description: Low stock alert threshold
 *         createdAt:
 *           type: string
 *           format: date-time
 *         updatedAt:
 *           type: string
 *           format: date-time
 */

// Book Schema
const bookSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true,
    trim: true
  },
  author: {
    type: String,
    required: true,
    trim: true
  },
  genre: {
    type: String,
    required: true,
    trim: true
  },
  isbn: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  summary: {
    type: String,
    required: true
  },
  publisher: {
    type: String,
    required: true,
    trim: true
  },
  publicationDate: {
    type: Date,
    required: true
  },
  pageCount: {
    type: Number,
    required: true,
    min: 1
  },
  language: {
    type: String,
    required: true,
    trim: true
  },
  coverImageUrl: {
    type: String,
    required: true,
    trim: true
  },
  quantity: {
    type: Number,
    required: true,
    min: 0,
    default: 0
  },
  price: {
    type: Number,
    required: true,
    min: 0
  },
  lowStockThreshold: {
    type: Number,
    required: true,
    min: 1,
    default: 5
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

// Add index for common queries
bookSchema.index({ title: 1, author: 1 });
bookSchema.index({ isbn: 1 });

const Book = mongoose.model('Book', bookSchema);

/**
 * @swagger
 * /api/books:
 *   get:
 *     summary: Returns a list of books
 *     parameters:
 *       - in: query
 *         name: genre
 *         schema:
 *           type: string
 *         description: Filter by genre
 *       - in: query
 *         name: language
 *         schema:
 *           type: string
 *         description: Filter by language
 *       - in: query
 *         name: inStock
 *         schema:
 *           type: boolean
 *         description: Filter for books in stock
 *     responses:
 *       200:
 *         description: List of books
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Book'
 */
router.get('/', async (req, res) => {
  try {
    const { genre, language, inStock } = req.query;
    let query = {};

    if (genre) query.genre = genre;
    if (language) query.language = language;
    if (inStock === 'true') query.quantity = { $gt: 0 };

    console.log('Collection name:', Book.collection.name);
    console.log('Database name:', mongoose.connection.db.databaseName);

    const books = await Book.find(query)
      .select('-__v')
      .sort({ title: 1 });
    console.log('Found books:', books.length);
    res.json(books);
  } catch (error) {
    console.error('Error in /api/books:', error);
    res.status(500).json({ error: 'Error fetching books' });
  }
});

/**
 * @swagger
 * /api/books/{id}:
 *   get:
 *     summary: Get a book by id
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: Book ID
 *     responses:
 *       200:
 *         description: Book details
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Book'
 *       404:
 *         description: Book not found
 */
router.get('/:id', async (req, res) => {
  try {
    const book = await Book.findById(req.params.id).select('-__v');
    if (!book) {
      return res.status(404).json({ error: 'Book not found' });
    }
    res.json(book);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching book' });
  }
});

/**
 * @swagger
 * /api/books:
 *   post:
 *     summary: Create a new book
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/Book'
 *     responses:
 *       201:
 *         description: Book created successfully
 *       400:
 *         description: Invalid input or ISBN already exists
 */
router.post('/', async (req, res) => {
  try {
    const book = new Book(req.body);
    const savedBook = await book.save();
    res.status(201).json(savedBook);
  } catch (error) {
    if (error.code === 11000) {
      return res.status(400).json({ error: 'ISBN already exists' });
    }
    res.status(400).json({ error: 'Error creating book', details: error.message });
  }
});

/**
 * @swagger
 * /api/books/{id}:
 *   put:
 *     summary: Update a book
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
 *             $ref: '#/components/schemas/Book'
 *     responses:
 *       200:
 *         description: Book updated successfully
 *       404:
 *         description: Book not found
 */
router.put('/:id', async (req, res) => {
  try {
    const updates = {
      ...req.body,
      updatedAt: Date.now()
    };

    const book = await Book.findByIdAndUpdate(
      req.params.id,
      updates,
      {
        new: true,
        runValidators: true
      }
    ).select('-__v');

    if (!book) {
      return res.status(404).json({ error: 'Book not found' });
    }

    // Check if stock is below threshold
    if (book.quantity <= book.lowStockThreshold) {
      // TODO: Implement notification system
      console.log(`Low stock alert for book: ${book.title}`);
    }

    res.json(book);
  } catch (error) {
    if (error.code === 11000) {
      return res.status(400).json({ error: 'ISBN already exists' });
    }
    res.status(400).json({ error: 'Error updating book', details: error.message });
  }
});

/**
 * @swagger
 * /api/books/{id}:
 *   delete:
 *     summary: Delete a book
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: Book ID
 *     responses:
 *       200:
 *         description: Book deleted successfully
 *       404:
 *         description: Book not found
 */
router.delete('/:id', async (req, res) => {
  try {
    const book = await Book.findByIdAndDelete(req.params.id);
    if (!book) {
      return res.status(404).json({ error: 'Book not found' });
    }
    res.json({ message: 'Book deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Error deleting book' });
  }
});

module.exports = router;
