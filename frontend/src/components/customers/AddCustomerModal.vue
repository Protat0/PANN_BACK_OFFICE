<template>
  <!-- Modal Backdrop -->
  <div 
    v-if="isVisible" 
    class="modal-backdrop"
    @click="handleBackdropClick"
  >
    <!-- Modal Container -->
    <div 
      class="modal-container"
      @click.stop
    >
      <!-- Modal Header -->
      <div class="modal-header">
        <h3 class="text-primary mb-0 fw-semibold">
          {{ mode === 'edit' ? 'Edit Customer' : 'Add New Customer' }}
        </h3>
        <button 
          class="btn-close"
          @click="closeModal"
          :disabled="isLoading"
          aria-label="Close"
        >
          <X :size="20" />
        </button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <!-- Error Message -->
        <div v-if="error" class="status-error mb-4">
          <div class="d-flex align-items-center gap-2">
            <AlertTriangle :size="16" />
            <span class="text-status-error fw-medium">{{ error }}</span>
          </div>
        </div>

        <!-- Customer Form -->
        <form @submit.prevent="handleSubmit">
          <!-- Full Name -->
          <div class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Full Name <span class="text-error">*</span>
            </label>
            <input
              v-model="form.full_name"
              type="text"
              class="form-control"
              placeholder="Enter customer's full name"
              required
              :disabled="isLoading"
            />
          </div>

          <!-- Email -->
          <div class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Email Address <span class="text-error">*</span>
            </label>
            <input
              v-model="form.email"
              type="email"
              class="form-control"
              placeholder="customer@example.com"
              required
              :disabled="isLoading"
            />
          </div>

          <!-- Phone -->
          <div class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Phone Number
            </label>
            <input
              v-model="form.phone"
              type="tel"
              class="form-control"
              placeholder="+1 (555) 123-4567"
              :disabled="isLoading"
            />
          </div>

          <!-- Password (only for new customers) -->
          <div v-if="mode === 'create'" class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Password <span class="text-error">*</span>
            </label>
            <input
              v-model="form.password"
              type="password"
              class="form-control"
              placeholder="Enter password for customer account"
              required
              :disabled="isLoading"
            />
          </div>

          <!-- Delivery Address -->
          <div class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Delivery Address
            </label>
            <textarea
              v-model="form.delivery_address"
              class="form-control"
              rows="3"
              placeholder="Street address, city, state, zip code"
              :disabled="isLoading"
            ></textarea>
          </div>

          <!-- Loyalty Points (only for edit mode) -->
          <div v-if="mode === 'edit'" class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Loyalty Points
            </label>
            <input
              v-model.number="form.loyalty_points"
              type="number"
              min="0"
              class="form-control"
              placeholder="0"
              :disabled="isLoading"
            />
          </div>

          <!-- Status (only for edit mode) -->
          <div v-if="mode === 'edit'" class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Status
            </label>
            <select
              v-model="form.status"
              class="form-select"
              :disabled="isLoading"
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </form>
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <div class="d-flex justify-content-end gap-3">
          <button
            type="button"
            class="btn btn-cancel"
            @click="closeModal"
            :disabled="isLoading"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-submit btn-with-icon"
            @click="handleSubmit"
            :disabled="isLoading || !isFormValid"
          >
            <div v-if="isLoading" class="spinner-border spinner-border-sm me-2"></div>
            {{ isLoading ? 'Saving...' : (mode === 'edit' ? 'Update Customer' : 'Add Customer') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useModal } from '@/composables/ui/useModal.js'
import { useCustomers } from '@/composables/api/useCustomers.js'

// Props
const props = defineProps({
  mode: {
    type: String,
    default: 'create',
    validator: (value) => ['create', 'edit'].includes(value)
  },
  customer: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['close', 'success'])

// Composables
const { isVisible, isLoading, error, show, hide, setLoading, setError, clearError } = useModal()
const { createCustomer, updateCustomer } = useCustomers()

// Form data
const form = ref({
  full_name: '',
  email: '',
  phone: '',
  password: '',
  delivery_address: '',
  loyalty_points: 0,
  status: 'active'
})

// Computed
const isFormValid = computed(() => {
  const hasRequiredFields = form.value.full_name.trim() && form.value.email.trim()
  const hasPasswordForCreate = props.mode === 'edit' || form.value.password.trim()
  return hasRequiredFields && hasPasswordForCreate
})

// Methods
const openModal = () => {
  clearError()
  if (props.mode === 'edit' && props.customer) {
    populateForm()
  } else {
    resetForm()
  }
  show()
}

const closeModal = () => {
  if (!isLoading.value) {
    hide()
    emit('close')
  }
}

const handleBackdropClick = () => {
  if (!isLoading.value) {
    closeModal()
  }
}

const resetForm = () => {
  form.value = {
    full_name: '',
    email: '',
    phone: '',
    password: '',
    delivery_address: '',
    loyalty_points: 0,
    status: 'active'
  }
}

const populateForm = () => {
  if (props.customer) {
    form.value = {
      full_name: props.customer.full_name || '',
      email: props.customer.email || '',
      phone: props.customer.phone || '',
      password: '',
      delivery_address: typeof props.customer.delivery_address === 'string' 
        ? props.customer.delivery_address 
        : props.customer.delivery_address?.street || '',
      loyalty_points: props.customer.loyalty_points || 0,
      status: props.customer.status || 'active'
    }
  }
}

const handleSubmit = async () => {
  if (!isFormValid.value || isLoading.value) return

  setLoading(true)
  clearError()

  try {
    const customerData = {
      full_name: form.value.full_name.trim(),
      email: form.value.email.trim(),
      phone: form.value.phone.trim(),
      delivery_address: form.value.delivery_address.trim(),
    }

    if (props.mode === 'create') {
      customerData.password = form.value.password
    }

    if (props.mode === 'edit') {
      customerData.loyalty_points = form.value.loyalty_points
      customerData.status = form.value.status
    }

    let result
    if (props.mode === 'edit') {
      const customerId = props.customer._id || props.customer.customer_id
      result = await updateCustomer(customerId, customerData)
    } else {
      result = await createCustomer(customerData)
    }

    emit('success', result)
    closeModal()
    
  } catch (err) {
    setError(err.message || `Failed to ${props.mode === 'edit' ? 'update' : 'create'} customer`)
  } finally {
    setLoading(false)
  }
}

// Watch for customer prop changes
watch(() => props.customer, () => {
  if (props.mode === 'edit' && props.customer && isVisible.value) {
    populateForm()
  }
})

// Expose methods for parent component
defineExpose({
  openModal,
  closeModal
})
</script>

<style scoped>
/* Modal Backdrop - Fixed positioning */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  animation: fadeIn 0.2s ease-out;
}

/* Modal Container */
.modal-container {
  background-color: var(--surface-elevated);
  border: 1px solid var(--border-primary);
  border-radius: 0.75rem;
  box-shadow: var(--shadow-2xl);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
  position: relative;
}

/* Modal Header */
.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-secondary);
  background-color: var(--surface-primary);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Modal Body */
