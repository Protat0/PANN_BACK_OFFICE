// composables/useCustomerValidation.js
import { ref, computed } from 'vue'
import apiService from '../../../services/apiCustomers.js'

export function useCustomerValidation() {
  const validationErrors = ref({})
  const isValidating = ref(false)
  const existingCustomers = ref([])

  // Load existing customers for validation
  const loadExistingCustomers = async () => {
    try {
      const customers = await apiService.getCustomers()
      existingCustomers.value = customers
      console.log('Loaded customers for validation:', customers.length)
    } catch (error) {
      console.error('Error loading customers for validation:', error)
    }
  }

  // Check for duplicate email
  const checkEmailDuplicate = (email, excludeId = null) => {
    if (!email) return false
    
    return existingCustomers.value.some(customer => {
      const customerId = customer._id || customer.customer_id
      const isDifferentCustomer = excludeId ? customerId !== excludeId : true
      return customer.email && 
             customer.email.toLowerCase() === email.toLowerCase() && 
             isDifferentCustomer
    })
  }

  // Check for duplicate username
  const checkUsernameDuplicate = (username, excludeId = null) => {
    if (!username) return false
    
    return existingCustomers.value.some(customer => {
      const customerId = customer._id || customer.customer_id
      const isDifferentCustomer = excludeId ? customerId !== excludeId : true
      return customer.username && 
             customer.username.toLowerCase() === username.toLowerCase() && 
             isDifferentCustomer
    })
  }

  // Validate individual field
  const validateField = (fieldName, value, excludeId = null) => {
    const errors = { ...validationErrors.value }

    switch (fieldName) {
      case 'email':
        if (!value) {
          errors.email = 'Email is required'
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          errors.email = 'Please enter a valid email address'
        } else if (checkEmailDuplicate(value, excludeId)) {
          errors.email = 'This email is already registered'
        } else {
          delete errors.email
        }
        break

      case 'username':
        if (!value) {
          errors.username = 'Username is required'
        } else if (value.length < 3) {
          errors.username = 'Username must be at least 3 characters long'
        } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
          errors.username = 'Username can only contain letters, numbers, and underscores'
        } else if (checkUsernameDuplicate(value, excludeId)) {
          errors.username = 'This username is already taken'
        } else {
          delete errors.username
        }
        break

      case 'full_name':
        if (!value) {
          errors.full_name = 'Full name is required'
        } else if (value.length < 2) {
          errors.full_name = 'Full name must be at least 2 characters long'
        } else {
          delete errors.full_name
        }
        break

      case 'phone':
        if (value && !/^[\+]?[\d\s\-\(\)]+$/.test(value)) {
          errors.phone = 'Please enter a valid phone number'
        } else {
          delete errors.phone
        }
        break

      case 'loyalty_points':
        if (value !== undefined && value !== null && value < 0) {
          errors.loyalty_points = 'Loyalty points cannot be negative'
        } else {
          delete errors.loyalty_points
        }
        break
    }

    validationErrors.value = errors
    return !errors[fieldName]
  }

  // Validate entire form
  const validateForm = async (formData, excludeId = null) => {
    isValidating.value = true
    validationErrors.value = {}

    // Ensure we have the latest customer data
    await loadExistingCustomers()

    // Validate all fields
    const fieldsToValidate = ['email', 'username', 'full_name', 'phone', 'loyalty_points']
    
    for (const field of fieldsToValidate) {
      validateField(field, formData[field], excludeId)
    }

    isValidating.value = false
    return Object.keys(validationErrors.value).length === 0
  }

  // Real-time validation for specific field
  const validateFieldRealTime = async (fieldName, value, excludeId = null) => {
    // For email and username, we need fresh data to check duplicates
    if ((fieldName === 'email' || fieldName === 'username') && existingCustomers.value.length === 0) {
      await loadExistingCustomers()
    }
    
    return validateField(fieldName, value, excludeId)
  }

  // Clear validation errors
  const clearValidation = () => {
    validationErrors.value = {}
  }

  // Clear specific field error
  const clearFieldError = (fieldName) => {
    const errors = { ...validationErrors.value }
    delete errors[fieldName]
    validationErrors.value = errors
  }

  // Check if form has any errors
  const hasValidationErrors = computed(() => {
    return Object.keys(validationErrors.value).length > 0
  })

  // Get error message for specific field
  const getFieldError = (fieldName) => {
    return validationErrors.value[fieldName] || null
  }

  // Get formatted error message for display
  const getErrorMessage = computed(() => {
    if (Object.keys(validationErrors.value).length === 0) return null
    
    const errorMessages = Object.values(validationErrors.value)
    return errorMessages.join(', ')
  })

  return {
    // State
    validationErrors,
    isValidating,
    existingCustomers,
    
    // Computed
    hasValidationErrors,
    getErrorMessage,
    
    // Methods
    loadExistingCustomers,
    checkEmailDuplicate,
    checkUsernameDuplicate,
    validateField,
    validateForm,
    validateFieldRealTime,
    clearValidation,
    clearFieldError,
    getFieldError
  }
}