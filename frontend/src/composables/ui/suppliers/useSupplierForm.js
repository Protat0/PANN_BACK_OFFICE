// composables/useSupplierForm.js
import { ref, reactive, computed } from 'vue'

export function useSupplierForm() {
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

  const saveSupplier = async (suppliers) => {
    if (!validateForm()) return

    formLoading.value = true

    try {
      if (isEditMode.value) {
        // Mock update - replace with actual API call
        const index = suppliers.findIndex(s => s.id === selectedSupplier.value.id)
        if (index !== -1) {
          suppliers[index] = {
            ...suppliers[index],
            ...formData
          }
        }
        return { success: true, message: `Supplier "${formData.name}" updated successfully` }
      } else {
        // Mock create - replace with actual API call
        const newSupplier = {
          id: Date.now(),
          ...formData,
          purchaseOrders: 0,
          createdAt: new Date().toISOString().split('T')[0]
        }
        suppliers.push(newSupplier)
        
        if (!addAnotherAfterSave.value) {
          closeAddModal()
        } else {
          resetForm()
        }
        
        return { success: true, message: `Supplier "${formData.name}" created successfully` }
      }
    } catch (error) {
      console.error('Error saving supplier:', error)
      formErrors.value.general = error.message
      return { success: false, error: error.message }
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