import { ref, computed } from 'vue'

export function useOrdersHistory() {
  // State
  const loading = ref(false)
  const error = ref(null)

  // Filters
  const filters = ref({
    status: 'all',
    supplier: 'all',
    dateRange: 'all',
    search: ''
  })

  // Mock data - in a real app, this would come from an API
  const allOrders = ref([
    // Current Active Orders (from reports)
    {
      id: 'PO-2025-001',
      supplier: 'Bravo Warehouse',
      supplierEmail: 'contact@bravowarehouse.com',
      orderDate: '2025-01-10',
      expectedDelivery: '2025-01-15',
      totalAmount: 25000,
      status: 'pending',
      items: [
        { name: 'Shin Ramyun Spicy', quantity: 100, unitPrice: 45 },
        { name: 'Buldak Hot Chicken', quantity: 50, unitPrice: 52 }
      ]
    },
    {
      id: 'PO-2025-002',
      supplier: 'John Doe Supplies',
      supplierEmail: 'john@johndoesupplies.com',
      orderDate: '2025-01-12',
      expectedDelivery: '2025-01-18',
      totalAmount: 18500,
      status: 'confirmed',
      items: [
        { name: 'Chapagetti Black Bean', quantity: 80, unitPrice: 48 },
        { name: 'Jin Ramen Mild', quantity: 120, unitPrice: 42 }
      ]
    },
    {
      id: 'PO-2025-003',
      supplier: 'San Juan Groups',
      supplierEmail: 'info@sanjuangroups.ph',
      orderDate: '2025-01-14',
      expectedDelivery: '2025-01-20',
      totalAmount: 32000,
      status: 'in_transit',
      items: [
        { name: 'Neoguri Seafood', quantity: 150, unitPrice: 50 },
        { name: 'Ottogi Jin Jjamppong', quantity: 90, unitPrice: 55 }
      ]
    },
    
    // Historical Orders
    {
      id: 'PO-2024-098',
      supplier: 'Bravo Warehouse',
      supplierEmail: 'contact@bravowarehouse.com',
      orderDate: '2024-12-28',
      expectedDelivery: '2025-01-02',
      deliveredDate: '2025-01-02',
      totalAmount: 22000,
      status: 'delivered',
      items: [
        { name: 'Samyang Hot Chicken', quantity: 120, unitPrice: 48 },
        { name: 'Jin Ramen Original', quantity: 80, unitPrice: 42 }
      ]
    },
    {
      id: 'PO-2024-097',
      supplier: 'San Juan Groups',
      supplierEmail: 'info@sanjuangroups.ph',
      orderDate: '2024-12-20',
      expectedDelivery: '2024-12-25',
      deliveredDate: '2024-12-24',
      totalAmount: 45000,
      status: 'delivered',
      items: [
        { name: 'Neoguri Seafood', quantity: 200, unitPrice: 50 },
        { name: 'Ottogi Jin Jjamppong', quantity: 150, unitPrice: 55 },
        { name: 'Shin Ramyun Spicy', quantity: 100, unitPrice: 45 }
      ]
    },
    {
      id: 'PO-2024-096',
      supplier: 'John Doe Supplies',
      supplierEmail: 'john@johndoesupplies.com',
      orderDate: '2024-12-15',
      expectedDelivery: '2024-12-20',
      deliveredDate: '2024-12-19',
      totalAmount: 28500,
      status: 'delivered',
      items: [
        { name: 'Chapagetti Black Bean', quantity: 150, unitPrice: 48 },
        { name: 'Jin Ramen Mild', quantity: 200, unitPrice: 42 }
      ]
    },
    {
      id: 'PO-2024-095',
      supplier: 'Bagatayam Inc.',
      supplierEmail: 'sales@bagatayam.com',
      orderDate: '2024-12-10',
      expectedDelivery: '2024-12-15',
      totalAmount: 15000,
      status: 'cancelled',
      cancelledDate: '2024-12-12',
      cancelReason: 'Supplier stock unavailable',
      items: [
        { name: 'Nissin Cup Noodles', quantity: 100, unitPrice: 35 },
        { name: 'Lucky Me Instant Pancit', quantity: 80, unitPrice: 32 }
      ]
    },
    {
      id: 'PO-2024-094',
      supplier: 'Bravo Warehouse',
      supplierEmail: 'contact@bravowarehouse.com',
      orderDate: '2024-12-05',
      expectedDelivery: '2024-12-10',
      deliveredDate: '2024-12-11',
      totalAmount: 35000,
      status: 'delivered',
      items: [
        { name: 'Buldak Hot Chicken', quantity: 180, unitPrice: 52 },
        { name: 'Samyang Carbonara', quantity: 120, unitPrice: 50 }
      ]
    },
    {
      id: 'PO-2024-093',
      supplier: 'San Juan Groups',
      supplierEmail: 'info@sanjuangroups.ph',
      orderDate: '2024-11-28',
      expectedDelivery: '2024-12-03',
      deliveredDate: '2024-12-03',
      totalAmount: 52000,
      status: 'delivered',
      items: [
        { name: 'Neoguri Seafood', quantity: 250, unitPrice: 50 },
        { name: 'Ottogi Jin Jjamppong', quantity: 200, unitPrice: 55 },
        { name: 'Shin Ramyun Black', quantity: 80, unitPrice: 60 }
      ]
    },
    {
      id: 'PO-2024-092',
      supplier: 'John Doe Supplies',
      supplierEmail: 'john@johndoesupplies.com',
      orderDate: '2024-11-25',
      expectedDelivery: '2024-11-30',
      deliveredDate: '2024-11-29',
      totalAmount: 19500,
      status: 'delivered',
      items: [
        { name: 'Jin Ramen Original', quantity: 150, unitPrice: 42 },
        { name: 'Chapagetti Black Bean', quantity: 100, unitPrice: 48 }
      ]
    },
    {
      id: 'PO-2024-091',
      supplier: 'Bagatayam Inc.',
      supplierEmail: 'sales@bagatayam.com',
      orderDate: '2024-11-20',
      expectedDelivery: '2024-11-25',
      totalAmount: 12000,
      status: 'cancelled',
      cancelledDate: '2024-11-22',
      cancelReason: 'Order modified and resubmitted',
      items: [
        { name: 'Lucky Me Beef', quantity: 120, unitPrice: 28 },
        { name: 'Nissin Yakisoba', quantity: 80, unitPrice: 38 }
      ]
    },
    {
      id: 'PO-2024-090',
      supplier: 'Bravo Warehouse',
      supplierEmail: 'contact@bravowarehouse.com',
      orderDate: '2024-11-15',
      expectedDelivery: '2024-11-20',
      deliveredDate: '2024-11-20',
      totalAmount: 38000,
      status: 'delivered',
      items: [
        { name: 'Shin Ramyun Spicy', quantity: 200, unitPrice: 45 },
        { name: 'Buldak 2x Spicy', quantity: 150, unitPrice: 55 }
      ]
    }
  ])

  // Computed values
  const filteredOrders = computed(() => {
    let filtered = [...allOrders.value]

    // Filter by status
    if (filters.value.status !== 'all') {
      filtered = filtered.filter(order => order.status === filters.value.status)
    }

    // Filter by supplier
    if (filters.value.supplier !== 'all') {
      const supplierMap = {
        'bravo_warehouse': 'Bravo Warehouse',
        'john_doe_supplies': 'John Doe Supplies',
        'san_juan_groups': 'San Juan Groups',
        'bagatayam_inc': 'Bagatayam Inc.'
      }
      filtered = filtered.filter(order => order.supplier === supplierMap[filters.value.supplier])
    }

    // Filter by date range
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

    // Search filter
    if (filters.value.search.trim()) {
      const search = filters.value.search.toLowerCase()
      filtered = filtered.filter(order => 
        order.id.toLowerCase().includes(search) ||
        order.supplier.toLowerCase().includes(search) ||
        order.supplierEmail.toLowerCase().includes(search) ||
        order.items?.some(item => item.name.toLowerCase().includes(search))
      )
    }

    // Sort by order date (newest first)
    return filtered.sort((a, b) => new Date(b.orderDate) - new Date(a.orderDate))
  })

  const totalOrders = computed(() => allOrders.value.length)
  
  const activeOrdersCount = computed(() => 
    allOrders.value.filter(order => 
      ['pending', 'confirmed', 'in_transit'].includes(order.status)
    ).length
  )
  
  const thisMonthOrders = computed(() => {
    const now = new Date()
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
    return allOrders.value.filter(order => 
      new Date(order.orderDate) >= startOfMonth
    ).length
  })
  
  const totalOrderValue = computed(() => 
    allOrders.value.reduce((sum, order) => sum + order.totalAmount, 0)
  )

  const deliveredOrdersCount = computed(() =>
    allOrders.value.filter(order => order.status === 'delivered').length
  )

  const cancelledOrdersCount = computed(() =>
    allOrders.value.filter(order => order.status === 'cancelled').length
  )

  const averageOrderValue = computed(() => {
    if (allOrders.value.length === 0) return 0
    return Math.round(totalOrderValue.value / allOrders.value.length)
  })

  const onTimeDeliveryRate = computed(() => {
    const deliveredOrders = allOrders.value.filter(order => 
      order.status === 'delivered' && order.deliveredDate && order.expectedDelivery
    )
    
    if (deliveredOrders.length === 0) return 0
    
    const onTimeOrders = deliveredOrders.filter(order => {
      const expectedDate = new Date(order.expectedDelivery)
      const deliveredDate = new Date(order.deliveredDate)
      return deliveredDate <= expectedDate
    })
    
    return Math.round((onTimeOrders.length / deliveredOrders.length) * 100)
  })

  // Methods
  const fetchOrders = async () => {
    loading.value = true
    error.value = null
    
    try {
      // Simulate API call with shorter delay for better UX
      console.log('Fetching orders history...')
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // In a real app, you would fetch from an API:
      // const response = await apiService.getOrdersHistory({
      //   page: 1,
      //   limit: 100,
      //   filters: filters.value
      // })
      // allOrders.value = response.data.orders
      
      console.log('Orders history fetched successfully:', allOrders.value.length, 'orders')
      console.log('Filtered orders:', filteredOrders.value.length)
    } catch (err) {
      error.value = err.message || 'Failed to fetch orders history'
      console.error('Error fetching orders history:', err)
    } finally {
      loading.value = false
    }
  }

  const applyFilters = () => {
    // Filters are reactive, so this will automatically update filteredOrders
    console.log('Filters applied:', filters.value)
    console.log('Filtered orders count:', filteredOrders.value.length)
  }

  const clearFilters = () => {
    filters.value = {
      status: 'all',
      supplier: 'all',
      dateRange: 'all',
      search: ''
    }
    console.log('Filters cleared')
  }

  const getOrderById = (id) => {
    return allOrders.value.find(order => order.id === id)
  }

  const getOrdersBySupplier = (supplier) => {
    return allOrders.value.filter(order => order.supplier === supplier)
  }

  const getOrdersByStatus = (status) => {
    return allOrders.value.filter(order => order.status === status)
  }

  const getOrdersByDateRange = (startDate, endDate) => {
    return allOrders.value.filter(order => {
      const orderDate = new Date(order.orderDate)
      return orderDate >= startDate && orderDate <= endDate
    })
  }

  const searchOrders = (searchTerm) => {
    if (!searchTerm.trim()) return allOrders.value
    
    const search = searchTerm.toLowerCase()
    return allOrders.value.filter(order => 
      order.id.toLowerCase().includes(search) ||
      order.supplier.toLowerCase().includes(search) ||
      order.supplierEmail.toLowerCase().includes(search) ||
      order.items?.some(item => item.name.toLowerCase().includes(search)) ||
      order.status.toLowerCase().includes(search)
    )
  }

  // Statistics methods
  const getMonthlyOrdersStats = () => {
    const months = {}
    allOrders.value.forEach(order => {
      const date = new Date(order.orderDate)
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
      
      if (!months[monthKey]) {
        months[monthKey] = {
          count: 0,
          totalValue: 0,
          delivered: 0,
          cancelled: 0,
          pending: 0,
          confirmed: 0,
          in_transit: 0
        }
      }
      
      months[monthKey].count++
      months[monthKey].totalValue += order.totalAmount
      months[monthKey][order.status]++
    })
    
    return months
  }

  const getSupplierStats = () => {
    const suppliers = {}
    allOrders.value.forEach(order => {
      if (!suppliers[order.supplier]) {
        suppliers[order.supplier] = {
          orderCount: 0,
          totalValue: 0,
          averageOrderValue: 0,
          delivered: 0,
          cancelled: 0,
          pending: 0,
          confirmed: 0,
          in_transit: 0,
          onTimeDeliveries: 0,
          lateDeliveries: 0,
          onTimeDeliveryRate: 0,
          email: order.supplierEmail
        }
      }
      
      const supplier = suppliers[order.supplier]
      supplier.orderCount++
      supplier.totalValue += order.totalAmount
      supplier[order.status]++
      
      if (order.status === 'delivered' && order.deliveredDate && order.expectedDelivery) {
        const expectedDate = new Date(order.expectedDelivery)
        const deliveredDate = new Date(order.deliveredDate)
        
        if (deliveredDate <= expectedDate) {
          supplier.onTimeDeliveries++
        } else {
          supplier.lateDeliveries++
        }
      }
    })
    
    // Calculate averages and percentages
    Object.keys(suppliers).forEach(supplierName => {
      const supplier = suppliers[supplierName]
      supplier.averageOrderValue = Math.round(supplier.totalValue / supplier.orderCount)
      
      const totalDeliveries = supplier.onTimeDeliveries + supplier.lateDeliveries
      supplier.onTimeDeliveryRate = totalDeliveries > 0 
        ? Math.round((supplier.onTimeDeliveries / totalDeliveries) * 100)
        : 0
    })
    
    return suppliers
  }

  const getOrderStatusStats = () => {
    const stats = {
      pending: 0,
      confirmed: 0,
      in_transit: 0,
      delivered: 0,
      cancelled: 0
    }
    
    allOrders.value.forEach(order => {
      stats[order.status]++
    })
    
    return stats
  }

  const getTopProductsFromOrders = (limit = 10) => {
    const products = {}
    
    allOrders.value.forEach(order => {
      if (order.status !== 'cancelled') {
        order.items?.forEach(item => {
          if (!products[item.name]) {
            products[item.name] = {
              name: item.name,
              totalQuantity: 0,
              totalValue: 0,
              orderCount: 0,
              averagePrice: 0
            }
          }
          
          products[item.name].totalQuantity += item.quantity
          products[item.name].totalValue += item.quantity * item.unitPrice
          products[item.name].orderCount++
        })
      }
    })
    
    // Calculate average prices and sort by total quantity
    const productArray = Object.values(products).map(product => ({
      ...product,
      averagePrice: Math.round(product.totalValue / product.totalQuantity)
    }))
    
    return productArray
      .sort((a, b) => b.totalQuantity - a.totalQuantity)
      .slice(0, limit)
  }

  const exportOrdersData = (format = 'csv') => {
    const exportData = filteredOrders.value.map(order => ({
      'Order ID': order.id,
      'Supplier': order.supplier,
      'Supplier Email': order.supplierEmail,
      'Status': order.status,
      'Order Date': order.orderDate,
      'Expected Delivery': order.expectedDelivery,
      'Delivered Date': order.deliveredDate || '',
      'Cancelled Date': order.cancelledDate || '',
      'Total Amount': order.totalAmount,
      'Items Count': order.items?.length || 0,
      'Cancel Reason': order.cancelReason || ''
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
    // State
    loading,
    error,
    filters,
    allOrders,
    
    // Computed
    filteredOrders,
    totalOrders,
    activeOrdersCount,
    thisMonthOrders,
    totalOrderValue,
    deliveredOrdersCount,
    cancelledOrdersCount,
    averageOrderValue,
    onTimeDeliveryRate,
    
    // Methods
    fetchOrders,
    applyFilters,
    clearFilters,
    getOrderById,
    getOrdersBySupplier,
    getOrdersByStatus,
    getOrdersByDateRange,
    searchOrders,
    getMonthlyOrdersStats,
    getSupplierStats,
    getOrderStatusStats,
    getTopProductsFromOrders,
    exportOrdersData
  }
}