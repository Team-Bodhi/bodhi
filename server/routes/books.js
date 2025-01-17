const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');
const Book = require('../models/book');

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

/**
 * @swagger
 * /api/books:
 *   get:
 *     summary: Returns a list of books
 *     tags: 
 *       - Book Inventory
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
 *     tags: 
 *       - Book Inventory
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
    const objectId = new mongoose.Types.ObjectId(req.params.id);
    const book = await Book.findOne({ _id: objectId }).select('-__v');
    if (!book) {
      return res.status(404).json({ error: 'Book not found' });
    }
    res.json(book);
  } catch (error) {
    if (error.name === 'CastError') {
      return res.status(400).json({ error: 'Invalid book ID format' });
    }
    res.status(500).json({ error: 'Error fetching book' });
  }
});

/**
 * @swagger
 * /api/books:
 *   post:
 *     summary: Create a new book
 *     tags: 
 *       - Book Inventory
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - title
 *               - author
 *               - genre
 *               - isbn
 *               - quantity
 *               - price
 *               - language
 *             properties:
 *               title:
 *                 type: string
 *               author:
 *                 type: string
  *               genre:
 *                 type: string
 *               isbn:
 *                 type: string
 *               quantity:
 *                 type: number
 *               price:
 *                 type: number
 *               language:
 *                 type: string
 *     responses:
 *       201:
 *         description: Book created successfully
 *       400:
 *         description: Invalid input or ISBN already exists
 */
router.post('/', async (req, res) => {
  try {
    const { title, author, genre, isbn, quantity, price, language } = req.body;
    const id = new mongoose.Types.ObjectId;
    
    const book = new Book();
    
    book._id = id;
    book.title = title;
    book.author = author;
    book.genre = genre;
    book.isbn = isbn;
    book.quantity = quantity;
    book.price = price;
    book.language = language;

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
 *     tags: 
 *       - Book Inventory
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
      new mongoose.Types.ObjectId(req.params.id),
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
 *     tags: 
 *       - Book Inventory
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
    const book = await Book.findByIdAndDelete(
      new mongoose.Types.ObjectId(req.params.id)
    );
    if (!book) {
      return res.status(404).json({ error: 'Book not found' });
    }
    res.json({ message: 'Book deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Error deleting book' });
  }
});

module.exports = router;
