import { ref, computed } from 'vue'

export function useSupplierReports() {
  // State
  const loading = ref(false)
  const error = ref(null)
  
  // Modal states
  const showActiveOrdersModal = ref(false)
  const showTopPerformersModal = ref(false)

  // Mock data - in a real app, this would come from an API
  const activeOrders = ref([
    {
      id: 'PO-2025-001',
      supplier: 'Bravo Warehouse',
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
      orderDate: '2025-01-14',
      expectedDelivery: '2025-01-20',
      totalAmount: 32000,
      status: 'in_transit',
      items: [
        { name: 'Neoguri Seafood', quantity: 150, unitPrice: 50 },
        { name: 'Ottogi Jin Jjamppong', quantity: 90, unitPrice: 55 }
      ]
    }
  ])

  const topPerformers = ref([
    {
      id: 1,
      name: 'San Juan Groups',
      email: 'info@sanjuangroups.ph',
      totalOrders: 12,
      totalValue: 156000,
      averageOrderValue: 13000,
      onTimeDelivery: 95,
      rating: 4.8,
      lastOrder: '2025-01-14',
      topProducts: ['Neoguri Seafood', 'Ottogi Jin Jjamppong', 'Shin Ramyun']
    }
  ])

  // Computed values
  const activeOrdersCount = computed(() => activeOrders.value.length)
  const topPerformersCount = computed(() => topPerformers.value.length)

  // Report data summary
  const reportData = computed(() => ({
    activeOrdersCount: activeOrdersCount.value,
    topSuppliersCount: topPerformersCount.value,
    totalOrderValue: activeOrders.value.reduce((sum, order) => sum + order.totalAmount, 0),
    pendingOrdersCount: activeOrders.value.filter(order => order.status === 'pending').length,
    averageOrderValue: activeOrdersCount.value > 0 
      ? Math.round(activeOrders.value.reduce((sum, order) => sum + order.totalAmount, 0) / activeOrdersCount.value)
      : 0
  }))

  // Methods
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

  const fetchActiveOrders = async () => {
    loading.value = true
    error.value = null
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // In a real app, you would fetch from an API:
      // const response = await apiService.getActiveOrders()
      // activeOrders.value = response.data
      
      console.log('Active orders fetched successfully')
    } catch (err) {
      error.value = err.message || 'Failed to fetch active orders'
      console.error('Error fetching active orders:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchTopPerformers = async () => {
    loading.value = true
    error.value = null
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // In a real app, you would fetch from an API:
      // const response = await apiService.getTopPerformers()
      // topPerformers.value = response.data
      
      console.log('Top performers fetched successfully')
    } catch (err) {
      error.value = err.message || 'Failed to fetch top performers'
      console.error('Error fetching top performers:', err)
    } finally {
      loading.value = false
    }
  }

  const refreshReports = async () => {
    await Promise.all([
      fetchActiveOrders(),
      fetchTopPerformers()
    ])
  }

  // Navigation actions
  const handleViewAllOrders = () => {
    console.log('Navigate to orders history page')
    // In a real app: router.push('/suppliers/orders')
    return { navigate: true, route: '/suppliers/orders' }
  }

  return {
    // State
    loading,
    error,
    showActiveOrdersModal,
    showTopPerformersModal,
    activeOrders,
    topPerformers,
    
    // Computed
    activeOrdersCount,
    topPerformersCount,
    reportData,
    
    // Methods
    openActiveOrdersModal,
    closeActiveOrdersModal,
    openTopPerformersModal,
    closeTopPerformersModal,
    fetchActiveOrders,
    fetchTopPerformers,
    refreshReports,
    handleViewAllOrders
  }
}