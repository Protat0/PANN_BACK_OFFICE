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
      <div class="modal-header d-flex justify-content-between align-items-center">
        <h3 class="text-primary mb-0 fw-semibold">
          {{ getModalTitle() }}
        </h3>

        <!-- Right-side buttons -->
        <div class="d-flex align-items-center gap-2">
          <!-- ✅ Purple Edit button beside Close -->
  
          <button 
            class="btn-close"
            @click="closeModal"
            :disabled="isLoading"
            aria-label="Close"
          >
            <X :size="20" />
          </button>
        </div>
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

        <!-- Customer Information -->
        <form @submit.prevent="handleSubmit">
          <!-- Username -->
          <div class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Username <span class="text-error">*</span>
            </label>
            <input
              v-model="form.username"
              type="text"
              class="form-control"
              placeholder="Enter unique username"
              required
              :disabled="isLoading || currentMode === 'edit'"
            />
            <small class="form-text text-tertiary-medium">
              {{ currentMode === 'edit' ? 'Username cannot be changed' : 'Username must be unique and cannot be changed later' }}
            </small>
          </div>

          <!-- Full Name -->
          <div class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Full Name <span v-if="mode !== 'view'" class="text-error">*</span>
            </label>
            <input
              v-if="mode !== 'view'"
              v-model="form.full_name"
              type="text"
              class="form-control"
              placeholder="Enter customer's full name"
              required
              :disabled="isLoading"
            />
            <div v-else class="form-control-plaintext text-primary fw-medium">
              {{ form.full_name || 'Not provided' }}
            </div>
          </div>

          <!-- Email -->
          <div class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Email Address <span v-if="mode !== 'view'" class="text-error">*</span>
            </label>
            <input
              v-if="mode !== 'view'"
              v-model="form.email"
              type="email"
              class="form-control"
              placeholder="customer@example.com"
              required
              :disabled="isLoading"
            />
            <div v-else class="form-control-plaintext text-secondary">
              {{ form.email || 'Not provided' }}
            </div>
          </div>

          <!-- Password (for new customers) -->
          <div v-if="currentMode === 'create'" class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Password <span class="text-error">*</span>
            </label>
            <input
              v-model="form.password"
              type="password"
              class="form-control"
              placeholder="Enter password for customer account"
              required
              minlength="6"
              :disabled="isLoading"
            />
            <small class="form-text text-tertiary-medium">
              Minimum 6 characters
            </small>
          </div>

          <!-- Change Password Section (for editing customers) -->
          <div v-if="currentMode === 'edit'" class="mb-4">
            <div class="d-flex align-items-center justify-content-between mb-2">
              <label class="form-label text-secondary fw-medium mb-0">
                Password
              </label>
              <button
                type="button"
                class="btn btn-sm btn-secondary"
                @click="togglePasswordChange"
                :disabled="isLoading"
              >
                {{ showPasswordFields ? 'Cancel Password Change' : 'Change Password' }}
              </button>
            </div>
            
            <!-- Password Change Fields -->
            <div v-if="showPasswordFields" class="password-change-section">
              <div class="mb-3">
                <input
                  v-model="form.new_password"
                  type="password"
                  class="form-control"
                  placeholder="Enter new password"
                  minlength="6"
                  :disabled="isLoading"
                />
                <small class="form-text text-tertiary-medium">
                  Minimum 6 characters
                </small>
              </div>
              <div>
                <input
                  v-model="form.confirm_password"
                  type="password"
                  class="form-control"
                  placeholder="Confirm new password"
                  :class="{ 'is-invalid': passwordMismatch }"
                  :disabled="isLoading"
                />
                <div v-if="passwordMismatch" class="invalid-feedback d-block">
                  Passwords do not match
                </div>
              </div>
            </div>
            
            <small v-else class="form-text text-tertiary-medium">
              Click "Change Password" to update customer's password
            </small>
          </div>

          <!-- Phone -->
          <div class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Phone Number
            </label>
            <input
              v-if="mode !== 'view'"
              v-model="form.phone"
              type="tel"
              class="form-control"
              placeholder="+1 (555) 123-4567"
              :disabled="isLoading"
            />
            <div v-else class="form-control-plaintext text-secondary">
              {{ form.phone || 'Not provided' }}
            </div>
          </div>

          <!-- Delivery Address -->
          <div class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Delivery Address
            </label>
            <div class="address-fields">
              <div class="row g-2">
                <div class="col-12">
                  <input
                    v-model="form.delivery_address.street"
                    type="text"
                    class="form-control mb-2"
                    placeholder="Street address"
                    :disabled="isLoading || currentMode === 'view'"
                  />
                </div>
                <div class="col-6">
                  <input
                    v-model="form.delivery_address.city"
                    type="text"
                    class="form-control"
                    placeholder="City"
                    :disabled="isLoading || currentMode === 'view'"
                  />
                </div>
                <div class="col-6">
                  <input
                    v-model="form.delivery_address.barangay"
                    type="text"
                    class="form-control"
                    placeholder="Barangay"
                    :disabled="isLoading || currentMode === 'view'"
                  />
                </div>
                <div class="col-6">
                  <input
                    v-model="form.delivery_address.postal_code"
                    type="text"
                    class="form-control"
                    placeholder="Postal code"
                    :disabled="isLoading || currentMode === 'view'"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Loyalty Points -->
          <div v-if="mode !== 'create'" class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Loyalty Points
            </label>
            <input
              v-if="mode === 'edit'"
              v-model.number="form.loyalty_points"
              type="number"
              min="0"
              class="form-control"
              placeholder="0"
              :disabled="isLoading"
            />
            <div v-else class="form-control-plaintext">
              <span class="badge bg-success text-inverse fw-medium">
                {{ form.loyalty_points || 0 }} points
              </span>
            </div>
          </div>

          <!-- Status -->
          <div v-if="mode !== 'create'" class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Status
            </label>
            <select
              v-if="mode === 'edit'"
              v-model="form.status"
              class="form-select"
              :disabled="isLoading"
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
            <div v-else class="form-control-plaintext">
              <span 
                class="badge fw-medium"
                :class="form.status === 'active' ? 'bg-success text-inverse' : 'surface-tertiary text-tertiary border-theme'"
              >
                {{ form.status || 'active' }}
              </span>
            </div>
          </div>

          <!-- Date Created (view mode only) -->
          <div v-if="mode === 'view'" class="mb-4">
            <label class="form-label text-secondary fw-medium mb-2">
              Date Created
            </label>
            <div class="form-control-plaintext text-tertiary small">
              {{ formatDate(customer?.date_created) }}
            </div>
          </div>
        </form>
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <div class="d-flex justify-content-end gap-3">
            <button 
            v-if="mode === 'view'"
            class="btn btn-edit btn-sm d-flex align-items-center gap-1"
            @click="switchToEditMode"
            :disabled="isLoading"
          >
            <Edit :size="16" />
            Edit
          </button>

          <button
            type="button"
            class="btn btn-cancel"
            @click="closeModal"
            :disabled="isLoading"
          >
            {{ mode === 'view' ? 'Close' : 'Cancel' }}
          </button>
          <button
            v-if="mode !== 'view'"
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
import { ref, computed, watch, nextTick } from 'vue'
import { X, Edit, AlertTriangle } from 'lucide-vue-next'
import { useModal } from '@/composables/ui/useModal.js'
import { useCustomers } from '@/composables/api/useCustomers.js'

