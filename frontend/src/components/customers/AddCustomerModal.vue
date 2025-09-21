<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <!-- Modal Header -->
      <div class="modal-header">
        <h2 class="modal-title">
          {{ mode === 'add' ? 'Add New Customer' : mode === 'edit' ? 'Edit Customer' : 'Customer Details' }}
        </h2>
        <button 
          type="button" 
          class="btn btn-cancel btn-sm btn-icon-only"
          @click="closeModal"
        >
          <X :size="16" />
        </button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <!-- View Mode -->
        <div v-if="mode === 'view'" class="customer-details">
          <div class="row mb-2">
            <div class="col-4 fw-bold detail-label">ID:</div>
            <div class="col-8 detail-value">{{ customer.customer_id || customer._id }}</div>
          </div>
          
          <div class="row mb-2">
            <div class="col-4 fw-bold detail-label">Name:</div>
            <div class="col-8 detail-value">{{ customer.full_name }}</div>
          </div>
          
          <div class="row mb-2">
            <div class="col-4 fw-bold detail-label">Username:</div>
            <div class="col-8 detail-value">{{ customer.username }}</div>
          </div>

          <div class="row mb-2">
            <div class="col-4 fw-bold detail-label">Email:</div>
            <div class="col-8 detail-value">{{ customer.email }}</div>
          </div>
          
          <div class="row mb-2">
            <div class="col-4 fw-bold detail-label">Phone:</div>
            <div class="col-8 detail-value">{{ customer.phone || 'N/A' }}</div>
          </div>
          
          <div class="row mb-2">
            <div class="col-4 fw-bold detail-label">Address:</div>
            <div class="col-8 detail-value">{{ formatAddress(customer.delivery_address) }}</div>
          </div>
          
          <div class="row mb-2">
            <div class="col-4 fw-bold detail-label">Loyalty Points:</div>
            <div class="col-8">
              <span class="badge bg-success">{{ customer.loyalty_points || 0 }}</span>
            </div>
          </div>
          
          <div class="row mb-2">
            <div class="col-4 fw-bold detail-label">Status:</div>
            <div class="col-8">
              <span class="badge" :class="customer.status === 'active' ? 'bg-success' : 'bg-secondary'">
                {{ customer.status || 'active' }}
              </span>
            </div>
          </div>
          
          <div class="row mb-2">
            <div class="col-4 fw-bold detail-label">Date Created:</div>
            <div class="col-8 detail-value">{{ formatDate(customer.date_created) }}</div>
          </div>
          
          <div class="row mb-3">
            <div class="col-4 fw-bold detail-label">Last Updated:</div>
            <div class="col-8 detail-value">{{ formatDate(customer.last_updated) }}</div>
          </div>
        </div>

        <!-- Add/Edit Mode -->
        <form v-else @submit.prevent="handleSubmit">
          <div class="mb-3">
            <label for="username" class="form-label">Username <span class="text-danger">*</span></label>
            <input 
              id="username"
              v-model="form.username" 
              type="text" 
              class="form-control"
              :class="{ 'is-invalid': errors.username }"
              required 
              :disabled="formLoading"
              placeholder="Enter username"
            />
            <div v-if="errors.username" class="invalid-feedback">{{ errors.username }}</div>
          </div>
          
          <div class="mb-3">
            <label for="full_name" class="form-label">Full Name <span class="text-danger">*</span></label>
            <input 
              id="full_name"
              v-model="form.full_name" 
              type="text" 
              class="form-control"
              :class="{ 'is-invalid': errors.full_name }"
              required 
              :disabled="formLoading"
              placeholder="Enter full name"
            />
            <div v-if="errors.full_name" class="invalid-feedback">{{ errors.full_name }}</div>
          </div>

          <div class="mb-3">
            <label for="email" class="form-label">Email <span class="text-danger">*</span></label>
            <input 
              id="email"
              v-model="form.email" 
              type="email" 
              class="form-control"
              :class="{ 'is-invalid': errors.email }"
              required 
              :disabled="formLoading"
              placeholder="Enter email address"
            />
            <div v-if="errors.email" class="invalid-feedback">{{ errors.email }}</div>
          </div>

          <!-- NEW PASSWORD FIELD -->
          <div v-if="mode === 'add'" class="mb-3">
            <label for="password" class="form-label">Password <span class="text-danger">*</span></label>
            <input 
              id="password"
              v-model="form.password" 
              type="password" 
              class="form-control"
              :class="{ 'is-invalid': errors.password }"
              required 
              :disabled="formLoading"
              placeholder="Enter customer password"
              minlength="6"
            />
            <div v-if="errors.password" class="invalid-feedback">{{ errors.password }}</div>
        
          </div>

          <div class="mb-3">
            <label for="phone" class="form-label">Phone</label>
            <input 
              id="phone"
              v-model="form.phone" 
              type="tel" 
              class="form-control"
              :class="{ 'is-invalid': errors.phone }"
              :disabled="formLoading"
              placeholder="Enter phone number"
            />
            <div v-if="errors.phone" class="invalid-feedback">{{ errors.phone }}</div>
          </div>

          <div class="mb-3">
            <label for="street" class="form-label">Street Address</label>
            <input 
              id="street"
              v-model="form.delivery_address.street" 
              type="text" 
              class="form-control"
              :class="{ 'is-invalid': errors.street }"
              :disabled="formLoading"
              placeholder="Enter street address"
            />
            <div v-if="errors.street" class="invalid-feedback">{{ errors.street }}</div>
          </div>

          <div class="row mb-3">
            <div class="col-md-6">
              <label for="city" class="form-label">City</label>
              <input 
                id="city"
                v-model="form.delivery_address.city" 
                type="text" 
                class="form-control"
                :class="{ 'is-invalid': errors.city }"
                :disabled="formLoading"
                placeholder="Enter city"
              />
              <div v-if="errors.city" class="invalid-feedback">{{ errors.city }}</div>
            </div>

            <div class="col-md-6">
              <label for="postal_code" class="form-label">Postal Code</label>
              <input 
                id="postal_code"
                v-model="form.delivery_address.postal_code" 
                type="text" 
                class="form-control"
                :class="{ 'is-invalid': errors.postal_code }"
                :disabled="formLoading"
                placeholder="Enter postal code"
              />
              <div v-if="errors.postal_code" class="invalid-feedback">{{ errors.postal_code }}</div>
            </div>
          </div>

          <div class="mb-3">
            <label for="loyalty_points" class="form-label">Loyalty Points</label>
            <input 
              id="loyalty_points"
              v-model.number="form.loyalty_points" 
              type="number" 
              class="form-control"
              :class="{ 'is-invalid': errors.loyalty_points }"
              min="0"
              :disabled="formLoading"
              placeholder="0"
            />
            <div v-if="errors.loyalty_points" class="invalid-feedback">{{ errors.loyalty_points }}</div>
          </div>

          <!-- Error Display -->
          <div v-if="generalError" class="alert alert-danger">
            {{ generalError }}
          </div>
        </form>
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <div class="d-flex justify-content-end gap-2">
          <button 
            type="button" 
            class="btn btn-cancel" 
            @click="closeModal" 
            :disabled="formLoading"
          >
            Cancel
          </button>
          
          <!-- View Mode Actions -->
          <template v-if="mode === 'view'">
            <button 
              class="btn btn-edit btn-with-icon" 
              @click="switchToEditMode"
              :disabled="loading"
            >
              <Edit :size="16" />
              <span>Edit</span>
            </button>
          </template>
          
          <!-- Add/Edit Mode Actions -->
          <template v-else>
            <button 
              type="submit" 
              class="btn btn-save" 
              @click="handleSubmit"
              :disabled="formLoading"
            >
              {{ formLoading ? 'Saving...' : (mode === 'edit' ? 'Update' : 'Create') }}
            </button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { X, Edit } from 'lucide-vue-next'
