<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content large-modal" @click.stop>
      <div class="modal-header">
        <h2 class="text-tertiary-dark">{{ isEditMode ? 'Edit Product' : 'Add New Product' }}</h2>
        <button class="btn-close" @click="closeModal" :disabled="loading" aria-label="Close">
          ✕
        </button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="product-form">
        <!-- Product Image Upload Section -->
        <div class="mb-3">
          <label class="form-label text-tertiary-dark fw-medium">Product Image:</label>
          <div class="image-upload-container">
            <div class="image-preview-area" @click="triggerFileInput" :class="{ 'has-image': imagePreview }">
              <div v-if="!imagePreview" class="upload-placeholder">
                <div class="upload-icon">📷</div>
                <p class="upload-text">Click to upload product image</p>
                <p class="upload-subtext">PNG, JPG, JPEG up to 5MB</p>
              </div>
              <div v-else class="image-preview">
                <img :src="imagePreview" :alt="form.product_name" class="preview-image" />
                <div class="image-overlay">
                  <button type="button" class="btn btn-sm btn-edit" @click.stop="triggerFileInput">
                    Change Image
                  </button>
                  <button type="button" class="btn btn-sm btn-delete" @click.stop="removeImage">
                    Remove
                  </button>
                </div>
              </div>
            </div>
            <input 
              ref="fileInput"
              type="file" 
              accept="image/*" 
              @change="handleImageUpload"
              class="d-none"
              :disabled="loading"
            />
          </div>
        </div>

        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label for="product_name" class="form-label text-tertiary-dark fw-medium">
              Product Name <span class="text-danger">*</span>
            </label>
            <input 
              id="product_name"
              v-model="form.product_name" 
              type="text" 
              required 
              :disabled="loading"
              placeholder="Enter product name"
              class="form-control"
            />
          </div>

          <div class="col-md-6">
            <label for="SKU" class="form-label text-tertiary-dark fw-medium">
              SKU <span class="text-danger">*</span>
            </label>
            <div class="position-relative">
              <input 
                id="SKU"
                v-model="form.SKU" 
                type="text" 
                required 
                :disabled="loading || isValidatingSku"
                placeholder="Enter SKU"
                class="form-control"
                :class="{ 'is-invalid': skuError }"
                @blur="validateSKU"
              />
              <div v-if="isValidatingSku" class="validation-spinner position-absolute top-50 end-0 translate-middle-y me-3">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                  <span class="visually-hidden">Validating...</span>
                </div>
              </div>
              <div v-if="skuError" class="invalid-feedback">
                {{ skuError }}
              </div>
            </div>
          </div>
        </div>

        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label for="category_id" class="form-label text-tertiary-dark fw-medium">
              Category <span class="text-danger">*</span>
            </label>
            <select 
              id="category_id"
              v-model="form.category_id" 
              required 
              :disabled="loading"
              class="form-select"
            >
              <option value="">Select Category</option>
              <option value="noodles">Noodles</option>
              <option value="drinks">Drinks</option>
              <option value="toppings">Toppings</option>
            </select>
          </div>

          <div class="col-md-6">
            <label for="unit" class="form-label text-tertiary-dark fw-medium">
              Unit <span class="text-danger">*</span>
            </label>
            <select 
              id="unit"
              v-model="form.unit" 
              required 
              :disabled="loading"
              class="form-select"
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
            <label for="cost_price" class="form-label text-tertiary-dark fw-medium">
              Cost Price (₱) <span class="text-danger">*</span>
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
              class="form-control"
            />
          </div>

          <div class="col-md-6">
            <label for="selling_price" class="form-label text-tertiary-dark fw-medium">
              Selling Price (₱) <span class="text-danger">*</span>
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
              class="form-control"
            />
          </div>
        </div>

        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label for="stock" class="form-label text-tertiary-dark fw-medium">
              Stock Quantity <span class="text-danger">*</span>
            </label>
            <input 
              id="stock"
              v-model.number="form.stock" 
              type="number" 
              min="0"
              required 
              :disabled="loading"
              placeholder="0"
              class="form-control"
            />
          </div>

          <div class="col-md-6">
            <label for="low_stock_threshold" class="form-label text-tertiary-dark fw-medium">
              Low Stock Threshold <span class="text-danger">*</span>
            </label>
            <input 
              id="low_stock_threshold"
              v-model.number="form.low_stock_threshold" 
              type="number" 
              min="0"
              required 
              :disabled="loading"
              placeholder="10"
              class="form-control"
            />
          </div>
        </div>

        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label for="expiry_date" class="form-label text-tertiary-dark fw-medium">Expiry Date:</label>
            <input 
              id="expiry_date"
              v-model="form.expiry_date" 
              type="date" 
              :disabled="loading"
              class="form-control"
            />
          </div>

          <div class="col-md-6">
            <label for="status" class="form-label text-tertiary-dark fw-medium">
              Status <span class="text-danger">*</span>
            </label>
            <select 
              id="status"
              v-model="form.status" 
              required 
              :disabled="loading"
              class="form-select"
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>

        <div class="row g-3 mb-3">
          <div class="col-md-8">
            <label for="barcode" class="form-label text-tertiary-dark fw-medium">Barcode:</label>
            <div class="input-group">
              <input 
                id="barcode"
                v-model="form.barcode" 
                type="text" 
                :disabled="loading"
                placeholder="Enter barcode or generate automatically"
                class="form-control"
              />
              <button 
                type="button" 
                @click="generateBarcode"
                :disabled="loading"
                class="btn btn-export"
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
                class="form-check-input"
              />
              <label for="is_taxable" class="form-check-label text-tertiary-dark">
                Taxable Item
              </label>
            </div>
          </div>
        </div>

        <div class="mb-3">
          <label for="description" class="form-label text-tertiary-dark fw-medium">Description:</label>
          <textarea 
            id="description"
            v-model="form.description" 
            :disabled="loading"
            placeholder="Enter product description (optional)"
            class="form-control"
            rows="3"
          ></textarea>
        </div>

        <div v-if="error" class="alert alert-danger d-flex align-items-center mb-3" role="alert">
          <span class="me-2">⚠️</span>
          {{ error }}
        </div>

        <div class="d-flex gap-2 justify-content-end pt-3 border-top">
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
            class="btn btn-save"
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
</template>

