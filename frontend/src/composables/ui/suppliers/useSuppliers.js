// composables/useSuppliers.js
import { ref, computed, reactive } from 'vue'

export function useSuppliers() {
  // Reactive state
  const suppliers = ref([])
  const loading = ref(false)
  const error = ref(null)
  const successMessage = ref(null)
  const selectedSuppliers = ref([])

  // Filters
  const filters = reactive({
    type: 'all',
    status: 'all',
    order: 'all',
    search: ''
  })

  // Report data
  const reportData = reactive({
    activeOrdersCount: 0,
    topSuppliersCount: 0
  })

  // Computed
  const filteredSuppliers = computed(() => {
    let filtered = [...suppliers.value]

    if (filters.type !== 'all') {
      filtered = filtered.filter(supplier => supplier.type === filters.type)
    }

    if (filters.status !== 'all') {
      filtered = filtered.filter(supplier => supplier.status === filters.status)
    }

    if (filters.order !== 'all') {
      if (filters.order === 'high') {
        filtered = filtered.filter(supplier => supplier.purchaseOrders >= 10)
      } else if (filters.order === 'medium') {
        filtered = filtered.filter(supplier => supplier.purchaseOrders >= 5 && supplier.purchaseOrders < 10)
      } else if (filters.order === 'low') {
        filtered = filtered.filter(supplier => supplier.purchaseOrders >= 1 && supplier.purchaseOrders < 5)
      } else if (filters.order === 'none') {
        filtered = filtered.filter(supplier => supplier.purchaseOrders === 0)
      }
    }

    if (filters.search.trim()) {
      const search = filters.search.toLowerCase()
      filtered = filtered.filter(supplier => 
        supplier.name?.toLowerCase().includes(search) ||
        supplier.email?.toLowerCase().includes(search) ||
        supplier.phone?.includes(search)
      )
    }

    return filtered
  })

  // Methods
  const fetchSuppliers = async () => {
    loading.value = true
    error.value = null
    
    try {
      // Mock data - replace with actual API call
      const mockSuppliers = [
        {
          id: 1,
          name: 'John Doe Supplies',
          email: 'john@johndoesupplies.com',
          phone: '+63 912 345 6789',
          address: '123 Supply Street, Business District, Manila, Philippines',
          purchaseOrders: 4,
          status: 'active',
          type: 'food',
          createdAt: '2024-01-15'
        },
        {
          id: 2,
          name: 'Bravo Warehouse',
          email: 'contact@bravowarehouse.com',
          phone: '+63 917 888 9999',
          address: '456 Warehouse Ave, Industrial Park, Quezon City, Philippines',
          purchaseOrders: 5,
          status: 'active',
          type: 'packaging',
          createdAt: '2024-02-01'
        },
        {
          id: 3,
          name: 'San Juan Groups',
          email: 'info@sanjuangroups.ph',
          phone: '+63 922 111 2222',
          address: '789 Corporate Blvd, Makati City, Philippines',
          purchaseOrders: 12,
          status: 'active',
          type: 'equipment',
          createdAt: '2024-01-10'
        },
        {
          id: 4,
          name: 'Bagatayam Inc.',
          email: 'sales@bagatayam.com',
          phone: '+63 933 444 5555',
          address: '321 Trading St, Pasig City, Philippines',
          purchaseOrders: 8,
          status: 'active',
          type: 'services',
          createdAt: '2024-03-05'
        },
        {
          id: 5,
          name: 'Inactive Supplier Co.',
          email: 'test@inactive.com',
          phone: '+63 900 000 0000',
          address: '999 Test Street, Test City, Philippines',
          purchaseOrders: 0,
          status: 'inactive',
          type: 'food',
          createdAt: '2024-01-01'
        }
      ]
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500))
      
      suppliers.value = mockSuppliers
      updateReportData()
      
    } catch (err) {
      console.error('Error fetching suppliers:', err)
      error.value = `Failed to load suppliers: ${err.message}`
    } finally {
      loading.value = false
    }
  }

  const updateReportData = () => {
    reportData.activeOrdersCount = suppliers.value.filter(s => s.purchaseOrders > 0 && s.status === 'active').length
    reportData.topSuppliersCount = suppliers.value.filter(s => s.purchaseOrders >= 10).length
  }

  const deleteSupplier = async (supplier) => {
    const confirmed = confirm(`Are you sure you want to delete "${supplier.name}"?`)
    if (!confirmed) return

    try {
      suppliers.value = suppliers.value.filter(s => s.id !== supplier.id)
      successMessage.value = `Supplier "${supplier.name}" deleted successfully`
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
    } catch (err) {
      console.error('Error deleting supplier:', err)
      error.value = `Failed to delete supplier: ${err.message}`
    }
  }

  const deleteSelected = async () => {
    if (selectedSuppliers.value.length === 0) return
    
    const confirmed = confirm(`Are you sure you want to delete ${selectedSuppliers.value.length} supplier(s)?`)
    if (!confirmed) return

    try {
      suppliers.value = suppliers.value.filter(s => !selectedSuppliers.value.includes(s.id))
      selectedSuppliers.value = []
      successMessage.value = `Successfully deleted supplier(s)`
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
    } catch (err) {
      console.error('Error deleting suppliers:', err)
      error.value = `Failed to delete suppliers: ${err.message}`
    }
  }

  const clearFilters = () => {
    filters.type = 'all'
    filters.status = 'all'
    filters.order = 'all'
    filters.search = ''
  }

  const refreshData = async () => {
    successMessage.value = null
    await fetchSuppliers()
  }

  // Utility functions
  const getStatusBadgeClass = (status) => {
    const classes = {
      active: 'text-bg-success',
      inactive: 'text-bg-danger',
      pending: 'text-bg-warning'
    }
    return classes[status] || 'text-bg-secondary'
  }

  const formatStatus = (status) => {
    return status.charAt(0).toUpperCase() + status.slice(1)
  }

  const getShortAddress = (address) => {
    if (!address) return 'No address'
    return address.length > 50 ? address.substring(0, 50) + '...' : address
  }

  return {
    // State
    suppliers,
    loading,
    error,
    successMessage,
    selectedSuppliers,
    filters,
    reportData,
    
    // Computed
    filteredSuppliers,
    
    // Methods
    fetchSuppliers,
    deleteSupplier,
    deleteSelected,
    clearFilters,
    refreshData,
    
    // Utilities
    getStatusBadgeClass,
    formatStatus,
    getShortAddress
  }
}