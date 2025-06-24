// routes/kpi.js - Express.js routes for KPI data
const express = require('express');
const router = express.Router();

// GET /api/kpi/dashboard - Get all KPI data for dashboard
router.get('/dashboard', async (req, res) => {
  try {
    // Get database collections
    const db = req.app.locals.db; // Assuming you have MongoDB connection in app.locals
    const ordersCollection = db.collection('orders');
    const customersCollection = db.collection('customers');
    
    // Calculate date ranges
    const now = new Date();
    const startOfCurrentMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    const startOfLastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    const endOfLastMonth = new Date(now.getFullYear(), now.getMonth(), 0);
    
    // 1. TOTAL PROFIT CALCULATION
    const currentMonthProfit = await ordersCollection.aggregate([
      {
        $match: {
          order_date: { $gte: startOfCurrentMonth },
          status: { $in: ['completed', 'delivered'] }
        }
      },
      {
        $group: {
          _id: null,
          totalProfit: {
            $sum: {
              $subtract: ['$total_amount', '$cost_amount'] // assuming you have cost_amount field
            }
          }
        }
      }
    ]).toArray();

    const lastMonthProfit = await ordersCollection.aggregate([
      {
        $match: {
          order_date: { $gte: startOfLastMonth, $lte: endOfLastMonth },
          status: { $in: ['completed', 'delivered'] }
        }
      },
      {
        $group: {
          _id: null,
          totalProfit: {
            $sum: {
              $subtract: ['$total_amount', '$cost_amount']
            }
          }
        }
      }
    ]).toArray();

    const currentProfit = currentMonthProfit[0]?.totalProfit || 0;
    const lastProfit = lastMonthProfit[0]?.totalProfit || 0;
    const profitChange = lastProfit > 0 ? ((currentProfit - lastProfit) / lastProfit * 100).toFixed(1) : 0;

    // 2. TOTAL CUSTOMERS CALCULATION
    const currentMonthCustomers = await customersCollection.countDocuments({
      date_created: { $gte: startOfCurrentMonth }
    });

    const lastMonthCustomers = await customersCollection.countDocuments({
      date_created: { $gte: startOfLastMonth, $lte: endOfLastMonth }
    });

    const totalCustomers = await customersCollection.countDocuments({
      status: { $ne: 'deleted' } // Only active customers
    });

    const customerChange = lastMonthCustomers > 0 ? 
      ((currentMonthCustomers - lastMonthCustomers) / lastMonthCustomers * 100).toFixed(1) : 0;

    // 3. AVERAGE ORDER VALUE CALCULATION
    const currentMonthOrders = await ordersCollection.aggregate([
      {
        $match: {
          order_date: { $gte: startOfCurrentMonth },
          status: { $in: ['completed', 'delivered'] }
        }
      },
      {
        $group: {
          _id: null,
          avgOrderValue: { $avg: '$total_amount' },
          totalOrders: { $sum: 1 }
        }
      }
    ]).toArray();

    const lastMonthOrders = await ordersCollection.aggregate([
      {
        $match: {
          order_date: { $gte: startOfLastMonth, $lte: endOfLastMonth },
          status: { $in: ['completed', 'delivered'] }
        }
      },
      {
        $group: {
          _id: null,
          avgOrderValue: { $avg: '$total_amount' }
        }
      }
    ]).toArray();

    const currentAvgOrder = currentMonthOrders[0]?.avgOrderValue || 0;
    const lastAvgOrder = lastMonthOrders[0]?.avgOrderValue || 0;
    const avgOrderChange = lastAvgOrder > 0 ? 
      ((currentAvgOrder - lastAvgOrder) / lastAvgOrder * 100).toFixed(1) : 0;

    // Format response
    const kpiData = {
      totalProfit: {
        value: currentProfit,
        formattedValue: `₱${currentProfit.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
        change: profitChange,
        changeType: profitChange >= 0 ? 'positive' : 'negative',
        subtitle: 'From this month'
      },
      totalCustomers: {
        value: totalCustomers,
        formattedValue: totalCustomers.toLocaleString(),
        change: customerChange,
        changeType: customerChange >= 0 ? 'positive' : 'negative',
        subtitle: 'Active customers'
      },
      avgOrderValue: {
        value: currentAvgOrder,
        formattedValue: `₱${currentAvgOrder.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
        change: avgOrderChange,
        changeType: avgOrderChange >= 0 ? 'positive' : 'negative',
        subtitle: 'Last 30 days'
      }
    };

    res.json({
      success: true,
      data: kpiData,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching KPI data:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch KPI data',
      error: error.message
    });
  }
});

// GET /api/kpi/profit - Get detailed profit data
router.get('/profit', async (req, res) => {
  try {
    const db = req.app.locals.db;
    const ordersCollection = db.collection('orders');
    
    const { period = 'month' } = req.query; // month, quarter, year
    
    let dateFilter;
    const now = new Date();
    
    switch (period) {
      case 'quarter':
        const quarterStart = new Date(now.getFullYear(), Math.floor(now.getMonth() / 3) * 3, 1);
        dateFilter = { order_date: { $gte: quarterStart } };
        break;
      case 'year':
        const yearStart = new Date(now.getFullYear(), 0, 1);
        dateFilter = { order_date: { $gte: yearStart } };
        break;
      default: // month
        const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
        dateFilter = { order_date: { $gte: monthStart } };
    }

    const profitData = await ordersCollection.aggregate([
      {
        $match: {
          ...dateFilter,
          status: { $in: ['completed', 'delivered'] }
        }
      },
      {
        $group: {
          _id: {
            year: { $year: '$order_date' },
            month: { $month: '$order_date' },
            day: { $dayOfMonth: '$order_date' }
          },
          dailyProfit: {
            $sum: {
              $subtract: ['$total_amount', '$cost_amount']
            }
          },
          orderCount: { $sum: 1 }
        }
      },
      {
        $sort: { '_id.year': 1, '_id.month': 1, '_id.day': 1 }
      }
    ]).toArray();

    res.json({
      success: true,
      data: profitData,
      period: period
    });

  } catch (error) {
    console.error('Error fetching profit data:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch profit data',
      error: error.message
    });
  }
});

module.exports = router;