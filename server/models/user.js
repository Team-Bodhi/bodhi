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
  username: {
    type: String,
    required: true,
    unique: true,
    trim: true,
    lowercase: true
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
  // Reference to either Customer or Employee document
  profileId: {
    type: mongoose.Schema.Types.ObjectId,
    // We'll set this after creating the profile
    required: false,
    refPath: 'profileType'
  },
  profileType: {
    type: String,
    required: true,
    enum: ['Customer', 'Employee']
  }
}, {
  timestamps: true
});

// Add index for faster lookups and cascading
userSchema.index({ profileId: 1, profileType: 1 });

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

// Method to get full profile
userSchema.methods.getProfile = async function() {
  const Model = mongoose.model(this.profileType);
  return await Model.findById(this.profileId);
};

const User = mongoose.model('User', userSchema);

// Set up cascading delete trigger in MongoDB
User.watch().on('change', async (change) => {
  if (change.operationType === 'delete') {
    try {
      const deletedUser = change.fullDocument;
      if (deletedUser && deletedUser.profileId && deletedUser.profileType) {
        const Model = mongoose.model(deletedUser.profileType);
        await Model.deleteOne({ _id: deletedUser.profileId });
      }
    } catch (error) {
      console.error('Error in cascade delete:', error);
    }
  }
});

module.exports = User; 