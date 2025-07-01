// composables/ui/modals/useStockUpdate.js
import { ref, computed, watch, nextTick } from 'vue'
import productsApiService from '../../../services/apiProducts.js'

export function useStockUpdate() {
  // Modal State
  const show = ref(false)
  const product = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  // Form data
  const form = ref({
    operation_type: 'add',
    quantity: 0,
    reason: ''
  })
  
  const selectedReason = ref('')
  const newStockPreview = ref(null)
  
  // Predefined reasons for stock operations
  const stockReasons = {
    increase: [
      'Purchase/Delivery',
      'Stock Return',
      'Stock Transfer In',
      'Manual Recount'
    ],
    decrease: [
      'Sale',
      'Damaged/Expired',
      'Stock Transfer Out',
      'Theft/Loss',
      'Manual Adjustment'
    ],
    other: [
      'Inventory Correction',
      'System Migration',
      'Custom'
    ]
  }
  
  // Computed properties
  const isFormValid = computed(() => {
    return form.value.operation_type &&
           form.value.quantity > 0 &&
           form.value.reason.trim() !== '' &&
           (form.value.operation_type !== 'remove' || form.value.quantity <= (product.value?.stock || 0))
  })
  
  const operationDescription = computed(() => {
    switch (form.value.operation_type) {
      case 'add':
        return 'Add the specified quantity to current stock'
      case 'remove':
        return 'Remove the specified quantity from current stock'
      case 'set':
        return 'Set the stock to the exact quantity specified'
      default:
        return ''
    }
  })
  
  // Watch for modal show/hide
  watch(show, (newVal) => {
    if (newVal) {
      initializeForm()
      // Focus on first input when modal opens
      nextTick(() => {
        const firstInput = document.querySelector('#operation_type')
        if (firstInput) firstInput.focus()
      })
    }
  })
  
  // Watch for product changes
  watch(product, () => {
    if (show.value) {
      initializeForm()
    }
  }, { deep: true })
  
  // Methods
  const initializeForm = () => {
    form.value = {
      operation_type: 'add',
      quantity: 0,
      reason: ''
    }
    selectedReason.value = ''
    newStockPreview.value = null
    error.value = null
  }
  
  const onOperationChange = () => {
    form.value.quantity = 0
    newStockPreview.value = null
    
    // Clear reason when operation changes
    selectedReason.value = ''
    form.value.reason = ''
  }
  
  const onReasonChange = () => {
    if (selectedReason.value && selectedReason.value !== 'Custom') {
      form.value.reason = selectedReason.value
    } else {
      form.value.reason = ''
    }
  }
  
  const calculateNewStock = () => {
    if (!product.value || !form.value.quantity) {
      newStockPreview.value = null
      return
    }
    
    const currentStock = product.value.stock
    const quantity = parseInt(form.value.quantity) || 0
    
    switch (form.value.operation_type) {
      case 'add':
        newStockPreview.value = currentStock + quantity
        break
      case 'remove':
        newStockPreview.value = Math.max(0, currentStock - quantity)
        break
      case 'set':
        newStockPreview.value = quantity
        break
      default:
        newStockPreview.value = null
    }
  }
  
  // Helper methods
  const getCategoryName = (categoryId) => {
    const categories = {
      'noodles': 'Noodles',
      'drinks': 'Drinks',
      'toppings': 'Toppings'
    }
    return categories[categoryId] || categoryId
  }
  
  const getStockClass = (productData) => {
    if (!productData) return ''
    if (productData.stock === 0) return 'text-danger fw-bold'
    if (productData.stock <= productData.low_stock_threshold) return 'text-warning fw-semibold'
    return 'text-success fw-medium'
  }
  
  const getPreviewStockClass = (stock) => {
    if (!product.value) return ''
    if (stock === 0) return 'text-danger fw-bold'
    if (stock <= product.value.low_stock_threshold) return 'text-warning fw-semibold'
    return 'text-success fw-medium'
  }
  
  const getSubmitButtonClass = () => {
    switch (form.value.operation_type) {
      case 'add':
        return 'btn-save'
      case 'remove':
        return 'btn-delete'
      case 'set':
        return 'btn-submit'
      default:
        return 'btn-submit'
    }
  }
  
  const getSubmitButtonText = () => {
    switch (form.value.operation_type) {
      case 'add':
        return `Add ${form.value.quantity || 0} Units`
      case 'remove':
        return `Remove ${form.value.quantity || 0} Units`
      case 'set':
        return `Set to ${form.value.quantity || 0} Units`
      default:
        return 'Update Stock'
    }
  }
  
  // Modal actions
  const openStockModal = (productData) => {
    product.value = productData
    error.value = null
    show.value = true
  }
  
  const closeModal = () => {
    show.value = false
    product.value = null
    error.value = null
    loading.value = false
  }
  
  // Form submission
  const submitStockUpdate = async (onSuccess) => {
    if (!isFormValid.value) return
    
    loading.value = true
    error.value = null
    
    try {
      const formData = {
        operation_type: form.value.operation_type,
        quantity: form.value.quantity,
        reason: form.value.reason
      }
      
      const result = await productsApiService.updateProductStock(product.value._id, formData)
      
      // Call success callback if provided
      if (onSuccess) {
        onSuccess(result, formData)
      }
      
      closeModal()
      
    } catch (err) {
      console.error('Error updating stock:', err)
      error.value = err.message || 'Failed to update stock'
    } finally {
      loading.value = false
    }
  }
  
  // Keyboard event handling
  const handleEscape = (e) => {
    if (e.key === 'Escape' && show.value && !loading.value) {
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
    loading,
    error,
    form,
    selectedReason,
    newStockPreview,
    stockReasons,
    
    // Computed
    isFormValid,
    operationDescription,
    
    // Actions
    openStockModal,
    closeModal,
    submitStockUpdate,
    
    // Form methods
    initializeForm,
    onOperationChange,
    onReasonChange,
    calculateNewStock,
    
    // Helper methods
    getCategoryName,
    getStockClass,
    getPreviewStockClass,
    getSubmitButtonClass,
    getSubmitButtonText,
    
    // Utility methods
    setupKeyboardListeners,
    cleanupKeyboardListeners
  }
}