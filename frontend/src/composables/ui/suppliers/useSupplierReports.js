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
  
  // Computed: Top Performers
  const topPerformers = computed(() => {
    return allSuppliers.value
      .filter(supplier => !supplier.isDeleted)
      .map(supplier => {
        const orders = supplier.purchase_orders?.filter(o => !o.isDeleted) || []
        const totalValue = orders.reduce((sum, o) => sum + (o.total_cost || 0), 0)
        const avgOrderValue = orders.length > 0 ? totalValue / orders.length : 0
        
        // Get last order date
        const sortedOrders = [...orders].sort((a, b) => 
          new Date(b.order_date) - new Date(a.order_date)
        )
        const lastOrderDate = sortedOrders[0]?.order_date || supplier.created_at
        
        // Get top products from order items
        const productCounts = {}
        orders.forEach(order => {
          order.items?.forEach(item => {
            const name = item.product_name
            productCounts[name] = (productCounts[name] || 0) + item.quantity
          })
        })
        
        const topProducts = Object.entries(productCounts)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 3)
          .map(([name]) => name)
        
        return {
          id: supplier._id,
          name: supplier.supplier_name,
          email: supplier.email || 'N/A',
          rating: 4.5,
          totalOrders: orders.length,
          totalValue: totalValue,
          averageOrderValue: avgOrderValue,
          lastOrder: lastOrderDate,
          onTimeDelivery: 95,
          topProducts: topProducts.length > 0 ? topProducts : ['No products yet']
        }
      })
      .filter(s => s.totalOrders >= 10)
      .sort((a, b) => b.totalValue - a.totalValue)
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
      
      // Enrich suppliers with their batches
      allSuppliers.value = backendSuppliers.map(supplier => ({
        ...supplier,
        batches: batchesBySupplier[supplier._id] || []
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