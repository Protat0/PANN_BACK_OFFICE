<template>
  <!-- Use Teleport to render modal at body level -->
  <Teleport to="body">
    <div v-if="show" class="modal-overlay modal-overlay-theme" @click="handleOverlayClick">
      <div class="modal-content modal-theme large-modal" @click.stop>
        <div class="modal-header border-bottom-theme">
          <h2 class="text-primary">{{ isEditMode ? 'Edit Product' : 'Add New Product' }}</h2>
          <button class="btn-close" @click="closeModal" :disabled="loading" aria-label="Close">
            ✕
          </button>
        </div>
        
        <form @submit.prevent="handleSubmit" class="product-form">
          <!-- Product Image Upload Section -->
          <div class="mb-3">
  <label class="form-label text-primary fw-medium">Product Image:</label>
  
            <!-- Image Preview (if exists) -->
            <div v-if="imagePreview" class="mb-3">
              <div class="image-preview-container bg-neutral-light rounded p-3 text-center">
                <img 
                  :src="imagePreview" 
                  alt="Product preview" 
                  class="img-fluid rounded mb-2" 
                  style="max-height: 120px;" 
                />
                <br>
                <small class="text-success">Image selected</small>
                <br>
                <button 
                  type="button" 
                  class="btn btn-outline-danger btn-xs mt-2"
                  @click="removeImage"
                >
                  Remove Image
                </button>
              </div>
            </div>
            
            <!-- File Input (always visible) -->
            <div class="product-image-upload">
              <div class="image-upload-container bg-neutral-light rounded p-4 text-center">
                <div class="upload-icon text-accent">📷</div>
                <p class="text-primary mb-2">
                  {{ imagePreview ? 'Change image' : 'Upload product image' }}
                </p>
                <input 
                  type="file" 
                  class="form-control" 
                  accept="image/*"
                  @change="handleImageUpload"
                  :key="'imageInput-' + (isEditMode ? 'edit' : 'new')"
                />
                <small class="text-muted mt-2 d-block">
                  Maximum file size: 5MB. Supported formats: JPEG, PNG, GIF, WebP
                </small>
              </div>
            </div>
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label for="product_name" class="form-label text-primary fw-medium">
                Product Name <span class="text-error">*</span>
              </label>
              <input 
                id="product_name"
                v-model="form.product_name" 
                type="text" 
                required 
                :disabled="loading"
                placeholder="Enter product name"
                class="form-control input-theme"
              />
            </div>

            <div class="col-md-6">
              <label for="SKU" class="form-label text-primary fw-medium">
                SKU <span class="text-error">*</span>
              </label>
              <div class="position-relative">
                <input 
                  id="SKU"
                  v-model="form.SKU" 
                  type="text" 
                  required 
                  :disabled="loading || isValidatingSku"
                  placeholder="Enter SKU"
                  class="form-control input-theme"
                  :class="{ 'border-error': skuError }"
                  @blur="validateSKU"
                />
                <div v-if="isValidatingSku" class="validation-spinner position-absolute top-50 end-0 translate-middle-y me-3">
                  <div class="spinner-border spinner-border-sm text-accent" role="status">
                    <span class="visually-hidden">Validating...</span>
                  </div>
                </div>
                <div v-if="skuError" class="invalid-feedback text-error">
                  {{ skuError }}
                </div>
              </div>
            </div>
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label for="category_id" class="form-label text-primary fw-medium">
                Category <span class="text-error">*</span>
              </label>
              <select 
                id="category_id"
                v-model="form.category_id" 
                class="form-select input-theme"
                required
                :disabled="loading"
              >
                <option value="">Select Category</option>
                <option 
                  v-for="category in categories" 
                  :key="category._id" 
                  :value="category._id"
                >
                  {{ category.category_name }}
                </option>
              </select>
            </div>

            <div class="col-md-6">
              <label for="unit" class="form-label text-primary fw-medium">
                Unit <span class="text-error">*</span>
              </label>
              <select 
                id="unit"
                v-model="form.unit" 
                required 
                :disabled="loading"
                class="form-select input-theme"
              >
                <option value="">Select Unit</option>
                <option value="pcs">Pieces</option>
                <option value="pack">Pack</option>
                <option value="bottle">Bottle</option>
                <option value="can">Can</option>
                <option value="kg">Kilogram</option>
                <option value="liter">Liter</option>
              </select>
            </div>
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label for="cost_price" class="form-label text-primary fw-medium">
                Cost Price (₱) <span class="text-error">*</span>
              </label>
              <input 
                id="cost_price"
                v-model.number="form.cost_price" 
                type="number" 
                step="0.01"
                min="0"
                required 
                :disabled="loading"
                placeholder="0.00"
                class="form-control input-theme"
              />
            </div>

            <div class="col-md-6">
               <label for="selling_price" class="form-label text-primary fw-medium">
                  Selling Price (₱) <span class="text-error">*</span>
                </label>
                <input 
                  id="selling_price"
                  v-model.number="form.selling_price" 
                  type="number" 
                  step="0.01"
                  min="0"
                  required 
                  :disabled="loading"
                  placeholder="0.00"
                  class="form-control input-theme"
                  @input="handleSellingPriceChange"
                />
            </div>
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label for="stock" class="form-label text-primary fw-medium">
                Stock Quantity <span class="text-error">*</span>
              </label>
              <input 
                id="stock"
                v-model.number="form.stock" 
                type="number" 
                min="0"
                required 
                :disabled="loading"
                placeholder="0"
                class="form-control input-theme"
              />
            </div>

            <div class="col-md-6">
              <label for="low_stock_threshold" class="form-label text-primary fw-medium">
                Low Stock Threshold <span class="text-error">*</span>
              </label>
              <input 
                id="low_stock_threshold"
                v-model.number="form.low_stock_threshold" 
                type="number" 
                min="0"
                required 
                :disabled="loading"
                placeholder="10"
                class="form-control input-theme"
              />
            </div>
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label for="expiry_date" class="form-label text-primary fw-medium">Expiry Date:</label>
              <input 
                id="expiry_date"
                v-model="form.expiry_date" 
                type="date" 
                :disabled="loading"
                class="form-control input-theme"
              />
            </div>

            <div class="col-md-6">
              <label for="status" class="form-label text-primary fw-medium">
                Status <span class="text-error">*</span>
              </label>
              <select 
                id="status"
                v-model="form.status" 
                required 
                :disabled="loading"
                class="form-select input-theme"
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-8">
              <label for="barcode" class="form-label text-primary fw-medium">Barcode:</label>
              <div class="input-group">
                <input 
                  id="barcode"
                  v-model="form.barcode" 
                  type="text" 
                  :disabled="loading"
                  placeholder="Enter barcode or generate automatically"
                  class="form-control input-theme"
                />
                <button 
                  type="button" 
                  @click="generateBarcode"
                  :disabled="loading"
                  class="btn btn-export btn-with-icon"
                >
                  Generate
                </button>
              </div>
            </div>

            <div class="col-md-4 d-flex align-items-end">
              <div class="form-check">
                <input 
                  id="is_taxable"
                  v-model="form.is_taxable" 
                  type="checkbox" 
                  :disabled="loading"
                  class="form-check-input focus-ring-theme"
                />
                <label for="is_taxable" class="form-check-label text-secondary">
                  Taxable Item
                </label>
              </div>
            </div>
          </div>

          <div class="mb-3">
            <label for="description" class="form-label text-primary fw-medium">Description:</label>
            <textarea 
              id="description"
              v-model="form.description" 
              :disabled="loading"
              placeholder="Enter product description (optional)"
              class="form-control input-theme"
              rows="3"
            ></textarea>
          </div>

          <div v-if="error" class="alert alert-danger status-error d-flex align-items-center mb-3" role="alert">
            <span class="me-2">⚠️</span>
            {{ error }}
          </div>

          <div class="d-flex gap-2 justify-content-end pt-3 divider-theme">
            <button 
              type="button" 
              @click="closeModal" 
              :disabled="loading"
              class="btn btn-cancel"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              :disabled="loading || !isFormValid" 
              class="btn btn-save btn-with-icon"
              :class="{ 'btn-loading': loading }"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">Loading...</span>
              </span>
              {{ loading ? 'Saving...' : (isEditMode ? 'Update Product' : 'Create Product') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { useAddProduct } from '@/composables/ui/products/useAddProduct'
import { onMounted, onBeforeUnmount, toRef } from 'vue'

export default {
  name: 'AddProductModal',
  props: {
    categories: {
      type: Array,
      default: () => []
    }
  },
  emits: ['success'],
 
  setup(props, { emit }) {
    const {
      // State
      show,
      loading,
      error,
      form,
      imagePreview,
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
      validateSKU,
      generateBarcode,
     
      // Image methods
      handleImageUpload,
      removeImage,
     
      // Utility methods
      setupKeyboardListeners,
      cleanupKeyboardListeners
    } = useAddProduct()
   
    // Setup keyboard listeners on mount
    onMounted(() => {
      setupKeyboardListeners()
    })
   
    // Cleanup on unmount
    onBeforeUnmount(() => {
      cleanupKeyboardListeners()
    })
   
    // Methods
    const triggerFileInput = () => {
      if (!loading.value) {
        // Use the template ref instead of querySelector
        const fileInput = document.querySelector('input[type="file"]')
        if (fileInput) {
          fileInput.click()
        }
      }
    }
   
    const handleSubmit = () => {
      submitProduct((result, wasEdit) => {
        const action = wasEdit ? 'updated' : 'created'
        emit('success', {
          message: `Product "${form.value.product_name}" ${action} successfully`,
          product: result,
          action
        })
      })
    }
   
    const handleOverlayClick = () => {
      if (!loading.value) {
        closeModal()
      }
    }
   
    // Expose methods for parent component
    const openAdd = () => {
      openAddModal()
    }
   
    const openEdit = (product) => {
      openEditModal(product)
    }
   
    return {
      // Props - make categories reactive and available to template
      categories: toRef(props, 'categories'),
      
      // State
      show,
      loading,
      error,
      form,
      imagePreview,
      skuError,
      isValidatingSku,
     
      // Computed
      isEditMode,
      isFormValid,
     
      // Methods
      closeModal,
      triggerFileInput,
      handleSubmit,
      handleOverlayClick,
      validateSKU,
      generateBarcode,
      handleImageUpload,
      removeImage,
     
      // Exposed methods
      openAdd,
      openEdit
    }
  }
}
</script>

<style scoped>

/* CRITICAL: Fixed positioning for modal overlay */
.modal-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  background-color: rgba(0, 0, 0, 0.5) !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  z-index: 9999 !important; /* Ensure it's above everything */
  animation: fadeIn 0.3s ease;
  backdrop-filter: blur(4px);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  position: relative !important;
  max-width: 800px;
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideIn 0.3s ease;
  z-index: 10000 !important; /* Higher than overlay */
}

@keyframes slideIn {
  from { 
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to { 
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  padding: 1.5rem 2rem 1rem 2rem;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-tertiary);
  padding: 0.25rem;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.btn-close:hover:not(:disabled) {
  background-color: var(--state-hover);
  color: var(--text-primary);
}

.btn-close:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.product-form {
  padding: 1.5rem 2rem 2rem 2rem;
}

/* Image Upload Styles using semantic classes */
.image-upload-container {
  width: 100%;
}

.image-preview-area {
  width: 200px;
  height: 200px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  background-color: var(--surface-secondary);
}

.image-preview-area:hover:not(.has-image) {
  background-color: var(--state-hover);
}

.upload-placeholder {
  text-align: center;
  padding: 1rem;
}

.upload-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.upload-text {
  font-weight: 500;
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
}

.upload-subtext {
  font-size: 0.75rem;
  margin: 0;
}

.image-preview {
  width: 100%;
  height: 100%;
  position: relative;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 10px;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: 10px;
}

.image-preview:hover .image-overlay {
  opacity: 1;
}

/* Override for divider-theme in this context */
.divider-theme {
  border-top: 1px solid var(--border-secondary) !important;
  margin: 0;
  padding-top: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .modal-content {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }

  .modal-header {
    padding: 1rem 1.5rem 0.75rem 1.5rem;
  }

  .modal-header h2 {
    font-size: 1.25rem;
  }

  .product-form {
    padding: 1rem 1.5rem 1.5rem 1.5rem;
  }

  .image-preview-area {
    width: 100%;
    max-width: 200px;
    margin: 0 auto;
  }
}

@media (max-width: 480px) {
  .modal-content {
    margin: 0.5rem;
    max-height: calc(100vh - 1rem);
    border-radius: 8px;
  }

  .modal-header {
    padding: 0.75rem 1rem 0.5rem 1rem;
  }

  .product-form {
    padding: 0.75rem 1rem 1rem 1rem;
  }
}

/* Custom scrollbar using semantic colors */
.modal-content::-webkit-scrollbar {
  width: 6px;
}

.modal-content::-webkit-scrollbar-track {
  background: var(--surface-tertiary);
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: var(--border-primary);
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: var(--border-accent);
}

/* Prevent body scroll when modal is open */
body:has(.modal-overlay) {
  overflow: hidden !important;
}
</style>