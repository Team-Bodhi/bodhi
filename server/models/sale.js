const mongoose = require('mongoose');

// book subschema
const orderItemsSchema = new mongoose.Schema({
    bookId: {
        type: mongoose.Types.ObjectId,
        ref: 'Book',
        required: [true, 'Book ID is required']
    },
    quantity: {
        type: Number,
        required: [true, 'Quantity is required'],
        min: [1, 'Quantity must be at least 1'],
        validate: {
            validator: Number.isInteger,
            message: 'Quantity must be a whole number'
        }
    },
    price: {
        type: Number,
        required: [true, 'Price is required'],
        min: [0, 'Price cannot be negative']
    },
    bookDetails: {
        title: String,
        author: String,
        isbn: String,
        genre: String,
        publisher: String,
        language: String,
        summary: String,
        publicationDate: Date,
        coverImageUrl: String
    }
});

// address schema
const addressSchema = new mongoose.Schema({
    street: {
        type: String,
        required: [true, 'Street address is required'],
        trim: true
    },
    city: {
        type: String,
        required: [true, 'City is required'],
        trim: true
    },
    state: {
        type: String,
        required: [true, 'State is required'],
        trim: true
    },
    zipCode: {
        type: String,
        required: [true, 'ZIP code is required'],
        trim: true,
        match: [/^\d{5}(-\d{4})?$/, 'Please enter a valid ZIP code']
    }
});

// sale Schema
const saleSchema = new mongoose.Schema({
    type: {
        type: String,
        required: [true, 'Sale type is required'],
        trim: true,
        enum: {
            values: ['instore', 'online'],
            message: 'Sale type must be either instore or online'
        }
    },
    orderItems: {
        type: [orderItemsSchema],
        required: [true, 'At least one book is required'],
        validate: {
            validator: function(array) {
                return array && array.length > 0;
            },
            message: 'At least one book must be ordered'
        }
    },
    orderStatus: {
        type: String,
        default: 'pending',
        required: true,
        enum: {
            values: ['pending', 'shipped', 'received', 'canceled'],
            message: 'Invalid order status'
        }
    },
    orderDate: {
        type: Date,
        default: Date.now,
        required: true
    },
    totalPrice: {
        type: Number,
        required: [true, 'Total price is required'],
        min: [0, 'Total price cannot be negative']
    },
    paymentMethod: {
        type: String,
        required: [true, 'Payment method is required'],
        trim: true,
        enum: {
            values: ['cash', 'credit', 'debit'],
            message: 'Invalid payment method'
        }
    },
    employeeId: {
        type: mongoose.Types.ObjectId,
        ref: 'User',
        required: false
    },
    customerId: {
        type: mongoose.Types.ObjectId,
        ref: 'Customer',
        required: false
    },
    shippingAddress: {
        type: addressSchema,
        required: [
            function() { return this.type === 'online'; },
            'Shipping address is required for online orders'
        ]
    }
}, {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
});

// Virtual for formatted address
saleSchema.virtual('formattedAddress').get(function() {
    if (!this.shippingAddress) return null;
    
    const { street, city, state, zipCode } = this.shippingAddress;
    if (!street || !city || !state || !zipCode) return null;
    
    return `${street}, ${city}, ${state} ${zipCode}`;
});

// Pre-save middleware to calculate and validate total price
saleSchema.pre('save', async function(next) {
    try {
        // Fetch all books to calculate total price
        const bookIds = this.orderItems.map(item => item.bookId);
        const books = await mongoose.model('Book').find({ _id: { $in: bookIds } });
        
        // Create a map for quick price lookup
        const bookPrices = new Map(books.map(book => [book._id.toString(), book.price]));
        
        // Calculate total
        const calculatedTotal = this.orderItems.reduce((sum, item) => {
            const price = bookPrices.get(item.bookId.toString());
            if (!price) {
                throw new Error(`Price not found for book ${item.bookId}`);
            }
            return sum + (price * item.quantity);
        }, 0);

        // Set the total price
        this.totalPrice = calculatedTotal;

        // For online orders, ensure shipping address exists
        if (this.type === 'online' && !this.shippingAddress) {
            throw new Error('Shipping address is required for online orders');
        }

        next();
    } catch (error) {
        next(error);
    }
});

module.exports = mongoose.model('Sale', saleSchema);