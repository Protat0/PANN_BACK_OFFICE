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

  // Aggregate all orders from all suppliers
  const allOrders = computed(() => {
    const orders = []
    
    allSuppliers.value.forEach(supplier => {
      if (supplier.purchase_orders) {
        supplier.purchase_orders
          .filter(order => !order.isDeleted) // Exclude soft-deleted orders
          .forEach(order => {
            orders.push({
              id: order.order_id,
              supplier: supplier.supplier_name,
              supplierEmail: supplier.email || 'N/A',
              supplierId: supplier._id,
              orderDate: order.order_date,
              expectedDelivery: order.expected_delivery_date,
              deliveredDate: order.delivered_date, // Add this to backend if needed
              totalAmount: order.total_cost || 0,
              status: order.status,
              items: (order.items || []).map(item => ({
                name: item.product_name,
                quantity: item.quantity,
                unitPrice: item.unit_price
              })),
              description: order.description,
              notes: order.notes
            })
          })
      }
    })
    
    return orders.sort((a, b) => new Date(b.orderDate) - new Date(a.orderDate))
  })

  // Filtered orders
  const filteredOrders = computed(() => {
    let filtered = [...allOrders.value]

    if (filters.value.status !== 'all') {
      filtered = filtered.filter(order => order.status === filters.value.status)
    }

    if (filters.value.supplier !== 'all') {
      const supplierMap = {
        'bravo_warehouse': 'Bravo Warehouse',
        'john_doe_supplies': 'John Doe Supplies',
        'san_juan_groups': 'San Juan Groups',
        'bagatayam_inc': 'Bagatayam Inc.'
      }
      const supplierName = supplierMap[filters.value.supplier]
      if (supplierName) {
        filtered = filtered.filter(order => order.supplier === supplierName)
      }
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
      ['pending', 'confirmed', 'in_transit'].includes(order.status)
    ).length
  )
  
  const deliveredOrdersCount = computed(() =>
    allOrders.value.filter(order => order.status === 'delivered').length
  )

  const cancelledOrdersCount = computed(() =>
    allOrders.value.filter(order => order.status === 'cancelled').length
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
      const response = await api.get('/suppliers/', {
        params: { per_page: 1000 }
      })

      allSuppliers.value = response.data.suppliers
      
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