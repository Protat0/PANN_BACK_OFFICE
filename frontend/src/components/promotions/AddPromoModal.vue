<template>
  <div class="modal fade" id="addPromoModal" tabindex="-1" aria-labelledby="addPromoModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="addPromoModalLabel">{{ modalTitle }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <!-- Modal content based on mode -->
          <div v-if="mode === 'add'" class="add-mode">
            <form @submit.prevent="savePromotion">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Promotion Name <span class="text-danger">*</span></label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="formData.promotion_name"
                    placeholder="Enter promotion name"
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Discount Type <span class="text-danger">*</span></label>
                  <select class="form-select" v-model="formData.discount_type" required>
                    <option value="">Select discount type</option>
                    <option value="percentage">Percentage</option>
                    <option value="fixed_amount">Fixed Amount</option>
                    <option value="buy_x_get_y">Buy One Get One (BOGO)</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Discount Value <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <input 
                      type="number" 
                      class="form-control" 
                      v-model="formData.discount_value"
                      :placeholder="formData.discount_type === 'percentage' ? 'Enter percentage (e.g., 20)' : 'Enter amount (e.g., 50)'"
                      :min="formData.discount_type === 'percentage' ? 1 : 0"
                      :max="formData.discount_type === 'percentage' ? 100 : undefined"
                      step="0.01"
                      required
                    >
                    <span class="input-group-text">
                      {{ formData.discount_type === 'percentage' ? '%' : '₱' }}
                    </span>
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Status</label>
                  <select class="form-select" v-model="formData.status">
                    <option value="scheduled">Scheduled</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Start Date <span class="text-danger">*</span></label>
                  <div class="date-picker-wrapper">
                    <VueDatePicker 
                      v-model="formData.start_date"
                      :enable-time-picker="false"
                      format="MM/dd/yyyy"
                      placeholder="Select start date"
                      :min-date="new Date()"
                      class="custom-datepicker"
                      required
                    />
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">End Date <span class="text-danger">*</span></label>
                  <div class="date-picker-wrapper">
                    <VueDatePicker 
                      v-model="formData.end_date"
                      :enable-time-picker="false"
                      format="MM/dd/yyyy"
                      placeholder="Select end date"
                      :min-date="formData.start_date || new Date()"
                      class="custom-datepicker"
                      required
                    />
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Usage Limit</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="formData.usage_limit"
                    placeholder="Leave empty for unlimited"
                    min="1"
                    step="1"
                  >
                  <small class="form-text text-muted">Maximum number of times this promotion can be used (optional)</small>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Apply to Category <span class="text-danger">*</span></label>
                  <select class="form-select" v-model="formData.affected_category" required>
                    <option value="">Select category</option>
                    <option value="all">All Products</option>
                    <option value="noodles">Noodles</option>
                    <option value="drinks">Drinks</option>
                    <option value="toppings">Toppings</option>
                  </select>
                  <small class="form-text text-muted">Choose which category this promotion applies to</small>
                </div>
                <div class="col-12 mb-3">
                  <label class="form-label">Description</label>
                  <textarea 
                    class="form-control" 
                    v-model="formData.description"
                    placeholder="Enter promotion description (optional)"
                    rows="3"
                  ></textarea>
                  <small class="form-text text-muted">Add details about this promotion (optional)</small>
                </div>
              </div>
            </form>
          </div>

          <div v-if="mode === 'edit'" class="edit-mode">
            <form @submit.prevent="updatePromotion">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Promotion Name <span class="text-danger">*</span></label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="formData.promotion_name"
                    placeholder="Enter promotion name"
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Discount Type <span class="text-danger">*</span></label>
                  <select class="form-select" v-model="formData.discount_type" required>
                    <option value="">Select discount type</option>
                    <option value="percentage">Percentage</option>
                    <option value="fixed_amount">Fixed Amount</option>
                    <option value="buy_x_get_y">Buy One Get One (BOGO)</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Discount Value <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <input 
                      type="number" 
                      class="form-control" 
                      v-model="formData.discount_value"
                      :placeholder="formData.discount_type === 'percentage' ? 'Enter percentage (e.g., 20)' : 'Enter amount (e.g., 50)'"
                      :min="formData.discount_type === 'percentage' ? 1 : 0"
                      :max="formData.discount_type === 'percentage' ? 100 : undefined"
                      step="0.01"
                      required
                    >
                    <span class="input-group-text">
                      {{ formData.discount_type === 'percentage' ? '%' : '₱' }}
                    </span>
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Status</label>
                  <select class="form-select" v-model="formData.status">
                    <option value="scheduled">Scheduled</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="expired">Expired</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Start Date <span class="text-danger">*</span></label>
                  <div class="date-picker-wrapper">
                    <VueDatePicker 
                      v-model="formData.start_date"
                      :enable-time-picker="false"
                      format="MM/dd/yyyy"
                      placeholder="Select start date"
                      :min-date="new Date()"
                      class="custom-datepicker"
                      required
                    />
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">End Date <span class="text-danger">*</span></label>
                  <div class="date-picker-wrapper">
                    <VueDatePicker 
                      v-model="formData.end_date"
                      :enable-time-picker="false"
                      format="MM/dd/yyyy"
                      placeholder="Select end date"
                      :min-date="formData.start_date || new Date()"
                      class="custom-datepicker"
                      required
                    />
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Usage Limit</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="formData.usage_limit"
                    placeholder="Leave empty for unlimited"
                    min="1"
                    step="1"
                  >
                  <small class="form-text text-muted">Maximum number of times this promotion can be used (optional)</small>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Apply to Category <span class="text-danger">*</span></label>
                  <select class="form-select" v-model="formData.affected_category" required>
                    <option value="">Select category</option>
                    <option value="all">All Products</option>
                    <option value="noodles">Noodles</option>
                    <option value="drinks">Drinks</option>
                    <option value="toppings">Toppings</option>
                  </select>
                  <small class="form-text text-muted">Choose which category this promotion applies to</small>
                </div>
                <div class="col-12 mb-3">
                  <label class="form-label">Description</label>
                  <textarea 
                    class="form-control" 
                    v-model="formData.description"
                    placeholder="Enter promotion description (optional)"
                    rows="3"
                  ></textarea>
                  <small class="form-text text-muted">Add details about this promotion (optional)</small>
                </div>
              </div>
            </form>
          </div>

          <div v-if="mode === 'view'" class="view-mode">
            <div class="promotion-details" v-if="selectedPromotion">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label text-tertiary-dark fw-semibold">Promotion Name</label>
                  <div class="form-control-plaintext">{{ selectedPromotion.promotion_name }}</div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label text-tertiary-dark fw-semibold">Discount Type</label>
                  <div class="form-control-plaintext">
                    <span :class="getDiscountTypeBadgeClass(selectedPromotion.discount_type)" class="badge">
                      {{ formatDiscountType(selectedPromotion.discount_type) }}
                    </span>
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label text-tertiary-dark fw-semibold">Discount Value</label>
                  <div class="form-control-plaintext">{{ formatDiscountValue(selectedPromotion.discount_value, selectedPromotion.discount_type) }}</div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label text-tertiary-dark fw-semibold">Status</label>
                  <div class="form-control-plaintext">
                    <span :class="getStatusBadgeClass(selectedPromotion.status)" class="badge">
                      {{ formatStatus(selectedPromotion.status) }}
                    </span>
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label text-tertiary-dark fw-semibold">Start Date</label>
                  <div class="form-control-plaintext">{{ formatDate(selectedPromotion.start_date) }}</div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label text-tertiary-dark fw-semibold">End Date</label>
                  <div class="form-control-plaintext">{{ formatDate(selectedPromotion.end_date) }}</div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label text-tertiary-dark fw-semibold">Usage Limit</label>
                  <div class="form-control-plaintext">
                    {{ selectedPromotion.usage_limit === null || selectedPromotion.usage_limit === undefined ? 'Unlimited' : selectedPromotion.usage_limit }}
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label text-tertiary-dark fw-semibold">Current Usage</label>
                  <div class="form-control-plaintext">
                    {{ selectedPromotion.current_usage || 0 }}
                    <span v-if="selectedPromotion.usage_limit !== null && selectedPromotion.usage_limit !== undefined" class="text-muted">
                      / {{ selectedPromotion.usage_limit }}
                    </span>
                    <span v-else class="text-muted">(Unlimited)</span>
                  </div>
                </div>
                <div class="col-12 mb-3">
                  <label class="form-label text-tertiary-dark fw-semibold">Applied to Category</label>
                  <div class="form-control-plaintext">
                    <span class="badge bg-info text-white">
                      {{ formatCategory(selectedPromotion.affected_category) }}
                    </span>
                  </div>
                </div>
                <div class="col-12 mb-3" v-if="selectedPromotion.description">
                  <label class="form-label text-tertiary-dark fw-semibold">Description</label>
                  <div class="form-control-plaintext">{{ selectedPromotion.description }}</div>
                </div>
                <div class="col-12 mb-3">
                  <label class="form-label text-tertiary-dark fw-semibold">Last Updated</label>
                  <div class="form-control-plaintext">{{ formatDateTime(selectedPromotion.last_updated) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <!-- Add Mode Footer -->
          <template v-if="mode === 'add'">
            <button type="button" class="btn btn-cancel" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-save" @click="savePromotion">Save Promotion</button>
          </template>

          <!-- Edit Mode Footer -->
          <template v-if="mode === 'edit'">
            <button type="button" class="btn btn-cancel" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-save" @click="updatePromotion">Update Promotion</button>
          </template>

          <!-- View Mode Footer -->
          <template v-if="mode === 'view'">
            <button type="button" class="btn btn-secondary" @click="switchToEdit">
              <Edit :size="14" class="me-1" />
              Edit
            </button>
            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import promotionApiService from '@/services/apiPromotions.js'

export default {
  name: 'AddPromoModal',
  data() {
    return {
      mode: 'add',
      selectedPromotion: null,
      formData: {
        promotion_name: '',
        discount_type: '',
        discount_value: '',
        status: 'scheduled',
        start_date: '',
        end_date: '',
        affected_category: '',
        usage_limit: null,
        description: ''
      }
    }
  },
  computed: {
    modalTitle() {
      const titles = {
        'add': 'Add Promotion',
        'edit': 'Edit Promotion',
        'view': 'View Promotion'
      }
      return titles[this.mode] || 'Promotion'
    }
  },
  methods: {
    openAdd() {
      this.mode = 'add'
      this.selectedPromotion = null
      this.resetForm()
      this.openModal()
    },
    openEdit(promotion) {
      this.mode = 'edit'
      this.selectedPromotion = { ...promotion }
      this.populateForm(promotion)
      this.openModal()
    },
    openView(promotion) {
      this.mode = 'view'
      this.selectedPromotion = { ...promotion }
      this.openModal()
    },
    switchToEdit() {
      this.mode = 'edit'
      this.populateForm(this.selectedPromotion)
    },

    resetForm() {
      this.formData = {
        promotion_name: '',
        discount_type: '',
        discount_value: '',
        status: 'scheduled',
        start_date: '',
        end_date: '',
        affected_category: '',
        usage_limit: null,
        description: ''
      }
    },
    
    populateForm(promotion) {
      this.formData = {
        promotion_name: promotion.promotion_name || '',
        discount_type: promotion.discount_type || '',
        discount_value: promotion.discount_value || '',
        status: promotion.status || 'scheduled',
        start_date: promotion.start_date || '',
        end_date: promotion.end_date || '',
        affected_category: promotion.affected_category || '',
        usage_limit: promotion.usage_limit || null,
        description: promotion.description || ''
      }
    },

    validateForm() {
      if (!this.formData.promotion_name.trim()) {
        alert('Please enter a promotion name')
        return false
      }
      if (!this.formData.discount_type) {
        alert('Please select a discount type')
        return false
      }
      if (!this.formData.discount_value || this.formData.discount_value <= 0) {
        alert('Please enter a valid discount value')
        return false
      }
      if (this.formData.discount_type === 'percentage' && this.formData.discount_value > 100) {
        alert('Percentage discount cannot exceed 100%')
        return false
      }
      if (!this.formData.affected_category) {
        alert('Please select which category this promotion affects')
        return false
      }
      if (!this.formData.start_date) {
        alert('Please select a start date')
        return false
      }
      if (!this.formData.end_date) {
        alert('Please select an end date')
        return false
      }
      if (this.formData.start_date && this.formData.end_date && new Date(this.formData.end_date) <= new Date(this.formData.start_date)) {
        alert('End date must be after start date')
        return false
      }
      if (this.formData.usage_limit !== null && 
          this.formData.usage_limit !== undefined && 
          this.formData.usage_limit !== '') {
        const limit = parseInt(this.formData.usage_limit);
        if (isNaN(limit) || limit <= 0) {
          alert('Usage limit must be a positive number or leave empty for unlimited')
          return false
        }
      }
      
      return true
    },

    openModal() {
      const modalElement = document.getElementById('addPromoModal')
      if (modalElement) {
        const modal = new bootstrap.Modal(modalElement)
        modal.show()
      }
    },

    closeModal() {
      const modalElement = document.getElementById('addPromoModal')
      if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement)
        if (modal) {
          modal.hide()
        }
      }
    },

    async savePromotion() {
      if (!this.validateForm()) return
      
      try {
        console.log('Creating promotion with data:', this.formData);
        
        const result = await promotionApiService.createPromotion(this.formData);
        
        console.log('Create promotion result:', result);
        
        if (result.success) {
          alert('Promotion created successfully!');
          this.$emit('promotion-saved', {
            action: 'add',
            data: result.promotion
          });
          this.closeModal();
        } else {
          alert('Failed to create promotion:\n' + result.message);
          console.error('Backend errors:', result.errors);
        }
      } catch (error) {
        console.error('Error saving promotion:', error);
        alert('Error creating promotion: ' + error.message);
      }
    },

    async updatePromotion() {
      if (!this.validateForm()) return
      
      try {
        console.log('Updating promotion:', {
          id: this.selectedPromotion.promotion_id,
          data: this.formData
        });
        
        const result = await promotionApiService.updatePromotion(
          this.selectedPromotion.promotion_id, 
          this.formData
        );
        
        console.log('Update promotion result:', result);
        
        if (result.success) {
          alert('Promotion updated successfully!');
          this.$emit('promotion-saved', {
            action: 'edit',
            id: this.selectedPromotion.promotion_id,
            data: result.promotion
          });
          this.closeModal();
        } else {
          alert('Failed to update promotion:\n' + result.message);
          console.error('Backend errors:', result.errors);
        }
      } catch (error) {
        console.error('Error updating promotion:', error);
        alert('Error updating promotion: ' + error.message);
      }
    },

    // Formatting methods
    formatDiscountType(type) {
      const types = {
        'percentage': 'Percentage',
        'fixed_amount': 'Fixed Amount',
        'buy_x_get_y': 'BOGO'
      }
      return types[type] || type
    },

    formatDiscountValue(value, type) {
      if (type === 'percentage') {
        return `${value}%`
      } else if (type === 'fixed_amount') {
        return `₱${value}`
      }
      return value
    },

    formatStatus(status) {
      const statuses = {
        'active': 'Active',
        'inactive': 'Inactive',
        'expired': 'Expired',
        'scheduled': 'Scheduled'
      }
      return statuses[status] || status
    },

    formatDate(dateString) {
      if (!dateString) return '—'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },

    formatDateTime(dateString) {
      if (!dateString) return '—'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    formatCategory(category) {
      const categories = {
        'all': 'All Products',
        'noodles': 'Noodles',
        'drinks': 'Drinks',
        'toppings': 'Toppings'
      }
      return categories[category] || category
    },

    getDiscountTypeBadgeClass(type) {
      const classes = {
        'percentage': 'bg-primary text-white',
        'fixed_amount': 'bg-success text-white',
        'buy_x_get_y': 'bg-info text-white'
      }
      return classes[type] || 'bg-secondary text-white'
    },

    getStatusBadgeClass(status) {
      const classes = {
        'active': 'bg-success text-white',
        'inactive': 'bg-secondary text-white',
        'expired': 'bg-danger text-white',
        'scheduled': 'bg-warning text-dark'
      }
      return classes[status] || 'bg-secondary text-white'
    }
  }
}
</script>

<style scoped>
.modal-content {
  border-radius: 0.75rem;
  border: none;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  border-bottom: 1px solid var(--neutral-light);
  padding: 1.5rem;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--tertiary-dark);
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  border-top: 1px solid var(--neutral-light);
  padding: 1.5rem;
  gap: 0.5rem;
}