import { useCustomers } from '@/composables/ui/customers/useCustomers'
import { ref, watch, computed } from 'vue'

export default {
  name: 'AddCustomerModal',
  components: {
    X,
    Edit
  },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    mode: {
      type: String,
      default: 'add',
      validator: value => ['add', 'edit', 'view'].includes(value)
    },
    customer: {
      type: Object,
      default: () => null
    }
  },
  emits: ['close', 'edit-mode'],
  setup(props, { emit }) {
    // Use the customers composable
    const {
      formLoading,
      formError,
      saveCustomer,
      formatAddress,
      formatDate
    } = useCustomers()

    // Local form state - Added password field
    const form = ref({
      username: '',
      full_name: '',
      email: '',
      password: '', // ← NEW FIELD ADDED
      phone: '',
      delivery_address: {
        street: '',
        city: '',
        postal_code: ''
      },
      loyalty_points: 0
    })

    const errors = ref({})

    // Initialize form when modal opens or customer changes
    const initializeForm = () => {
      if (props.mode === 'add') {
        form.value = {
          username: '',
          full_name: '',
          email: '',
          password: '', // ← NEW FIELD ADDED
          phone: '',
          delivery_address: {
            street: '',
            city: '',
            postal_code: ''
          },
          loyalty_points: 0
        }
      } else if (props.customer && (props.mode === 'edit' || props.mode === 'view')) {
        form.value = {
          username: props.customer.username || '',
          full_name: props.customer.full_name || '',
          email: props.customer.email || '',
          password: '', // ← Don't populate password for edit mode
          phone: props.customer.phone || '',
          delivery_address: {
            street: props.customer.delivery_address?.street || '',
            city: props.customer.delivery_address?.city || '',
            postal_code: props.customer.delivery_address?.postal_code || ''
          },
          loyalty_points: props.customer.loyalty_points || 0
        }
      }
    }

    const clearErrors = () => {
      errors.value = {}
    }

    const validateForm = () => {
      errors.value = {}
      let isValid = true

      // Required field validations
      if (!form.value.username?.trim()) {
        errors.value.username = 'Username is required'
        isValid = false
      }

      if (!form.value.full_name?.trim()) {
        errors.value.full_name = 'Full name is required'
        isValid = false
      }

      if (!form.value.email?.trim()) {
        errors.value.email = 'Email is required'
        isValid = false
      } else if (!isValidEmail(form.value.email)) {
        errors.value.email = 'Please enter a valid email address'
        isValid = false
      }

      // Password validation - only required for add mode
      if (props.mode === 'add') {
        if (!form.value.password?.trim()) {
          errors.value.password = 'Password is required'
          isValid = false
        } else if (form.value.password.length < 6) {
          errors.value.password = 'Password must be at least 6 characters long'
          isValid = false
        }
      }

      // Loyalty points validation
      if (form.value.loyalty_points < 0) {
        errors.value.loyalty_points = 'Loyalty points cannot be negative'
        isValid = false
      }

      return isValid
    }

    const isValidEmail = (email) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    }

    // In AddCustomerModal.vue - modify the handleSubmit function
  const handleSubmit = async () => {
    clearErrors()
    
    if (!validateForm()) {
      return
    }

    try {
      const submitData = { ...form.value }
      if (props.mode === 'edit' && !submitData.password) {
        delete submitData.password
      }
      
      console.log('=== MODAL SUBMIT DEBUG ===')
      console.log('Props mode:', props.mode)
      console.log('Props customer:', props.customer)
      console.log('Submit data:', submitData)
      
      // Pass mode and customer info directly to saveCustomer
      if (props.mode === 'edit' && props.customer) {
        const customerId = props.customer._id || props.customer.customer_id
        await saveCustomer(submitData, 'edit', customerId)
      } else {
        await saveCustomer(submitData, 'add')
      }
      
      emit('close')
    } catch (error) {
      console.error('Form submission error:', error)
    }
  }

    const switchToEditMode = () => {
      emit('edit-mode', props.customer)
    }

    const closeModal = () => {
      emit('close')
    }

    const handleOverlayClick = () => {
      if (!formLoading.value) {
        closeModal()
      }
    }

    // Watch for prop changes
    watch(() => props.show, (newVal) => {
      if (newVal) {
        initializeForm()
        clearErrors()
      }
    })

    watch(() => props.customer, (newVal) => {
      if (newVal && props.show) {
        initializeForm()
      }
    })

    // Computed property for general error display
    const generalError = computed(() => formError.value)

    return {
      form,
      errors,
      generalError,
      formLoading,
      initializeForm,
      clearErrors,
      validateForm,
      isValidEmail,
      handleSubmit,
      switchToEditMode,
      closeModal,
      handleOverlayClick,
      formatAddress,
      formatDate
    }
  }
}
</script>

