const mongoose = require('mongoose');

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
    type: String
  },
  publisher: {
    type: String,
    trim: true
  },
  publicationDate: {
    type: Date
  },
  pageCount: {
    type: Number,
    min: 1
  },
  language: {
    type: String,
    required: true,
    trim: true
  },
  coverImageUrl: {
    type: String,
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
    min: 0,
    default: 0
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, { timestamps: true });

// Add index for common queries
bookSchema.index({ title: 1, author: 1 });

module.exports = mongoose.model('Book', bookSchema);