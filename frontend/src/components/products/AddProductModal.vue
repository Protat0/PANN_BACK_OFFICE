<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content large-modal" @click.stop>
      <div class="modal-header">
        <h2>{{ isEditMode ? 'Edit Product' : 'Add New Product' }}</h2>
        <button class="close-btn" @click="$emit('close')" :disabled="loading">
          ✕
        </button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="product-form">
        <!-- Product Image Upload Section -->
        <div class="form-group image-upload-section">
          <label class="image-upload-label">Product Image:</label>
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
                  <button type="button" class="change-image-btn" @click.stop="triggerFileInput">
                    Change Image
                  </button>
                  <button type="button" class="remove-image-btn" @click.stop="removeImage">
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
              class="hidden-file-input"
              :disabled="loading"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="product_name">Product Name: <span class="required">*</span></label>
            <input 
              id="product_name"
              v-model="form.product_name" 
              type="text" 
              required 
              :disabled="loading"
              placeholder="Enter product name"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="SKU">SKU: <span class="required">*</span></label>
            <input 
              id="SKU"
              v-model="form.SKU" 
              type="text" 
              required 
              :disabled="loading"
              placeholder="Enter SKU"
              class="form-input"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="category_id">Category: <span class="required">*</span></label>
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

          <div class="form-group">
            <label for="unit">Unit: <span class="required">*</span></label>
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

        <div class="form-row">
          <div class="form-group">
            <label for="cost_price">Cost Price (₱): <span class="required">*</span></label>
            <input 
              id="cost_price"
              v-model.number="form.cost_price" 
              type="number" 
              step="0.01"
              min="0"
              required 
              :disabled="loading"
              placeholder="0.00"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="selling_price">Selling Price (₱): <span class="required">*</span></label>
            <input 
              id="selling_price"
              v-model.number="form.selling_price" 
              type="number" 
              step="0.01"
              min="0"
              required 
              :disabled="loading"
              placeholder="0.00"
              class="form-input"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="stock">Stock Quantity: <span class="required">*</span></label>
            <input 
              id="stock"
              v-model.number="form.stock" 
              type="number" 
              min="0"
              required 
              :disabled="loading"
              placeholder="0"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="low_stock_threshold">Low Stock Threshold: <span class="required">*</span></label>
            <input 
              id="low_stock_threshold"
              v-model.number="form.low_stock_threshold" 
              type="number" 
              min="0"
              required 
              :disabled="loading"
              placeholder="10"
              class="form-input"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="expiry_date">Expiry Date:</label>
            <input 
              id="expiry_date"
              v-model="form.expiry_date" 
              type="date" 
              :disabled="loading"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="status">Status: <span class="required">*</span></label>
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

        <div class="form-row">
          <div class="form-group">
            <label for="barcode">Barcode:</label>
            <div class="barcode-input-group">
              <input 
                id="barcode"
                v-model="form.barcode" 
                type="text" 
                :disabled="loading"
                placeholder="Enter barcode or generate automatically"
                class="form-input"
              />
              <button 
                type="button" 
                @click="generateBarcode"
                :disabled="loading"
                class="btn btn-secondary"
              >
                Generate
              </button>
            </div>
          </div>

          <div class="form-group checkbox-group">
            <label for="is_taxable" class="checkbox-label">
              <input 
                id="is_taxable"
                v-model="form.is_taxable" 
                type="checkbox" 
                :disabled="loading"
              />
              <span class="checkmark"></span>
              Taxable Item
            </label>
          </div>
        </div>

        <div class="form-group">
          <label for="description">Description:</label>
          <textarea 
            id="description"
            v-model="form.description" 
            :disabled="loading"
            placeholder="Enter product description (optional)"
            class="form-textarea"
            rows="3"
          ></textarea>
        </div>

        <div v-if="error" class="form-error">
          <span class="error-icon">⚠️</span>
          {{ error }}
        </div>

        <div class="form-actions">
          <button 
            type="button" 
            @click="$emit('close')" 
            :disabled="loading"
            class="btn btn-secondary"
          >
            Cancel
          </button>
          <button 
            type="submit" 
            :disabled="loading || !isFormValid" 
            class="btn btn-primary"
          >
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? 'Saving...' : (isEditMode ? 'Update Product' : 'Create Product') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AddProductModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    product: {
      type: Object,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: null
    }
  },
  emits: ['close', 'submit'],
  data() {
    return {
      form: {
        product_name: '',
        category_id: '',
        SKU: '',
        unit: '',
        stock: 0,
        low_stock_threshold: 10,
        cost_price: 0,
        selling_price: 0,
        expiry_date: '',
        status: 'active',
        is_taxable: false,
        barcode: '',
        description: '',
        image: null
      },
      imagePreview: null,
      imageFile: null
    }
  },
  computed: {
    isEditMode() {
      return this.product !== null
    },
    isFormValid() {
      return this.form.product_name.trim() !== '' &&
             this.form.SKU.trim() !== '' &&
             this.form.category_id !== '' &&
             this.form.unit !== '' &&
             this.form.cost_price >= 0 &&
             this.form.selling_price >= 0 &&
             this.form.stock >= 0 &&
             this.form.low_stock_threshold >= 0
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        this.initializeForm()
        // Focus on first input when modal opens
        this.$nextTick(() => {
          const firstInput = this.$el.querySelector('#product_name')
          if (firstInput) firstInput.focus()
        })
      }
    },
    product: {
      handler() {
        if (this.show) {
          this.initializeForm()
        }
      },
      deep: true
    }
  },
  methods: {
    initializeForm() {
      if (this.isEditMode && this.product) {
        this.form = {
          product_name: this.product.product_name || '',
          category_id: this.product.category_id || '',
          SKU: this.product.SKU || '',
          unit: this.product.unit || '',
          stock: this.product.stock || 0,
          low_stock_threshold: this.product.low_stock_threshold || 10,
          cost_price: this.product.cost_price || 0,
          selling_price: this.product.selling_price || 0,
          expiry_date: this.product.expiry_date ? this.product.expiry_date.split('T')[0] : '',
          status: this.product.status || 'active',
          is_taxable: this.product.is_taxable || false,
          barcode: this.product.barcode || '',
          description: this.product.description || '',
          image: null
        }
        
        // Set image preview if product has an image
        if (this.product.image_url || this.product.image) {
          this.imagePreview = this.product.image_url || this.product.image
        } else {
          this.imagePreview = null
        }
        this.imageFile = null
      } else {
        this.form = {
          product_name: '',
          category_id: '',
          SKU: '',
          unit: '',
          stock: 0,
          low_stock_threshold: 10,
          cost_price: 0,
          selling_price: 0,
          expiry_date: '',
          status: 'active',
          is_taxable: false,
          barcode: '',
          description: '',
          image: null
        }
        this.imagePreview = null
        this.imageFile = null
      }
    },

    triggerFileInput() {
      if (!this.loading) {
        this.$refs.fileInput.click()
      }
    },

    handleImageUpload(event) {
      const file = event.target.files[0]
      if (!file) return

      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please select a valid image file (PNG, JPG, JPEG)')
        return
      }

      // Validate file size (5MB limit)
      if (file.size > 5 * 1024 * 1024) {
        alert('Image size should be less than 5MB')
        return
      }

      this.imageFile = file
      
      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        this.imagePreview = e.target.result
      }
      reader.readAsDataURL(file)
    },

    removeImage() {
      this.imagePreview = null
      this.imageFile = null
      this.form.image = null
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
    },

    async convertImageToBase64() {
      if (!this.imageFile) return null
      
      return new Promise((resolve) => {
        const reader = new FileReader()
        reader.onload = (e) => resolve(e.target.result)
        reader.readAsDataURL(this.imageFile)
      })
    },

    async handleSubmit() {
      if (!this.isFormValid) return
      
      // Create a clean copy of the form data
      const formData = { ...this.form }
      
      // Handle image upload
      if (this.imageFile) {
        // Convert image to base64 or handle file upload based on your backend requirements
        const imageBase64 = await this.convertImageToBase64()
        formData.image = imageBase64
      } else if (this.imagePreview && this.isEditMode) {
        // Keep existing image URL for edit mode
        formData.image_url = this.imagePreview
      }
      
      // Clean up empty strings and convert to proper types
      if (!formData.expiry_date) {
        delete formData.expiry_date
      }
      if (!formData.barcode) {
        delete formData.barcode
      }
      if (!formData.description) {
        delete formData.description
      }
      
      this.$emit('submit', formData)
    },

    handleOverlayClick() {
      if (!this.loading) {
        this.$emit('close')
      }
    },

    generateBarcode() {
      // Generate a simple barcode based on SKU and timestamp
      const timestamp = Date.now().toString().slice(-6)
      const sku = this.form.SKU.replace(/[^a-zA-Z0-9]/g, '').toUpperCase()
      this.form.barcode = `${sku}${timestamp}`
    }
  },
  mounted() {
    this.handleEscape = (e) => {
      if (e.key === 'Escape' && this.show && !this.loading) {
        this.$emit('close')
      }
    }
    
    document.addEventListener('keydown', this.handleEscape)
  },

  beforeUnmount() {
    if (this.handleEscape) {
      document.removeEventListener('keydown', this.handleEscape)
    }
  }
}
</script>