<style scoped>
/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 1.5rem 2rem 1rem;
  border-bottom: 1px solid var(--neutral-light);
  display: flex;
  justify-content: between;
  align-items: center;
}

.modal-title {
  color: var(--tertiary-dark);
  font-weight: 600;
  margin: 0;
  flex-grow: 1;
}

.modal-body {
  padding: 1.5rem 2rem;
}

.modal-footer {
  padding: 1rem 2rem 1.5rem;
  border-top: 1px solid var(--neutral-light);
}

/* Form Styles */
.form-label {
  color: var(--tertiary-dark);
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.form-control:focus,
.form-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.25rem rgba(115, 146, 226, 0.25);
}

.form-text {
  font-size: 0.875em;
  color: #6c757d;
  margin-top: 0.25rem;
}

/* Detail View Styles */
.customer-details .detail-label {
  color: var(--tertiary-dark);
}

.customer-details .detail-value {
  color: var(--tertiary-medium);
}

/* Button Icon Styles */
.btn-icon-only {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  aspect-ratio: 1;
  padding: 0.375rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    max-width: none;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding-left: 1rem;
    padding-right: 1rem;
  }
}

@media (max-width: 576px) {
  .modal-header,
  .modal-body,
  .modal-footer {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
  }
  
  .modal-header {
    padding-top: 1rem;
  }
  
  .modal-footer {
    padding-bottom: 1rem;
  }
}
</style>