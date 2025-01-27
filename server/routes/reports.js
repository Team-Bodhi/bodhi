const express = require('express');
const router = express.Router();
const Sale = require('../models/sale');
const Book = require('../models/book');

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
        const { startDate, endDate } = req.query;
        const query = {};

        if (startDate || endDate) {
            query.orderDate = {};
            if (startDate) query.orderDate.$gte = new Date(startDate);
            if (endDate) query.orderDate.$lte = new Date(endDate);
        }

        const dailyStats = await Sale.aggregate([
            { $match: query },
            {
                $group: {
                    _id: { $dateToString: { format: "%Y-%m-%d", date: "$orderDate" } },
                    totalSales: { $sum: "$totalPrice" },
                    totalItems: {
                        $sum: {
                            $reduce: {
                                input: "$orderItems",
                                initialValue: 0,
                                in: { $add: ["$$value", "$$this.quantity"] }
                            }
                        }
                    },
                    orderCount: { $sum: 1 }
                }
            },
            { $sort: { _id: 1 } }
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
        const limit = parseInt(req.query.limit) || 5;

        const topGenres = await Sale.aggregate([
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
                    _id: "$bookDetails.genre",
                    totalSales: { $sum: "$orderItems.quantity" },
                    revenue: { $sum: { $multiply: ["$orderItems.price", "$orderItems.quantity"] } }
                }
            },
            { $sort: { totalSales: -1 } },
            { $limit: limit }
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
        const { startDate, endDate } = req.query;
        const query = {};

        if (startDate || endDate) {
            query.orderDate = {};
            if (startDate) query.orderDate.$gte = new Date(startDate);
            if (endDate) query.orderDate.$lte = new Date(endDate);
        }

        const summary = await Sale.aggregate([
            { $match: query },
            {
                $facet: {
                    totalRevenue: [
                        { $group: { _id: null, total: { $sum: "$totalPrice" } } }
                    ],
                    totalOrders: [
                        { $group: { _id: null, count: { $sum: 1 } } }
                    ],
                    averageOrderValue: [
                        { $group: { _id: null, avg: { $avg: "$totalPrice" } } }
                    ],
                    salesByType: [
                        { $group: { 
                            _id: "$type", 
                            count: { $sum: 1 }, 
                            revenue: { $sum: "$totalPrice" } 
                        } }
                    ],
                    salesByStatus: [
                        { $group: { _id: "$status", count: { $sum: 1 } } }
                    ],
                    totalItems: [
                        {
                            $group: {
                                _id: null,
                                count: {
                                    $sum: {
                                        $reduce: {
                                            input: "$orderItems",
                                            initialValue: 0,
                                            in: { $add: ["$$value", "$$this.quantity"] }
                                        }
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        ]);

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