const morgan = require('morgan');
const Log = require('../models/log');

// Helper function to get normalized environment name
const getNormalizedEnvironment = () => {
  const env = (process.env.NODE_ENV || 'development').toLowerCase();
  const envMap = {
    'dev': 'development',
    'prod': 'production',
    'stage': 'staging',
    'test': 'test'
  };
  return envMap[env] || env;
};

// Helper function to determine the action based on the request
const determineAction = (req) => {
  const method = req.method;
  const path = req.path;

  // Special routes handling
  if (path === '/health') return 'HEALTH_CHECK';
  if (path === '/') return 'ROOT_ACCESS';
  if (path === '/api-docs') return 'DOCS_VIEW';
  if (path.startsWith('/api-docs/')) return 'DOCS_RESOURCE_VIEW';
  if (method === 'POST' && path.endsWith('/login')) return 'USER_LOGIN';

  // Extract the base resource (e.g., 'books', 'users', etc.)
  const pathParts = path.split('/');
  const resource = pathParts.length > 2 ? pathParts[2] : 'UNKNOWN';

  const actionMap = {
    GET: 'VIEW',
    POST: 'CREATE',
    PUT: 'UPDATE',
    DELETE: 'DELETE',
    PATCH: 'UPDATE',
    OPTIONS: 'OPTIONS',
    HEAD: 'VIEW'
  };

  const action = actionMap[method] || 'UNKNOWN';
  return `${resource.toUpperCase()}_${action}`;
};

// Helper function to extract relevant details based on the action
const extractDetails = (req) => {
  const details = {};

  // Don't log sensitive information like passwords
  const body = { ...req.body };
  delete body.password;
  delete body.passwordConfirm;
  delete body.token;

  // Add query parameters for GET requests
  if (req.method === 'GET' && Object.keys(req.query).length > 0) {
    details.queryParams = req.query;
  }

  switch (req.method) {
    case 'POST':
    case 'PUT':
    case 'PATCH':
      details.requestBody = body;
      break;
    case 'DELETE':
      details.resourceId = req.params.id;
      break;
  }

  // Add path parameters if they exist
  if (Object.keys(req.params).length > 0) {
    details.pathParams = req.params;
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
  const environment = getNormalizedEnvironment();

  return async (req, res, next) => {
    // Start timing the request
    const startAt = process.hrtime();

    // Add response timing calculation
    res.on('finish', async () => {
      const endAt = process.hrtime();

      try {
        const responseTime = calculateResponseTime(startAt, endAt);
        const action = determineAction(req);

        // Create log entry
        const log = new Log({
          method: req.method,
          url: req.originalUrl || req.url,
          status: res.statusCode,
          responseTime,
          userId: req.user?._id,
          username: req.user?.username,
          userRole: req.user?.role,
          action,
          details: extractDetails(req),
          ipAddress: req.ip || req.connection.remoteAddress,
          userAgent: req.get('user-agent') || 'Unknown',
          environment
        });

        await log.save();
      } catch (error) {
        console.error('Error saving log:', error);
      }
    });

    // Apply morgan logging for development
    if (environment === 'development') {
      morganLogger(req, res, (err) => {
        if (err) console.error('Morgan logging error:', err);
      });
    }

    next();
  };
};

module.exports = customLogger; 