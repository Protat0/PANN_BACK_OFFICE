// composables/ui/suppliers/useSuppliers.js
import { ref, computed, reactive } from 'vue'
import axios from 'axios'

// Configure axios base URL - adjust to your backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Create axios instance with auth token
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export function useSuppliers() {
  // Reactive state
  const suppliers = ref([])
  const loading = ref(false)
  const error = ref(null)
  const successMessage = ref(null)
  const selectedSuppliers = ref([])
  const pagination = ref({
    current_page: 1,
    per_page: 50,
    total_count: 0,
    total_pages: 1
  })

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

  // Transform backend data to frontend format
  const transformSupplier = (backendSupplier) => {
    return {
      id: backendSupplier._id, // Use _id from backend
      name: backendSupplier.supplier_name,
      email: backendSupplier.email || '',
      phone: backendSupplier.phone_number || '',
      address: backendSupplier.address || '',
      contactPerson: backendSupplier.contact_person || '',
      purchaseOrders: backendSupplier.purchase_orders?.length || 0,
      status: backendSupplier.isDeleted ? 'inactive' : 'active',
      type: backendSupplier.type || 'food', // You may need to add this field to backend
      createdAt: backendSupplier.created_at,
      updatedAt: backendSupplier.updated_at,
      raw: backendSupplier // Keep original data for updates
    }
  }

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
        supplier.phone?.includes(search) ||
        supplier.contactPerson?.toLowerCase().includes(search)
      )
    }

    return filtered
  })

  // Methods
  const fetchSuppliers = async (page = 1) => {
    loading.value = true
    error.value = null
    
    try {
      const params = {
        page,
        per_page: pagination.value.per_page
      }

      // Add search filter if exists
      if (filters.search.trim()) {
        params.search = filters.search.trim()
      }

      const response = await api.get('/suppliers/', { params })
      
      // Transform the backend data
      const transformedSuppliers = response.data.suppliers.map(transformSupplier)
      
      suppliers.value = transformedSuppliers
      pagination.value = response.data.pagination
      
      updateReportData()
      
      console.log('Suppliers loaded:', transformedSuppliers.length)
      
    } catch (err) {
      console.error('Error fetching suppliers:', err)
      
      if (err.response) {
        // Server responded with error
        error.value = err.response.data.error || `Failed to load suppliers: ${err.response.statusText}`
      } else if (err.request) {
        // Request made but no response
        error.value = 'Cannot connect to server. Please check your connection.'
      } else {
        // Something else happened
        error.value = `Failed to load suppliers: ${err.message}`
      }
    } finally {
      loading.value = false
    }
  }

  const addSupplier = async (supplierData) => {
    loading.value = true
    error.value = null
    
    try {
      // Transform frontend data to backend format
      const backendData = {
        supplier_name: supplierData.name,
        email: supplierData.email,
        phone_number: supplierData.phone,
        address: supplierData.address,
        contact_person: supplierData.contactPerson,
        type: supplierData.type || 'food'
      }

      const response = await api.post('/suppliers/', backendData)
      
      // Transform and add to local state
      const newSupplier = transformSupplier(response.data)
      suppliers.value.unshift(newSupplier)
      
      successMessage.value = `Supplier "${newSupplier.name}" added successfully`
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
      
      return { success: true, supplier: newSupplier }
      
    } catch (err) {
      console.error('Error adding supplier:', err)
      
      let errorMessage = 'Failed to add supplier'
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error
      }
      
      error.value = errorMessage
      
      return { success: false, error: errorMessage }
      
    } finally {
      loading.value = false
    }
  }

  const updateSupplier = async (supplierId, supplierData) => {
    loading.value = true
    error.value = null
    
    try {
      // Transform frontend data to backend format
      const backendData = {
        supplier_name: supplierData.name,
        email: supplierData.email,
        phone_number: supplierData.phone,
        address: supplierData.address,
        contact_person: supplierData.contactPerson,
        type: supplierData.type
      }

      const response = await api.put(`/suppliers/${supplierId}/`, backendData)
      
      // Transform and update local state
      const updatedSupplier = transformSupplier(response.data)
      const index = suppliers.value.findIndex(s => s.id === supplierId)
      
      if (index !== -1) {
        suppliers.value[index] = updatedSupplier
      }
      
      successMessage.value = `Supplier "${updatedSupplier.name}" updated successfully`
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
      
      return { success: true, supplier: updatedSupplier }
      
    } catch (err) {
      console.error('Error updating supplier:', err)
      
      let errorMessage = 'Failed to update supplier'
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error
      }
      
      error.value = errorMessage
      
      return { success: false, error: errorMessage }
      
    } finally {
      loading.value = false
    }
  }

  const deleteSupplier = async (supplier) => {
    const confirmed = confirm(`Are you sure you want to delete "${supplier.name}"?`)
    if (!confirmed) return { success: false, cancelled: true }

    loading.value = true
    error.value = null
    
    try {
      await api.delete(`/suppliers/${supplier.id}/`)
      
      // Remove from local state
      suppliers.value = suppliers.value.filter(s => s.id !== supplier.id)
      
      successMessage.value = `Supplier "${supplier.name}" deleted successfully`
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
      
      return { success: true }
      
    } catch (err) {
      console.error('Error deleting supplier:', err)
      
      let errorMessage = 'Failed to delete supplier'
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error
      }
      
      error.value = errorMessage
      
      return { success: false, error: errorMessage }
      
    } finally {
      loading.value = false
    }
  }

  const deleteSelected = async () => {
    if (selectedSuppliers.value.length === 0) return
    
    const confirmed = confirm(`Are you sure you want to delete ${selectedSuppliers.value.length} supplier(s)?`)
    if (!confirmed) return

    loading.value = true
    error.value = null
    
    try {
      // Delete each selected supplier
      const deletePromises = selectedSuppliers.value.map(id => 
        api.delete(`/suppliers/${id}/`)
      )
      
      await Promise.all(deletePromises)
      
      // Remove from local state
      suppliers.value = suppliers.value.filter(s => !selectedSuppliers.value.includes(s.id))
      
      const count = selectedSuppliers.value.length
      selectedSuppliers.value = []
      
      successMessage.value = `Successfully deleted ${count} supplier(s)`
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
      
      return { success: true }
      
    } catch (err) {
      console.error('Error deleting suppliers:', err)
      
      let errorMessage = 'Failed to delete some suppliers'
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error
      }
      
      error.value = errorMessage
      
      return { success: false, error: errorMessage }
      
    } finally {
      loading.value = false
    }
  }

  const updateReportData = () => {
    reportData.activeOrdersCount = suppliers.value.filter(
      s => s.purchaseOrders > 0 && s.status === 'active'
    ).length
    
    reportData.topSuppliersCount = suppliers.value.filter(
      s => s.purchaseOrders >= 10
    ).length
  }

  const clearFilters = () => {
    filters.type = 'all'
    filters.status = 'all'
    filters.order = 'all'
    filters.search = ''
  }

  const applyFilters = () => {
    // Client-side filtering is handled by computed property
    // But you could also call fetchSuppliers() to do server-side filtering
    updateReportData()
  }

  const refreshData = async () => {
    successMessage.value = null
    await fetchSuppliers(pagination.value.current_page)
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
    pagination,
    
    // Computed
    filteredSuppliers,
    
    // Methods
    fetchSuppliers,
    addSupplier,
    updateSupplier,
    deleteSupplier,
    deleteSelected,
    clearFilters,
    applyFilters,
    refreshData,
    
    // Utilities
    getStatusBadgeClass,
    formatStatus,
    getShortAddress
  }
}