// composables/ui/modals/useViewProduct.js
import { ref, computed } from 'vue'

export function useViewProduct() {
  // Modal State
  const show = ref(false)
  const product = ref(null)
  
  // Helper methods for categories
  const getCategoryName = (categoryId) => {
    const categories = {
      'noodles': 'Noodles',
      'drinks': 'Drinks',
      'toppings': 'Toppings'
    }
    return categories[categoryId] || categoryId
  }
  
  const getCategorySlug = (categoryId) => {
    return categoryId?.toLowerCase().replace(/\s+/g, '-') || 'unknown'
  }
  
  // Stock-related methods
  const getStockClass = (productData) => {
    if (!productData) return ''
    if (productData.stock === 0) return 'text-danger fw-bold'
    if (productData.stock <= productData.low_stock_threshold) return 'text-warning fw-semibold'
    return 'text-success fw-medium'
  }
  
  const getStockStatusClass = (productData) => {
    if (!productData) return ''
    if (productData.stock === 0) return 'badge text-bg-danger'
    if (productData.stock <= productData.low_stock_threshold) return 'badge text-bg-warning'
    return 'badge text-bg-success'
  }
  
  const getStockStatusText = (productData) => {
    if (!productData) return 'Unknown'
    if (productData.stock === 0) return 'Out of Stock'
    if (productData.stock <= productData.low_stock_threshold) return 'Low Stock'
    return 'In Stock'
  }
  
  // Status badge methods
  const getStatusBadgeClass = (status) => {
    return status === 'active' ? 'badge text-bg-success' : 'badge text-bg-danger'
  }
  
  const getCategoryBadgeClass = (categoryId) => {
    const classes = {
      'noodles': 'badge text-bg-warning',
      'drinks': 'badge text-bg-primary',
      'toppings': 'badge text-bg-info'
    }
    return classes[categoryId] || 'badge text-bg-secondary'
  }
  
  // Expiry-related methods
  const getExpiryClass = (expiryDate) => {
    if (!expiryDate) return ''
    
    const today = new Date()
    const expiry = new Date(expiryDate)
    const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
    
    if (daysUntilExpiry < 0) return 'text-danger fw-bold'
    if (daysUntilExpiry <= 7) return 'text-warning fw-semibold'
    if (daysUntilExpiry <= 30) return 'text-info fw-medium'
    return ''
  }
  
  const getDaysUntilExpiry = (expiryDate) => {
    if (!expiryDate) return ''
    
    const today = new Date()
    const expiry = new Date(expiryDate)
    const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
    
    if (daysUntilExpiry < 0) return `Expired ${Math.abs(daysUntilExpiry)} days ago`
    if (daysUntilExpiry === 0) return 'Expires today'
    if (daysUntilExpiry === 1) return 'Expires tomorrow'
    return `${daysUntilExpiry} days remaining`
  }
  
  // Pricing calculations
  const getProfitMargin = (productData) => {
    if (!productData || !productData.selling_price || !productData.cost_price) return '0.00'
    const margin = ((productData.selling_price - productData.cost_price) / productData.selling_price * 100)
    return margin.toFixed(2)
  }
  
  const getProfitPerUnit = (productData) => {
    if (!productData || !productData.selling_price || !productData.cost_price) return '0.00'
    const profit = productData.selling_price - productData.cost_price
    return profit.toFixed(2)
  }
  
  // Formatting methods
  const formatPrice = (price) => {
    return parseFloat(price || 0).toFixed(2)
  }
  
  const formatStatus = (status) => {
    return status.charAt(0).toUpperCase() + status.slice(1).replace('-', ' ')
  }
  
  const formatDate = (dateString) => {
    if (!dateString) return 'Not set'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }
  
  const formatDateTime = (dateString) => {
    if (!dateString) return 'Not available'
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  // Stock status computed properties
  const stockCardClass = computed(() => {
    if (!product.value) return ''
    if (product.value.stock === 0) return 'border-danger bg-danger-subtle'
    if (product.value.stock <= product.value.low_stock_threshold) return 'border-warning bg-warning-subtle'
    return 'border-success bg-success-subtle'
  })
  
  const thresholdCardClass = computed(() => 'border-info bg-info-subtle')
  const statusCardClass = computed(() => 'border-primary bg-primary-subtle')
  
  // Quick action button states
  const canGenerateBarcode = computed(() => {
    return product.value && !product.value.barcode
  })
  
  const statusToggleText = computed(() => {
    if (!product.value) return 'Toggle Status'
    return product.value.status === 'active' ? 'Deactivate Product' : 'Activate Product'
  })
  
  const statusToggleSubtext = computed(() => {
    if (!product.value) return ''
    return product.value.status === 'active' 
      ? 'Make unavailable for sale' 
      : 'Make available for sale'
  })
  
  // Modal actions
  const openViewModal = (productData) => {
    product.value = productData
    show.value = true
  }
  
  const closeModal = () => {
    show.value = false
    product.value = null
  }
  
  // Action handlers
  const handleEdit = (onEdit) => {
    if (onEdit && product.value) {
      onEdit(product.value)
    }
  }
  
  const handleRestock = (onRestock) => {
    if (onRestock && product.value) {
      onRestock(product.value)
    }
  }
  
  const handleToggleStatus = (onToggleStatus) => {
    if (onToggleStatus && product.value) {
      onToggleStatus(product.value)
    }
  }
  
  const handleGenerateBarcode = (onGenerateBarcode) => {
    if (onGenerateBarcode && product.value && !product.value.barcode) {
      onGenerateBarcode(product.value)
    }
  }
  
  // Keyboard event handling
  const handleEscape = (e) => {
    if (e.key === 'Escape' && show.value) {
      closeModal()
    }
  }
  
  // Auto-setup keyboard listeners
  const setupKeyboardListeners = () => {
    document.addEventListener('keydown', handleEscape)
  }
  
  const cleanupKeyboardListeners = () => {
    document.removeEventListener('keydown', handleEscape)
  }
  
  return {
    // State
    show,
    product,
    
    // Computed
    stockCardClass,
    thresholdCardClass,
    statusCardClass,
    canGenerateBarcode,
    statusToggleText,
    statusToggleSubtext,
    
    // Actions
    openViewModal,
    closeModal,
    handleEdit,
    handleRestock,
    handleToggleStatus,
    handleGenerateBarcode,
    
    // Helper methods
    getCategoryName,
    getCategorySlug,
    getStockClass,
    getStockStatusClass,
    getStockStatusText,
    getStatusBadgeClass,
    getCategoryBadgeClass,
    getExpiryClass,
    getDaysUntilExpiry,
    getProfitMargin,
    getProfitPerUnit,
    
    // Formatting methods
    formatPrice,
    formatStatus,
    formatDate,
    formatDateTime,
    
    // Utility methods
    setupKeyboardListeners,
    cleanupKeyboardListeners
  }
}