<style scoped>
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
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  color: var(--tertiary-dark);
  font-size: 1.5rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--tertiary-medium);
  padding: 0.25rem;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.close-btn:hover:not(:disabled) {
  background-color: var(--neutral-light);
  color: var(--tertiary-dark);
}

.close-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.product-form {
  padding: 1.5rem 2rem 2rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Image Upload Styles */
.image-upload-section {
  margin-bottom: 1rem;
}

.image-upload-label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
  display: block;
}

.image-upload-container {
  width: 100%;
}

.image-preview-area {
  width: 200px;
  height: 200px;
  border: 2px dashed #d1d5db;
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
  border-color: #3b82f6;
  background-color: #f8fafc;
}

.image-preview-area.has-image {
  border: 2px solid #e5e7eb;
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

.change-image-btn,
.remove-image-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.change-image-btn {
  background-color: var(--primary);
  color: white;
}

.change-image-btn:hover {
  background-color: var(--primary-dark);
}

.remove-image-btn {
  background-color: var(--error);
  color: white;
}

.remove-image-btn:hover {
  background-color: var(--error-dark);
}

.hidden-file-input {
  display: none;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: var(--tertiary-dark);
  font-size: 0.875rem;
}

.required {
  color: var(--error);
}

.form-input,
.form-select,
.form-textarea {
  padding: 0.75rem;
  border: 1px solid var(--neutral-medium);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  background: white;
  color: var(--tertiary-dark);
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(115, 146, 226, 0.1);
}

.form-input:disabled,
.form-select:disabled,
.form-textarea:disabled {
  background-color: var(--neutral-light);
  cursor: not-allowed;
  opacity: 0.7;
}

.barcode-input-group {
  display: flex;
  gap: 0.5rem;
}

.barcode-input-group .form-input {
  flex: 1;
}

.checkbox-group {
  justify-content: center;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 0.5rem;
  font-weight: 400 !important;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--primary);
  cursor: pointer;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-error {
  background-color: var(--error-light);
  border: 1px solid var(--error);
  color: var(--error-dark);
  padding: 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.error-icon {
  font-size: 1rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--neutral);
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 42px;
}

.btn-primary {
  background-color: var(--primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--primary-dark);
  transform: translateY(-1px);
}

.btn-secondary {
  background-color: var(--neutral-light);
  color: var(--tertiary-dark);
  border: 1px solid var(--neutral-medium);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--neutral-medium);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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
    gap: 1rem;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .form-actions {
    flex-direction: column-reverse;
    gap: 0.75rem;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .barcode-input-group {
    flex-direction: column;
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