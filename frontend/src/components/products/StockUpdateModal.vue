<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>Update Stock</h2>
        <button class="close-btn" @click="$emit('close')" :disabled="loading">
          ✕
        </button>
      </div>

      <div v-if="product" class="product-info">
        <div class="product-details">
          <div class="product-name">{{ product.product_name }}</div>
          <div class="product-meta">
            <span class="sku">SKU: {{ product.SKU }}</span>
            <span class="category">{{ getCategoryName(product.category_id) }}</span>
          </div>
        </div>
        <div class="current-stock">
          <div class="stock-label">Current Stock</div>
          <div class="stock-value" :class="getStockClass(product)">
            {{ product.stock }} {{ product.unit }}
          </div>
          <div class="stock-threshold">Min: {{ product.low_stock_threshold }}</div>
        </div>
      </div>
      
      <form @submit.prevent="handleSubmit" class="stock-form">
        <div class="form-group">
          <label for="operation_type">Operation: <span class="required">*</span></label>
          <select 
            id="operation_type" 
            v-model="form.operation_type" 
            required
            :disabled="loading"
            class="form-select"
            @change="onOperationChange"
          >
            <option value="add">Add Stock</option>
            <option value="remove">Remove Stock</option>
            <option value="set">Set Exact Stock</option>
          </select>
          <div class="operation-description">
            {{ operationDescription }}
          </div>
        </div>

        <div class="form-group">
          <label for="quantity">
            {{ form.operation_type === 'set' ? 'New Stock Quantity' : 'Quantity' }}: 
            <span class="required">*</span>
          </label>
          <input 
            id="quantity"
            v-model.number="form.quantity" 
            type="number" 
            :min="form.operation_type === 'remove' ? 1 : 0"
            :max="form.operation_type === 'remove' ? product?.stock : undefined"
            required 
            :disabled="loading"
            placeholder="Enter quantity"
            class="form-input"
            @input="calculateNewStock"
          />
          <div v-if="newStockPreview !== null" class="stock-preview">
            New stock will be: 
            <span :class="getPreviewStockClass(newStockPreview)">
              {{ newStockPreview }} {{ product?.unit }}
            </span>
          </div>
        </div>

        <div class="form-group">
          <label for="reason">Reason: <span class="required">*</span></label>
          <select 
            id="reason_select" 
            v-model="selectedReason" 
            :disabled="loading"
            class="form-select"
            @change="onReasonChange"
          >
            <option value="">Select a reason</option>
            <optgroup label="Stock Increase">
              <option value="Purchase/Delivery">Purchase/Delivery</option>
              <option value="Stock Return">Stock Return</option>
              <option value="Stock Transfer In">Stock Transfer In</option>
              <option value="Manual Recount">Manual Recount</option>
            </optgroup>
            <optgroup label="Stock Decrease">
              <option value="Sale">Sale</option>
              <option value="Damaged/Expired">Damaged/Expired</option>
              <option value="Stock Transfer Out">Stock Transfer Out</option>
              <option value="Theft/Loss">Theft/Loss</option>
              <option value="Manual Adjustment">Manual Adjustment</option>
            </optgroup>
            <optgroup label="Other">
              <option value="Inventory Correction">Inventory Correction</option>
              <option value="System Migration">System Migration</option>
              <option value="Custom">Custom Reason</option>
            </optgroup>
          </select>
          
          <input 
            v-if="selectedReason === 'Custom' || selectedReason === ''"
            id="reason"
            v-model="form.reason" 
            type="text" 
            required 
            :disabled="loading"
            placeholder="Enter reason for stock update"
            class="form-input custom-reason"
          />
        </div>

        <div v-if="form.operation_type === 'remove'" class="warning-message">
          <span class="warning-icon">⚠️</span>
          <div>
            <strong>Warning:</strong> This will remove {{ form.quantity || 0 }} units from stock.
            <br>Make sure this is correct as this action will be logged.
          </div>
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
            class="btn"
            :class="getSubmitButtonClass()"
          >
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? 'Updating...' : getSubmitButtonText() }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StockUpdateModal',
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
        operation_type: 'add',
        quantity: 0,
        reason: ''
      },
      selectedReason: '',
      newStockPreview: null
    }
  },
  computed: {
    isFormValid() {
      return this.form.operation_type &&
             this.form.quantity > 0 &&
             this.form.reason.trim() !== '' &&
             (this.form.operation_type !== 'remove' || this.form.quantity <= (this.product?.stock || 0))
    },
    operationDescription() {
      switch (this.form.operation_type) {
        case 'add':
          return 'Add the specified quantity to current stock'
        case 'remove':
          return 'Remove the specified quantity from current stock'
        case 'set':
          return 'Set the stock to the exact quantity specified'
        default:
          return ''
      }
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        this.initializeForm()
        this.$nextTick(() => {
          const firstInput = this.$el.querySelector('#operation_type')
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
      this.form = {
        operation_type: 'add',
        quantity: 0,
        reason: ''
      }
      this.selectedReason = ''
      this.newStockPreview = null
    },
    handleSubmit() {
      if (!this.isFormValid) return
      
      const formData = {
        operation_type: this.form.operation_type,
        quantity: this.form.quantity,
        reason: this.form.reason
      }
      
      this.$emit('submit', formData)
    },
    handleOverlayClick() {
      if (!this.loading) {
        this.$emit('close')
      }
    },
    onOperationChange() {
      this.form.quantity = 0
      this.newStockPreview = null
      
      // Clear reason when operation changes
      this.selectedReason = ''
      this.form.reason = ''
    },
    onReasonChange() {
      if (this.selectedReason && this.selectedReason !== 'Custom') {
        this.form.reason = this.selectedReason
      } else {
        this.form.reason = ''
      }
    },
    calculateNewStock() {
      if (!this.product || !this.form.quantity) {
        this.newStockPreview = null
        return
      }
      
      const currentStock = this.product.stock
      const quantity = parseInt(this.form.quantity) || 0
      
      switch (this.form.operation_type) {
        case 'add':
          this.newStockPreview = currentStock + quantity
          break
        case 'remove':
          this.newStockPreview = Math.max(0, currentStock - quantity)
          break
        case 'set':
          this.newStockPreview = quantity
          break
        default:
          this.newStockPreview = null
      }
    },
    getCategoryName(categoryId) {
      const categories = {
        'noodles': 'Noodles',
        'drinks': 'Drinks',
        'toppings': 'Toppings'
      }
      return categories[categoryId] || categoryId
    },
    getStockClass(product) {
      if (!product) return ''
      if (product.stock === 0) return 'stock-zero'
      if (product.stock <= product.low_stock_threshold) return 'stock-low'
      return 'stock-normal'
    },
    getPreviewStockClass(stock) {
      if (!this.product) return ''
      if (stock === 0) return 'stock-zero'
      if (stock <= this.product.low_stock_threshold) return 'stock-low'
      return 'stock-normal'
    },
    getSubmitButtonClass() {
      switch (this.form.operation_type) {
        case 'add':
          return 'btn-success'
        case 'remove':
          return 'btn-warning'
        case 'set':
          return 'btn-primary'
        default:
          return 'btn-primary'
      }
    },
    getSubmitButtonText() {
      switch (this.form.operation_type) {
        case 'add':
          return `Add ${this.form.quantity || 0} Units`
        case 'remove':
          return `Remove ${this.form.quantity || 0} Units`
        case 'set':
          return `Set to ${this.form.quantity || 0} Units`
        default:
          return 'Update Stock'
      }
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
  max-width: 500px;
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
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0.25rem;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.close-btn:hover:not(:disabled) {
  background-color: #f3f4f6;
  color: #374151;
}

.close-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.product-info {
  padding: 1.5rem 2rem;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-details {
  flex: 1;
}

.product-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.product-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.current-stock {
  text-align: right;
}

.stock-label {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.stock-value {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.stock-threshold {
  font-size: 0.75rem;
  color: #6b7280;
}

.stock-zero {
  color: #dc2626;
}

.stock-low {
  color: #ea580c;
}

.stock-normal {
  color: #059669;
}

.stock-form {
  padding: 1.5rem 2rem 2rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.required {
  color: #dc2626;
}

.form-input,
.form-select {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  background: white;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input:disabled,
.form-select:disabled {
  background-color: #f9fafb;
  cursor: not-allowed;
  opacity: 0.7;
}

.custom-reason {
  margin-top: 0.5rem;
}

.operation-description {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.stock-preview {
  font-size: 0.75rem;
  margin-top: 0.25rem;
  padding: 0.5rem;
  background: #f8fafc;
  border-radius: 0.375rem;
  border: 1px solid #e5e7eb;
}

.warning-message {
  background-color: #fef3c7;
  border: 1px solid #f59e0b;
  color: #92400e;
  padding: 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.warning-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.form-error {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
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
  border-top: 1px solid #e5e7eb;
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
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
  transform: translateY(-1px);
}

.btn-success {
  background-color: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #059669;
  transform: translateY(-1px);
}

.btn-warning {
  background-color: #f59e0b;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background-color: #d97706;
  transform: translateY(-1px);
}

.btn-secondary {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #e5e7eb;
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

  .product-info {
    padding: 1rem 1.5rem;
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .current-stock {
    text-align: left;
    width: 100%;
  }

  .stock-form {
    padding: 1rem 1.5rem 1.5rem 1.5rem;
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

  .product-info {
    padding: 0.75rem 1rem;
  }

  .stock-form {
    padding: 0.75rem 1rem 1rem 1rem;
  }

  .product-meta {
    flex-direction: column;
    gap: 0.25rem;
  }
}

/* Custom scrollbar */
.modal-content::-webkit-scrollbar {
  width: 6px;
}

.modal-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>