// Props
const props = defineProps({
  mode: {
    type: String,
    default: 'create',
    validator: (value) => ['create', 'edit', 'view'].includes(value)
  },
  customer: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['close', 'success', 'mode-changed'])

// Composables
const { isVisible, isLoading, error, show, hide, setLoading, setError, clearError } = useModal()
const { createCustomer, updateCustomer } = useCustomers()

// Form data
const form = ref({
  username: '',
  full_name: '',
  email: '',
  phone: '',
  password: '',
  new_password: '',
  confirm_password: '',
  delivery_address: {
    street: '',
    city: '',
    barangay: '',
    postal_code: ''
  },
  loyalty_points: 0,
  status: 'active'
})

// Local mode state for switching between view/edit
const currentMode = ref(props.mode)
const showPasswordFields = ref(false)

// Computed
const passwordMismatch = computed(() => {
  if (!showPasswordFields.value) return false
  if (!form.value.new_password || !form.value.confirm_password) return false
  return form.value.new_password !== form.value.confirm_password
})

const isFormValid = computed(() => {
  const hasRequiredFields = form.value.username.trim() && 
                           form.value.full_name.trim() && 
                           form.value.email.trim()
  
  // For create mode, password is required
  if (currentMode.value === 'create') {
    return hasRequiredFields && form.value.password.trim() && form.value.password.length >= 6
  }
  
  // For edit mode, if password change is enabled, validate passwords
  if (currentMode.value === 'edit' && showPasswordFields.value) {
    const hasValidPassword = form.value.new_password && 
                            form.value.new_password.length >= 6 &&
                            form.value.new_password === form.value.confirm_password
    return hasRequiredFields && hasValidPassword
  }
  
  return hasRequiredFields
})

// Methods
const getModalTitle = () => {
  switch (currentMode.value) {
    case 'view': return 'Customer Details'
    case 'edit': return 'Edit Customer'
    default: return 'Add New Customer'
  }
}

const switchToEditMode = () => {
  currentMode.value = 'edit'
  emit('mode-changed', 'edit')
}

const togglePasswordChange = () => {
  showPasswordFields.value = !showPasswordFields.value
  if (!showPasswordFields.value) {
    form.value.new_password = ''
    form.value.confirm_password = ''
  }
}

const openModal = () => {
  clearError()
  showPasswordFields.value = false
  currentMode.value = props.mode
  if ((props.mode === 'edit' || props.mode === 'view') && props.customer) {
    populateForm()
  } else {
    resetForm()
  }
  show()
}

const closeModal = () => {
  if (!isLoading.value) {
    showPasswordFields.value = false
    currentMode.value = props.mode // Reset to original mode
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
    username: '',
    full_name: '',
    email: '',
    phone: '',
    password: '',
    new_password: '',
    confirm_password: '',
    delivery_address: {
      street: '',
      city: '',
      barangay: '',
      postal_code: ''
    },
    loyalty_points: 0,
    status: 'active'
  }
  showPasswordFields.value = false
}

const populateForm = () => {
  if (props.customer) {
    form.value = {
      username: props.customer.username || '',
      full_name: props.customer.full_name || '',
      email: props.customer.email || '',
      phone: props.customer.phone || '',
      password: '', // Never populate password for security
      new_password: '',
      confirm_password: '',
      delivery_address: {
        street: props.customer.delivery_address?.street || '',
        city: props.customer.delivery_address?.city || '',
        barangay: props.customer.delivery_address?.barangay || '',
        postal_code: props.customer.delivery_address?.postal_code || ''
      },
      loyalty_points: props.customer.loyalty_points || 0,
      status: props.customer.status || 'active'
    }
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'Invalid Date'
  }
}

const handleSubmit = async () => {
  if (!isFormValid.value || isLoading.value || currentMode.value === 'view') return

  setLoading(true)
  clearError()

  try {
    const customerData = {
      username: form.value.username.trim(),
      full_name: form.value.full_name.trim(),
      email: form.value.email.trim(),
      phone: form.value.phone.trim(),
      delivery_address: form.value.delivery_address
    }

    // For create mode, password is required
    if (currentMode.value === 'create') {
      customerData.password = form.value.password
    } 
    // For edit mode, only include password if changing it
    else if (currentMode.value === 'edit') {
      customerData.loyalty_points = form.value.loyalty_points
      customerData.status = form.value.status
      
      // Include new password only if user chose to change it
      if (showPasswordFields.value && form.value.new_password) {
        customerData.password = form.value.new_password
      }
    }

    let result
    if (currentMode.value === 'edit') {
      const customerId = props.customer._id || props.customer.customer_id
      result = await updateCustomer(customerId, customerData)
    } else {
      result = await createCustomer(customerData)
    }

    emit('success', result)

    await nextTick()

    resetForm()
    closeModal()
    
  } catch (err) {
    setError(err.message || `Failed to ${currentMode.value === 'edit' ? 'update' : 'create'} customer`)
  } finally {
    setLoading(false)
  }
}

// Watch for customer prop changes
watch(() => props.customer, () => {
  if ((props.mode === 'edit' || props.mode === 'view') && props.customer && isVisible.value) {
    populateForm()
  }
})

// Watch for mode prop changes
watch(() => props.mode, (newMode) => {
  currentMode.value = newMode
})

// Expose methods for parent component
defineExpose({
  openModal,
  closeModal
})
</script>

<style scoped>
/* All existing styles remain the same */
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

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-secondary);
  background-color: var(--surface-primary);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-body {
  padding: 1.5rem;
  max-height: 60vh;
  overflow-y: auto;
  background-color: var(--surface-primary);
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--border-secondary);
  background-color: var(--surface-secondary);
}

