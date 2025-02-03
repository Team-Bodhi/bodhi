const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    trim: true,
    lowercase: true
  },
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
  password: {
    type: String,
    required: true
  },
  role: {
    type: String,
    enum: ['customer', 'employee', 'admin'],
    required: true
  },
  isActive: {
    type: Boolean,
    default: true
  },
  lastLogin: {
    type: Date
  },
  // References to profiles (optional)
  customerId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Customer',
    required: false
  },
  employeeId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Employee',
    required: false
  }
}, {
  timestamps: true
});

// Add index for faster lookups
userSchema.index({ customerId: 1 });
userSchema.index({ employeeId: 1 });

// Virtual for full name
userSchema.virtual('fullName').get(function() {
  return `${this.firstName} ${this.lastName}`;
});

// Pre-save hook to hash password
userSchema.pre('save', async function(next) {
  if (this.isModified('password')) {
    this.password = await bcrypt.hash(this.password, 10);
  }
  next();
});

// Method to compare password
userSchema.methods.comparePassword = async function(candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

// Method to get profile based on role
userSchema.methods.getProfile = async function() {
  if (this.role === 'customer' && this.customerId) {
    return await mongoose.model('Customer').findById(this.customerId);
  } else if (['employee', 'admin'].includes(this.role) && this.employeeId) {
    return await mongoose.model('Employee').findById(this.employeeId);
  }
  return null;
};

const User = mongoose.model('User', userSchema);

// Set up cascading delete trigger in MongoDB
User.watch().on('change', async (change) => {
  if (change.operationType === 'delete') {
    try {
      const deletedUser = change.fullDocument;
      if (deletedUser) {
        if (deletedUser.customerId) {
          await mongoose.model('Customer').deleteOne({ _id: deletedUser.customerId });
        }
        if (deletedUser.employeeId) {
          await mongoose.model('Employee').deleteOne({ _id: deletedUser.employeeId });
        }
      }
    } catch (error) {
      console.error('Error in cascade delete:', error);
    }
  }
});

module.exports = User; 