.text-tertiary-medium {
  color: var(--tertiary-medium);
}

.text-tertiary-dark {
  color: var(--tertiary-dark);
}

.form-label {
  font-weight: 500;
  color: var(--tertiary-dark);
  margin-bottom: 0.5rem;
}

.form-control,
.form-select {
  border: 1px solid var(--neutral);
  border-radius: 0.5rem;
  padding: 0.625rem 0.875rem;
  font-size: 0.875rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-control:focus,
.form-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25);
}

.input-group-text {
  background-color: var(--neutral-light);
  border-color: var(--neutral);
  color: var(--tertiary-dark);
  font-weight: 500;
}

.form-text {
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.text-danger {
  color: var(--error) !important;
}

.text-muted {
  color: var(--tertiary-medium) !important;
}

.date-picker-wrapper {
  position: relative;
}

.custom-datepicker {
  width: 100%;
}

.modal-content .custom-datepicker .dp__input {
  border: 1px solid var(--neutral) !important;
  border-radius: 0.5rem !important;
  padding: 0.625rem 2.75rem 0.625rem 0.875rem !important;
  font-size: 0.875rem !important;
  transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
  width: 100% !important;
  color: var(--tertiary-dark) !important;
  background-color: var(--bg-secondary) !important;
  height: auto !important;
  min-height: 2.5rem !important;
}

.modal-content .custom-datepicker .dp__input:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25) !important;
  outline: none !important;
}

.modal-content .custom-datepicker .dp__menu {
  z-index: 1060 !important;
  border: 1px solid var(--neutral) !important;
  border-radius: 0.75rem !important;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1) !important;
}

.form-control-plaintext {
  padding: 0.375rem 0;
  color: var(--tertiary-dark);
  background-color: transparent;
  border: none;
  font-weight: 500;
}

.badge {
  font-size: 0.75rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
}

@media (max-width: 768px) {
  .modal-dialog {
    margin: 0.5rem;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 1rem;
  }
}
</style>