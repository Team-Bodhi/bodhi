const morgan = require('morgan');
const Log = require('../models/log');

// Helper function to determine the action based on the request
const determineAction = (req) => {
  const method = req.method;
  const path = req.path;

  // Extract the base resource (e.g., 'books', 'users', etc.)
  const resource = path.split('/')[2];

  if (method === 'POST' && path.endsWith('/login')) {
    return 'USER_LOGIN';
  }

  const actionMap = {
    GET: 'VIEW',
    POST: 'CREATE',
    PUT: 'UPDATE',
    DELETE: 'DELETE'
  };

  return `${resource?.toUpperCase()}_${actionMap[method]}` || 'UNKNOWN_ACTION';
};

// Helper function to extract relevant details based on the action
const extractDetails = (req) => {
  const details = {};

  // Don't log sensitive information like passwords
  const body = { ...req.body };
  delete body.password;

  switch (req.method) {
    case 'POST':
    case 'PUT':
      details.requestBody = body;
      break;
    case 'DELETE':
      details.resourceId = req.params.id;
      break;
  }

  return details;
};

// Calculate response time in milliseconds
const calculateResponseTime = (startAt, endAt) => {
  if (!startAt || !endAt) {
    return 0;
  }

  const ms = (endAt[0] - startAt[0]) * 1e3 +
    (endAt[1] - startAt[1]) * 1e-6;
  return Math.max(0, parseFloat(ms.toFixed(3)));
};

// Create custom logging middleware
const customLogger = () => {
  // Use morgan's combined format for console logging
  const morganLogger = morgan('combined');

  return async (req, res, next) => {
    // Start timing the request
    const startAt = process.hrtime();

    // Add response timing calculation
    res.on('finish', async () => {
      const endAt = process.hrtime();

      try {
        const responseTime = calculateResponseTime(startAt, endAt);

        // Create log entry
        const log = new Log({
          method: req.method,
          url: req.originalUrl || req.url,
          status: res.statusCode,
          responseTime,
          userId: req.user?._id,
          username: req.user?.username,
          userRole: req.user?.role,
          action: determineAction(req),
          details: extractDetails(req),
          ipAddress: req.ip || req.connection.remoteAddress,
          userAgent: req.get('user-agent') || 'Unknown'
        });

        await log.save();
      } catch (error) {
        console.error('Error saving log:', error);
      }
    });

    // Apply morgan logging for development
    if (process.env.NODE_ENV !== 'production') {
      morganLogger(req, res, (err) => {
        if (err) console.error('Morgan logging error:', err);
      });
    }

    next();
  };
};

module.exports = customLogger; 