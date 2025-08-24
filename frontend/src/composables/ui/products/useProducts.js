// composables/useProducts.js
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import productsApiService from '@/services/apiProducts.js'
import categoryApiService from '@/services/apiCategory.js'
import { useRouter } from 'vue-router'

export function useProducts() {
  const router = useRouter()
  
  // State
  const products = ref([])
  const filteredProducts = ref([])
  const selectedProducts = ref([])
  const categories = ref([])
  const loading = ref(false)
  const error = ref(null)
  const successMessage = ref(null)
  
  // UI State
  const showAddDropdown = ref(false)
  const searchMode = ref(false)
  const showColumnFilter = ref(false)
  
  // Pagination
  const currentPage = ref(1)
  const itemsPerPage = ref(10)
  
  // Report data
  const lowStockCount = ref(0)
  const expiringCount = ref(0)
  
  // Column visibility
  const visibleColumns = ref({
    sku: true,
    category: true,
    stock: true,
    costPrice: false,
    sellingPrice: true,
    status: true,
    expiryDate: false
  })
  
  // Filters
  const categoryFilter = ref('all')
  const stockFilter = ref('all')
  const searchFilter = ref('')
  
  // Computed
  const paginatedProducts = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value
    const end = start + itemsPerPage.value
    return filteredProducts.value.slice(start, end)
  })
  
  const allSelected = computed(() => {
    return paginatedProducts.value.length > 0 && 
           selectedProducts.value.length === paginatedProducts.value.length
  })
  
  const someSelected = computed(() => {
    return selectedProducts.value.length > 0 && 
           selectedProducts.value.length < paginatedProducts.value.length
  })
  
  // Methods
  const fetchCategories = async () => {
    try {
      console.log('Fetching categories for product enrichment...')
      const response = await categoryApiService.getAllCategories()
      
      // Handle different response formats
      if (Array.isArray(response)) {
        categories.value = response
      } else if (response.categories) {
        categories.value = response.categories
      } else {
        categories.value = []
      }
      
      console.log(`Fetched ${categories.value.length} categories:`, categories.value.map(c => c.category_name))
    } catch (err) {
      console.error('Error fetching categories:', err)
      categories.value = [] // Fallback to empty array
    }
  }
  
  const fetchProducts = async () => {
    loading.value = true
    error.value = null
    
    try {
      const data = await productsApiService.getProducts()
      
      if (data.results) {
        products.value = data.results
      } else if (Array.isArray(data)) {
        products.value = data
      } else {
        products.value = data.products || []
      }
      
      // ALWAYS enrich products with category info after fetching categories
      await enrichProductsWithCategoryNames()
      
      applyFilters()
      await fetchReportCounts()
    } catch (err) {
      console.error('Error fetching products:', err)
      error.value = `Failed to load products: ${err.message}`
    } finally {
      loading.value = false
    }
  }

  const enrichProductsWithCategoryNames = async () => {
    try {
      // Ensure we have categories first
      if (categories.value.length === 0) {
        await fetchCategories()
      }
      
      // Create a map for faster lookups
      const categoryMap = new Map(
        categories.value.map(cat => [cat._id, cat.category_name])
      )
      
      // Enrich each product with category name
      products.value = products.value.map(product => ({
        ...product,
        category_name: categoryMap.get(product.category_id) || 'Uncategorized'
      }))
      
      console.log('Products enriched with category names:', products.value.slice(0, 2))
    } catch (err) {
      console.error('Error enriching products with category names:', err)
      // Fallback: add 'Uncategorized' to all products without breaking the flow
      products.value = products.value.map(product => ({
        ...product,
        category_name: product.category_name || 'Uncategorized'
      }))
    }
  }
  
  const fetchReportCounts = async () => {
    try {
      const lowStockData = await productsApiService.getLowStockProducts()
      lowStockCount.value = Array.isArray(lowStockData) ? lowStockData.length : (lowStockData.count || 0)
      
      const expiringData = await productsApiService.getExpiringProducts({ days_ahead: 30 })
      expiringCount.value = Array.isArray(expiringData) ? expiringData.length : (expiringData.count || 0)
    } catch (err) {
      console.error('Error fetching report counts:', err)
    }
  }
  
  const applyFilters = () => {
    let filtered = [...products.value]
    
    if (categoryFilter.value !== 'all') {
      filtered = filtered.filter(product => {
        // Handle both category_id and enriched category_name
        return product.category_id === categoryFilter.value || 
               product.category_name?.toLowerCase() === categoryFilter.value.toLowerCase()
      })
    }
    
    if (stockFilter.value !== 'all') {
      if (stockFilter.value === 'out-of-stock') {
        filtered = filtered.filter(product => product.stock === 0)
      } else if (stockFilter.value === 'low-stock') {
        filtered = filtered.filter(product => 
          product.stock > 0 && product.stock <= product.low_stock_threshold
        )
      } else if (stockFilter.value === 'in-stock') {
        filtered = filtered.filter(product => product.stock > product.low_stock_threshold)
      }
    }
    
    if (searchFilter.value.trim()) {
      const search = searchFilter.value.toLowerCase()
      filtered = filtered.filter(product => 
        product.product_name?.toLowerCase().includes(search) ||
        product.SKU?.toLowerCase().includes(search) ||
        product._id?.toLowerCase().includes(search) ||
        product.category_name?.toLowerCase().includes(search)
      )
    }
    
    currentPage.value = 1
    selectedProducts.value = []
    filteredProducts.value = filtered
  }
  
  const clearFilters = () => {
    categoryFilter.value = 'all'
    stockFilter.value = 'all'
    searchFilter.value = ''
    searchMode.value = false
    applyFilters()
  }
  
  const refreshData = async () => {
    successMessage.value = null
    await fetchProducts()
  }
  
  const selectAll = (checked) => {
    if (checked) {
      selectedProducts.value = paginatedProducts.value.map(product => product._id)
    } else {
      selectedProducts.value = []
    }
  }
  
  const deleteSelected = async () => {
    if (selectedProducts.value.length === 0) return
    
    const confirmed = confirm(`Are you sure you want to delete ${selectedProducts.value.length} product(s)?`)
    if (!confirmed) return
    
    loading.value = true
    
    try {
      // Delete products one by one since bulk delete might not be available
      for (const productId of selectedProducts.value) {
        await productsApiService.deleteProduct(productId)
      }
      
      successMessage.value = `Successfully deleted ${selectedProducts.value.length} product(s)`
      selectedProducts.value = []
      await fetchProducts()
    } catch (err) {
      console.error('Error deleting products:', err)
      error.value = `Failed to delete products: ${err.message}`
    } finally {
      loading.value = false
    }
    
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
  }
  
  const deleteProduct = async (product) => {
    const confirmed = confirm(`Are you sure you want to delete "${product.product_name}"?`)
    if (!confirmed) return
    
    try {
      await productsApiService.deleteProduct(product._id)
      successMessage.value = `Product "${product.product_name}" deleted successfully`
      await fetchProducts()
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
    } catch (err) {
      console.error('Error deleting product:', err)
      error.value = `Failed to delete product: ${err.message}`
    }
  }
  
  const toggleProductStatus = async (product) => {
    const newStatus = product.status === 'active' ? 'inactive' : 'active'
    const action = newStatus === 'active' ? 'activate' : 'deactivate'
    
    const confirmed = confirm(`Are you sure you want to ${action} "${product.product_name}"?`)
    if (!confirmed) return
    
    try {
      await productsApiService.updateProduct(product._id, { status: newStatus })
      successMessage.value = `Product "${product.product_name}" ${action}d successfully`
      await fetchProducts()
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
    } catch (err) {
      console.error('Error updating product status:', err)
      error.value = `Failed to ${action} product: ${err.message}`
    }
  }
  
  const exportData = async () => {
    try {
      const blob = await productsApiService.exportProducts({
        format: 'csv',
        filters: {
          category: categoryFilter.value !== 'all' ? categoryFilter.value : undefined,
          stock: stockFilter.value !== 'all' ? stockFilter.value : undefined,
          search: searchFilter.value || undefined
        }
      })
      
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `products_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('API export failed, falling back to client-side export:', err)
      
      // Client-side fallback
      const headers = ['Name', 'SKU', 'Category', 'Price', 'Cost', 'Margin', 'Stock']
      const csvContent = [
        headers.join(','),
        ...filteredProducts.value.map(product => [
          `"${product.product_name}"`,
          product.SKU || '',
          getCategoryName(product.category_id),
          product.selling_price,
          product.cost_price,
          calculateMargin(product.cost_price, product.selling_price),
          product.stock
        ].join(','))
      ].join('\n')
      
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `products_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      window.URL.revokeObjectURL(url)
    }
  }
  
  // UI Methods
  const toggleAddDropdown = (event) => {
    if (event) event.stopPropagation()
    showAddDropdown.value = !showAddDropdown.value
  }
  
  const closeAddDropdown = () => {
    showAddDropdown.value = false
  }
  
  const toggleSearchMode = () => {
    searchMode.value = !searchMode.value
    
    if (!searchMode.value) {
      searchFilter.value = ''
      applyFilters()
    }
  }
  
  const clearSearch = () => {
    searchFilter.value = ''
    searchMode.value = false
    applyFilters()
  }
  
  const toggleColumnFilter = () => {
    showColumnFilter.value = true
  }
  
  const handleColumnChanges = (newColumnSettings) => {
    visibleColumns.value = { ...newColumnSettings }
  }
  
  // Navigation Methods
  const handleSingleProduct = () => {
    closeAddDropdown()
    // Return signal to open modal
    return 'single'
  }
  
  const handleBulkAdd = () => {
    closeAddDropdown()
    router.push('/products/bulk')
  }
  
  const handleImport = () => {
    closeAddDropdown()
    // Return signal to open modal
    return 'import'
  }
  
  // Pagination
  const handlePageChange = (page) => {
    currentPage.value = page
    selectedProducts.value = []
  }
  
  // Formatting Methods
  const getCategoryName = (categoryId) => {
    if (!categoryId) return 'Uncategorized'
    
    // First check if the current product in context already has enriched category_name
    const product = products.value.find(p => p.category_id === categoryId)
    if (product?.category_name) return product.category_name
    
    // Then check our categories array as fallback
    const category = categories.value.find(c => c._id === categoryId)
    if (category) return category.category_name
    
    // Final fallback
    return 'Uncategorized'
  }
  
  const getCategoryBadgeClass = (categoryId) => {
    // You can enhance this based on actual category data
    const categoryName = getCategoryName(categoryId).toLowerCase()
    
    if (categoryName.includes('noodle')) return 'status-info'
    if (categoryName.includes('drink')) return 'status-success'
    if (categoryName.includes('topping')) return 'status-warning'
    
    return 'status-info'
  }
  
  const calculateMargin = (costPrice, sellingPrice) => {
    if (!costPrice || !sellingPrice) return 0
    const margin = ((sellingPrice - costPrice) / sellingPrice) * 100
    return Math.round(margin)
  }
  
  const formatPrice = (price) => {
    return parseFloat(price || 0).toFixed(2)
  }
  
  const formatExpiryDate = (expiryDate) => {
    if (!expiryDate) return '—'
    try {
      const date = new Date(expiryDate)
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
      })
    } catch (err) {
      return '—'
    }
  }
  
  // Style Methods
  const getProductNameClass = (product) => {
    if (product.stock === 0) return 'text-error fw-bold'
    if (product.stock <= product.low_stock_threshold) return 'text-warning fw-semibold'
    return 'text-primary'
  }
  
  const getRowClass = (product) => {
    const classes = []
    
    if (selectedProducts.value.includes(product._id)) {
      classes.push('table-primary')
    }
    
    if (product.status === 'inactive') {
      classes.push('text-muted')
    }
    
    return classes.join(' ')
  }
  
  const getStockDisplayClass = (product) => {
    if (product.stock === 0) return 'text-error fw-bold'
    if (product.stock <= product.low_stock_threshold) return 'text-warning fw-semibold'
    return 'text-secondary'
  }
  
  const getMarginClass = (costPrice, sellingPrice) => {
    const margin = calculateMargin(costPrice, sellingPrice)
    if (margin < 10) return 'text-error'
    if (margin < 20) return 'text-warning'
    return 'text-success'
  }
  
  const getStatusBadgeClass = (status) => {
    const baseClasses = 'badge rounded-pill'
    if (status === 'active') return `${baseClasses} status-success`
    return `${baseClasses} status-info`
  }
  
  const getStatusText = (status) => {
    return status === 'active' ? 'Active' : 'Inactive'
  }
  
  const getExpiryDateClass = (expiryDate) => {
    if (!expiryDate) return 'text-tertiary'
    
    try {
      const expiry = new Date(expiryDate)
      const today = new Date()
      const diffDays = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      
      if (diffDays < 0) return 'text-error fw-bold'
      if (diffDays <= 7) return 'text-error'
      if (diffDays <= 30) return 'text-warning'
      return 'text-tertiary'
    } catch (err) {
      return 'text-tertiary'
    }
  }
  
  const isColumnVisible = (columnKey) => {
    return visibleColumns.value[columnKey]
  }
  
  // Handle click outside for dropdown
  const handleClickOutside = (event) => {
    const dropdown = document.querySelector('.dropdown')
    if (dropdown && !dropdown.contains(event.target)) {
      showAddDropdown.value = false
    }
  }
  
  // Success/Error handlers
  const handleProductSuccess = (result) => {
    successMessage.value = result.message
    fetchProducts()
    
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
  }
  
  const handleStockUpdateSuccess = (result) => {
    successMessage.value = result.message
    fetchProducts()
    
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
  }
  
  const handleImportSuccess = (result) => {
    successMessage.value = `Import completed! ${result.totalSuccessful || 0} products imported successfully.`
    fetchProducts()
    
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  }
  
  const handleImportError = (err) => {
    error.value = `Import failed: ${err.message || 'An unexpected error occurred'}`
    
    setTimeout(() => {
      error.value = null
    }, 5000)
  }
  
  // Lifecycle
  const initializeProducts = async () => {
    await fetchCategories() // Fetch categories first
    await fetchProducts()   // Then fetch and enrich products
    document.addEventListener('click', handleClickOutside)
  }
  
  const cleanupProducts = () => {
    document.removeEventListener('click', handleClickOutside)
  }
  
  return {
    // State
    products,
    filteredProducts,
    selectedProducts,
    categories,
    loading,
    error,
    successMessage,
    
    // UI State
    showAddDropdown,
    searchMode,
    showColumnFilter,
    
    // Pagination
    currentPage,
    itemsPerPage,
    paginatedProducts,
    
    // Report data
    lowStockCount,
    expiringCount,
    
    // Column visibility
    visibleColumns,
    
    // Filters
    categoryFilter,
    stockFilter,
    searchFilter,
    
    // Computed
    allSelected,
    someSelected,
    
    // Methods
    fetchProducts,
    fetchCategories,
    fetchReportCounts,
    applyFilters,
    clearFilters,
    refreshData,
    selectAll,
    deleteSelected,
    deleteProduct,
    toggleProductStatus,
    exportData,
    enrichProductsWithCategoryNames,
    
    // UI Methods
    toggleAddDropdown,
    closeAddDropdown,
    toggleSearchMode,
    clearSearch,
    toggleColumnFilter,
    handleColumnChanges,
    handleClickOutside,
    
    // Navigation Methods
    handleSingleProduct,
    handleBulkAdd,
    handleImport,
    
    // Pagination
    handlePageChange,
    
    // Formatting Methods
    getCategoryName,
    getCategoryBadgeClass,
    calculateMargin,
    formatPrice,
    formatExpiryDate,
    
    // Style Methods
    getProductNameClass,
    getRowClass,
    getStockDisplayClass,
    getMarginClass,
    getStatusBadgeClass,
    getStatusText,
    getExpiryDateClass,
    isColumnVisible,
    
    // Success/Error handlers
    handleProductSuccess,
    handleStockUpdateSuccess,
    handleImportSuccess,
    handleImportError,
    
    // Lifecycle
    initializeProducts,
    cleanupProducts
  }
}