/* New Password Change Section Styles */
.password-change-section {
  padding: 1rem;
  background-color: var(--surface-secondary);
  border: 1px solid var(--border-secondary);
  border-radius: 0.5rem;
  margin-top: 0.5rem;
}

.form-control:focus,
.form-select:focus {
  border-color: var(--border-accent) !important;
  box-shadow: 0 0 0 0.25rem rgba(160, 123, 227, 0.25) !important;
}

.form-text {
  font-size: 0.875em;
  color: var(--text-tertiary-medium);
  margin-top: 0.25rem;
  display: block;
}

.form-label {
  display: block;
}

.is-invalid {
  border-color: var(--border-error) !important;
}

.invalid-feedback {
  display: none;
  width: 100%;
  margin-top: 0.25rem;
  font-size: 0.875em;
  color: var(--status-error);
}

.invalid-feedback.d-block {
  display: block !important;
}

.address-fields .row {
  margin: 0;
}

.address-fields .col-12,
.address-fields .col-6 {
  padding: 0 0.25rem;
}

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

.d-flex { display: flex; }
.justify-content-between { justify-content: space-between; }
.justify-content-end { justify-content: flex-end; }
.align-items-center { align-items: center; }
.gap-2 { gap: 0.5rem; }
.gap-3 { gap: 0.75rem; }
.mb-0 { margin-bottom: 0; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-3 { margin-bottom: 0.75rem; }
.mb-4 { margin-bottom: 1rem; }
.me-1 { margin-right: 0.25rem; }
.me-2 { margin-right: 0.5rem; }
.fw-medium { font-weight: 500; }
.fw-semibold { font-weight: 600; }

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

.form-control-plaintext {
  display: block;
  width: 100%;
  padding: 0.375rem 0;
  margin-bottom: 0;
  line-height: 1.5;
  background-color: transparent;
  border: none;
  border-bottom: 1px solid transparent;
}

.small {
  font-size: 0.875rem;
}

.text-wrap {
  word-wrap: break-word;
  white-space: pre-wrap;
}

/* Badge styles */
.badge {
  display: inline-block;
  padding: 0.35em 0.65em;
  font-size: 0.75em;
  font-weight: 600;
  line-height: 1;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: 0.25rem;
}

.bg-success {
  background-color: var(--status-success) !important;
  color: white !important;
}

.btn-edit {
  background-color: var(--accent, #6c3ef0);
  color: #fff;
  border: none;
  padding: 0.35rem 0.75rem;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-edit:hover:not(:disabled) {
  background-color: #5a32c8;
}

.btn-edit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>