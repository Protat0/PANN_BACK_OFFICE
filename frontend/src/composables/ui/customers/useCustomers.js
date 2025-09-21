// composables/ui/customers/useCustomers.js
import { ref, computed, readonly, nextTick } from 'vue'
import CustomerApiService from '@/services/apiCustomers.js'

export function useCustomers() {
  // Reactive state
  const customers = ref([])
  const filteredCustomers = ref([])
  const selectedCustomers = ref([])
  const loading = ref(false)
  const error = ref(null)
  const successMessage = ref(null)

  // Search and filter state
  const searchQuery = ref('')
  const searchMode = ref(false)
  const statusFilter = ref('all')
  const pointsFilter = ref('all')

  // Pagination state
  const currentPage = ref(1)
  const itemsPerPage = ref(10)

  // Modal state
  const modalMode = ref('add') // 'add', 'edit', 'view'
  const showCustomerModal = ref(false)
  const modalCustomer = ref(null)
  const formLoading = ref(false)
  const formError = ref(null)

  // KPI state
  const activeUsersCount = ref('Loading...')
  const monthlyUsersCount = ref('Loading...')
  const dailyUsersCount = ref('Loading...')

  const autoRefreshEnabled = ref(true)
  const countdown = ref(30)
  const connectionLost = ref(false)
  const exporting = ref(false)
  const refreshProgress = ref('')

  // Computed properties
  const allSelected = computed(() => {
    return filteredCustomers.value.length > 0 && 
           selectedCustomers.value.length === filteredCustomers.value.length
  })

  const someSelected = computed(() => {
    return selectedCustomers.value.length > 0 && 
           selectedCustomers.value.length < filteredCustomers.value.length
  })

  const paginatedCustomers = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value
    const end = start + itemsPerPage.value
    return filteredCustomers.value.slice(start, end)
  })

  const totalPages = computed(() => {
    return Math.ceil(filteredCustomers.value.length / itemsPerPage.value)
  })

  const activeCustomers = computed(() => {
    return customers.value.filter(customer => (customer.status || 'active') === 'active')
  })

  const inactiveCustomers = computed(() => {
    return customers.value.filter(customer => customer.status === 'inactive')
  })

  const totalLoyaltyPoints = computed(() => {
    return customers.value.reduce((sum, customer) => sum + (customer.loyalty_points || 0), 0)
  })

  const averageLoyaltyPoints = computed(() => {
    if (customers.value.length === 0) return 0
    return Math.round(totalLoyaltyPoints.value / customers.value.length)
  })

  // Core data fetching methods
  const fetchCustomers = async () => {
    try {
      console.log('Fetching customers from API...')
      const response = await CustomerApiService.getAllCustomers()
      
      // Handle paginated response structure
      if (response && response.customers) {
        customers.value = response.customers || []
        console.log(`Loaded ${customers.value.length} customers`)
      } else if (Array.isArray(response)) {
        // Fallback for direct array response
        customers.value = response
      } else {
        customers.value = []
      }
      
      applyFilters()
    } catch (error) {
      console.error('Error fetching customers:', error)
      error.value = error.message
      customers.value = []
    }
  }

  const refreshData = async () => {
    successMessage.value = null
    await fetchCustomers()
  }

  // KPI data fetching
  const fetchKPIData = async () => {
    try {
      const stats = await CustomerApiService.getCustomerStatistics()
      
      // Extract the values from the stats response
      activeUsersCount.value = stats.active_customers?.toString() || '0'
      monthlyUsersCount.value = stats.monthly_customers?.toString() || '0'
      dailyUsersCount.value = stats.daily_customers?.toString() || '0'
      
    } catch (error) {
      console.error('Failed to load customer statistics:', error)
      activeUsersCount.value = 'Error'
      monthlyUsersCount.value = 'Error'
      dailyUsersCount.value = 'Error'
    }
  }

  // Search and filtering methods
  const toggleSearchMode = () => {
    searchMode.value = !searchMode.value
    
    if (searchMode.value) {
      nextTick(() => {
        // Focus search input when toggled on
        // This would need to be handled in the component
      })
    } else {
      searchQuery.value = ''
      applyFilters()
    }
  }

  const handleSearch = () => {
    applyFilters()
  }

  const clearSearch = () => {
    searchQuery.value = ''
    searchMode.value = false
    applyFilters()
  }

  const applyFilters = () => {
    let filtered = [...customers.value]

    // Apply status filter
    if (statusFilter.value !== 'all') {
      filtered = filtered.filter(customer => 
        (customer.status || 'active') === statusFilter.value
      )
    }

    // Apply points filter
    if (pointsFilter.value !== 'all') {
      filtered = filtered.filter(customer => {
        const points = customer.loyalty_points || 0
        switch (pointsFilter.value) {
          case '0-100':
            return points >= 0 && points <= 100
          case '101-500':
            return points >= 101 && points <= 500
          case '501+':
            return points > 500
          default:
            return true
        }
      })
    }

    // Apply search filter
    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(customer => {
        const fullName = (customer.full_name || '').toLowerCase()
        const email = (customer.email || '').toLowerCase()
        const phone = (customer.phone || '').toLowerCase()
        const address = formatAddress(customer.delivery_address).toLowerCase()
        
        return fullName.includes(query) ||
               email.includes(query) ||
               phone.includes(query) ||
               address.includes(query)
      })
    }

    // Reset to first page when filtering
    currentPage.value = 1
    // Clear selections when filtering
    selectedCustomers.value = []
    filteredCustomers.value = filtered
  }

  const clearFilters = () => {
    statusFilter.value = 'all'
    pointsFilter.value = 'all'
    searchQuery.value = ''
    searchMode.value = false
    applyFilters()
  }

  // Selection methods
  const selectAll = (isChecked) => {
    if (isChecked) {
      selectedCustomers.value = filteredCustomers.value.map(customer => 
        customer._id || customer.customer_id
      )
    } else {
      selectedCustomers.value = []
    }
  }

  const toggleCustomerSelection = (customerId) => {
    const index = selectedCustomers.value.indexOf(customerId)
    if (index > -1) {
      selectedCustomers.value.splice(index, 1)
    } else {
      selectedCustomers.value.push(customerId)
    }
  }

  // CRUD operations
  const createCustomer = async (customerData) => {
    formLoading.value = true
    formError.value = null

    try {
      await CustomerApiService.createCustomer(customerData)
      successMessage.value = `Customer "${customerData.full_name}" created successfully`
      closeCustomerModal()
      await fetchCustomers()
      clearSuccessMessage()
    } catch (error) {
      console.error('Error creating customer:', error)
      formError.value = error.message
    } finally {
      formLoading.value = false
    }
  }

  const updateCustomer = async (customerId, customerData) => {
    formLoading.value = true
    formError.value = null

    try {
      await CustomerApiService.updateCustomer(customerId, customerData)
      successMessage.value = `Customer "${customerData.full_name}" updated successfully`
      closeCustomerModal()
      await fetchCustomers()
      clearSuccessMessage()
    } catch (error) {
      console.error('Error updating customer:', error)
      formError.value = error.message
    } finally {
      formLoading.value = false
    }
  }

  const deleteCustomer = async (customer) => {
    const confirmed = confirm(`Are you sure you want to delete customer "${customer.full_name}"?`)
    if (!confirmed) return

    try {
      await CustomerApiService.deleteCustomer(customer._id)
      successMessage.value = `Customer "${customer.full_name}" deleted successfully`
      await fetchCustomers()
      clearSuccessMessage()
    } catch (error) {
      console.error('Error deleting customer:', error)
      error.value = `Failed to delete customer: ${error.message}`
    }
  }

  const deleteSelectedCustomers = async () => {
    if (selectedCustomers.value.length === 0) return
    
    const confirmed = confirm(`Are you sure you want to delete ${selectedCustomers.value.length} customer(s)?`)
    if (!confirmed) return

    loading.value = true
    let successCount = 0
    let errorCount = 0

    for (const customerId of selectedCustomers.value) {
      try {
        await CustomerApiService.deleteCustomer(customerId)
        successCount++
      } catch (error) {
        console.error(`Error deleting customer ${customerId}:`, error)
        errorCount++
      }
    }

    if (successCount > 0) {
      successMessage.value = `Successfully deleted ${successCount} customer(s)`
      if (errorCount > 0) {
        successMessage.value += ` (${errorCount} failed)`
      }
      selectedCustomers.value = []
      await fetchCustomers()
      clearSuccessMessage()
    } else {
      error.value = 'Failed to delete customers'
    }

    loading.value = false
  }

  // Modal management
  const showAddCustomerModal = () => {
    modalMode.value = 'add'
    modalCustomer.value = null
    showCustomerModal.value = true
  }

  const editCustomer = (customer) => {
    modalMode.value = 'edit'
    modalCustomer.value = customer
    showCustomerModal.value = true
  }

  const viewCustomer = (customer) => {
    modalMode.value = 'view'
    modalCustomer.value = customer
    showCustomerModal.value = true
  }

  const handleEditMode = (customer) => {
    modalMode.value = 'edit'
    modalCustomer.value = customer
    // Modal stays open, just switches mode
  }

  const closeCustomerModal = () => {
    showCustomerModal.value = false
    modalMode.value = 'add'
    modalCustomer.value = null
    formError.value = null
  }

  const saveCustomer = async (formData, mode = null, customerId = null) => {
    // Use passed parameters or fall back to modal state
    const actualMode = mode || modalMode.value
    const actualCustomerId = customerId || (modalCustomer.value?._id || modalCustomer.value?.customer_id)
    
    console.log('=== SAVE CUSTOMER DEBUG ===')
    console.log('actualMode:', actualMode)
    console.log('actualCustomerId:', actualCustomerId)
    console.log('formData:', formData)
    
    if (actualMode === 'edit' && actualCustomerId) {
      await updateCustomer(actualCustomerId, formData)
    } else {
      await createCustomer(formData)
    }
  }

  // Pagination methods
  const handlePageChange = (page) => {
    currentPage.value = page
  }

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
      currentPage.value = page
    }
  }

  const previousPage = () => {
    goToPage(currentPage.value - 1)
  }

  const nextPage = () => {
    goToPage(currentPage.value + 1)
  }

  // Utility methods
  const exportData = () => {
    const headers = ['ID', 'Name', 'Email', 'Phone', 'Address', 'Loyalty Points', 'Date Created']
    const csvContent = [
      headers.join(','),
      ...filteredCustomers.value.map(customer => [
        customer.customer_id || customer._id,
        customer.full_name,
        customer.email,
        customer.phone || '',
        formatAddress(customer.delivery_address),
        customer.loyalty_points || 0,
        formatDate(customer.date_created)
      ].join(','))
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `customers_${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const formatAddress = (address) => {
    if (!address) return 'N/A'
    if (typeof address === 'string') return address
    
    const parts = []
    if (address.street) parts.push(address.street)
    if (address.city) parts.push(address.city)
    if (address.postal_code) parts.push(address.postal_code)
    
    return parts.length > 0 ? parts.join(', ') : 'N/A'
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  }

  const highlightMatch = (text, query) => {
    if (!query || !text) return text
    
    const regex = new RegExp(`(${query})`, 'gi')
    return text.replace(regex, '<mark style="background-color: var(--secondary-light); color: var(--secondary-dark); padding: 0.125rem 0.25rem; border-radius: 0.25rem;">$1</mark>')
  }

  const clearSuccessMessage = () => {
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
  }

  // Initialize data on composable creation
  const initialize = async () => {
    await Promise.all([
      fetchCustomers(),
      fetchKPIData()
    ])
  }
    const getConnectionStatus = () => {
    if (connectionLost.value) return 'connection-lost'
    if (error.value) return 'connection-unstable'
    if (loading.value) return 'connection-unknown'
    return 'connection-good'
  }

  const getConnectionIcon = () => {
    const status = getConnectionStatus()
    switch (status) {
      case 'connection-good':
        return 'bi bi-wifi'
      case 'connection-unstable':
        return 'bi bi-wifi-1'
      case 'connection-lost':
        return 'bi bi-wifi-off'
      default:
        return 'bi bi-question-circle'
    }
  }

  const getConnectionText = () => {
    const status = getConnectionStatus()
    switch (status) {
      case 'connection-good':
        return 'Connected'
      case 'connection-unstable':
        return 'Unstable'
      case 'connection-lost':
        return 'Disconnected'
      default:
        return 'Unknown'
    }
  }

  const toggleAutoRefresh = () => {
    autoRefreshEnabled.value = !autoRefreshEnabled.value
    // Add your auto-refresh logic here
  }

  const emergencyReconnect = async () => {
    connectionLost.value = false
    await fetchCustomers()
  }

  const deleteSelected = async () => {
    await deleteSelectedCustomers()
  }

  // Return reactive state and methods
  return {
    // Reactive state (readonly to prevent direct mutation)
    customers: readonly(customers),
    filteredCustomers: readonly(filteredCustomers),
    selectedCustomers: readonly(selectedCustomers),
    loading: readonly(loading),
    error: readonly(error),
    successMessage: readonly(successMessage),

    // Search and filter state
    searchQuery,
    searchMode: readonly(searchMode),
    statusFilter,
    pointsFilter,

    // Pagination state
    currentPage: readonly(currentPage),
    itemsPerPage: readonly(itemsPerPage),

    // Modal state
    modalMode: readonly(modalMode),
    showCustomerModal: readonly(showCustomerModal),
    modalCustomer: readonly(modalCustomer),
    formLoading: readonly(formLoading),
    formError: readonly(formError),

    // KPI state
    activeUsersCount: readonly(activeUsersCount),
    monthlyUsersCount: readonly(monthlyUsersCount),
    dailyUsersCount: readonly(dailyUsersCount),

    autoRefreshEnabled: readonly(autoRefreshEnabled),
    countdown: readonly(countdown),
    connectionLost: readonly(connectionLost),
    exporting: readonly(exporting),
    refreshProgress: readonly(refreshProgress),

    // Computed properties
    allSelected,
    someSelected,
    paginatedCustomers,
    totalPages,
    activeCustomers,
    inactiveCustomers,
    totalLoyaltyPoints,
    averageLoyaltyPoints,

    // Methods
    initialize,
    fetchCustomers,
    refreshData,
    fetchKPIData,
    toggleSearchMode,
    handleSearch,
    clearSearch,
    applyFilters,
    clearFilters,
    selectAll,
    toggleCustomerSelection,
    createCustomer,
    updateCustomer,
    deleteCustomer,
    deleteSelectedCustomers,
    showAddCustomerModal,
    editCustomer,
    viewCustomer,
    handleEditMode,
    closeCustomerModal,
    saveCustomer,
    handlePageChange,
    goToPage,
    previousPage,
    nextPage,
    exportData,
    formatAddress,
    formatDate,
    highlightMatch,
    getConnectionStatus,
    getConnectionIcon,
    getConnectionText,
    toggleAutoRefresh,
    emergencyReconnect,
    deleteSelected
  }
}