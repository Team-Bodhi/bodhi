const express = require('express');
const router = express.Router();
const Sale = require('../models/sale');
const Book = require('../models/book');

// Helper function to build MongoDB query from request parameters
function buildSalesQuery(req) {
    const { startDate, endDate, type, orderStatus, bookTitle, genre } = req.query;
    const query = {};

    // Date range filter
    if (startDate || endDate) {
        query.orderDate = {};
        if (startDate) query.orderDate.$gte = new Date(startDate);
        if (endDate) query.orderDate.$lte = new Date(endDate);
    }

    // Sale type filter
    if (type && type !== 'All') {
        query.type = type;
    }

    // Order status filter
    if (orderStatus && orderStatus !== 'All') {
        query.orderStatus = orderStatus;
    }

    // Book title filter - using $regex for fuzzy matching
    if (bookTitle) {
        // Split the search term into words for better matching
        const searchTerms = bookTitle.split(/\s+/).filter(term => term.length > 0);
        if (searchTerms.length > 0) {
            // Create a regex pattern that matches any of the words
            const regexPatterns = searchTerms.map(term => 
                new RegExp(term.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'), 'i')
            );
            query['$or'] = [
                { 'orderItems.bookId.title': { $in: regexPatterns } }
            ];
        }
    }

    // Genre filter - handle both single genre and comma-separated list
    if (genre) {
        const genres = genre.split(',').map(g => g.trim());
        if (genres.length === 1) {
            query['orderItems.bookId.genre'] = genres[0];
        } else {
            query['orderItems.bookId.genre'] = { $in: genres };
        }
    }

    console.log('Built query:', JSON.stringify(query, null, 2));
    return query;
}

/**
 * @swagger
 * /api/reports/sales/daily:
 *   get:
 *     summary: Get daily sales statistics
 *     tags: [Reports]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: startDate
 *         schema:
 *           type: string
 *           format: date
 *         description: Start date for the report (YYYY-MM-DD)
 *       - in: query
 *         name: endDate
 *         schema:
 *           type: string
 *           format: date
 *         description: End date for the report (YYYY-MM-DD)
 */
router.get('/sales/daily', async (req, res) => {
    try {
        const query = buildSalesQuery(req);

        // First lookup books to get their details
        const dailyStats = await Sale.aggregate([
            {
                $unwind: "$orderItems"
            },
            {
                $lookup: {
                    from: "books",
                    localField: "orderItems.bookId",
                    foreignField: "_id",
                    as: "orderItems.bookId"
                }
            },
            {
                $unwind: "$orderItems.bookId"
            },
            {
                $match: query
            },
            {
                $group: {
                    _id: { $dateToString: { format: "%Y-%m-%d", date: "$orderDate" } },
                    totalSales: { $sum: "$totalPrice" },
                    totalItems: { $sum: "$orderItems.quantity" },
                    orderCount: { 
                        $addToSet: "$_id" // Use addToSet to count unique orders
                    }
                }
            },
            {
                $project: {
                    _id: 1,
                    totalSales: 1,
                    totalItems: 1,
                    orderCount: { $size: "$orderCount" }
                }
            },
            { 
                $sort: { _id: 1 } 
            }
        ]);

        res.json(dailyStats);
    } catch (error) {
        console.error('Error fetching daily sales stats:', error);
        res.status(500).json({ error: 'Failed to fetch daily sales statistics' });
    }
});

/**
 * @swagger
 * /api/reports/sales/top-genres:
 *   get:
 *     summary: Get top selling genres
 *     tags: [Reports]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 5
 *         description: Number of top genres to return
 */
router.get('/sales/top-genres', async (req, res) => {
    try {
        const query = buildSalesQuery(req);
        const limit = parseInt(req.query.limit) || 5;

        const topGenres = await Sale.aggregate([
            {
                $unwind: "$orderItems"
            },
            {
                $lookup: {
                    from: "books",
                    localField: "orderItems.bookId",
                    foreignField: "_id",
                    as: "orderItems.bookId"
                }
            },
            {
                $unwind: "$orderItems.bookId"
            },
            {
                $match: query
            },
            {
                $group: {
                    _id: "$orderItems.bookId.genre",
                    totalSales: { $sum: "$orderItems.quantity" },
                    revenue: { $sum: { $multiply: ["$orderItems.price", "$orderItems.quantity"] } }
                }
            },
            { 
                $sort: { totalSales: -1 } 
            },
            { 
                $limit: limit 
            }
        ]);

        res.json(topGenres);
    } catch (error) {
        console.error('Error fetching top genres:', error);
        res.status(500).json({ error: 'Failed to fetch top genres' });
    }
});

/**
 * @swagger
 * /api/reports/sales/top-books:
 *   get:
 *     summary: Get top selling books
 *     tags: [Reports]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 10
 *         description: Number of top books to return
 */
router.get('/sales/top-books', async (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 10;

        const topBooks = await Sale.aggregate([
            { $unwind: "$orderItems" },
            {
                $lookup: {
                    from: "books",
                    localField: "orderItems.bookId",
                    foreignField: "_id",
                    as: "bookDetails"
                }
            },
            { $unwind: "$bookDetails" },
            {
                $group: {
                    _id: {
                        bookId: "$bookDetails._id",
                        title: "$bookDetails.title",
                        author: "$bookDetails.author",
                        isbn: "$bookDetails.isbn"
                    },
                    totalSold: { $sum: "$orderItems.quantity" },
                    revenue: { $sum: { $multiply: ["$orderItems.price", "$orderItems.quantity"] } }
                }
            },
            { $sort: { totalSold: -1 } },
            { $limit: limit }
        ]);

        res.json(topBooks);
    } catch (error) {
        console.error('Error fetching top books:', error);
        res.status(500).json({ error: 'Failed to fetch top books' });
    }
});

