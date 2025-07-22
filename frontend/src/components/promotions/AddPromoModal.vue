<template>
  <div class="modal fade" id="addPromoModal" tabindex="-1" aria-labelledby="addPromoModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="addPromoModalLabel">{{ modalTitle }}</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <!-- Error Alert -->
        <div v-if="error" class="alert alert-danger" role="alert">
          <strong>Error:</strong> {{ error }}
        </div>

        <!-- Loading Overlay -->
        <div v-if="loading" class="loading-overlay">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

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
                  :disabled="loading"
                  placeholder="Enter promotion name"
                  required
                >
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Discount Type <span class="text-danger">*</span></label>
                <select class="form-select" v-model="formData.discount_type" :disabled="loading" required>
                  <option value="">Select discount type</option>
                  <option value="percentage">Percentage</option>
                  <option value="fixed">Fixed Amount</option>
                  <option value="buy_one_get_one">Buy One Get One (BOGO)</option>
                </select>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Discount Value <span class="text-danger">*</span></label>
                <div class="input-group">
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="formData.discount_value"
                    :disabled="loading"
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
                <select class="form-select" v-model="formData.status" :disabled="loading">
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="scheduled">Scheduled</option>
                </select>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Start Date <span class="text-danger">*</span></label>
                <div class="date-picker-wrapper">
                  <VueDatePicker 
                    v-model="formData.start_date"
                    :enable-time-picker="false"
                    :disabled="loading"
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
                    :disabled="loading"
                    format="MM/dd/yyyy"
                    placeholder="Select end date"
                    :min-date="formData.start_date || new Date()"
                    class="custom-datepicker"
                    required
                  />
                </div>
              </div>
              <div class="col-12 mb-3">
                <label class="form-label">Affected Products <span class="text-danger">*</span></label>
                <select class="form-select" v-model="formData.affected_products" :disabled="loading" required>
                  <option value="">Select product category</option>
                  <option value="all">All Products</option>
                  <option 
                    v-for="category in availableCategories" 
                    :key="category._id" 
                    :value="category._id"
                  >
                    {{ category.category_name }}
                    <small v-if="category.description"> - {{ category.description }}</small>
                  </option>
                </select>
                <small class="form-text text-muted">
                  Choose which category of products this promotion applies to
                  <span v-if="availableCategories.length === 0" class="text-warning">
                    (Loading categories...)
                  </span>
                </small>
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
                  :disabled="loading"
                  placeholder="Enter promotion name"
                  required
                >
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Discount Type <span class="text-danger">*</span></label>
                <select class="form-select" v-model="formData.discount_type" :disabled="loading" required>
                  <option value="">Select discount type</option>
                  <option value="percentage">Percentage</option>
                  <option value="fixed">Fixed Amount</option>
                  <option value="buy_one_get_one">Buy One Get One (BOGO)</option>
                </select>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Discount Value <span class="text-danger">*</span></label>
                <div class="input-group">
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="formData.discount_value"
                    :disabled="loading"
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
                <select class="form-select" v-model="formData.status" :disabled="loading">
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="expired">Expired</option>
                  <option value="scheduled">Scheduled</option>
                </select>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Start Date <span class="text-danger">*</span></label>
                <div class="date-picker-wrapper">
                  <VueDatePicker 
                    v-model="formData.start_date"
                    :enable-time-picker="false"
                    :disabled="loading"
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
                    :disabled="loading"
                    format="MM/dd/yyyy"
                    placeholder="Select end date"
                    :min-date="formData.start_date || new Date()"
                    class="custom-datepicker"
                    required
                  />
                </div>
              </div>
              <div class="col-12 mb-3">
                <label class="form-label">Affected Products <span class="text-danger">*</span></label>
                <select class="form-select" v-model="formData.affected_products" :disabled="loading" required>
                  <option value="">Select product category</option>
                  <option value="all">All Products</option>
                  <option 
                    v-for="category in availableCategories" 
                    :key="category._id" 
                    :value="category._id"
                  >
                    {{ category.category_name }}
                    <small v-if="category.description"> - {{ category.description }}</small>
                  </option>
                </select>
                <small class="form-text text-muted">
                  Choose which category of products this promotion applies to
                  <span v-if="availableCategories.length === 0" class="text-warning">
                    (Loading categories...)
                  </span>
                </small>
              </div>
            </div>
          </form>
        </div>

        <div v-if="mode === 'view'" class="view-mode">
          <p class="text-tertiary-medium">View promotion details...</p>
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
              <div class="col-12 mb-3">
                <label class="form-label text-tertiary-dark fw-semibold">Affected Products</label>
                <div class="form-control-plaintext">
                  <span class="badge bg-info text-white">
                    {{ formatAffectedProducts(selectedPromotion.applicable_products) }}
                  </span>
                </div>
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
          <button type="button" class="btn btn-cancel" :disabled="loading" data-bs-dismiss="modal">Cancel</button>
          <button type="button" class="btn btn-save" :disabled="loading" @click="savePromotion">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
            {{ loading ? 'Saving...' : 'Save Promotion' }}
          </button>
        </template>

        <!-- Edit Mode Footer -->
        <template v-if="mode === 'edit'">
          <button type="button" class="btn btn-cancel" :disabled="loading" data-bs-dismiss="modal">Cancel</button>
          <button type="button" class="btn btn-save" :disabled="loading" @click="updatePromotion">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
            {{ loading ? 'Updating...' : 'Update Promotion' }}
          </button>
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
import categoryApiService from '@/services/apiCategory'

