import { ref, computed, watch } from 'vue'
import productsApiService from '../../../services/apiProducts.js'

export function useReportsModal() {
  // State
  const isVisible = ref(false)
  const loading = ref(false)
  const data = ref([])
  const reportType = ref('low-stock') // 'low-stock' or 'expiring'
  const title = ref('')
  const error = ref(null)

  const categoryStats = ref(null)
  const categoryStatsLoading = ref(false)
  const categoryStatsError = ref(null)

  // Filters
  const filters = ref({
    category: '',
    severity: '',
    search: ''
  })

  // Sorting
  const sortField = ref('')
  const sortOrder = ref('asc')

  // Pagination
  const currentPage = ref(1)
  const itemsPerPage = ref(20)


  // Category Stats API Method
  const fetchCategoryStats = async () => {
    try {
      categoryStatsLoading.value = true
      categoryStatsError.value = null
      
      const response = await fetch('/api/v1/category/stats/')
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        categoryStats.value = result.stats
        return result.stats
      } else {
        throw new Error(result.error || 'Failed to fetch category stats')
      }
    } catch (err) {
      categoryStatsError.value = err.message || 'Failed to fetch category statistics'
      console.error('Error fetching category stats:', err)
      throw err
    } finally {
      categoryStatsLoading.value = false
    }
  }

  
  const refreshCategoryStats = async () => {
    try {
      await fetchCategoryStats()
    } catch (err) {
      console.error('Error refreshing category stats:', err)
    }
  }


  const clearCategoryStatsError = () => {
    categoryStatsError.value = null
  }

  // NEW: Computed properties for easy access to stats
  const totalCategories = computed(() => {
    return categoryStats.value?.category_overview?.total_categories || 0
  })

  const activeCategories = computed(() => {
    return categoryStats.value?.category_overview?.active_categories || 0
  })

  const totalSubcategories = computed(() => {
    return categoryStats.value?.structure_stats?.total_subcategories || 0
  })

  const totalProducts = computed(() => {
    return categoryStats.value?.structure_stats?.total_products || 0
  })

  const avgSubcategoriesPerCategory = computed(() => {
    return categoryStats.value?.structure_stats?.avg_subcategories_per_category || 0
  })

  const avgProductsPerCategory = computed(() => {
    return categoryStats.value?.structure_stats?.avg_products_per_category || 0
  })

  // API Methods
  const fetchLowStockItems = async (params = {}) => {
    try {
      setLoading(true)
      error.value = null
      
      const response = await productsApiService.getLowStockProducts(params)
      updateData(response || [])

      return response
    } catch (err) {
      error.value = err.message || 'Failed to fetch low stock items'
      console.error('Error fetching low stock items:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchExpiringItems = async (params = {}) => {
    try {
      setLoading(true)
      error.value = null
      
      // Default to 30 days ahead if not specified
      const queryParams = {
        days_ahead: 30,
        ...params
      }
      
      const response = await productsApiService.getExpiringProducts(queryParams)
      updateData(response || [])

      return response
    } catch (err) {
      error.value = err.message || 'Failed to fetch expiring items'
      console.error('Error fetching expiring items:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const refreshReportData = async () => {
    try {
      if (reportType.value === 'low-stock') {
        await fetchLowStockItems()
      } else if (reportType.value === 'expiring') {
        await fetchExpiringItems()
      }
    } catch (err) {
      console.error('Error refreshing report data:', err)
      throw err
    }
  }

  // Enhanced Modal Actions
  const showModal = async (type, modalTitle, modalData = null, autoFetch = true) => {
    reportType.value = type
    title.value = modalTitle
    isVisible.value = true
    resetFilters()
    
    if (modalData) {
      // Use provided data
      updateData(modalData)
    } else if (autoFetch) {
      // Fetch data automatically
      try {
        if (type === 'low-stock') {
          await fetchLowStockItems()
        } else if (type === 'expiring') {
          await fetchExpiringItems()
        }
      } catch (err) {
        console.error('Error auto-fetching data for modal:', err)
      }
    }
  }

  const showLowStockModal = async (params = {}) => {
    await showModal('low-stock', 'Low Stock Report', null, true)
    if (Object.keys(params).length > 0) {
      await fetchLowStockItems(params)
    }
  }

  const showExpiringModal = async (params = {}) => {
    await showModal('expiring', 'Expiring Products Report', null, true)
    if (Object.keys(params).length > 0) {
      await fetchExpiringItems(params)
    }
  }

  const hideModal = () => {
    isVisible.value = false
    loading.value = false
    error.value = null
  }

  const setLoading = (state) => {
    loading.value = state
  }

  const updateData = (newData) => {
    data.value = Array.isArray(newData) ? newData : []
    currentPage.value = 1
  }

  const clearError = () => {
    error.value = null
  }

  // Filter and Sort Logic
  const resetFilters = () => {
    filters.value = {
      category: '',
      severity: '',
      search: ''
    }
    sortField.value = ''
    sortOrder.value = 'asc'
    currentPage.value = 1
  }

  const applyFilters = () => {
    currentPage.value = 1
  }

  const sortBy = (field) => {
    if (sortField.value === field) {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortField.value = field
      sortOrder.value = 'asc'
    }
  }

  // Data Processing
  const getItemSeverity = (item) => {
    if (reportType.value === 'low-stock') {
      if (item.stock === 0) return 'critical'
      if (item.stock <= (item.low_stock_threshold || 0)) return 'warning'
      return 'normal'
    } else {
      if (!item.expiry_date) return 'normal'
      const expiry = new Date(item.expiry_date)
      const today = new Date()
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      
      if (daysUntilExpiry < 0) return 'critical'
      if (daysUntilExpiry <= 7) return 'warning'
      return 'normal'
    }
  }

  const processedData = computed(() => {
    let filtered = [...data.value]

    // Category filter
    if (filters.value.category) {
      filtered = filtered.filter(item => item.category_id === filters.value.category)
    }

    // Severity filter
    if (filters.value.severity) {
      filtered = filtered.filter(item => getItemSeverity(item) === filters.value.severity)
    }

    // Search filter
    if (filters.value.search) {
      const search = filters.value.search.toLowerCase()
      filtered = filtered.filter(item => 
        item.product_name?.toLowerCase().includes(search) ||
        item.SKU?.toLowerCase().includes(search)
      )
    }

    // Apply sorting
    if (sortField.value) {
      filtered.sort((a, b) => {
        let aVal = a[sortField.value]
        let bVal = b[sortField.value]
        
        if (sortField.value === 'expiry_date') {
          aVal = new Date(aVal)
          bVal = new Date(bVal)
        }
        
        if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1
        if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1
        return 0
      })
    }

    return filtered
  })

  const totalPages = computed(() => {
    return Math.ceil(processedData.value.length / itemsPerPage.value)
  })

  const paginatedData = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value
    const end = start + itemsPerPage.value
    return processedData.value.slice(start, end)
  })

  // Summary Calculations
  const getCriticalStockCount = () => {
    return data.value.filter(item => item.stock === 0).length
  }

  const getLowStockCount = () => {
    return data.value.filter(item => item.stock > 0 && item.stock <= (item.low_stock_threshold || 0)).length
  }

  const getExpiredCount = () => {
    return data.value.filter(item => {
      if (!item.expiry_date) return false
      const expiry = new Date(item.expiry_date)
      return expiry < new Date()
    }).length
  }

  const getExpiringSoonCount = () => {
    return data.value.filter(item => {
      if (!item.expiry_date) return false
      const expiry = new Date(item.expiry_date)
      const today = new Date()
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      return daysUntilExpiry >= 0 && daysUntilExpiry <= 7
    }).length
  }

  const getTotalValue = () => {
    const total = data.value.reduce((sum, item) => {
      return sum + (item.stock * (item.cost_price || 0))
    }, 0)
    return total.toFixed(2)
  }

  // Utility Functions
  const getReportTypeLabel = () => {
    return reportType.value === 'low-stock' ? 'Inventory Alert' : 'Expiry Alert'
  }

  const getRowClass = (item) => {
    const severity = getItemSeverity(item)
    return `severity-${severity}`
  }

  const getShortage = (item) => {
    return Math.max(0, (item.low_stock_threshold || 0) - item.stock)
  }

  const getItemValue = (item) => {
    const value = item.stock * (item.cost_price || 0)
    return value.toFixed(2)
  }

  const getCategoryName = (categoryId) => {
    const categories = {
      'noodles': 'Noodles',
      'drinks': 'Drinks',
      'toppings': 'Toppings'
    }
    return categories[categoryId] || categoryId || 'Unknown'
  }

  const getCategorySlug = (categoryId) => {
    return categoryId?.toLowerCase().replace(/\s+/g, '-') || 'unknown'
  }

  const getStockClass = (item) => {
    if (item.stock === 0) return 'stock-critical'
    if (item.stock <= (item.low_stock_threshold || 0)) return 'stock-warning'
    return 'stock-normal'
  }

  const getExpiryClass = (expiryDate) => {
    if (!expiryDate) return ''
    const today = new Date()
    const expiry = new Date(expiryDate)
    const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
    
    if (daysUntilExpiry < 0) return 'expired'
    if (daysUntilExpiry <= 7) return 'expiring-soon'
    if (daysUntilExpiry <= 30) return 'expiring-month'
    return ''
  }

  const getDaysClass = (expiryDate) => {
    if (!expiryDate) return ''
    const today = new Date()
    const expiry = new Date(expiryDate)
    const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
    
    if (daysUntilExpiry < 0) return 'days-expired'
    if (daysUntilExpiry <= 7) return 'days-critical'
    if (daysUntilExpiry <= 30) return 'days-warning'
    return 'days-normal'
  }

  const getDaysUntilExpiry = (expiryDate) => {
    if (!expiryDate) return 'N/A'
    
    const today = new Date()
    const expiry = new Date(expiryDate)
    const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
    
    if (daysUntilExpiry < 0) return `${Math.abs(daysUntilExpiry)} days ago`
    if (daysUntilExpiry === 0) return 'Today'
    if (daysUntilExpiry === 1) return 'Tomorrow'
    return `${daysUntilExpiry} days`
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    } catch (error) {
      console.error('Error formatting date:', error)
      return 'Invalid Date'
    }
  }

  const formatDateTime = (date) => {
    try {
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch (error) {
      console.error('Error formatting datetime:', error)
      return 'Invalid Date'
    }
  }

  // Export Function with CSV generation
  const generateExportData = () => {
    return {
      type: reportType.value,
      title: title.value,
      data: processedData.value,
      filters: filters.value,
      generatedAt: new Date()
    }
  }

  const exportToCSV = () => {
    const exportData = generateExportData()
    const headers = getCSVHeaders()
    const rows = exportData.data.map(item => formatRowForCSV(item))
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    
    link.setAttribute('href', url)
    link.setAttribute('download', `${exportData.type}-report-${formatDateForFilename(new Date())}.csv`)
    link.style.visibility = 'hidden'
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const getCSVHeaders = () => {
    const baseHeaders = ['Product Name', 'SKU', 'Category', 'Current Stock']
    
    if (reportType.value === 'low-stock') {
      return [...baseHeaders, 'Low Stock Threshold', 'Shortage', 'Value Impact']
    } else {
      return [...baseHeaders, 'Expiry Date', 'Days Until Expiry', 'Value Impact']
    }
  }

  const formatRowForCSV = (item) => {
    const baseRow = [
      `"${item.product_name || ''}"`,
      `"${item.SKU || ''}"`,
      `"${getCategoryName(item.category_id)}"`,
      item.stock || 0
    ]
    
    if (reportType.value === 'low-stock') {
      return [
        ...baseRow,
        item.low_stock_threshold || 0,
        getShortage(item),
        getItemValue(item)
      ]
    } else {
      return [
        ...baseRow,
        `"${formatDate(item.expiry_date)}"`,
        `"${getDaysUntilExpiry(item.expiry_date)}"`,
        getItemValue(item)
      ]
    }
  }

  const formatDateForFilename = (date) => {
    return date.toISOString().slice(0, 10)
  }

  // Watch for data changes to reset pagination
  watch(data, () => {
    currentPage.value = 1
  }, { deep: true })

  // Watch for modal visibility to reset filters
  watch(isVisible, (newVal) => {
    if (newVal) {
      resetFilters()
    }
  })

  return {
    // State
    isVisible,
    loading,
    data,
    reportType,
    title,
    error,
    filters,
    sortField,
    sortOrder,
    currentPage,
    itemsPerPage,

    // Computed
    processedData,
    totalPages,
    paginatedData,
    
    //Category Stats Computed
    totalCategories,
    activeCategories,
    totalSubcategories,
    totalProducts,
    avgSubcategoriesPerCategory,
    avgProductsPerCategory,

    //Category Stats State
    categoryStats,
    categoryStatsLoading,
    categoryStatsError,

    // API Actions
    fetchLowStockItems,
    fetchExpiringItems,
    refreshReportData,

    //Category Stats Actions
    fetchCategoryStats,
    refreshCategoryStats,
    clearCategoryStatsError,

    // Modal Actions
    showModal,
    showLowStockModal,
    showExpiringModal,
    hideModal,
    setLoading,
    updateData,
    clearError,
    resetFilters,
    applyFilters,
    sortBy,

    // Summary Methods
    getCriticalStockCount,
    getLowStockCount,
    getExpiredCount,
    getExpiringSoonCount,
    getTotalValue,

    // Utility Methods
    getReportTypeLabel,
    getItemSeverity,
    getRowClass,
    getShortage,
    getItemValue,
    getCategoryName,
    getCategorySlug,
    getStockClass,
    getExpiryClass,
    getDaysClass,
    getDaysUntilExpiry,
    formatDate,
    formatDateTime,
    generateExportData,
    exportToCSV
  }
}