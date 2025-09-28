// composables/ui/modals/useAddProduct.js
import { ref, computed, watch, nextTick } from 'vue'
import productsApiService from '../../../services/apiProducts.js'

export function useAddProduct() {
  // Modal State
  const show = ref(false)
  const product = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const autoCalculateSellingPrice = ref(true)
  const hasUserEditedSellingPrice = ref(false)
  const hasManuallyEditedSellingPrice = ref(false)
  
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
  
  // Watcher for auto-calculating selling price
  watch(() => form.value.cost_price, (newCostPrice) => {
    // Convert to number and validate
    const costPrice = parseFloat(newCostPrice) || 0
    
    // Only auto-calculate if user hasn't manually edited the selling price
    if (costPrice > 0 && !hasManuallyEditedSellingPrice.value) {
      // Calculate 30% markup
      const markup = costPrice * 0.30
      const sellingPrice = costPrice + markup
      
      // Round to 2 decimal places and convert to number
      form.value.selling_price = Math.round(sellingPrice * 100) / 100
    }
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
  
  // Handle manual selling price changes
  const handleSellingPriceChange = () => {
    hasManuallyEditedSellingPrice.value = true
    console.log('User manually edited selling price')
  }

  // Form initialization
  const initializeForm = () => {
    hasManuallyEditedSellingPrice.value = false
    
    if (isEditMode.value && product.value) {
      hasManuallyEditedSellingPrice.value = true
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
      // 404 means product not found, which is good for new products
      if (error.response?.status === 404) {
        skuError.value = null // SKU is available
      } else {
        console.error('Error validating SKU:', error)
        skuError.value = null // Don't block creation on validation errors
      }
    } finally {
      isValidatingSku.value = false
    }
  }
  
  // Image handling methods
  const handleImageUpload = (event) => {
    const file = event.target.files[0]
    console.log('=== IMAGE UPLOAD DEBUG ===')
    console.log('File selected:', file)
    
    if (!file) {
      console.log('No file selected')
      return
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      console.log('Invalid file type:', file.type)
      alert('Please select a valid image file (PNG, JPG, JPEG)')
      return
    }

    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      console.log('File too large:', file.size)
      alert('Image size should be less than 5MB')
      return
    }

    console.log('Setting imageFile.value to:', file)
    imageFile.value = file
    
    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      console.log('Preview created, length:', e.target.result.length)
      imagePreview.value = e.target.result
    }
    reader.onerror = (error) => {
      console.error('Error creating preview:', error)
    }
    reader.readAsDataURL(file)
  }
  
  const removeImage = () => {
    console.log('Removing image')
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
    if (!imageFile.value) {
      console.log('No image file to convert')
      return null
    }
    
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        console.log('Base64 conversion successful, length:', e.target.result.length)
        resolve(e.target.result)
      }
      reader.onerror = (error) => {
        console.error('Base64 conversion failed:', error)
        reject(error)
      }
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
    // Create base form data without image field
    const formData = {
      product_name: form.value.product_name,
      category_id: form.value.category_id,
      SKU: form.value.SKU,
      unit: form.value.unit,
      stock: form.value.stock,
      low_stock_threshold: form.value.low_stock_threshold,
      cost_price: form.value.cost_price,
      selling_price: form.value.selling_price,
      status: form.value.status,
      is_taxable: form.value.is_taxable
    }
    
    // Add optional fields only if they have values
    if (form.value.expiry_date?.trim()) {
      formData.expiry_date = form.value.expiry_date.trim()
    }
    if (form.value.barcode?.trim()) {
      formData.barcode = form.value.barcode.trim()
    }
    if (form.value.description?.trim()) {
      formData.description = form.value.description.trim()
    }
    
    // DEBUG IMAGE HANDLING
    console.log('=== FRONTEND IMAGE DEBUG ===')
    console.log('imageFile.value:', imageFile.value)
    console.log('imagePreview.value:', imagePreview.value)
    
    // Handle image upload - ONLY add image fields if image exists
     if (imageFile.value && imagePreview.value) {
      // New image uploaded - SAME AS CATEGORY
      console.log('Adding NEW image data')
      formData.image_filename = imageFile.value.name
      formData.image_size = imageFile.value.size
      formData.image_type = imageFile.value.type
      formData.image_url = imagePreview.value  // Use the base64 preview directly
      formData.image_uploaded_at = new Date().toISOString()
      
      console.log('Image data added:', {
        image_filename: formData.image_filename,
        image_size: formData.image_size,
        image_type: formData.image_type,
        image_url_length: formData.image_url.length
      })
    } else {
      console.log('No image data to process')
    }
    
    console.log('Final formData keys:', Object.keys(formData))
    console.log('Has image in formData:', 'image' in formData)
    
    let result
    if (isEditMode.value) {
      result = await productsApiService.updateProduct(product.value._id, formData)
    } else {
      result = await productsApiService.createProduct(formData)
    }
    
    if (onSuccess) {
      onSuccess(result, isEditMode.value)
    }
    
    closeModal()
    
  } catch (err) {
    console.error('Error saving product:', err)
    error.value = err.response?.data?.error || err.message || 'Failed to save product'
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
    hasManuallyEditedSellingPrice,
    
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
    handleSellingPriceChange,
    
    // Image methods
    handleImageUpload,
    removeImage,
    convertImageToBase64,
    
    // Utility methods
    setupKeyboardListeners,
    cleanupKeyboardListeners
  }
}