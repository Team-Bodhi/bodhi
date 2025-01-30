const mongoose = require('mongoose');

const employeeSchema = new mongoose.Schema({
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
    email: {
        type: String,
        required: true,
        unique: true,
        trim: true,
        lowercase: true
    },
    phone: {
        type: String,
        required: true
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
            type: String
        },
        zipCode: {
            type: String,
            required: true
        }
    },
    jobTitle: {
        type: String,
        required: true
    },
    role: {
        type: String,
        enum: ['employee', 'admin'],
        required: true
    },
    hireDate: {
        type: Date,
        default: Date.now
    },
    salary: {
        type: Number,
        required: true
    },
    isActive: {
        type: Boolean,
        default: true
    },
    // Reference to User document for authentication
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    }
}, {
    timestamps: true
});

// Virtual for full name
employeeSchema.virtual('fullName').get(function() {
    return `${this.firstName} ${this.lastName}`;
});

const Employee = mongoose.model('Employee', employeeSchema);

module.exports = Employee; 