// composables/useCategories.js
import { ref, computed } from 'vue'
import categoryApiService from '@/services/apiCategory.js'

export function useCategories() {
  // State
  const categories = ref([])
  const filteredCategories = ref([])
  const selectedCategories = ref([])
  const loading = ref(false)
  const error = ref(null)
  const successMessage = ref(null)
  const uncategorizedCount = ref(0)
  const UNCATEGORIZED_CATEGORY_ID = 'UNCTGRY-001'
  
  // UI State
  const showAddDropdown = ref(false)
  const searchMode = ref(false)
  const showColumnFilter = ref(false)
  
  // Pagination
  const currentPage = ref(1)
  const itemsPerPage = ref(10)
  
  // Filters
  const statusFilter = ref('all')
  const searchFilter = ref('')
  const includeDeleted = ref(false)
  
  // Product management state
  const categoryProducts = ref({}) // Store products by category ID
  const loadingProducts = ref({}) // Track loading state per category
  
  // Computed
  const ensureUncategorizedExists = async () => {
    try {
      // Check if uncategorized category exists in our current categories
      const uncategorized = categories.value.find(cat => cat._id === 'UNCTGRY-001')
      
      if (!uncategorized) {
        console.log('Uncategorized category not found, will be created on next fetch')
        // The backend will create it automatically when we fetch categories
        await fetchCategories()
      }
      
      return uncategorized || categories.value.find(cat => cat._id === 'UNCTGRY-001')
    } catch (error) {
      console.error('Error ensuring uncategorized category exists:', error)
      return null
    }
  }

  const paginatedCategories = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value
    const end = start + itemsPerPage.value
    return filteredCategories.value.slice(start, end)
  })
  
  const allSelected = computed(() => {
    return paginatedCategories.value.length > 0 && 
           selectedCategories.value.length === paginatedCategories.value.length
  })
  
  const someSelected = computed(() => {
    return selectedCategories.value.length > 0 && 
           selectedCategories.value.length < paginatedCategories.value.length
  })

  const activeCategories = computed(() => {
    return categories.value.filter(cat => cat.status === 'active' && !cat.isDeleted)
  })

  const deletedCategories = computed(() => {
    return categories.value.filter(cat => cat.isDeleted === true)
  })

  const categoriesWithSalesData = computed(() => {
    return categories.value.filter(cat => cat.total_sales > 0)
  })

  // Core Methods
  const fetchCategories = async (params = {}) => {
    loading.value = true
    error.value = null
    
    try {
      console.log('Fetching categories...')
      const data = await categoryApiService.getAllCategories({
        include_deleted: includeDeleted.value,
        ...params
      })
      
      categories.value = Array.isArray(data) ? data : []
      console.log(`Fetched ${categories.value.length} categories`)
      
      // Ensure uncategorized category exists
      await ensureUncategorizedExists()
      
      applyFilters()
      
    } catch (err) {
      console.error('Error fetching categories:', err)
      error.value = `Failed to load categories: ${err.message}`
      categories.value = []
    } finally {
      loading.value = false
    }
  }

  const fetchCategoriesWithSalesData = async (params = {}) => {
    loading.value = true
    error.value = null
    
    try {
      console.log('Fetching categories with sales data...')
      const data = await categoryApiService.CategoryData(params)
      
      categories.value = Array.isArray(data) ? data : (data.categories || [])
      console.log(`Fetched ${categories.value.length} categories with sales data`)
      
      applyFilters()
      
    } catch (err) {
      console.error('Error fetching categories with sales data:', err)
      error.value = `Failed to load category data: ${err.message}`
      categories.value = []
    } finally {
      loading.value = false
    }
  }

  const getCategorySubtitle = (category) => {
    if (category.isDeleted) {
      return `Deleted ${formatDate(category.deleted_at)}`
    }
    return category.description || category.subtitle || `${category.category_name} products`
  }

  const getProductCount = (category) => {
    if (category.subcategories) {
      return category.subcategories.reduce((total, sub) => total + (sub.product_count || 0), 0)
    }
    if (category.sub_categories) {
      return category.sub_categories.reduce((total, sub) => total + (sub.products?.length || 0), 0)
    }
    return category.product_count || 0
  }

  // Fixed: Use the actual API method that exists
  const fetchUncategorizedCount = async () => {
    try {
      console.log('Fetching uncategorized products count...')
      
      // First, make sure we have categories loaded
      if (categories.value.length === 0) {
        await fetchCategories()
      }
      
      // Check if uncategorized category exists in our loaded categories
      const uncategorizedCategory = categories.value.find(cat => cat._id === 'UNCTGRY-001')
      
      if (!uncategorizedCategory) {
        console.log('Uncategorized category not found in loaded categories')
        uncategorizedCount.value = 0
        return
      }
      
      // Get products count from the category data we already have
      const productCount = getProductCount(uncategorizedCategory)
      uncategorizedCount.value = productCount
      
      console.log(`Found ${uncategorizedCount.value} uncategorized products`)
    } catch (error) {
      console.error('Error fetching uncategorized count:', error)
      uncategorizedCount.value = 0
    }
  }

  // Fixed: Use the actual API method
  const getCategoryById = async (categoryId, includeDeleted = false) => {
    try {
      console.log(`Fetching category ${categoryId}`)
      
      // Use FindCategoryData which matches your API service
      const response = await categoryApiService.FindCategoryData({ 
        id: categoryId,
        include_deleted: includeDeleted 
      })
      
      // Handle different response formats
      let category = null
      if (response && response.category) {
        category = response.category
      } else if (response && typeof response === 'object' && !Array.isArray(response)) {
        category = response
      }
      
      if (category) {
        // Update category in local state if it exists
        const index = categories.value.findIndex(cat => cat._id === categoryId)
        if (index !== -1) {
          categories.value[index] = category
          applyFilters()
        }
      }
      
      return category
    } catch (err) {
      console.error(`Error fetching category ${categoryId}:`, err)
      error.value = `Failed to load category: ${err.message}`
      return null
    }
  }

  const createCategory = async (categoryData) => {
    loading.value = true
    error.value = null
    
    try {
      console.log('Creating category...', categoryData)
      const newCategory = await categoryApiService.AddCategoryData(categoryData)
      
      // Add to local state
      categories.value.unshift(newCategory)
      applyFilters()
      
      successMessage.value = `Category "${categoryData.category_name}" created successfully`
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
      
      return newCategory
    } catch (err) {
      console.error('Error creating category:', err)
      error.value = `Failed to create category: ${err.message}`
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateCategory = async (categoryId, updateData) => {
    loading.value = true
    error.value = null
    
    try {
      console.log(`Updating category ${categoryId}...`, updateData)
      const updatedCategory = await categoryApiService.UpdateCategoryData({
        id: categoryId,
        ...updateData
      })
      
      // Update in local state
      const index = categories.value.findIndex(cat => cat._id === categoryId)
      if (index !== -1) {
        categories.value[index] = updatedCategory
        applyFilters()
      }
      
      successMessage.value = `Category "${updateData.category_name || 'Unknown'}" updated successfully`
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
      
      return updatedCategory
    } catch (err) {
      console.error(`Error updating category ${categoryId}:`, err)
      error.value = `Failed to update category: ${err.message}`
      throw err
    } finally {
      loading.value = false
    }
  }

  const softDeleteCategory = async (categoryId) => {
    try {
      console.log(`Soft deleting category ${categoryId}`)
      const result = await categoryApiService.SoftDeleteCategory(categoryId)
      
      // Update in local state
      const category = categories.value.find(cat => cat._id === categoryId)
      if (category) {
        category.isDeleted = true
        category.deleted_at = new Date().toISOString()
      }
      
      applyFilters()
      successMessage.value = `Category moved to trash successfully`
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
      
      return result
    } catch (err) {
      console.error(`Error soft deleting category ${categoryId}:`, err)
      error.value = `Failed to delete category: ${err.message}`
      throw err
    }
  }

  const hardDeleteCategory = async (categoryId) => {
    try {
      console.log(`Hard deleting category ${categoryId}`)
      const result = await categoryApiService.HardDeleteCategory(categoryId)
      
      // Remove from local state
      categories.value = categories.value.filter(cat => cat._id !== categoryId)
      selectedCategories.value = selectedCategories.value.filter(id => id !== categoryId)
      
      applyFilters()
      successMessage.value = `Category permanently deleted`
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
      
      return result
    } catch (err) {
      console.error(`Error hard deleting category ${categoryId}:`, err)
      error.value = `Failed to permanently delete category: ${err.message}`
      throw err
    }
  }

  const restoreCategory = async (categoryId) => {
    try {
      console.log(`Restoring category ${categoryId}`)
      const result = await categoryApiService.RestoreCategory(categoryId)
      
      // Update in local state
      const category = categories.value.find(cat => cat._id === categoryId)
      if (category) {
        category.isDeleted = false
        category.deleted_at = null
      }
      
      applyFilters()
      successMessage.value = `Category restored successfully`
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
      
      return result
    } catch (err) {
      console.error(`Error restoring category ${categoryId}:`, err)
      error.value = `Failed to restore category: ${err.message}`
      throw err
    }
  }

  const getCategoryDeleteInfo = async (categoryId) => {
    try {
      console.log(`Getting delete info for category ${categoryId}`)
      return await categoryApiService.GetCategoryDeleteInfo(categoryId)
    } catch (err) {
      console.error(`Error getting delete info for category ${categoryId}:`, err)
      throw err
    }
  }

  // Product Management Methods - Fixed to match API
  const fetchCategoryProducts = async (categoryId, forceRefresh = false) => {
    if (loadingProducts.value[categoryId] && !forceRefresh) return
    
    loadingProducts.value[categoryId] = true
    
    try {
      console.log(`Fetching products for category ${categoryId}`)
      const products = await categoryApiService.FindProdcategory({ id: categoryId })
      
      categoryProducts.value[categoryId] = products
      console.log(`Fetched ${products.length} products for category ${categoryId}`)
      
      return products
    } catch (err) {
      console.error(`Error fetching products for category ${categoryId}:`, err)
      categoryProducts.value[categoryId] = []
      return []
    } finally {
      loadingProducts.value[categoryId] = false
    }
  }

  const moveProductToUncategorized = async (productId, currentCategoryId) => {
    try {
      console.log(`Moving product ${productId} to uncategorized`)
      const result = await categoryApiService.MoveProductToUncategorized({
        product_id: productId,
        current_category_id: currentCategoryId
      })
      
      // Refresh category products if we have them loaded
      if (categoryProducts.value[currentCategoryId]) {
        await fetchCategoryProducts(currentCategoryId, true)
      }
      
      successMessage.value = `Product moved to uncategorized successfully`
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
      
      return result
    } catch (err) {
      console.error(`Error moving product to uncategorized:`, err)
      error.value = `Failed to move product: ${err.message}`
      throw err
    }
  }

  const bulkMoveProductsToUncategorized = async (productIds, currentCategoryId) => {
    try {
      console.log(`Bulk moving ${productIds.length} products to uncategorized`)
      const result = await categoryApiService.BulkMoveProductsToUncategorized({
        product_ids: productIds,
        current_category_id: currentCategoryId
      })
      
      // Refresh category products if we have them loaded
      if (categoryProducts.value[currentCategoryId]) {
        await fetchCategoryProducts(currentCategoryId, true)
      }
      
      successMessage.value = `${productIds.length} products moved to uncategorized successfully`
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
      
      return result
    } catch (err) {
      console.error(`Error in bulk move to uncategorized:`, err)
      error.value = `Failed to move products: ${err.message}`
      throw err
    }
  }

  const updateProductSubcategory = async (productId, categoryId, newSubcategory) => {
    try {
      console.log(`Updating product ${productId} subcategory to ${newSubcategory}`)
      const result = await categoryApiService.SubCatChangeTab({
        product_id: productId,
        category_id: categoryId,
        new_subcategory: newSubcategory
      })
      
      // Refresh category products if we have them loaded
      if (categoryProducts.value[categoryId]) {
        await fetchCategoryProducts(categoryId, true)
      }
      
      successMessage.value = `Product subcategory updated successfully`
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
      
      return result
    } catch (err) {
      console.error(`Error updating product subcategory:`, err)
      error.value = `Failed to update subcategory: ${err.message}`
      throw err
    }
  }

  // Subcategory Methods
  const addSubcategory = async (categoryId, subcategoryData) => {
    try {
      console.log(`Adding subcategory to category ${categoryId}`)
      const result = await categoryApiService.AddSubCategoryData(categoryId, subcategoryData)
      
      // Refresh category data
      await getCategoryById(categoryId)
      
      successMessage.value = `Subcategory "${subcategoryData.name}" added successfully`
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
      
      return result
    } catch (err) {
      console.error(`Error adding subcategory:`, err)
      error.value = `Failed to add subcategory: ${err.message}`
      throw err
    }
  }

  const getSubcategories = async (categoryId) => {
    try {
      console.log(`Fetching subcategories for category ${categoryId}`)
      return await categoryApiService.getSubcategories(categoryId)
    } catch (err) {
      console.error(`Error fetching subcategories:`, err)
      return []
    }
  }

  // Export Methods
  const exportCategories = async (params = {}) => {
    try {
      console.log('Exporting categories...', params)
      const blob = await categoryApiService.ExportCategoryData(params)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `categories_${new Date().toISOString().split('T')[0]}.${params.format || 'csv'}`
      a.click()
      window.URL.revokeObjectURL(url)
      
      successMessage.value = 'Categories exported successfully'
      
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
      
    } catch (err) {
      console.error('Export failed:', err)
      error.value = `Export failed: ${err.message}`
    }
  }

  // Filter and Search Methods
  // In useCategories.js
  const applyFilters = () => {
    let filtered = [...categories.value]
    
    // Filter out uncategorized category from main display (but keep in exports)
    filtered = filtered.filter(category => category._id !== 'UNCTGRY-001')
    
    // Status filter
    if (statusFilter.value !== 'all') {
      if (statusFilter.value === 'deleted') {
        filtered = filtered.filter(category => category.isDeleted === true)
      } else {
        filtered = filtered.filter(category => 
          category.status === statusFilter.value && !category.isDeleted
        )
      }
    } else if (!includeDeleted.value) {
      filtered = filtered.filter(category => !category.isDeleted)
    }
    
    // Search filter
    if (searchFilter.value.trim()) {
      const search = searchFilter.value.toLowerCase()
      filtered = filtered.filter(category => 
        category.category_name?.toLowerCase().includes(search) ||
        category.description?.toLowerCase().includes(search) ||
        category._id?.toLowerCase().includes(search)
      )
    }
    
    currentPage.value = 1
    selectedCategories.value = []
    filteredCategories.value = filtered
  }

  const clearFilters = () => {
    statusFilter.value = 'all'
    searchFilter.value = ''
    searchMode.value = false
    includeDeleted.value = false
    applyFilters()
  }

  const refreshData = async () => {
    successMessage.value = null
    error.value = null
    await fetchCategories()
  }

  // Selection Methods
  const selectAll = (checked) => {
    if (checked) {
      selectedCategories.value = paginatedCategories.value.map(category => category._id)
    } else {
      selectedCategories.value = []
    }
  }

  const deleteSelected = async () => {
    if (selectedCategories.value.length === 0) return
    
    const confirmed = confirm(`Are you sure you want to delete ${selectedCategories.value.length} category(s)?`)
    if (!confirmed) return
    
    loading.value = true
    
    try {
      // Soft delete each selected category
      for (const categoryId of selectedCategories.value) {
        await softDeleteCategory(categoryId)
      }
      
      successMessage.value = `Successfully deleted ${selectedCategories.value.length} category(s)`
      selectedCategories.value = []
      await fetchCategories()
    } catch (err) {
      console.error('Error deleting categories:', err)
      error.value = `Failed to delete categories: ${err.message}`
    } finally {
      loading.value = false
    }
    
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
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

  // Pagination
  const handlePageChange = (page) => {
    currentPage.value = page
    selectedCategories.value = []
  }

  // Formatting Methods
  const formatDate = (dateString) => {
    if (!dateString) return '—'
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
      })
    } catch (err) {
      return '—'
    }
  }

  const formatSalesData = (amount) => {
    if (!amount || amount === 0) return '₱0.00'
    return `₱${parseFloat(amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}`
  }

  const getCategoryStatusClass = (status) => {
    const baseClasses = 'badge rounded-pill'
    if (status === 'active') return `${baseClasses} status-success`
    return `${baseClasses} status-warning`
  }

  const getCategoryStatusText = (status) => {
    return status === 'active' ? 'Active' : 'Inactive'
  }

  const getRowClass = (category) => {
    const classes = []
    
    if (selectedCategories.value.includes(category._id)) {
      classes.push('table-primary')
    }
    
    if (category.isDeleted) {
      classes.push('text-muted')
    }
    
    return classes.join(' ')
  }

  // Success/Error handlers
  const handleCategorySuccess = (result) => {
    successMessage.value = result.message
    fetchCategories()
    
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
  }

  const handleCategoryError = (err) => {
    error.value = `Category operation failed: ${err.message || 'An unexpected error occurred'}`
    
    setTimeout(() => {
      error.value = null
    }, 5000)
  }

  // Handle click outside for dropdown
  const handleClickOutside = (event) => {
    const dropdown = document.querySelector('.dropdown')
    if (dropdown && !dropdown.contains(event.target)) {
      showAddDropdown.value = false
    }
  }

  // Lifecycle
  const initializeCategories = async () => {
    await fetchCategories()
    document.addEventListener('click', handleClickOutside)
  }

  const cleanupCategories = () => {
    document.removeEventListener('click', handleClickOutside)
  }

  return {
    // State
    categories,
    filteredCategories,
    selectedCategories,
    loading,
    error,
    successMessage,
    categoryProducts,
    loadingProducts,
    
    // UI State
    showAddDropdown,
    searchMode,
    showColumnFilter,
    
    // Pagination
    currentPage,
    itemsPerPage,
    paginatedCategories,
    
    // Filters
    statusFilter,
    searchFilter,
    includeDeleted,
    
    // Computed
    allSelected,
    someSelected,
    activeCategories,
    deletedCategories,
    categoriesWithSalesData,
    
    // Core Methods
    fetchCategories,
    fetchCategoriesWithSalesData,
    getCategoryById,
    createCategory,
    updateCategory,
    softDeleteCategory,
    hardDeleteCategory,
    restoreCategory,
    getCategoryDeleteInfo,
    refreshData,
    uncategorizedCount,
    fetchUncategorizedCount,
    getProductCount,
    getCategorySubtitle,
    
    // Product Management
    fetchCategoryProducts,
    moveProductToUncategorized,
    bulkMoveProductsToUncategorized,
    updateProductSubcategory,
    
    // Subcategory Methods
    addSubcategory,
    getSubcategories,
    
    // Export Methods
    exportCategories,
    
    // Filter and Search
    applyFilters,
    clearFilters,
    
    // Selection Methods
    selectAll,
    deleteSelected,
    
    // UI Methods
    toggleAddDropdown,
    closeAddDropdown,
    toggleSearchMode,
    clearSearch,
    toggleColumnFilter,
    handleClickOutside,
    
    // Pagination
    handlePageChange,
    
    // Formatting Methods
    formatDate,
    formatSalesData,
    getCategoryStatusClass,
    getCategoryStatusText,
    getRowClass,
    
    // Success/Error handlers
    handleCategorySuccess,
    handleCategoryError,
    
    // Lifecycle
    initializeCategories,
    cleanupCategories
  }
}