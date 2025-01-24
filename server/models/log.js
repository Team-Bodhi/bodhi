const mongoose = require('mongoose');

const logSchema = new mongoose.Schema({
  timestamp: {
    type: Date,
    default: Date.now,
  },
  method: {
    type: String,
    required: true,
    enum: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']
  },
  url: {
    type: String,
    required: true,
    trim: true
  },
  status: {
    type: Number,
    required: true,
    min: 100,
    max: 599
  },
  responseTime: {
    type: Number,
    required: true,
    min: 0,
    default: 0
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    default: null
  },
  username: {
    type: String,
    trim: true,
    default: null
  },
  userRole: {
    type: String,
    trim: true,
    default: null
  },
  action: {
    type: String,
    required: true,
    trim: true,
    default: 'UNKNOWN_ACTION'
  },
  details: {
    type: mongoose.Schema.Types.Mixed,
    default: null
  },
  ipAddress: {
    type: String,
    trim: true,
    default: 'Unknown'
  },
  userAgent: {
    type: String,
    trim: true,
    default: 'Unknown'
  },
  environment: {
    type: String,
    required: true,
    enum: ['development', 'production', 'test', 'staging'],
    default: 'development'
  }
});

// Index for common queries
logSchema.index({ timestamp: -1 }, { expireAfterSeconds: 604800 });
logSchema.index({ userId: 1 });
logSchema.index({ action: 1 });

module.exports = mongoose.model('Log', logSchema); 