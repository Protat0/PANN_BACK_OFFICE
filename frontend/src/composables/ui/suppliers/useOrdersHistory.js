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

export function useOrdersHistory() {
  const loading = ref(false)
  const error = ref(null)
  const allSuppliers = ref([])

  const filters = ref({
    status: 'all',
    supplier: 'all',
    dateRange: 'all',
    search: ''
  })

  // Aggregate all orders from all suppliers using batch-based logic (same as SupplierDetails.vue)
  const allOrders = computed(() => {
    const orders = []
    
    allSuppliers.value.forEach(supplier => {
      // Get batches for this supplier (same logic as SupplierDetails.vue)
      const supplierBatches = supplier.batches || []
      
      if (supplierBatches.length > 0) {
        // Group batches by date (same logic as SupplierDetails.vue)
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
        
        // Convert grouped batches to orders (same logic as SupplierDetails.vue)
        Object.entries(batchesByDate).forEach(([date, batches]) => {
          const totalCost = batches.reduce((sum, b) => sum + ((b.cost_price || 0) * (b.quantity_received || 0)), 0)
          const totalQuantity = batches.reduce((sum, b) => sum + (b.quantity_received || 0), 0)
          
          // Determine order status (same logic as SupplierDetails.vue)
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
          
          // Create order ID
          let receiptId = `SR-${date.replace(/-/g, '')}`
          const firstBatchNotes = batches[0].notes || ''
          const receiptMatch = firstBatchNotes.match(/Receipt:\s*([^\|]+)/)
          if (receiptMatch) {
            receiptId = receiptMatch[1].trim()
          }
          
          // Get expected_delivery_date and date_received from first batch
          const firstBatch = batches[0]
          const expectedDate = firstBatch.expected_delivery_date ? 
            (typeof firstBatch.expected_delivery_date === 'string' ? firstBatch.expected_delivery_date.split('T')[0] : new Date(firstBatch.expected_delivery_date).toISOString().split('T')[0]) : 
            date
          const receivedDate = firstBatch.date_received ? 
            (typeof firstBatch.date_received === 'string' ? firstBatch.date_received.split('T')[0] : new Date(firstBatch.date_received).toISOString().split('T')[0]) : 
            null
          
          orders.push({
            id: receiptId,
            supplier: supplier.supplier_name,
            supplierEmail: supplier.email || 'N/A',
            supplierId: supplier._id,
            orderDate: firstBatch.created_at ? firstBatch.created_at.split('T')[0] : date, // Order date (when PO was created)
            expectedDelivery: expectedDate, // Expected delivery date
            deliveredDate: receivedDate, // Actual received date (null for pending)
            totalAmount: totalCost,
            status: orderStatus,
            items: batches.map(batch => ({
              name: batch.product_name || batch.name || 'Unknown Product',
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
            notes: firstBatchNotes
          })
        })
      }
    })
    
    return orders.sort((a, b) => new Date(b.orderDate) - new Date(a.orderDate))
  })

  const supplierOptions = computed(() => {
    const uniqueNames = new Set()
    const options = []

    allSuppliers.value.forEach(supplier => {
      const name = supplier.supplier_name || supplier.name
      if (name && !uniqueNames.has(name)) {
        uniqueNames.add(name)
        options.push({
          value: name,
          label: name,
          email: supplier.email || ''
        })
      }
    })

    return options.sort((a, b) => a.label.localeCompare(b.label))
  })

  // Filtered orders
  const filteredOrders = computed(() => {
    let filtered = [...allOrders.value]

    if (filters.value.status !== 'all') {
      const statusMap = {
        'pending_delivery': 'Pending Delivery',
        'partially_received': 'Partially Received',
        'received': 'Received',
        'depleted': 'Depleted',
        'mixed_status': 'Mixed Status'
      }
      const targetStatus = statusMap[filters.value.status]
      if (targetStatus) {
        filtered = filtered.filter(order => order.status === targetStatus)
      }
    }

    if (filters.value.supplier !== 'all') {
      filtered = filtered.filter(order => order.supplier === filters.value.supplier)
    }

    if (filters.value.dateRange !== 'all') {
      const now = new Date()
      const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      
      let startDate
      switch (filters.value.dateRange) {
        case 'today':
          startDate = startOfDay
          break
        case 'week':
          startDate = new Date(startOfDay.getTime() - 7 * 24 * 60 * 60 * 1000)
          break
        case 'month':
          startDate = new Date(startOfDay.getFullYear(), startOfDay.getMonth(), 1)
          break
        case 'quarter':
          const quarter = Math.floor(startOfDay.getMonth() / 3)
          startDate = new Date(startOfDay.getFullYear(), quarter * 3, 1)
          break
      }
      
      if (startDate) {
        filtered = filtered.filter(order => new Date(order.orderDate) >= startDate)
      }
    }

    if (filters.value.search.trim()) {
      const search = filters.value.search.toLowerCase()
      filtered = filtered.filter(order => 
        order.id.toLowerCase().includes(search) ||
        order.supplier.toLowerCase().includes(search) ||
        order.supplierEmail.toLowerCase().includes(search) ||
        order.items?.some(item => item.name.toLowerCase().includes(search))
      )
    }

    return filtered
  })

  // Statistics
  const totalOrders = computed(() => allOrders.value.length)
  
  const activeOrdersCount = computed(() => 
    allOrders.value.filter(order => 
      ['Pending Delivery', 'Partially Received'].includes(order.status)
    ).length
  )
  
  const deliveredOrdersCount = computed(() =>
    allOrders.value.filter(order => order.status === 'Received').length
  )

  const cancelledOrdersCount = computed(() =>
    allOrders.value.filter(order => order.status === 'Depleted').length
  )

  const totalOrderValue = computed(() => 
    allOrders.value.reduce((sum, order) => sum + order.totalAmount, 0)
  )

  const averageOrderValue = computed(() => {
    if (allOrders.value.length === 0) return 0
    return Math.round(totalOrderValue.value / allOrders.value.length)
  })

  // Methods
  const fetchOrders = async () => {
    loading.value = true
    error.value = null
    
    try {
      // Fetch suppliers
      const response = await api.get('/suppliers/', {
        params: { per_page: 1000 }
      })
      
      const backendSuppliers = response.data.suppliers
      
      // Fetch all batches at once (same logic as SupplierDetails.vue)
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
        console.warn('Failed to fetch batches for orders history:', batchesError)
        allBatches = []
      }

      // Fetch product details to enrich batches with product names/category info
      // Note: Backend now enriches batches with product_name (including deleted products),
      // but we still fetch products as a fallback and for additional category info
      // IMPORTANT: Include deleted products because historical records (orders/receipts)
      // need to show product names even if products have been soft-deleted
      const productMap = {}
      try {
        // Fetch all products with pagination handling (including deleted for historical data)
        let allProducts = []
        let page = 1
        let hasMore = true
        const perPage = 1000
        
        while (hasMore) {
          const productsResponse = await api.get('/products/', { 
            params: { 
              page, 
              per_page: perPage,
              include_deleted: 'true' // Include deleted products for historical data integrity
            } 
          })
          
          const productsPayload = productsResponse.data?.products ||
            productsResponse.data?.data ||
            productsResponse.data
          
          if (Array.isArray(productsPayload)) {
            allProducts = allProducts.concat(productsPayload)
            // Check if there are more pages
            const pagination = productsResponse.data?.pagination
            if (pagination) {
              hasMore = page < pagination.total_pages
            } else {
              // If no pagination info, assume done if we got less than perPage
              hasMore = productsPayload.length === perPage
            }
            page++
          } else {
            hasMore = false
          }
        }
        
        // Build product map
        allProducts.forEach(product => {
          const productId = product._id || product.id
          if (!productId) {
            console.warn('Product missing ID:', product)
            return
          }
          productMap[productId] = {
            name: product.product_name || product.name || 'Unknown Product',
            categoryId: product.category_id || '',
            categoryName: product.category_name || '',
            subcategoryName: product.subcategory_name || ''
          }
        })
        
        console.log(`[OrdersHistory] Fetched ${allProducts.length} products for enrichment`)
      } catch (productsError) {
        console.error('[OrdersHistory] Failed to fetch products for enrichment:', productsError)
      }

      // Enrich batches with product information
      // Prefer backend-enriched product_name, fallback to productMap lookup
      const batchesWithoutProductName = []
      allBatches = allBatches.map(batch => {
        const productId = batch.product_id
        const productInfo = productId ? productMap[productId] : null
        
        // Determine product name - prioritize backend-enriched name
        let productName = batch.product_name || batch.name
        if (!productName && productInfo) {
          productName = productInfo.name
        }
        if (!productName && productId) {
          productName = 'Unknown Product'
          // Track batches missing product names for debugging
          if (!batchesWithoutProductName.find(b => b.product_id === productId)) {
            batchesWithoutProductName.push({
              batch_id: batch._id,
              product_id: productId,
              reason: productInfo ? 'Product name field missing' : 'Product not found in database'
            })
          }
        }
        if (!productName) {
          productName = 'Unknown Product'
          console.warn(`[OrdersHistory] Batch ${batch._id} has no product_id`)
        }
        
        return {
          ...batch,
          product_name: productName,
          name: productName, // Ensure name field is also set
          category_id: batch.category_id || productInfo?.categoryId || '',
          category_name: batch.category_name || productInfo?.categoryName || '',
          subcategory_name: batch.subcategory_name || productInfo?.subcategoryName || ''
        }
      })
      
      // Log batches with missing product names for debugging
      if (batchesWithoutProductName.length > 0) {
        const missingProductIds = [...new Set(batchesWithoutProductName.map(b => b.product_id))]
        console.warn(`[OrdersHistory] ${batchesWithoutProductName.length} batches have missing product names`)
        console.warn(`[OrdersHistory] Missing product IDs:`, missingProductIds)
        console.warn(`[OrdersHistory] Detailed batch info:`, batchesWithoutProductName)
        console.warn(`[OrdersHistory] Total products in productMap:`, Object.keys(productMap).length)
        console.warn(`[OrdersHistory] Sample productMap keys (first 10):`, Object.keys(productMap).slice(0, 10))
      }
      
      // Group batches by supplier_id (same logic as SupplierDetails.vue)
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
      
      // Enrich suppliers with their batches
      allSuppliers.value = backendSuppliers.map(supplier => ({
        ...supplier,
        batches: batchesBySupplier[supplier._id] || []
      }))
      
      
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch orders history'
      console.error('Error fetching orders history:', err)
    } finally {
      loading.value = false
    }
  }

  const applyFilters = () => {
    // Filters applied via computed property
  }

  const clearFilters = () => {
    filters.value = {
      status: 'all',
      supplier: 'all',
      dateRange: 'all',
      search: ''
    }
  }

  const exportOrdersData = (format = 'csv') => {
    const exportData = filteredOrders.value.map(order => ({
      'Order ID': order.id,
      'Supplier': order.supplier,
      'Supplier Email': order.supplierEmail,
      'Status': order.status,
      'Order Date': order.orderDate,
      'Expected Delivery': order.expectedDelivery,
      'Total Amount': order.totalAmount,
      'Items Count': order.items?.length || 0
    }))
    
    if (format === 'csv') {
      const headers = Object.keys(exportData[0]).join(',')
      const rows = exportData.map(row => Object.values(row).join(','))
      const csvContent = [headers, ...rows].join('\n')
      
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `orders_history_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      window.URL.revokeObjectURL(url)
    }
    
    return exportData
  }

  return {
    loading,
    error,
    filters,
    allOrders,
    filteredOrders,
    supplierOptions,
    totalOrders,
    activeOrdersCount,
    deliveredOrdersCount,
    cancelledOrdersCount,
    totalOrderValue,
    averageOrderValue,
    fetchOrders,
    applyFilters,
    clearFilters,
    exportOrdersData
  }
}