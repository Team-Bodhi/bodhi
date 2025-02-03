const mongoose = require('mongoose');

const employeeSchema = new mongoose.Schema({
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

// Add indexes for common queries
employeeSchema.index({ userId: 1 });  // Index for faster lookups and cascading

// Virtual for full name
employeeSchema.virtual('fullName').get(function() {
    return `${this.firstName} ${this.lastName}`;
});

// Virtual for email (from User document)
employeeSchema.virtual('email', {
    ref: 'User',
    localField: 'userId',
    foreignField: '_id',
    justOne: true,
    get: function(user) {
        return user ? user.email : null;
    }
});

const Employee = mongoose.model('Employee', employeeSchema);

// Set up cascading delete trigger in MongoDB
Employee.watch().on('change', async (change) => {
    if (change.operationType === 'delete') {
        try {
            await mongoose.model('User').deleteOne({ _id: change.documentKey.userId });
        } catch (error) {
            console.error('Error in cascade delete:', error);
        }
    }
});

module.exports = Employee; 