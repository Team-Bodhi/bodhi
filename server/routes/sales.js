const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');
const Sale = require('../models/sale');
const Book = require('../models/book');

/**
 * @swagger
 * /api/sales:
 *   get:
 *     summary: Get all sales with optional filters
 *     tags:
 *       - Sales
 *     parameters:
 *       - in: query
 *         name: startDate
 *         schema:
 *           type: string
 *           format: date
 *         description: Filter sales after this date (inclusive)
 *       - in: query
 *         name: endDate
 *         schema:
 *           type: string
 *           format: date
 *         description: Filter sales before this date (inclusive)
 *       - in: query
 *         name: bookTitle
 *         schema:
 *           type: string
 *         description: Filter by book title (case-insensitive partial match)
 *       - in: query
 *         name: genre
 *         schema:
 *           type: string
 *         description: Filter by book genre
 *       - in: query
 *         name: status
 *         schema:
 *           type: string
 *           enum: [pending, shipped, received, canceled]
 *         description: Filter by sale status
 *       - in: query
 *         name: type
 *         schema:
 *           type: string
 *           enum: [instore, online]
 *         description: Filter by sale type
 *     responses:
 *       200:
 *         description: A list of filtered sales
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
    const {
      startDate,
      endDate,
      bookTitle,
      genre,
      status,
      type
    } = req.query;

    // Build the query object
    let query = {};

    // Date range filter
    if (startDate || endDate) {
      query.saleDate = {};
      if (startDate) query.saleDate.$gte = new Date(startDate);
      if (endDate) query.saleDate.$lte = new Date(endDate);
    }

    // Status and type filters
    if (status) query.status = status;
    if (type) query.type = type;

    // Book title and genre filters (now checking embedded data and references)
    if (bookTitle) {
      query['$or'] = [
        { 'bookOrdered.bookId.title': new RegExp(bookTitle, 'i') }
      ];
    }

    if (genre) {
      query['$or'] = [
        { 'bookOrdered.bookId.genre': new RegExp(genre, 'i') }
      ];
    }

    // Execute the query with all filters
    const sales = await Sale.find(query)
      .populate({
        path: 'bookOrdered.bookId',
        model: 'Book',
        select: 'title author isbn price coverImageUrl summary publisher publicationDate language genre quantity'
      })
      .populate({
        path: 'customerId',
        model: 'Customer',
        select: 'firstName lastName email phone address'
      })
      .populate({
        path: 'employeeId',
        model: 'User',
        select: 'firstName lastName email role'
      })
      .select('-__v')
      .sort({ saleDate: -1 });

    // Transform the response
    const transformedSales = sales.map(sale => {
      const saleObj = sale.toObject();
      
      // Update bookDetails from the populated bookId
      saleObj.bookOrdered = saleObj.bookOrdered.map(item => {
        if (item.bookId) {
          item.bookDetails = {
            title: item.bookId.title,
            author: item.bookId.author,
            isbn: item.bookId.isbn,
            genre: item.bookId.genre,
            publisher: item.bookId.publisher,
            language: item.bookId.language,
            summary: item.bookId.summary,
            publicationDate: item.bookId.publicationDate,
            coverImageUrl: item.bookId.coverImageUrl
          };
          // Convert bookId back to just the ID string
          item.bookId = item.bookId._id;
        }
        return item;
      });
      
      // Calculate total items
      saleObj.totalItems = sale.bookOrdered.reduce((sum, item) => sum + item.quantity, 0);
      
      // Format dates
      saleObj.saleDate = sale.saleDate.toISOString();
      saleObj.createdAt = sale.createdAt?.toISOString();
      saleObj.updatedAt = sale.updatedAt?.toISOString();
      
      return saleObj;
    });

    console.log('Found sales:', transformedSales.length);
    res.json(transformedSales);
  } catch (error) {
    console.error('Error in /api/sales:', error);
    res.status(500).json({ error: 'Error fetching sales', details: error.message });
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
    console.log('Creating new sale with data:', JSON.stringify(req.body, null, 2));
    const orderData = { ...req.body };
    
    // Validate and fetch books to check quantities
    const bookIds = orderData.bookOrdered.map(item => item.bookId);
    const books = await Book.find({ _id: { $in: bookIds } });
    const bookMap = new Map(books.map(book => [book._id.toString(), book]));

    // Validate each book order and add price
    orderData.bookOrdered = orderData.bookOrdered.map(item => {
      const book = bookMap.get(item.bookId.toString());
      if (!book) {
        throw new Error(`Book with ID ${item.bookId} does not exist`);
      }
      if (book.quantity < item.quantity) {
        throw new Error(`Only ${book.quantity} copies of "${book.title}" available`);
      }

      // Only include bookId, quantity, and price in the POST
      return {
        bookId: item.bookId,
        quantity: item.quantity,
        price: book.price
      };
    });

    // Create and save the sale
    const newSale = new Sale(orderData);
    const savedSale = await newSale.save();
    console.log('Sale saved successfully with ID:', savedSale._id);

    // Update book quantities
    await Promise.all(orderData.bookOrdered.map(item => 
      Book.findByIdAndUpdate(
        item.bookId,
        { $inc: { quantity: -item.quantity } },
        { new: true }
      )
    ));
    console.log('Book quantities updated successfully');

    // For the response, populate all references
    const populatedSale = await Sale.findById(savedSale._id)
      .populate({
        path: 'bookOrdered.bookId',
        model: 'Book',
        select: 'title author isbn price coverImageUrl summary publisher publicationDate language genre quantity'
      })
      .populate({
        path: 'customerId',
        model: 'Customer',
        select: 'firstName lastName email phone address'
      })
      .populate({
        path: 'employeeId',
        model: 'User',
        select: 'firstName lastName email role'
      });

    // Transform the response
    const responseData = populatedSale.toObject();
    
    // Update bookDetails in the response
    responseData.bookOrdered = responseData.bookOrdered.map(item => {
      if (item.bookId) {
        item.bookDetails = {
          title: item.bookId.title,
          author: item.bookId.author,
          isbn: item.bookId.isbn,
          genre: item.bookId.genre,
          publisher: item.bookId.publisher,
          language: item.bookId.language,
          summary: item.bookId.summary,
          publicationDate: item.bookId.publicationDate,
          coverImageUrl: item.bookId.coverImageUrl
        };
        item.bookId = item.bookId._id;
      }
      return item;
    });

    responseData.totalItems = populatedSale.bookOrdered.reduce((sum, item) => sum + item.quantity, 0);

    console.log('Sending response with populated sale data');
    res.status(201).json(responseData);
  } catch (error) {
    console.error('Error creating sale:', error);
    res.status(400).json({ 
      error: 'Error creating sale', 
      details: error.message,
      validationErrors: error.errors
    });
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