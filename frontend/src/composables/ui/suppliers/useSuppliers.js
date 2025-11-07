// composables/ui/suppliers/useSuppliers.js
import { ref, computed, reactive } from 'vue'
import axios from 'axios'
import { useToast } from '@/composables/ui/useToast'

// Configure axios base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// Create axios instance with auth token
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || localStorage.getItem('authToken') || sessionStorage.getItem('authToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export function useSuppliers() {
  const { success: showSuccess, error: showError } = useToast()
  // Reactive state
  const suppliers = ref([])
  const allBatches = ref([])
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

  // Calculate purchase orders count by grouping batches (same logic as SupplierDetails.vue)
  const calculatePurchaseOrdersCount = (batches) => {
    if (!batches || !Array.isArray(batches) || batches.length === 0) {
      return 0
    }
    
    // Group batches by date
    const batchesByDate = {}
    batches.forEach(batch => {
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
    
    return Object.keys(batchesByDate).length
  }

  // Helper functions for supplier stats
  const getReceiptStatus = (batches) => {
    if (!batches || batches.length === 0) return 'Unknown'
    
    const allPending = batches.every(b => b.status === 'pending')
    const allActive = batches.every(b => b.status === 'active')
    const allInactive = batches.every(b => b.status === 'inactive')
    const hasPending = batches.some(b => b.status === 'pending')
    
    if (allPending) return 'Pending Delivery'
    if (allActive) return 'Received'
    if (allInactive) return 'Depleted'
    if (hasPending) return 'Partially Received'
    
    return 'Mixed Status'
  }

  const getActiveOrdersCount = (batches) => {
    if (!batches || batches.length === 0) return 0
    
    // Group batches by date to create orders
    const batchesByDate = {}
    batches.forEach(batch => {
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
    
    // Convert to orders and count active ones
    const orders = Object.entries(batchesByDate).map(([date, batches]) => ({
      status: getReceiptStatus(batches)
    }))
    
    // Count orders that are currently pending
    return orders.filter(order => 
      order.status === 'Pending Delivery' || order.status === 'Partially Received'
    ).length
  }

  const getTotalSpent = (batches) => {
    if (!batches || batches.length === 0) return 0
    
    // Group batches by date to create orders
    const batchesByDate = {}
    batches.forEach(batch => {
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
    
    // Convert to orders and calculate total spent on received orders
    const orders = Object.entries(batchesByDate).map(([date, batches]) => {
      const totalCost = batches.reduce((sum, b) => sum + ((b.cost_price || 0) * (b.quantity_received || 0)), 0)
      return {
        status: getReceiptStatus(batches),
        total: totalCost
      }
    })
    
    return orders
      .filter(order => order.status === 'Received')
      .reduce((total, order) => total + order.total, 0)
  }

  const getDaysActive = (createdAt) => {
    if (!createdAt) return 0
    const createdDate = new Date(createdAt)
    const today = new Date()
    const diffTime = Math.abs(today - createdDate)
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  }

  // Get active orders for modal with product enrichment
  const getActiveOrdersForModal = async () => {
    const allActiveOrders = []
    
    for (let i = 0; i < suppliers.value.length; i++) {
      const supplier = suppliers.value[i]
      const supplierBatches = allBatches.value.filter(batch => batch.supplier_id === supplier.id)
      
      if (supplierBatches.length > 0) {
        // Group batches by date
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
        
        // Enrich batches with product details
        const enrichedBatchesByDate = {}
        for (const [dateKey, batches] of Object.entries(batchesByDate)) {
          enrichedBatchesByDate[dateKey] = await Promise.all(
            batches.map(async (batch) => {
              try {
                if (batch.product_id) {
                  const productResponse = await api.get(`/products/${batch.product_id}/`)
                  
                  const product = productResponse.data.data
                  
                  if (product) {
                    const enrichedBatch = {
                      ...batch,
                      product_name: product.product_name || product.name || batch.product_id || 'Unknown Product',
                      category_id: product.category_id || '',
                      category_name: product.category_name || '',
                      subcategory_name: product.subcategory_name || ''
                    }
                    return enrichedBatch
                  } else {
                    console.warn(`⚠️ No product data returned for ${batch.product_id}`)
                  }
                } else {
                  console.warn(`⚠️ No product_id found in batch:`, batch)
                }
                return batch
              } catch (err) {
                console.error(`❌ Failed to fetch product details for batch ${batch._id}:`, err)
                console.error(`❌ Error details:`, err.response?.data || err.message)
                return batch
              }
            })
          )
        }
        
        // Convert grouped batches to orders using enriched data
        Object.entries(enrichedBatchesByDate).forEach(([date, enrichedBatches]) => {
          const totalCost = enrichedBatches.reduce((sum, b) => sum + ((b.cost_price || 0) * (b.quantity_received || 0)), 0)
          
          let receiptId = `SR-${date.replace(/-/g, '')}`
          const firstBatchNotes = enrichedBatches[0].notes || ''
          const receiptMatch = firstBatchNotes.match(/Receipt:\s*([^\|]+)/)
          if (receiptMatch) {
            receiptId = receiptMatch[1].trim()
          }
          
          const firstBatch = enrichedBatches[0]
          const expectedDate = firstBatch.expected_delivery_date ? 
            (typeof firstBatch.expected_delivery_date === 'string' ? firstBatch.expected_delivery_date.split('T')[0] : new Date(firstBatch.expected_delivery_date).toISOString().split('T')[0]) : 
            date
          const receivedDate = firstBatch.date_received ? 
            (typeof firstBatch.date_received === 'string' ? firstBatch.date_received.split('T')[0] : new Date(firstBatch.date_received).toISOString().split('T')[0]) : 
            null
          
          // Determine order status
          const allPending = enrichedBatches.every(b => b.status === 'pending')
          const allActive = enrichedBatches.every(b => b.status === 'active')
          const allInactive = enrichedBatches.every(b => b.status === 'inactive')
          const hasPending = enrichedBatches.some(b => b.status === 'pending')
          
          let orderStatus
          if (allPending) orderStatus = 'Pending Delivery'
          else if (allActive) orderStatus = 'Received'
          else if (allInactive) orderStatus = 'Depleted'
          else if (hasPending) orderStatus = 'Partially Received'
          else orderStatus = 'Mixed Status'
          
          // Only include active orders
          if (orderStatus === 'Pending Delivery' || orderStatus === 'Partially Received') {
            allActiveOrders.push({
              id: receiptId,
              supplier: supplier.name,
              supplierId: supplier.id,
              supplierEmail: supplier.email || 'N/A',
              orderDate: firstBatch.created_at ? firstBatch.created_at.split('T')[0] : date,
              expectedDelivery: expectedDate,
              deliveredDate: receivedDate,
              totalAmount: totalCost,
              status: orderStatus,
              items: enrichedBatches.map(batch => {
                const item = {
                  name: batch.product_name || batch.name || batch.product_id || 'Unknown Product',
                  product_name: batch.product_name || batch.name || 'Unknown Product',
                  product_id: batch.product_id,
                  quantity: batch.quantity_received,
                  unitPrice: batch.cost_price || 0,
                  totalPrice: (batch.cost_price || 0) * (batch.quantity_received || 0),
                  batchNumber: batch.batch_number,
                  batchId: batch._id,
                  expiryDate: batch.expiry_date,
                  quantityRemaining: batch.quantity_remaining
                }
                return item
              }),
              description: `Stock receipt with ${enrichedBatches.length} item(s)`,
              notes: firstBatchNotes
            })
          }
        })
      }
    }
    
    return allActiveOrders.sort((a, b) => new Date(b.orderDate) - new Date(a.orderDate))
  }

  // Transform backend data to frontend format
  const transformSupplier = (backendSupplier, batchesCount = 0, supplierBatches = []) => {
    const activeOrders = getActiveOrdersCount(supplierBatches)
    const totalSpent = getTotalSpent(supplierBatches)
    const daysActive = getDaysActive(backendSupplier.created_at)
    
    return {
      id: backendSupplier._id,
      name: backendSupplier.supplier_name,
      email: backendSupplier.email || '',
      phone: backendSupplier.phone_number || '',
      address: backendSupplier.address || '',
      contactPerson: backendSupplier.contact_person || '',
      purchaseOrders: batchesCount,
      activeOrders: activeOrders,
      totalSpent: totalSpent,
      daysActive: daysActive,
      status: backendSupplier.isDeleted ? 'inactive' : 'active',
      type: backendSupplier.type || 'food',
      isFavorite: backendSupplier.isFavorite || false,
      createdAt: backendSupplier.created_at,
      updatedAt: backendSupplier.updated_at,
      raw: backendSupplier
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

    // Sort: Favorites first, then by name alphabetically
    filtered.sort((a, b) => {
      // First, sort by favorite status (favorites first)
      if (a.isFavorite && !b.isFavorite) return -1
      if (!a.isFavorite && b.isFavorite) return 1
      
      // If both have same favorite status, sort alphabetically by name
      return (a.name || '').localeCompare(b.name || '')
    })

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

      if (filters.search.trim()) {
        params.search = filters.search.trim()
      }

      const response = await api.get('/suppliers/', { params })
      const backendSuppliers = response.data.suppliers
      
      // Fetch all batches for purchase orders calculation
      let fetchedBatches = []
      try {
        const batchesResponse = await api.get('/batches/', { params: { per_page: 1000 } })
        
        if (batchesResponse.data && batchesResponse.data.success && Array.isArray(batchesResponse.data.data)) {
          fetchedBatches = batchesResponse.data.data
        } else if (batchesResponse.data && Array.isArray(batchesResponse.data)) {
          fetchedBatches = batchesResponse.data
        } else if (batchesResponse.data && Array.isArray(batchesResponse.data.batches)) {
          fetchedBatches = batchesResponse.data.batches
        }
      } catch (batchesError) {
        console.warn('Failed to fetch batches:', batchesError)
      }
      
      allBatches.value = fetchedBatches
      
      // Group batches by supplier_id for efficient lookup
      const batchesBySupplier = {}
      fetchedBatches.forEach(batch => {
        const supplierId = batch.supplier_id
        if (supplierId) {
          if (!batchesBySupplier[supplierId]) {
            batchesBySupplier[supplierId] = []
          }
          batchesBySupplier[supplierId].push(batch)
        }
      })
      
      // Transform suppliers with calculated stats
      const transformedSuppliers = backendSuppliers.map(backendSupplier => {
        const supplierBatches = batchesBySupplier[backendSupplier._id] || []
        const purchaseOrdersCount = calculatePurchaseOrdersCount(supplierBatches)
        return transformSupplier(backendSupplier, purchaseOrdersCount, supplierBatches)
      })
      
      suppliers.value = transformedSuppliers
      pagination.value = response.data.pagination
      updateReportData()
      
    } catch (err) {
      console.error('Error fetching suppliers:', err)
      
      if (err.response) {
        error.value = err.response.data.error || `Failed to load suppliers: ${err.response.statusText}`
      } else if (err.request) {
        error.value = 'Cannot connect to server. Please check your connection.'
      } else {
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
      const backendData = {
        supplier_name: supplierData.name,
        email: supplierData.email,
        phone_number: supplierData.phone,
        address: supplierData.address,
        contact_person: supplierData.contactPerson,
        type: supplierData.type || 'food'
      }

      const response = await api.post('/suppliers/', backendData)
      const newSupplier = transformSupplier(response.data)
      suppliers.value.unshift(newSupplier)
      
      const message = `Supplier "${newSupplier.name}" added successfully`
      successMessage.value = message
      setTimeout(() => { successMessage.value = null }, 3000)
      showSuccess(message)
      
      return { success: true, supplier: newSupplier }
      
    } catch (err) {
      console.error('Error adding supplier:', err)
      const errorMessage = err.response?.data?.error || 'Failed to add supplier'
      error.value = errorMessage
      showError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  const updateSupplier = async (supplierId, supplierData) => {
    loading.value = true
    error.value = null
    
    try {
      const backendData = {
        supplier_name: supplierData.name,
        email: supplierData.email,
        phone_number: supplierData.phone,
        address: supplierData.address,
        contact_person: supplierData.contactPerson,
        type: supplierData.type
      }

      const response = await api.put(`/suppliers/${supplierId}/`, backendData)
      const updatedSupplier = transformSupplier(response.data)
      const index = suppliers.value.findIndex(s => s.id === supplierId)
      
      if (index !== -1) {
        suppliers.value[index] = updatedSupplier
      }
      
      const message = `Supplier "${updatedSupplier.name}" updated successfully`
      successMessage.value = message
      setTimeout(() => { successMessage.value = null }, 3000)
      showSuccess(message)
      
      return { success: true, supplier: updatedSupplier }
      
    } catch (err) {
      console.error('Error updating supplier:', err)
      const errorMessage = err.response?.data?.error || 'Failed to update supplier'
      error.value = errorMessage
      showError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  const toggleFavorite = async (supplier) => {
    const previousFavoriteState = supplier.isFavorite
    supplier.isFavorite = !supplier.isFavorite
    
    try {
      await api.put(`/suppliers/${supplier.id}/`, {
        isFavorite: supplier.isFavorite
      })
      
      // Update the supplier in the list
      const index = suppliers.value.findIndex(s => s.id === supplier.id)
      if (index !== -1) {
        suppliers.value[index].isFavorite = supplier.isFavorite
      }
      
      return { success: true }
      
    } catch (err) {
      // Revert on error
      supplier.isFavorite = previousFavoriteState
      console.error('Error updating favorite status:', err)
      const errorMessage = err.response?.data?.error || 'Failed to update favorite status'
      error.value = errorMessage
      return { success: false, error: errorMessage }
    }
  }

  const deleteSupplier = async (supplier) => {
    const confirmed = confirm(`Are you sure you want to delete "${supplier.name}"?`)
    if (!confirmed) return { success: false, cancelled: true }

    loading.value = true
    error.value = null
    
    try {
      await api.delete(`/suppliers/${supplier.id}/`)
      suppliers.value = suppliers.value.filter(s => s.id !== supplier.id)
      
      const message = `Supplier "${supplier.name}" deleted successfully`
      successMessage.value = message
      setTimeout(() => { successMessage.value = null }, 3000)
      showSuccess(message)
      
      return { success: true }
      
    } catch (err) {
      console.error('Error deleting supplier:', err)
      const errorMessage = err.response?.data?.error || 'Failed to delete supplier'
      error.value = errorMessage
      showError(errorMessage)
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
      const deletePromises = selectedSuppliers.value.map(id => 
        api.delete(`/suppliers/${id}/`)
      )
      
      await Promise.all(deletePromises)
      suppliers.value = suppliers.value.filter(s => !selectedSuppliers.value.includes(s))
      
      const count = selectedSuppliers.value.length
      selectedSuppliers.value = []
      
      const message = `Successfully deleted ${count} supplier(s)`
      successMessage.value = message
      setTimeout(() => { successMessage.value = null }, 3000)
      showSuccess(message)
      
      return { success: true }
      
    } catch (err) {
      console.error('Error deleting suppliers:', err)
      const errorMessage = err.response?.data?.error || 'Failed to delete some suppliers'
      error.value = errorMessage
      showError(errorMessage)
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
    updateReportData()
  }

  const refreshData = async () => {
    try {
      successMessage.value = null
      error.value = null
      await fetchSuppliers(pagination.value?.current_page || 1)
    } catch (err) {
      console.error('Error refreshing data:', err)
      error.value = err.message || 'Failed to refresh data'
    }
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
    toggleFavorite,
    deleteSupplier,
    deleteSelected,
    clearFilters,
    applyFilters,
    refreshData,
    getActiveOrdersForModal,
    
    // Utilities
    getStatusBadgeClass,
    formatStatus,
    getShortAddress
  }
}