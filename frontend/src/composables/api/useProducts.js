import { ref, computed, watch } from 'vue'
import apiProductsService from '../../services/apiProducts.js'
import { useToast } from '../ui/useToast.js'

const toast = useToast()

// Global state for products
const products = ref([])
const currentProduct = ref(null)
const deletedProducts = ref([])
const lowStockProducts = ref([])
const expiringProducts = ref([])

// Loading states - Fixed naming conflicts
const loading = ref(false)
const deleteLoading = ref(false)
const bulkDeleteLoading = ref(false)
const exportLoading = ref(false)
const stockLoading = ref(false)
const importLoading = ref(false)
const categoryMoveLoading = ref(false)

// Filters and pagination
const filters = ref({
  category_id: '',
  subcategory_name: '',
  status: '',
  stock_level: '',
  search: '',
  include_deleted: false
})

// Error states
const error = ref(null)
const validationErrors = ref([])

export function useProducts() {
  // ================ COMPUTED PROPERTIES ================
  
  const filteredProducts = computed(() => {
    let result = products.value
    
    if (filters.value.search) {
      const searchTerm = filters.value.search.toLowerCase()
      result = result.filter(product => 
        product.product_name?.toLowerCase().includes(searchTerm) ||
        product.SKU?.toLowerCase().includes(searchTerm) ||
        product._id?.toLowerCase().includes(searchTerm) ||
        product.barcode?.toLowerCase().includes(searchTerm)
      )
    }
    
    if (filters.value.category_id) {
      result = result.filter(product => product.category_id === filters.value.category_id)
    }

    if (filters.value.subcategory_name) {
      result = result.filter(product => product.subcategory_name === filters.value.subcategory_name)
    }
    
    if (filters.value.status) {
      result = result.filter(product => product.status === filters.value.status)
    }
    
    if (filters.value.stock_level) {
      if (filters.value.stock_level === 'out_of_stock') {
        result = result.filter(product => (product.total_stock || product.stock) === 0)
      } else if (filters.value.stock_level === 'low_stock') {
        result = result.filter(product => {
          const currentStock = product.total_stock || product.stock
          return currentStock > 0 && currentStock <= product.low_stock_threshold
        })
      }
    }
    
    return result
  })

  const isTrackedStock = (product) => {
    if (!product) return false
    const stockField = product.total_stock ?? product.stock
    return typeof stockField === 'number'
  }

  const lowStockItems = computed(() => products.value.filter(p => {
    if (!isTrackedStock(p)) return false
    const currentStock = p.total_stock ?? p.stock
    const threshold = typeof p.low_stock_threshold === 'number' ? p.low_stock_threshold : 0
    return currentStock > 0 && currentStock < threshold
  }))

  const productStats = computed(() => ({
    total: products.value.length,
    active: products.value.filter(p => p.status === 'active').length,
    inactive: products.value.filter(p => p.status === 'inactive').length,
    outOfStock: products.value.filter(p => {
      if (!isTrackedStock(p)) return false
      const currentStock = p.total_stock ?? p.stock
      return currentStock === 0
    }).length,
    lowStock: lowStockItems.value.length
  }))

  const productsByCategory = computed(() => {
    const grouped = {}
    products.value.forEach(product => {
      const categoryId = product.category_id || 'uncategorized'
      if (!grouped[categoryId]) {
        grouped[categoryId] = {}
      }
      
      const subcategory = product.subcategory_name || 'None'
      if (!grouped[categoryId][subcategory]) {
        grouped[categoryId][subcategory] = []
      }
      
      grouped[categoryId][subcategory].push(product)
    })
    return grouped
  })

  const hasProducts = computed(() => products.value.length > 0)
  const hasCurrentProduct = computed(() => currentProduct.value !== null)

  // ================ VALIDATION METHODS ================

  const checkSkuExists = async (sku) => {
    try {
      const response = await apiProductsService.getProductBySku(sku)
      return true
    } catch (err) {
      if (err.message.includes('404') || err.message.includes('not found')) {
        return false
      }
      throw err
    }
  }

  // ================ CRUD OPERATIONS ================

  const fetchProducts = async (customFilters = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const mergedFilters = { ...filters.value, ...customFilters }
      const response = await apiProductsService.getAllProducts(mergedFilters)
      products.value = response.data || []
      
      if (Object.keys(customFilters).length > 0 || products.value.length > 0) {
        toast.success(`Loaded ${products.value.length} products`)
      }
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to load products: ${err.message}`)
      products.value = []
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchProductById = async (productId, includeDeleted = false) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.getProductById(productId, includeDeleted)
      currentProduct.value = response.data
      return response
    } catch (err) {
      error.value = err.message
      currentProduct.value = null
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchProductBySku = async (sku, includeDeleted = false) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.getProductBySku(sku, includeDeleted)
      currentProduct.value = response.data
      return response
    } catch (err) {
      error.value = err.message
      currentProduct.value = null
      throw err
    } finally {
      loading.value = false
    }
  }

  const createProduct = async (productData) => {
    loading.value = true
    error.value = null
    validationErrors.value = []
    
    try {
      const response = await apiProductsService.createProduct(productData)
      
      products.value.unshift(response.data)
      currentProduct.value = response.data
      
      toast.success(`Product "${productData.product_name}" created successfully`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to create product: ${err.message}`)
      throw err
    } finally {
      loading.value = false
    }
  }

  const createProductWithCategory = async (productData, categoryId, subcategoryName = 'None') => {
    loading.value = true
    error.value = null
    validationErrors.value = []
    
    try {
      const response = await apiProductsService.createProductWithCategory(productData, categoryId, subcategoryName)
      
      products.value.unshift(response.data)
      currentProduct.value = response.data
      
      toast.success(`Product "${productData.product_name}" created successfully`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to create product: ${err.message}`)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateProduct = async (productId, productData, partial = false) => {
    loading.value = true
    error.value = null
    validationErrors.value = []
    
    try {
      const response = await apiProductsService.updateProduct(productId, productData, partial)
      
      const index = products.value.findIndex(p => p._id === productId)
      if (index !== -1) {
        products.value[index] = response.data
      }
      
      if (currentProduct.value?._id === productId) {
        currentProduct.value = response.data
      }
      
      toast.success(`Product updated successfully`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to update product: ${err.message}`)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteProduct = async (productId, hardDelete = false) => {
    deleteLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.deleteProduct(productId, hardDelete)
      
      if (hardDelete) {
        products.value = products.value.filter(p => p._id !== productId)
        deletedProducts.value = deletedProducts.value.filter(p => p._id !== productId)
      } else {
        const deletedProduct = products.value.find(p => p._id === productId)
        if (deletedProduct) {
          deletedProduct.isDeleted = true
          products.value = products.value.filter(p => p._id !== productId)
          deletedProducts.value.unshift(deletedProduct)
        }
      }
      
      if (currentProduct.value?._id === productId) {
        currentProduct.value = null
      }
      
      toast.success(`Product deleted successfully`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to delete product: ${err.message}`)
      throw err
    } finally {
      deleteLoading.value = false
    }
  }

  const restoreProduct = async (productId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.restoreProduct(productId)
      
      const restoredProduct = deletedProducts.value.find(p => p._id === productId)
      if (restoredProduct) {
        restoredProduct.isDeleted = false
        deletedProducts.value = deletedProducts.value.filter(p => p._id !== productId)
        products.value.unshift(restoredProduct)
      }
      
      toast.success(`Product restored successfully`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to restore product: ${err.message}`)
      throw err
    } finally {
      loading.value = false
    }
  }

  // ================ BULK OPERATIONS ================

const bulkDeleteProducts = async (productIds, hardDelete = false) => {
  bulkDeleteLoading.value = true
  error.value = null
  
  try {
    const response = await apiProductsService.bulkDeleteProducts(productIds, hardDelete)
    
    // Update local state - remove deleted products
    products.value = products.value.filter(p => !productIds.includes(p._id))
    
    // Handle the response structure from your backend
    const deletedCount = response.details?.deleted_count || productIds.length
    const failedCount = response.details?.failed_count || 0
    
    if (failedCount > 0) {
      toast.success(`${deletedCount} products deleted successfully. ${failedCount} failed.`)
    } else {
      toast.success(`${deletedCount} products deleted successfully`)
    }
    
    return response
  } catch (err) {
    error.value = err.message
    toast.error(`Failed to delete products: ${err.message}`)
    throw err
  } finally {
    bulkDeleteLoading.value = false
  }
}

  // ================ EXPORT OPERATIONS ================

  const exportProducts = async (customFilters = {}, format = 'csv') => {
    exportLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.exportProducts(customFilters, format)
      toast.success('Products exported successfully')
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Export failed: ${err.message}`)
      throw err
    } finally {
      exportLoading.value = false
    }
  }

  

  // ================ PRODUCT-CATEGORY RELATIONSHIP MANAGEMENT ================

  const moveProductToCategory = async (productId, newCategoryId, newSubcategoryName = null) => {
    categoryMoveLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.moveProductToCategory(productId, newCategoryId, newSubcategoryName)
      
      const index = products.value.findIndex(p => p._id === productId)
      if (index !== -1) {
        products.value[index] = response.data
      }
      
      if (currentProduct.value?._id === productId) {
        currentProduct.value = response.data
      }
      
      toast.success(`Product moved to different category successfully`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to move product: ${err.message}`)
      throw err
    } finally {
      categoryMoveLoading.value = false
    }
  }

  const bulkMoveProductsToCategory = async (productIds, newCategoryId, newSubcategoryName = null) => {
    bulkDeleteLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.bulkMoveProductsToCategory(productIds, newCategoryId, newSubcategoryName)
      
      await fetchProducts()
      
      toast.success(`${response.moved_count} products moved successfully`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to move products: ${err.message}`)
      throw err
    } finally {
      bulkDeleteLoading.value = false
    }
  }

  // ================ BATCH-AWARE STOCK MANAGEMENT ================

  const updateStock = async (productId, stockData) => {
    stockLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.updateStock(productId, stockData)
      
      const index = products.value.findIndex(p => p._id === productId)
      if (index !== -1) {
        products.value[index] = response.data
      }
      
      if (currentProduct.value?._id === productId) {
        currentProduct.value = response.data
      }
      
      toast.success(`Stock updated successfully`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to update stock: ${err.message}`)
      throw err
    } finally {
      stockLoading.value = false
    }
  }

  const adjustStockForSale = async (productId, quantitySold) => {
    stockLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.adjustStockForSale(productId, quantitySold)
      
      const index = products.value.findIndex(p => p._id === productId)
      if (index !== -1) {
        products.value[index] = response.data
      }
      
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      stockLoading.value = false
    }
  }

  const restockProduct = async (productId, quantityReceived, supplierInfo = null) => {
    stockLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.restockProduct(productId, quantityReceived, supplierInfo)
      
      const index = products.value.findIndex(p => p._id === productId)
      if (index !== -1) {
        products.value[index] = response.data
      }
      
      if (currentProduct.value?._id === productId) {
        currentProduct.value = response.data
      }
      
      toast.success(`Product restocked successfully`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to restock product: ${err.message}`)
      throw err
    } finally {
      stockLoading.value = false
    }
  }

  // NEW: Batch-aware restock
  const restockWithBatch = async (productId, restockData) => {
    stockLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.restockWithBatch(productId, restockData)
      
      const index = products.value.findIndex(p => p._id === productId)
      if (index !== -1) {
        products.value[index] = response.data
      }
      
      if (currentProduct.value?._id === productId) {
        currentProduct.value = response.data
      }
      
      toast.success(`Product restocked with batch successfully`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to restock product: ${err.message}`)
      throw err
    } finally {
      stockLoading.value = false
    }
  }

  const bulkUpdateStock = async (stockUpdates) => {
    bulkDeleteLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.bulkUpdateStock(stockUpdates)
      
      await fetchProducts()
      
      toast.success(`Bulk stock update completed`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to update stock: ${err.message}`)
      throw err
    } finally {
      bulkDeleteLoading.value = false
    }
  }

  const getStockHistory = async (productId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.getStockHistory(productId)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // NEW: Get product with batch information
  const getProductWithBatches = async (productId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.getProductWithBatches(productId)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // NEW: Get products with expiry summary
  const getProductsWithExpirySummary = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.getProductsWithExpirySummary()
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // ================ BULK OPERATIONS (CONTINUED) ================

  const bulkCreateProducts = async (productsData) => {
    bulkDeleteLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.bulkCreateProducts(productsData)
      
      if (response.results?.successful) {
        products.value.unshift(...response.results.successful)
      }
      
      toast.success(`Bulk creation completed`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to create products: ${err.message}`)
      throw err
    } finally {
      bulkDeleteLoading.value = false
    }
  }

  const bulkCreateProductsWithCategory = async (productsData, defaultCategoryId, defaultSubcategoryName = 'None') => {
    bulkDeleteLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.bulkCreateProductsWithCategory(productsData, defaultCategoryId, defaultSubcategoryName)
      
      if (response.results?.successful) {
        products.value.unshift(...response.results.successful)
      }
      
      toast.success(`Bulk creation with category completed`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to create products: ${err.message}`)
      throw err
    } finally {
      bulkDeleteLoading.value = false
    }
  }

  // ================ REPORTS AND ANALYTICS ================

  const fetchLowStockProducts = async (branchId = null) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.getLowStockProducts(branchId)
      lowStockProducts.value = response.data || []
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchExpiringProducts = async (daysAhead = 30) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.getExpiringProducts(daysAhead)
      expiringProducts.value = response.data || []
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchProductsByCategory = async (categoryId, subcategoryName = null) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.getProductsByCategory(categoryId, subcategoryName)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchProductsBySubcategory = async (categoryId, subcategoryName) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.getProductsBySubcategory(categoryId, subcategoryName)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchDeletedProducts = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.getDeletedProducts()
      deletedProducts.value = response.data || []
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // ================ IMPORT/EXPORT ================

  const importProducts = async (file, validateOnly = false) => {
    importLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.importProducts(file, validateOnly)
      
      if (!validateOnly) {
        await fetchProducts()
        toast.success('Products imported successfully')
      } else {
        toast.info('Validation completed')
      }
      
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Import failed: ${err.message}`)
      throw err
    } finally {
      importLoading.value = false
    }
  }

  const downloadImportTemplate = async (format = 'csv') => {
    try {
      const response = await apiProductsService.downloadImportTemplate(format)
      toast.success('Template downloaded successfully')
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Download failed: ${err.message}`)
      throw err
    }
  }

  const exportProductDetails = async (productId) => {
    try {
      await apiProductsService.exportProductDetails(productId);
    } catch (err) {
      console.error('❌ Export product details failed:', err);
      throw err;
    }
  }

  // ================ UTILITY METHODS ================

  const searchProducts = async (query) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.searchProducts(query, filters.value)
      products.value = response.data || []
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const searchProductsAdvanced = async (query, customFilters = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const mergedFilters = { ...filters.value, ...customFilters }
      const response = await apiProductsService.searchProductsAdvanced(query, mergedFilters)
      products.value = response.data || []
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const getProductStock = async (productId) => {
    try {
      const response = await apiProductsService.getProductStock(productId)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const clearError = () => {
    error.value = null
    validationErrors.value = []
  }

  const clearCurrentProduct = () => {
    currentProduct.value = null
  }

  const setFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  const resetFilters = () => {
    filters.value = {
      category_id: '',
      subcategory_name: '',
      status: '',
      stock_level: '',
      search: '',
      include_deleted: false
    }
  }

  // ================ INITIALIZATION ================

  const initializeProducts = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.getAllProducts(filters.value)
      products.value = response.data || []
      return response
    } catch (err) {
      error.value = err.message
      products.value = []
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    products,
    currentProduct,
    deletedProducts,
    lowStockProducts,
    expiringProducts,
    filters,
    error,
    validationErrors,
    loading,
    deleteLoading,
    bulkDeleteLoading,
    exportLoading,
    stockLoading,
    importLoading,
    categoryMoveLoading,

    // Computed
    filteredProducts,
    productStats,
    productsByCategory,
    hasProducts,
    hasCurrentProduct,

    // Validation
    checkSkuExists,
    exportProductDetails,

    // CRUD Operations
    fetchProducts,
    fetchProductById,
    fetchProductBySku,
    createProduct,
    createProductWithCategory,
    updateProduct,
    deleteProduct,
    restoreProduct,

    // Bulk Operations
    bulkDeleteProducts,
    bulkCreateProducts,
    bulkCreateProductsWithCategory,

    // Export
    exportProducts,

    // Product-Category Management
    moveProductToCategory,
    bulkMoveProductsToCategory,

    // Stock Management (Batch-aware)
    updateStock,
    adjustStockForSale,
    restockProduct,
    restockWithBatch,
    bulkUpdateStock,
    getStockHistory,
    getProductWithBatches,
    getProductsWithExpirySummary,

    // Reports
    fetchLowStockProducts,
    fetchExpiringProducts,
    fetchProductsByCategory,
    fetchProductsBySubcategory,
    fetchDeletedProducts,

    // Import/Export
    importProducts,
    downloadImportTemplate,

    // Utilities
    searchProducts,
    searchProductsAdvanced,
    getProductStock,
    clearError,
    clearCurrentProduct,
    setFilters,
    resetFilters,
    initializeProducts
  }
}