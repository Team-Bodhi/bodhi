const mongoose = require('mongoose');

// book subschema
const bookOrderedSchema = new mongoose.Schema({
  bookId: {
    type: mongoose.Types.ObjectId,
    ref: 'books', 
    required: true,
  },
  quantity: {
    type: Number,
    required: true,
    min: 1,
  },
});

// Mfr Order Schema
const mfrOrderSchema = new mongoose.Schema({
  orderNumber: {
    type: String,
    required: true,
    trim: true
  },
  supplierName: {
    type: String,
    required: true,
    trim: true
  },
  booksOrdered: [ bookOrderedSchema ],
  status: {
    type: String,
    default: 'pending',
    required: true,
    enum: ['pending', 'shipped', 'received', 'canceled']
  },
  totalCost: {
    type: Number,
    min: 0.0
  },
  orderDate: {
    type: Date,
    default: Date.now
  },
  expectedDeliveryDate: {
    type: Date,
    default: Date.now
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  },
},
{
  timestamps: true
}
);

module.exports = mongoose.model('MfrOrder', mfrOrderSchema);