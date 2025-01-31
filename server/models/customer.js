const mongoose = require('mongoose');

const customerSchema = new mongoose.Schema({
  firstName: {
    type: String,
    required: true,
    trim: true
  },
  lastName: {
    type: String,
    required: true,
    trim: true
  },
  phone: {
    type: String,
    required: true,
    trim: true
  },
  address: {
    street: {
      type: String,
      required: true
    },
    city: {
      type: String,
      required: true
    },
    state: {
      type: String,
      required: true
    },
    zip: {
      type: String,
      required: true
    }
  },
  // Reference to User document for authentication
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  // Customer-specific fields
  orderCount: {
    type: Number,
    default: 0
  },
  totalSpent: {
    type: Number,
    default: 0
  },
  lastPurchase: {
    type: Date
  }
}, {
  timestamps: true // This automatically adds createdAt and updatedAt fields
});

// Virtual for full name
customerSchema.virtual('fullName').get(function() {
  return `${this.firstName} ${this.lastName}`;
});


// Add index for common queries
customerSchema.index({ phone: 1 });
customerSchema.index({ userId: 1 });  // Index for faster lookups and cascading

const Customer = mongoose.model('Customer', customerSchema);

// Set up cascading delete trigger in MongoDB
Customer.watch().on('change', async (change) => {
  if (change.operationType === 'delete') {
    try {
      await mongoose.model('User').deleteOne({ _id: change.documentKey.userId });
    } catch (error) {
      console.error('Error in cascade delete:', error);
    }
  }
});

module.exports = Customer; 