export default {
  name: 'AddPromoModal',
  props: {
    productCategories: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      mode: 'add',
      selectedPromotion: null,
      loading: false,
      error: null,
      categories: [], // Store fetched categories
      formData: {
        promotion_id: null,
        promotion_name: '',
        discount_type: '',
        discount_value: '',
        status: 'active',
        start_date: '',
        end_date: '',
        affected_products: '',
        applicable_products: []
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
    },
    
    // CHANGED: Display ALL categories without any filtering
    availableCategories() {
      // Return all categories without any filtering
      return this.categories || []
    }
  },
  
  async mounted() {
    // Fetch categories when component is mounted
    await this.fetchCategories()
  },
  
  methods: {
    // Add method to fetch categories
    async fetchCategories() {
      try {
        // console.log('Fetching categories...') // Debug log
        const response = await categoryApiService.CategoryData()
        // console.log('Categories response:', response) // Debug log
        
        // ✅ FIXED: Handle the correct response structure
        if (response && response.categories) {
          // Filter out deleted categories and map to the format we need
          this.categories = response.categories
            .filter(category => !category.isDeleted) // Only show active categories
            .map(category => ({
              _id: category._id,
              category_name: category.category_name,
              description: category.description || '',
              status: category.status
            }))
          
          // console.log('Categories processed:', this.categories) // Debug log
        } else if (response && Array.isArray(response)) {
          // Handle case where response is directly an array
          this.categories = response
            .filter(category => !category.isDeleted)
            .map(category => ({
              _id: category._id,
              category_name: category.category_name,
              description: category.description || '',
              status: category.status
            }))
        } else {
          // console.log('No categories found in response')
          this.categories = []
        }
        
        // console.log('Final categories available:', this.categories.length)
        
      } catch (error) {
        console.error('Error fetching categories:', error)
        this.categories = []
      }
    },

    // Mode switching methods
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

    // Form management methods
    resetForm() {
      this.formData = {
        promotion_id: null,
        promotion_name: '',
        discount_type: '',
        discount_value: '',
        status: 'active',
        start_date: '',
        end_date: '',
        affected_products: '',
        applicable_products: []
      }
      this.error = null
    },
    
    populateForm(promotion) {
      this.formData = {
        promotion_id: promotion.promotion_id,
        promotion_name: promotion.promotion_name || '',
        discount_type: promotion.discount_type || '',
        discount_value: promotion.discount_value || '',
        status: promotion.status || 'active',
        start_date: promotion.start_date || '',
        end_date: promotion.end_date || '',
        affected_products: this.mapApplicableProductsToCategory(promotion.applicable_products) || '',
        applicable_products: promotion.applicable_products || []
      }
      this.error = null
    },
    
    validateForm() {
      if (!this.formData.promotion_name.trim()) {
        this.error = 'Please enter a promotion name'
        return false
      }
      if (!this.formData.discount_type) {
        this.error = 'Please select a discount type'
        return false
      }
      if (!this.formData.discount_value || this.formData.discount_value <= 0) {
        this.error = 'Please enter a valid discount value'
        return false
      }
      if (this.formData.discount_type === 'percentage' && this.formData.discount_value > 100) {
        this.error = 'Percentage discount cannot exceed 100%'
        return false
      }
      if (!this.formData.affected_products) {
        this.error = 'Please select which products this promotion affects'
        return false
      }
      if (!this.formData.start_date) {
        this.error = 'Please select a start date'
        return false
      }
      if (!this.formData.end_date) {
        this.error = 'Please select an end date'
        return false
      }
      if (this.formData.start_date && this.formData.end_date && new Date(this.formData.end_date) <= new Date(this.formData.start_date)) {
        this.error = 'End date must be after start date'
        return false
      }
      
      this.error = null
      return true
    },

    // Modal control methods
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
      this.resetForm()
    },

    // Action methods - Updated for API integration
    async savePromotion() {
      if (!this.validateForm()) return
      
      try {
        this.loading = true
        this.error = null
        
        // Map category selection to applicable_products array
        const applicableProducts = this.mapCategoryToApplicableProducts(this.formData.affected_products)
        
        // Prepare data for API
        const promotionData = {
          promotion_name: this.formData.promotion_name,
          discount_type: this.formData.discount_type,
          discount_value: this.formData.discount_value,
          start_date: this.formatDateForAPI(this.formData.start_date),
          end_date: this.formatDateForAPI(this.formData.end_date),
          status: this.formData.status,
          applicable_products: applicableProducts
        }
        
        // console.log('Saving new promotion:', promotionData)
        
        // Emit to parent component to handle API call
        this.$emit('promotion-saved', promotionData)
        
      } catch (error) {
        this.error = error.message || 'Failed to save promotion'
      } finally {
        this.loading = false
      }
    },
    
    async updatePromotion() {
      if (!this.validateForm()) return
      
      try {
        this.loading = true
        this.error = null
        
        // Map category selection to applicable_products array
        const applicableProducts = this.mapCategoryToApplicableProducts(this.formData.affected_products)
        
        // Prepare data for API
        const promotionData = {
          promotion_id: this.formData.promotion_id,
          promotion_name: this.formData.promotion_name,
          discount_type: this.formData.discount_type,
          discount_value: this.formData.discount_value,
          start_date: this.formatDateForAPI(this.formData.start_date),
          end_date: this.formatDateForAPI(this.formData.end_date),
          status: this.formData.status,
          applicable_products: applicableProducts
        }
        
        // console.log('Updating promotion:', promotionData)
        
        // Emit to parent component to handle API call
        this.$emit('promotion-updated', promotionData)
        
      } catch (error) {
        this.error = error.message || 'Failed to update promotion'
      } finally {
        this.loading = false
      }
    },

    // Helper methods for data transformation - Updated for new data structure
    formatDateForAPI(dateValue) {
      if (!dateValue) return ''
      
      if (dateValue instanceof Date) {
        return dateValue.toISOString().split('T')[0]
      }
      
      if (typeof dateValue === 'string') {
        if (dateValue.match(/^\d{4}-\d{2}-\d{2}$/)) {
          return dateValue
        }
        const date = new Date(dateValue)
        return date.toISOString().split('T')[0]
      }
      
      return dateValue
    },
    
    mapCategoryToApplicableProducts(categoryId) {
      // console.log('🔍 Mapping category to applicable products:', categoryId);
      // console.log('🔍 Available categories:', this.categories);
      
      // If "all" is selected, return all category names (not IDs)
      if (categoryId === 'all') {
        const allCategoryNames = this.categories.map(cat => cat.category_name);
        // console.log('🔍 All category names:', allCategoryNames);
        return allCategoryNames;
      }
      
      // For specific category, find the category name
      const selectedCategory = this.categories.find(cat => cat._id === categoryId);
      if (selectedCategory) {
        // console.log('🔍 Selected category name:', selectedCategory.category_name);
        return [selectedCategory.category_name];
      }
      
      // console.log('🔍 No matching category found for ID:', categoryId);
      return [];
    },

    mapApplicableProductsToCategory(applicableProducts) {
      // console.log('🔍 Mapping applicable products to category:', applicableProducts);
      
      if (!applicableProducts || applicableProducts.length === 0) {
        return '';
      }
      
      // Check if all categories are selected by comparing category names
      const allCategoryNames = this.categories.map(cat => cat.category_name);
      const isAllSelected = allCategoryNames.every(catName => 
        applicableProducts.includes(catName)
      );
      
      if (isAllSelected || applicableProducts.length === allCategoryNames.length) {
        return 'all';
      }
      
      // Find the category ID for the first applicable product (category name)
      const firstProductName = applicableProducts[0];
      const matchingCategory = this.categories.find(cat => cat.category_name === firstProductName);
      
      if (matchingCategory) {
        // console.log('🔍 Found matching category ID:', matchingCategory._id);
        return matchingCategory._id;
      }
      
      // console.log('🔍 No matching category found for:', firstProductName);
      return '';
    },

    // Add method to handle successful operations from parent
    onOperationSuccess() {
      this.closeModal()
    },

    // Formatting methods - Updated for new data structure
    formatDiscountType(type) {
      const types = {
        'percentage': 'Percentage',
        'fixed': 'Fixed Amount',
        'buy_one_get_one': 'BOGO'
      }
      return types[type] || type
    },
    
    formatDiscountValue(value, type) {
      if (type === 'percentage') {
        return `${value}%`
      } else if (type === 'fixed') {
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
    
    getDiscountTypeBadgeClass(type) {
      const classes = {
        'percentage': 'bg-primary text-white',
        'fixed': 'bg-success text-white',
        'buy_one_get_one': 'bg-info text-white'
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
    },
    
    formatAffectedProducts(applicableProducts) {
      // console.log('🔍 Formatting affected products:', applicableProducts);
      
      if (!applicableProducts || applicableProducts.length === 0) {
        return 'No products selected';
      }
      
      // Since applicable_products contains category names, display them directly
      if (applicableProducts.length === 1) {
        return applicableProducts[0];
      } else if (applicableProducts.length <= 3) {
        return applicableProducts.join(', ');
      } else {
        return `${applicableProducts.length} Categories`;
      }
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

/* Form styling */
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

.form-control:disabled,
.form-select:disabled {
  background-color: var(--neutral-light);
  border-color: var(--neutral-medium);
  color: var(--tertiary-medium);
  cursor: not-allowed;
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

/* Date picker styling - Override global styles for this modal */
.date-picker-wrapper {
  position: relative;
}

.custom-datepicker {
  width: 100%;
}

/* Override the global dp__input styles specifically for this modal */
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
  background-color: var(--bg-secondary) !important;
}

.modal-content .custom-datepicker .dp__input:hover {
  border-color: var(--primary) !important;
}

/* Position the calendar icon properly within the modal */
.modal-content .custom-datepicker .dp__input_wrap {
  position: relative !important;
  width: 100% !important;
}

.modal-content .custom-datepicker .dp__input_icon {
  position: absolute !important;
  right: 0.875rem !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  color: var(--tertiary-medium) !important;
  pointer-events: none !important;
  z-index: 10 !important;
  width: 1rem !important;
  height: 1rem !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.modal-content .custom-datepicker .dp__input_icon svg {
  width: 14px !important;
  height: 14px !important;
  display: block !important;
}

/* Ensure the datepicker menu appears above modal */
.modal-content .custom-datepicker .dp__menu {
  z-index: 1060 !important;
  border: 1px solid var(--neutral) !important;
  border-radius: 0.75rem !important;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1) !important;
  background-color: var(--bg-secondary) !important;
}

:deep(.dp__menu) {
  border: 1px solid var(--neutral);
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  margin-top: 0.25rem;
}

:deep(.dp__calendar_header) {
  background-color: var(--primary-light);
  color: var(--primary-dark);
  font-weight: 600;
}

:deep(.dp__today) {
  border: 2px solid var(--primary);
}

:deep(.dp__active_date) {
  background-color: var(--primary);
  color: white;
}

:deep(.dp__date_hover) {
  background-color: var(--primary-light);
  color: var(--primary-dark);
}

:deep(.dp__calendar_item) {
  padding: 0.5rem;
  text-align: center;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

:deep(.dp__calendar_item:hover) {
  background-color: var(--primary-light);
  color: var(--primary-dark);
}

:deep(.dp__overlay) {
  z-index: 1050;
}

/* View mode styling */
.form-control-plaintext {
  padding: 0.375rem 0;
  color: var(--tertiary-dark);
  background-color: transparent;
  border: none;
  font-weight: 500;
}

.promotion-details .form-label {
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.badge {
  font-size: 0.75rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .modal-dialog {
    margin: 0.5rem;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 1rem;
  }
  
  .col-md-6 {
    margin-bottom: 1rem;
  }
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  border-radius: 0.75rem;
}

/* Error alert styling */
.alert-danger {
  margin-bottom: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #f5c6cb;
  background-color: #f8d7da;
  color: #721c24;
  padding: 0.75rem;
  font-size: 0.875rem;
}

/* Button loading states */
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.1rem;
}

/* Enhanced form disabled states */
.form-control:disabled,
.form-select:disabled {
  background-color: var(--neutral-light);
  border-color: var(--neutral-medium);
  color: var(--tertiary-medium);
  cursor: not-allowed;
  opacity: 0.7;
}
.action-btn {
  width: 32px;
  height: 32px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.btn-outline-success:hover {
  background-color: #198754;
  border-color: #198754;
  color: white;
}

.btn-outline-danger:hover {
  background-color: #dc3545;
  border-color: #dc3545;
  color: white;
}

/* Status badge for deleted items */
.badge.bg-dark {
  background-color: #495057 !important;
}

/* Ensure consistent spacing for action buttons */
.d-flex.gap-1 {
  gap: 0.25rem !important;
}

</style>