<script>
import { useAddProduct } from '@/composables/ui/modals/useAddProduct'
import { onMounted, onBeforeUnmount } from 'vue'

export default {
  name: 'AddProductModal',
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
        const fileInput = document.querySelector('input[type="file"]')
        if (fileInput) fileInput.click()
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
/* Modal overlay and animation */
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
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 800px;
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideIn 0.3s ease;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem 1rem 2rem;
  border-bottom: 1px solid var(--neutral);
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
  color: var(--tertiary-medium);
  padding: 0.25rem;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.btn-close:hover:not(:disabled) {
  background-color: var(--neutral-light);
  color: var(--tertiary-dark);
}

.btn-close:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.product-form {
  padding: 1.5rem 2rem 2rem 2rem;
}

/* Image Upload Styles */
.image-upload-container {
  width: 100%;
}

.image-preview-area {
  width: 200px;
  height: 200px;
  border: 2px dashed var(--neutral);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.image-preview-area:hover {
  border-color: var(--primary);
  background-color: var(--neutral-light);
}

.image-preview-area.has-image {
  border: 2px solid var(--neutral);
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
  color: var(--tertiary-dark);
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
}

.upload-subtext {
  color: var(--tertiary-medium);
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
  background: rgba(0, 0, 0, 0.7);
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

/* Custom text colors using colors.css variables */
.text-tertiary-dark {
  color: var(--tertiary-dark) !important;
}

.text-tertiary-medium {
  color: var(--tertiary-medium) !important;
}

/* Form controls focus states using colors.css */
.form-select:focus,
.form-control:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25);
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

/* Custom scrollbar for modal content */
.modal-content::-webkit-scrollbar {
  width: 6px;
}

.modal-content::-webkit-scrollbar-track {
  background: var(--neutral-light);
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: var(--neutral-medium);
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: var(--neutral-dark);
}
</style>