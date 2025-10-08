import { ref, computed, watch } from 'vue'
import apiProductsService from '../../services/apiProducts.js'
import { useToast } from '../ui/useToast.js'

// Create toast instance
const toast = useToast()

// Global state for products
const products = ref([])
const currentProduct = ref(null)
const deletedProducts = ref([])
const lowStockProducts = ref([])
const expiringProducts = ref([])

// Loading states
const loading = ref(false)
const bulkLoading = ref(false)
const stockLoading = ref(false)
const importLoading = ref(false)
const categoryMoveLoading = ref(false)

// Filters and pagination - Updated for subcategory support
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
        result = result.filter(product => product.stock === 0)
      } else if (filters.value.stock_level === 'low_stock') {
        result = result.filter(product => 
          product.stock > 0 && product.stock <= product.low_stock_threshold
        )
      }
    }
    
    return result
  })

  const productStats = computed(() => ({
    total: products.value.length,
    active: products.value.filter(p => p.status === 'active').length,
    inactive: products.value.filter(p => p.status === 'inactive').length,
    outOfStock: products.value.filter(p => p.stock === 0).length,
    lowStock: products.value.filter(p => 
      p.stock > 0 && p.stock <= p.low_stock_threshold
    ).length
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
      // If we get a response, the SKU exists
      return true
    } catch (err) {
      // If we get a 404, the SKU doesn't exist
      if (err.message.includes('404') || err.message.includes('not found')) {
        return false
      }
      // For other errors, throw to let the caller handle
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
      
      // Only show success toast on manual refresh, not on initial load
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
      
      // Add to local state
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
      
      // Add to local state
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
      
      // Update local state
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
    loading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.deleteProduct(productId, hardDelete)
      
      if (hardDelete) {
        // Remove from local state completely
        products.value = products.value.filter(p => p._id !== productId)
        deletedProducts.value = deletedProducts.value.filter(p => p._id !== productId)
      } else {
        // Move to deleted products
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
      loading.value = false
    }
  }

  const restoreProduct = async (productId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.restoreProduct(productId)
      
      // Move back to active products
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

  const bulkDeleteProducts = async (productIds) => {
    bulkLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.bulkDeleteProducts(productIds)
      
      // Remove deleted products from local state
      products.value = products.value.filter(p => !productIds.includes(p._id))
      
      toast.success(`${productIds.length} products deleted successfully`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to delete products: ${err.message}`)
      throw err
    } finally {
      bulkLoading.value = false
    }
  }

  // ================ EXPORT OPERATIONS ================

  const exportProducts = async (customFilters = {}, format = 'csv') => {
    const exportLoading = ref(true)
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
      
      // Update local state
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
    bulkLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.bulkMoveProductsToCategory(productIds, newCategoryId, newSubcategoryName)
      
      // Refresh products to get updated categories
      await fetchProducts()
      
      toast.success(`${response.moved_count} products moved successfully`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to move products: ${err.message}`)
      throw err
    } finally {
      bulkLoading.value = false
    }
  }

  // ================ STOCK MANAGEMENT ================

  const updateStock = async (productId, stockData) => {
    stockLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.updateStock(productId, stockData)
      
      // Update local state
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
      
      // Update local state
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
      
      // Update local state
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

  const bulkUpdateStock = async (stockUpdates) => {
    bulkLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.bulkUpdateStock(stockUpdates)
      
      // Refresh products to get updated stock levels
      await fetchProducts()
      
      toast.success(`Bulk stock update completed`)
      return response
    } catch (err) {
      error.value = err.message
      toast.error(`Failed to update stock: ${err.message}`)
      throw err
    } finally {
      bulkLoading.value = false
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

  // ================ BULK OPERATIONS (CONTINUED) ================

  const bulkCreateProducts = async (productsData) => {
    bulkLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.bulkCreateProducts(productsData)
      
      // Add successful products to local state
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
      bulkLoading.value = false
    }
  }

  const bulkCreateProductsWithCategory = async (productsData, defaultCategoryId, defaultSubcategoryName = 'None') => {
    bulkLoading.value = true
    error.value = null
    
    try {
      const response = await apiProductsService.bulkCreateProductsWithCategory(productsData, defaultCategoryId, defaultSubcategoryName)
      
      // Add successful products to local state
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
      bulkLoading.value = false
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
        // Refresh products after successful import
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
    // Don't show toast on initial load
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
    bulkLoading,
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

    // Stock Management
    updateStock,
    adjustStockForSale,
    restockProduct,
    bulkUpdateStock,
    getStockHistory,

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