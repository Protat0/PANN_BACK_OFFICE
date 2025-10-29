import { ref, computed } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || localStorage.getItem('authToken') || sessionStorage.getItem('authToken')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export function useSupplierReports() {
  const loading = ref(false)
  const error = ref(null)
  const showActiveOrdersModal = ref(false)
  const showTopPerformersModal = ref(false)
  const allSuppliers = ref([])
  
  // Computed: Active Orders (from all suppliers using batches like SupplierCard.vue)
  const activeOrders = computed(() => {
    const orders = []
    
    allSuppliers.value.forEach(supplier => {
      // Get batches for this supplier (same logic as SupplierCard.vue)
      const supplierBatches = supplier.batches || []
      
      if (supplierBatches.length > 0) {
        // Group batches by date (same logic as SupplierCard.vue)
        const batchesByDate = {}
        supplierBatches.forEach(batch => {
          let dateKey
          if (batch.date_received) {
            dateKey = typeof batch.date_received === 'string' ? batch.date_received.split('T')[0] : new Date(batch.date_received).toISOString().split('T')[0]
          } else if (batch.expected_delivery_date) {
            dateKey = typeof batch.expected_delivery_date === 'string' ? batch.expected_delivery_date.split('T')[0] : new Date(batch.expected_delivery_date).toISOString().split('T')[0]
          } else {
            dateKey = batch.created_at.split('T')[0]
          }
          
          if (!batchesByDate[dateKey]) {
            batchesByDate[dateKey] = []
          }
          batchesByDate[dateKey].push(batch)
        })
        
        // Convert grouped batches to orders (same logic as SupplierCard.vue)
        Object.entries(batchesByDate).forEach(([date, batches]) => {
          const totalCost = batches.reduce((sum, b) => sum + ((b.cost_price || 0) * (b.quantity_received || 0)), 0)
          const totalQuantity = batches.reduce((sum, b) => sum + (b.quantity_received || 0), 0)
          
          // Determine order status (same logic as SupplierCard.vue)
          const allPending = batches.every(b => b.status === 'pending')
          const allActive = batches.every(b => b.status === 'active')
          const allInactive = batches.every(b => b.status === 'inactive')
          const hasPending = batches.some(b => b.status === 'pending')
          
          let orderStatus
          if (allPending) orderStatus = 'Pending Delivery'
          else if (allActive) orderStatus = 'Received'
          else if (allInactive) orderStatus = 'Depleted'
          else if (hasPending) orderStatus = 'Partially Received'
          else orderStatus = 'Mixed Status'
          
          // Only include active orders (same logic as SupplierCard.vue)
          if (orderStatus === 'Pending Delivery' || orderStatus === 'Partially Received') {
            orders.push({
              id: `SR-${date.replace(/-/g, '')}`,
              supplier: supplier.supplier_name,
              supplierId: supplier._id,
              supplierEmail: supplier.email || 'N/A',
              orderDate: batches[0].created_at ? batches[0].created_at.split('T')[0] : date,
              expectedDelivery: batches[0].expected_delivery_date ? 
                (typeof batches[0].expected_delivery_date === 'string' ? batches[0].expected_delivery_date.split('T')[0] : new Date(batches[0].expected_delivery_date).toISOString().split('T')[0]) : 
                date,
              deliveredDate: batches[0].date_received ? 
                (typeof batches[0].date_received === 'string' ? batches[0].date_received.split('T')[0] : new Date(batches[0].date_received).toISOString().split('T')[0]) : 
                null,
              totalAmount: totalCost,
              status: orderStatus,
              items: batches.map(batch => ({
                name: batch.product_name || batch.product_id || 'Unknown Product',
                product_name: batch.product_name || 'Unknown Product',
                product_id: batch.product_id,
                quantity: batch.quantity_received,
                unitPrice: batch.cost_price || 0,
                totalPrice: (batch.cost_price || 0) * (batch.quantity_received || 0),
                batchNumber: batch.batch_number,
                batchId: batch._id,
                expiryDate: batch.expiry_date,
                quantityRemaining: batch.quantity_remaining
              })),
              description: `Stock receipt with ${batches.length} item(s)`,
              notes: batches[0].notes || ''
            })
          }
        })
      }
    })
    
    return orders.sort((a, b) => new Date(b.orderDate) - new Date(a.orderDate))
  })
  
  // Helper: Calculate performance rating from batches (same logic as SupplierDetails)
  const calculatePerformanceRating = (supplierBatches, supplierCreatedAt) => {
    if (!supplierBatches || supplierBatches.length === 0) {
      return null
    }

    // Group batches by date to create orders (same logic as SupplierDetails)
    const batchesByDate = {}
    supplierBatches.forEach(batch => {
      let dateKey
      if (batch.date_received) {
        dateKey = typeof batch.date_received === 'string' ? batch.date_received.split('T')[0] : new Date(batch.date_received).toISOString().split('T')[0]
      } else if (batch.expected_delivery_date) {
        dateKey = typeof batch.expected_delivery_date === 'string' ? batch.expected_delivery_date.split('T')[0] : new Date(batch.expected_delivery_date).toISOString().split('T')[0]
      } else {
        dateKey = batch.created_at.split('T')[0]
      }
      
      if (!batchesByDate[dateKey]) {
        batchesByDate[dateKey] = []
      }
      batchesByDate[dateKey].push(batch)
    })

    const orders = Object.entries(batchesByDate).map(([date, batches]) => {
      const firstBatch = batches[0]
      const expectedDate = firstBatch.expected_delivery_date ? 
        (typeof firstBatch.expected_delivery_date === 'string' ? firstBatch.expected_delivery_date.split('T')[0] : new Date(firstBatch.expected_delivery_date).toISOString().split('T')[0]) : 
        date
      const receivedDate = firstBatch.date_received ? 
        (typeof firstBatch.date_received === 'string' ? firstBatch.date_received.split('T')[0] : new Date(firstBatch.date_received).toISOString().split('T')[0]) : 
        null
      
      // Determine status (same logic as SupplierDetails.getReceiptStatus)
      const allPending = batches.every(b => b.status === 'pending')
      const allActive = batches.every(b => b.status === 'active')
      const allInactive = batches.every(b => b.status === 'inactive')
      const hasPending = batches.some(b => b.status === 'pending')
      
      let status = 'Mixed Status'
      if (allPending) status = 'Pending Delivery'
      else if (allActive) status = 'Received'
      else if (allInactive) status = 'Depleted'
      else if (hasPending) status = 'Partially Received'

      return {
        date,
        expectedDate,
        receivedDate,
        status,
        total: batches.reduce((sum, b) => sum + ((b.cost_price || 0) * (b.quantity_received || 0)), 0),
        batches
      }
    })

    const receivedOrders = orders.filter(order => 
      order.status === 'Received' && order.expectedDate && order.receivedDate
    )

    if (receivedOrders.length === 0) {
      return null
    }

    // Factor 1: On-time Delivery Rate (40% weight)
    let onTimeCount = 0
    receivedOrders.forEach(order => {
      const expectedDate = new Date(order.expectedDate)
      const receivedDate = new Date(order.receivedDate)
      const diffDays = Math.ceil((receivedDate - expectedDate) / (1000 * 60 * 60 * 24))

      if (diffDays <= 0) {
        onTimeCount++
      } else if (diffDays <= 3) {
        onTimeCount += 0.7
      }
    })
    const onTimeDeliveryRate = receivedOrders.length > 0 ? (onTimeCount / receivedOrders.length) * 100 : 0

    // Factor 2: Order Frequency/Activity (25% weight)
    const daysActive = supplierCreatedAt ? (() => {
      const createdDate = new Date(supplierCreatedAt)
      const today = new Date()
      const diffTime = Math.abs(today - createdDate)
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) || 1
    })() : 1
    const ordersPerMonth = (orders.length / (daysActive / 30))
    const frequencyScore = Math.min(ordersPerMonth / 2, 1) * 100

    // Factor 3: Value Contribution (20% weight)
    const totalSpent = receivedOrders.reduce((sum, o) => sum + o.total, 0)
    const avgOrderValue = receivedOrders.length > 0 ? totalSpent / receivedOrders.length : 0
    const valueScore = Math.min((avgOrderValue / 10000) * 100, 100)

    // Factor 4: Consistency (15% weight)
    const orderDates = orders
      .filter(o => o.date)
      .map(o => new Date(o.date))
      .sort((a, b) => a - b)
    
    let consistencyScore = 50
    if (orderDates.length >= 3) {
      const intervals = []
      for (let i = 1; i < orderDates.length; i++) {
        const diffDays = (orderDates[i] - orderDates[i-1]) / (1000 * 60 * 60 * 24)
        intervals.push(diffDays)
      }
      
      if (intervals.length > 0) {
        const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length
        const variance = intervals.reduce((sum, interval) => {
          return sum + Math.pow(interval - avgInterval, 2)
        }, 0) / intervals.length
        const stdDev = Math.sqrt(variance)
        
        consistencyScore = Math.max(0, Math.min(100, 100 - (stdDev / avgInterval) * 100))
      }
    }

    // Calculate weighted average
    const weightedRating = (
      (onTimeDeliveryRate * 0.40) +
      (frequencyScore * 0.25) +
      (valueScore * 0.20) +
      (consistencyScore * 0.15)
    ) / 100 * 5

    return Math.max(0, Math.min(5, Math.round(weightedRating * 10) / 10))
  }

  // Helper: Calculate on-time delivery percentage
  const calculateOnTimeDelivery = (supplierBatches) => {
    // Group batches by date
    const batchesByDate = {}
    supplierBatches.forEach(batch => {
      let dateKey
      if (batch.date_received) {
        dateKey = typeof batch.date_received === 'string' ? batch.date_received.split('T')[0] : new Date(batch.date_received).toISOString().split('T')[0]
      } else if (batch.expected_delivery_date) {
        dateKey = typeof batch.expected_delivery_date === 'string' ? batch.expected_delivery_date.split('T')[0] : new Date(batch.expected_delivery_date).toISOString().split('T')[0]
      } else {
        return // Skip batches without dates
      }
      
      if (!batchesByDate[dateKey]) {
        batchesByDate[dateKey] = []
      }
      batchesByDate[dateKey].push(batch)
    })

    const receivedOrders = Object.entries(batchesByDate)
      .map(([date, batches]) => {
        const firstBatch = batches[0]
        return {
          expectedDate: firstBatch.expected_delivery_date ? 
            (typeof firstBatch.expected_delivery_date === 'string' ? firstBatch.expected_delivery_date.split('T')[0] : new Date(firstBatch.expected_delivery_date).toISOString().split('T')[0]) : 
            null,
          receivedDate: firstBatch.date_received ? 
            (typeof firstBatch.date_received === 'string' ? firstBatch.date_received.split('T')[0] : new Date(firstBatch.date_received).toISOString().split('T')[0]) : 
            null
        }
      })
      .filter(order => order.expectedDate && order.receivedDate)

    if (receivedOrders.length === 0) return 0

    let onTimeCount = 0
    receivedOrders.forEach(order => {
      const expectedDate = new Date(order.expectedDate)
      const receivedDate = new Date(order.receivedDate)
      const diffDays = Math.ceil((receivedDate - expectedDate) / (1000 * 60 * 60 * 24))
      
      if (diffDays <= 0) {
        onTimeCount++
      } else if (diffDays <= 3) {
        onTimeCount += 0.7 // Partial credit for slightly late
      }
    })

    return Math.round((onTimeCount / receivedOrders.length) * 100)
  }

  // Computed: Top Performers
  const topPerformers = computed(() => {
    return allSuppliers.value
      .filter(supplier => !supplier.isDeleted && supplier.batches && supplier.batches.length > 0)
      .map(supplier => {
        const supplierBatches = supplier.batches || []
        
        // Group batches into orders to calculate metrics
        const batchesByDate = {}
        supplierBatches.forEach(batch => {
          let dateKey
          if (batch.date_received) {
            dateKey = typeof batch.date_received === 'string' ? batch.date_received.split('T')[0] : new Date(batch.date_received).toISOString().split('T')[0]
          } else if (batch.expected_delivery_date) {
            dateKey = typeof batch.expected_delivery_date === 'string' ? batch.expected_delivery_date.split('T')[0] : new Date(batch.expected_delivery_date).toISOString().split('T')[0]
          } else {
            dateKey = batch.created_at?.split('T')[0] || new Date().toISOString().split('T')[0]
          }
          
          if (!batchesByDate[dateKey]) {
            batchesByDate[dateKey] = []
          }
          batchesByDate[dateKey].push(batch)
        })

        const orders = Object.entries(batchesByDate).map(([date, batches]) => {
          const allPending = batches.every(b => b.status === 'pending')
          const allActive = batches.every(b => b.status === 'active')
          const hasPending = batches.some(b => b.status === 'pending')
          
          let status = 'Received'
          if (allPending) status = 'Pending Delivery'
          else if (hasPending) status = 'Partially Received'
          else if (!allActive) status = 'Received'

          return {
            date,
            status,
            total: batches.reduce((sum, b) => sum + ((b.cost_price || 0) * (b.quantity_received || 0)), 0),
            batches
          }
        })

        const receivedOrders = orders.filter(o => o.status === 'Received')
        
        // Calculate metrics
        const totalValue = receivedOrders.reduce((sum, o) => sum + o.total, 0)
        const avgOrderValue = receivedOrders.length > 0 ? totalValue / receivedOrders.length : 0
        
        // Get last order date
        const sortedOrders = [...orders].sort((a, b) => new Date(b.date) - new Date(a.date))
        const lastOrderDate = sortedOrders[0]?.date || supplier.created_at
        
        // Get top products from batches
        const productCounts = {}
        supplierBatches.forEach(batch => {
          const productName = batch.product_name || batch.product_id || 'Unknown Product'
          productCounts[productName] = (productCounts[productName] || 0) + (batch.quantity_received || 0)
        })
        
        const topProducts = Object.entries(productCounts)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 3)
          .map(([name]) => name)

        // Calculate performance rating
        const rating = calculatePerformanceRating(supplierBatches, supplier.created_at)
        
        // Calculate on-time delivery
        const onTimeDelivery = calculateOnTimeDelivery(supplierBatches)

        return {
          id: supplier._id,
          name: supplier.supplier_name,
          email: supplier.email || 'N/A',
          rating: rating !== null ? rating.toFixed(1) : 'N/A',
          totalOrders: orders.length,
          completedOrders: receivedOrders.length,
          totalValue: totalValue,
          averageOrderValue: avgOrderValue,
          lastOrder: lastOrderDate,
          onTimeDelivery: onTimeDelivery,
          topProducts: topProducts.length > 0 ? topProducts : ['No products yet'],
          performanceScore: rating !== null ? rating : 0 // For sorting
        }
      })
      .filter(s => s.completedOrders >= 3) // Require at least 3 completed orders
      .sort((a, b) => {
        // Sort by composite score: rating (60%) + value score (40%)
        const aScore = a.performanceScore * 0.6 + Math.min(a.totalValue / 100000, 5) * 0.4
        const bScore = b.performanceScore * 0.6 + Math.min(b.totalValue / 100000, 5) * 0.4
        return bScore - aScore
      })
      .slice(0, 10)
  })
  
  const activeOrdersCount = computed(() => activeOrders.value.length)
  const topPerformersCount = computed(() => topPerformers.value.length)
  
  const reportData = computed(() => ({
    activeOrdersCount: activeOrdersCount.value,
    topSuppliersCount: topPerformersCount.value,
    totalOrderValue: activeOrders.value.reduce((sum, order) => sum + order.totalAmount, 0),
    pendingOrdersCount: activeOrders.value.filter(order => order.status === 'pending').length,
    averageOrderValue: activeOrdersCount.value > 0 
      ? Math.round(activeOrders.value.reduce((sum, order) => sum + order.totalAmount, 0) / activeOrdersCount.value)
      : 0
  }))
  
  // Fetch all suppliers with their batches (same logic as useSuppliers.js)
  const fetchAllSuppliers = async () => {
    loading.value = true
    error.value = null
    
    try {
      // Fetch suppliers
      const response = await api.get('/suppliers/', {
        params: { per_page: 1000 }
      })
      
      const backendSuppliers = response.data.suppliers
      
      // Fetch all batches at once (same logic as useSuppliers.js)
      let allBatches = []
      try {
        const batchesResponse = await api.get('/batches/', { params: { per_page: 1000 } })
        
        // Handle the correct response format from BatchListView
        if (batchesResponse.data && batchesResponse.data.success && Array.isArray(batchesResponse.data.data)) {
          allBatches = batchesResponse.data.data
        } else if (batchesResponse.data && Array.isArray(batchesResponse.data)) {
          allBatches = batchesResponse.data
        } else if (batchesResponse.data && Array.isArray(batchesResponse.data.batches)) {
          allBatches = batchesResponse.data.batches
        } else {
          console.warn('Unexpected batches response format:', batchesResponse.data)
          allBatches = []
        }
      } catch (batchesError) {
        console.warn('Failed to fetch batches for reports:', batchesError)
        allBatches = []
      }
      
      // Group batches by supplier_id (same logic as useSuppliers.js)
      const batchesBySupplier = {}
      allBatches.forEach(batch => {
        const supplierId = batch.supplier_id
        if (supplierId) {
          if (!batchesBySupplier[supplierId]) {
            batchesBySupplier[supplierId] = []
          }
          batchesBySupplier[supplierId].push(batch)
        }
      })
      
      // Get unique product IDs to fetch product names
      const uniqueProductIds = [...new Set(allBatches
        .filter(b => b.product_id)
        .map(b => b.product_id)
      )]
      
      // Fetch product names for all unique products
      const productNamesMap = {}
      await Promise.all(
        uniqueProductIds.map(async (productId) => {
          try {
            const productResponse = await api.get(`/products/${productId}/`)
            const product = productResponse.data?.data || productResponse.data
            if (product) {
              productNamesMap[productId] = product.product_name || product.name || productId
            } else {
              productNamesMap[productId] = productId
            }
          } catch (err) {
            console.warn(`Failed to fetch product name for ${productId}:`, err)
            productNamesMap[productId] = productId
          }
        })
      )
      
      // Enrich batches with product names
      const enrichedBatchesBySupplier = {}
      Object.entries(batchesBySupplier).forEach(([supplierId, batches]) => {
        enrichedBatchesBySupplier[supplierId] = batches.map(batch => ({
          ...batch,
          product_name: batch.product_name || productNamesMap[batch.product_id] || batch.product_id || 'Unknown Product'
        }))
      })
      
      // Enrich suppliers with their batches (now with product names)
      allSuppliers.value = backendSuppliers.map(supplier => ({
        ...supplier,
        batches: enrichedBatchesBySupplier[supplier._id] || []
      }))
      
      console.log('Suppliers fetched for reports:', allSuppliers.value.length)
      console.log('Total batches:', allBatches.length)
      console.log('Active orders found:', activeOrders.value.length)
      console.log('Top performers found:', topPerformers.value.length)
      
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch supplier reports'
      console.error('Error fetching suppliers for reports:', err)
    } finally {
      loading.value = false
    }
  }
  
  const openActiveOrdersModal = () => {
    showActiveOrdersModal.value = true
  }
  
  const closeActiveOrdersModal = () => {
    showActiveOrdersModal.value = false
  }
  
  const openTopPerformersModal = () => {
    showTopPerformersModal.value = true
  }
  
  const closeTopPerformersModal = () => {
    showTopPerformersModal.value = false
  }
  
  const refreshReports = async () => {
    await fetchAllSuppliers()
  }
  
  const handleViewAllOrders = () => {
    return { name: 'OrdersHistory' }
  }
  
  return {
    loading,
    error,
    showActiveOrdersModal,
    showTopPerformersModal,
    activeOrders,
    topPerformers,
    activeOrdersCount,
    topPerformersCount,
    reportData,
    openActiveOrdersModal,
    closeActiveOrdersModal,
    openTopPerformersModal,
    closeTopPerformersModal,
    refreshReports,
    handleViewAllOrders
  }
}