.modal-body {
  padding: 1.5rem;
  max-height: 60vh;
  overflow-y: auto;
  background-color: var(--surface-primary);
}

/* Modal Footer */
.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--border-secondary);
  background-color: var(--surface-secondary);
}

/* Form styling */
.form-control:focus,
.form-select:focus {
  border-color: var(--border-accent) !important;
  box-shadow: 0 0 0 0.25rem rgba(160, 123, 227, 0.25) !important;
}

.form-label {
  display: block;
}

/* Loading spinner */
.spinner-border {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  vertical-align: text-bottom;
  border: 0.125em solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spinner-border 0.75s linear infinite;
}

.spinner-border-sm {
  width: 0.875rem;
  height: 0.875rem;
  border-width: 0.125em;
}

.btn-close {
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 0.375rem;
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  background-color: var(--state-hover);
  color: var(--text-secondary);
}

.btn-close:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(1rem) scale(0.95);
  }
  to { 
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes spinner-border {
  to { transform: rotate(360deg); }
}

/* Utility classes */
.d-flex { display: flex; }
.justify-content-between { justify-content: space-between; }
.justify-content-end { justify-content: flex-end; }
.align-items-center { align-items: center; }
.gap-2 { gap: 0.5rem; }
.gap-3 { gap: 0.75rem; }
.mb-0 { margin-bottom: 0; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-4 { margin-bottom: 1rem; }
.me-2 { margin-right: 0.5rem; }
.fw-medium { font-weight: 500; }
.fw-semibold { font-weight: 600; }

/* Responsive adjustments */
@media (max-width: 640px) {
  .modal-container {
    margin: 0.5rem;
    max-height: 95vh;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 1rem;
  }
}
</style>