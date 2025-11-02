// composables/ui/suppliers/useSupplierForm.js
import { ref, reactive, computed } from 'vue'
import axios from 'axios'
import { useToast } from '@/composables/ui/useToast'

// Configure axios
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export function useSupplierForm() {
  // Initialize toast composable
  const { success, error: showError } = useToast()
  
  // State
  const showAddModal = ref(false)
  const isEditMode = ref(false)
  const formLoading = ref(false)
  const selectedSupplier = ref(null)
  const addAnotherAfterSave = ref(false)

  // Form data
  const formData = reactive({
    name: '',
    contactPerson: '',
    email: '',
    phone: '',
    address: '',
    type: '',
    status: 'active',
    notes: ''
  })

  const formErrors = ref({})

  // Computed
  const isFormValid = computed(() => {
    return formData.name.trim() !== '' && Object.keys(formErrors.value).length === 0
  })

  // Methods
  const showAddSupplierModal = () => {
    isEditMode.value = false
    selectedSupplier.value = null
    resetForm()
    showAddModal.value = true
  }

  const editSupplier = (supplier) => {
    isEditMode.value = true
    selectedSupplier.value = supplier
    formData.name = supplier.name || ''
    formData.contactPerson = supplier.contactPerson || ''
    formData.email = supplier.email || ''
    formData.phone = supplier.phone || ''
    formData.address = supplier.address || ''
    formData.type = supplier.type || ''
    formData.status = supplier.status || 'active'
    formData.notes = supplier.notes || ''
    formErrors.value = {}
    addAnotherAfterSave.value = false
    showAddModal.value = true
  }

  const closeAddModal = () => {
    showAddModal.value = false
    isEditMode.value = false
    selectedSupplier.value = null
    resetForm()
  }

  const resetForm = () => {
    formData.name = ''
    formData.contactPerson = ''
    formData.email = ''
    formData.phone = ''
    formData.address = ''
    formData.type = ''
    formData.status = 'active'
    formData.notes = ''
    formErrors.value = {}
    addAnotherAfterSave.value = false
  }

  const validateForm = () => {
    const errors = {}

    // Name validation
    if (!formData.name.trim()) {
      errors.name = 'Supplier name is required'
    } else if (formData.name.trim().length < 2) {
      errors.name = 'Supplier name must be at least 2 characters'
    }

    // Email validation (optional but must be valid if provided)
    if (formData.email && !isValidEmail(formData.email)) {
      errors.email = 'Please enter a valid email address'
    }

    // Phone validation (optional but must be valid if provided)
    if (formData.phone && !isValidPhone(formData.phone)) {
      errors.phone = 'Please enter a valid phone number'
    }

    formErrors.value = errors
    return Object.keys(errors).length === 0
  }

  const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const isValidPhone = (phone) => {
    const phoneRegex = /^[\d\s\+\-\(\)]+$/
    return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10
  }

  const clearFormError = (field) => {
    if (formErrors.value[field]) {
      delete formErrors.value[field]
    }
  }

  const saveSupplier = async (suppliersComposable) => {
    if (!validateForm()) {
      showError('Please correct the form errors before submitting')
      return { success: false, error: 'Please fix form errors' }
    }

    formLoading.value = true

    try {
      // Prepare data for backend
      const backendData = {
        supplier_name: formData.name,
        contact_person: formData.contactPerson,
        email: formData.email,
        phone_number: formData.phone,
        address: formData.address,
        type: formData.type,
        notes: formData.notes
      }

      let response
      let message

      if (isEditMode.value && selectedSupplier.value) {
        // UPDATE existing supplier
        response = await api.put(`/suppliers/${selectedSupplier.value.id}/`, backendData)
        message = `${formData.name} has been updated successfully`
        
        // Transform response
        const updatedSupplier = {
          id: response.data._id,
          name: response.data.supplier_name,
          email: response.data.email || '',
          phone: response.data.phone_number || '',
          address: response.data.address || '',
          contactPerson: response.data.contact_person || '',
          purchaseOrders: response.data.purchase_orders?.length || 0,
          status: response.data.isDeleted ? 'inactive' : 'active',
          type: response.data.type || 'food',
          createdAt: response.data.created_at,
          updatedAt: response.data.updated_at,
          notes: response.data.notes || '',
          raw: response.data
        }

        // Update in local state - FIXED: Add null checks
        if (suppliersComposable && suppliersComposable.suppliers && Array.isArray(suppliersComposable.suppliers.value)) {
          const index = suppliersComposable.suppliers.value.findIndex(
            s => s.id === selectedSupplier.value.id
          )
          if (index !== -1) {
            suppliersComposable.suppliers.value[index] = updatedSupplier
          }
        }
        
      } else {
        // CREATE new supplier
        response = await api.post('/suppliers/', backendData)
        message = `${formData.name} has been added as a new supplier`
        
        // Add to local state
        const newSupplier = {
          id: response.data._id,
          name: response.data.supplier_name,
          email: response.data.email || '',
          phone: response.data.phone_number || '',
          address: response.data.address || '',
          contactPerson: response.data.contact_person || '',
          purchaseOrders: 0,
          status: 'active',
          type: response.data.type || 'food',
          createdAt: response.data.created_at,
          updatedAt: response.data.updated_at,
          notes: response.data.notes || '',
          raw: response.data
        }
        
        // FIXED: Add null checks before adding to suppliers list
        if (suppliersComposable && suppliersComposable.suppliers && Array.isArray(suppliersComposable.suppliers.value)) {
          suppliersComposable.suppliers.value.unshift(newSupplier)
        }
      }

      // Update report data - FIXED: Add null checks
      if (suppliersComposable && suppliersComposable.updateReportData && typeof suppliersComposable.updateReportData === 'function') {
        suppliersComposable.updateReportData()
      }

      // Show success toast
      success(message)

      // Handle modal closure - FIXED: Always close modal on success
      if (!isEditMode.value && addAnotherAfterSave.value) {
        // Keep modal open for another entry, just reset form
        resetForm()
      } else {
        // Close modal automatically
        setTimeout(() => {
          closeAddModal()
        }, 100) // Small delay to ensure state updates
      }

      return { success: true, message }
      
    } catch (error) {
      console.error('Error saving supplier:', error)
      
      let errorMessage = 'Failed to save supplier'
      
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.statusText) {
        errorMessage = `Failed to save supplier: ${error.response.statusText}`
      } else if (error.message) {
        errorMessage = error.message
      }
      
      // Show error toast
      showError(errorMessage)
      
      return { success: false, error: errorMessage }
      
    } finally {
      formLoading.value = false
    }
  }

  return {
    // State
    showAddModal,
    isEditMode,
    formLoading,
    selectedSupplier,
    addAnotherAfterSave,
    formData,
    formErrors,
    
    // Computed
    isFormValid,
    
    // Methods
    showAddSupplierModal,
    editSupplier,
    closeAddModal,
    resetForm,
    validateForm,
    clearFormError,
    saveSupplier
  }
}