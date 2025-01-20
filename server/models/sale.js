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
    price: {
        type: Number,
        required: true,
        min: 0.0,
    },
});

// address schema

const addressSchema = new mongoose.Schema({
    street: {
        type: String,
        required: true,
        trim: true,
    },
    city: {
        type: String,
        required: true,
        trim: true,
    },
    state: {
        type: String,
        required: true,
        trim: true,
    },
    zipCode: {
        type: String,
        required: true,
        trim: true,
    },
});
// sale Schema
const saleSchema = new mongoose.Schema({
    type: {
        type: String,
        required: true,
        trim: true,
        enum: ['instore', 'online']
    
    },
    bookOrdered: [bookOrderedSchema],
    status: {
        type: String,
        default: 'pending',
        required: true,
        enum: ['pending', 'shipped', 'received', 'canceled']
    },
    saleDate: {
        type: Date,
        default: Date.now
    },
    totalPrice: {
        type: Number,
        min: 0.0
    },
    paymentMethod: {
        type: String,
        required: true,
        trim: true,
        enum: ['cash', 'credit', 'debit']
    },

    employeeId: {
        type: mongoose.Types.ObjectId,
        ref: 'employees',
        required: false,
    },
    customerId: {
        type: mongoose.Types.ObjectId,
        ref: 'customers',
        required: false,
    },
    shippingAddress: addressSchema,
},
    {
        timestamps: true
    }
);

module.exports = mongoose.model('Sale', saleSchema);