/**
 * @swagger
 * /api/reports/sales/summary:
 *   get:
 *     summary: Get sales summary statistics
 *     tags: [Reports]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: startDate
 *         schema:
 *           type: string
 *           format: date
 *         description: Start date for the summary (YYYY-MM-DD)
 *       - in: query
 *         name: endDate
 *         schema:
 *           type: string
 *           format: date
 *         description: End date for the summary (YYYY-MM-DD)
 */
router.get('/sales/summary', async (req, res) => {
    try {
        const query = buildSalesQuery(req);

        const pipeline = [
            {
                $unwind: "$orderItems"
            },
            {
                $lookup: {
                    from: "books",
                    localField: "orderItems.bookId",
                    foreignField: "_id",
                    as: "orderItems.bookId"
                }
            },
            {
                $unwind: "$orderItems.bookId"
            },
            {
                $match: query
            },
            {
                $facet: {
                    totalRevenue: [
                        { 
                            $group: { 
                                _id: null, 
                                total: { $sum: "$totalPrice" } 
                            } 
                        }
                    ],
                    totalOrders: [
                        { 
                            $group: { 
                                _id: null, 
                                count: { $addToSet: "$_id" } 
                            } 
                        },
                        {
                            $project: {
                                count: { $size: "$count" }
                            }
                        }
                    ],
                    averageOrderValue: [
                        { 
                            $group: { 
                                _id: null, 
                                avg: { $avg: "$totalPrice" } 
                            } 
                        }
                    ],
                    salesByType: [
                        { 
                            $group: { 
                                _id: "$type", 
                                count: { $addToSet: "$_id" },
                                revenue: { $sum: "$totalPrice" } 
                            } 
                        },
                        {
                            $project: {
                                _id: 1,
                                count: { $size: "$count" },
                                revenue: 1
                            }
                        }
                    ],
                    salesByStatus: [
                        { 
                            $group: { 
                                _id: "$orderStatus", 
                                count: { $addToSet: "$_id" } 
                            } 
                        },
                        {
                            $project: {
                                _id: 1,
                                count: { $size: "$count" }
                            }
                        }
                    ],
                    totalItems: [
                        {
                            $group: {
                                _id: null,
                                count: { $sum: "$orderItems.quantity" }
                            }
                        }
                    ]
                }
            }
        ];

        const summary = await Sale.aggregate(pipeline);

        // Format the response
        const formattedSummary = {
            totalRevenue: summary[0].totalRevenue[0]?.total || 0,
            totalOrders: summary[0].totalOrders[0]?.count || 0,
            totalItems: summary[0].totalItems[0]?.count || 0,
            averageOrderValue: summary[0].averageOrderValue[0]?.avg || 0,
            salesByType: summary[0].salesByType,
            salesByStatus: summary[0].salesByStatus
        };

        res.json(formattedSummary);
    } catch (error) {
        console.error('Error fetching sales summary:', error);
        res.status(500).json({ error: 'Failed to fetch sales summary' });
    }
});

module.exports = router; 