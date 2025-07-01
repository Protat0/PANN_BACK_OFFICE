// composables/ui/modals/useAddProduct.js
import { ref, computed, watch, nextTick } from 'vue'
import productsApiService from '../../../services/apiProducts.js'

export function useAddProduct() {
  // Modal State
  const show = ref(false)
  const product = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  // Form data
  const form = ref({
    product_name: '',
    category_id: '',
    SKU: '',
    unit: '',
    stock: 0,
    low_stock_threshold: 10,
    cost_price: 0,
    selling_price: 0,
    expiry_date: '',
    status: 'active',
    is_taxable: false,
    barcode: '',
    description: '',
    image: null
  })
  
  // Image handling
  const imagePreview = ref(null)
  const imageFile = ref(null)
  
  // SKU validation
  const skuError = ref(null)
  const isValidatingSku = ref(false)
  
  // Computed properties
  const isEditMode = computed(() => product.value !== null)
  
  const isFormValid = computed(() => {
    return form.value.product_name.trim() !== '' &&
           form.value.SKU.trim() !== '' &&
           form.value.category_id !== '' &&
           form.value.unit !== '' &&
           form.value.cost_price >= 0 &&
           form.value.selling_price >= 0 &&
           form.value.stock >= 0 &&
           form.value.low_stock_threshold >= 0 &&
           !skuError.value
  })
  
  // Watch for modal show/hide
  watch(show, (newVal) => {
    if (newVal) {
      initializeForm()
      // Focus on first input when modal opens
      nextTick(() => {
        const firstInput = document.querySelector('#product_name')
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
  
  // Form initialization
  const initializeForm = () => {
    if (isEditMode.value && product.value) {
      form.value = {
        product_name: product.value.product_name || '',
        category_id: product.value.category_id || '',
        SKU: product.value.SKU || '',
        unit: product.value.unit || '',
        stock: product.value.stock || 0,
        low_stock_threshold: product.value.low_stock_threshold || 10,
        cost_price: product.value.cost_price || 0,
        selling_price: product.value.selling_price || 0,
        expiry_date: product.value.expiry_date ? product.value.expiry_date.split('T')[0] : '',
        status: product.value.status || 'active',
        is_taxable: product.value.is_taxable || false,
        barcode: product.value.barcode || '',
        description: product.value.description || '',
        image: null
      }
      
      // Set image preview if product has an image
      if (product.value.image_url || product.value.image) {
        imagePreview.value = product.value.image_url || product.value.image
      } else {
        imagePreview.value = null
      }
      imageFile.value = null
    } else {
      // Reset form for new product
      form.value = {
        product_name: '',
        category_id: '',
        SKU: '',
        unit: '',
        stock: 0,
        low_stock_threshold: 10,
        cost_price: 0,
        selling_price: 0,
        expiry_date: '',
        status: 'active',
        is_taxable: false,
        barcode: '',
        description: '',
        image: null
      }
      imagePreview.value = null
      imageFile.value = null
      skuError.value = null
      isValidatingSku.value = false
    }
  }
  
  // SKU validation
  const validateSKU = async () => {
    if (!form.value.SKU || form.value.SKU.trim() === '') {
      skuError.value = null
      return
    }

    // Don't validate if we're editing and SKU hasn't changed
    if (isEditMode.value && product.value && form.value.SKU === product.value.SKU) {
      skuError.value = null
      return
    }

    isValidatingSku.value = true
    
    try {
      const exists = await productsApiService.productExistsBySku(form.value.SKU)
      if (exists) {
        skuError.value = 'This SKU already exists'
      } else {
        skuError.value = null
      }
    } catch (error) {
      console.error('Error validating SKU:', error)
      skuError.value = null
    } finally {
      isValidatingSku.value = false
    }
  }
  
  // Image handling methods
  const handleImageUpload = (event) => {
    const file = event.target.files[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select a valid image file (PNG, JPG, JPEG)')
      return
    }

    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      alert('Image size should be less than 5MB')
      return
    }

    imageFile.value = file
    
    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
  
  const removeImage = () => {
    imagePreview.value = null
    imageFile.value = null
    form.value.image = null
    
    // Clear file input if it exists
    const fileInput = document.querySelector('input[type="file"]')
    if (fileInput) {
      fileInput.value = ''
    }
  }
  
  const convertImageToBase64 = async () => {
    if (!imageFile.value) return null
    
    return new Promise((resolve) => {
      const reader = new FileReader()
      reader.onload = (e) => resolve(e.target.result)
      reader.readAsDataURL(imageFile.value)
    })
  }
  
  // Barcode generation
  const generateBarcode = () => {
    // Generate a simple barcode based on SKU and timestamp
    const timestamp = Date.now().toString().slice(-6)
    const sku = form.value.SKU.replace(/[^a-zA-Z0-9]/g, '').toUpperCase()
    form.value.barcode = `${sku}${timestamp}`
  }
  
  // Modal actions
  const openAddModal = () => {
    product.value = null
    error.value = null
    show.value = true
  }
  
  const openEditModal = (productData) => {
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
  const submitProduct = async (onSuccess) => {
    if (!isFormValid.value) return
    
    loading.value = true
    error.value = null
    
    try {
      // Create a clean copy of the form data
      const formData = { ...form.value }
      
      // Handle image upload
      if (imageFile.value) {
        // Convert image to base64 or handle file upload based on your backend requirements
        const imageBase64 = await convertImageToBase64()
        formData.image = imageBase64
      } else if (imagePreview.value && isEditMode.value) {
        // Keep existing image URL for edit mode
        formData.image_url = imagePreview.value
      }
      
      // Clean up empty strings and convert to proper types
      if (!formData.expiry_date) {
        delete formData.expiry_date
      }
      if (!formData.barcode) {
        delete formData.barcode
      }
      if (!formData.description) {
        delete formData.description
      }
      
      let result
      if (isEditMode.value) {
        result = await productsApiService.updateProduct(product.value._id, formData)
      } else {
        result = await productsApiService.createProduct(formData)
      }
      
      // Call success callback if provided
      if (onSuccess) {
        onSuccess(result, isEditMode.value)
      }
      
      closeModal()
      
    } catch (err) {
      console.error('Error saving product:', err)
      error.value = err.message || 'Failed to save product'
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
    imagePreview,
    imageFile,
    skuError,
    isValidatingSku,
    
    // Computed
    isEditMode,
    isFormValid,
    
    // Actions
    openAddModal,
    openEditModal,
    closeModal,
    submitProduct,
    
    // Form methods
    initializeForm,
    validateSKU,
    generateBarcode,
    
    // Image methods
    handleImageUpload,
    removeImage,
    
    // Utility methods
    setupKeyboardListeners,
    cleanupKeyboardListeners
  }
}