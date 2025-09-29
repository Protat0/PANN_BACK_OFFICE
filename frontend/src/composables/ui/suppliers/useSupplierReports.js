import { ref, computed } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export function useSupplierReports() {
  const loading = ref(false)
  const error = ref(null)
  const showActiveOrdersModal = ref(false)
  const showTopPerformersModal = ref(false)
  const allSuppliers = ref([])
  
  // Computed: Active Orders (from all suppliers)
  const activeOrders = computed(() => {
    const orders = []
    
    allSuppliers.value.forEach(supplier => {
      if (supplier.purchase_orders) {
        supplier.purchase_orders
          .filter(order => !order.isDeleted && (order.status === 'pending' || order.status === 'confirmed'))
          .forEach(order => {
            orders.push({
              id: order.order_id,
              supplier: supplier.supplier_name,
              supplierId: supplier._id,
              orderDate: order.order_date,
              expectedDelivery: order.expected_delivery_date,
              totalAmount: order.total_cost || 0,
              status: order.status,
              items: (order.items || []).map(item => ({
                name: item.product_name,
                quantity: item.quantity,
                unitPrice: item.unit_price
              }))
            })
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
  
  // Fetch all suppliers with their purchase orders
  const fetchAllSuppliers = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/suppliers/', {
        params: { per_page: 1000 }
      })
      
      allSuppliers.value = response.data.suppliers
      console.log('Suppliers fetched for reports:', allSuppliers.value.length)
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