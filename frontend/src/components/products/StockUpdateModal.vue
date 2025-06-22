<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="text-tertiary-dark">Update Stock</h2>
        <button class="btn-close" @click="closeModal" :disabled="loading" aria-label="Close">
          ✕
        </button>
      </div>

      <div v-if="product" class="product-info bg-light border-bottom">
        <div class="product-details">
          <div class="product-name fw-semibold text-tertiary-dark">{{ product.product_name }}</div>
          <div class="product-meta d-flex gap-3">
            <span class="text-tertiary-medium">SKU: {{ product.SKU }}</span>
            <span class="text-tertiary-medium">{{ getCategoryName(product.category_id) }}</span>
          </div>
        </div>
        <div class="current-stock text-end">
          <div class="stock-label text-uppercase text-tertiary-medium">Current Stock</div>
          <div class="stock-value" :class="getStockClass(product)">
            {{ product.stock }} {{ product.unit }}
          </div>
          <div class="stock-threshold text-tertiary-medium">Min: {{ product.low_stock_threshold }}</div>
        </div>
      </div>
      
      <form @submit.prevent="handleSubmit" class="stock-form">
        <div class="mb-3">
          <label for="operation_type" class="form-label text-tertiary-dark fw-medium">
            Operation <span class="text-danger">*</span>
          </label>
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
          <div class="form-text text-tertiary-medium">
            {{ operationDescription }}
          </div>
        </div>

        <div class="mb-3">
          <label for="quantity" class="form-label text-tertiary-dark fw-medium">
            {{ form.operation_type === 'set' ? 'New Stock Quantity' : 'Quantity' }}
            <span class="text-danger">*</span>
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
            class="form-control"
            @input="calculateNewStock"
          />
          <div v-if="newStockPreview !== null" class="mt-2 p-2 bg-light border rounded">
            <small class="text-tertiary-medium">
              New stock will be: 
              <span :class="getPreviewStockClass(newStockPreview)" class="fw-semibold">
                {{ newStockPreview }} {{ product?.unit }}
              </span>
            </small>
          </div>
        </div>

        <div class="mb-3">
          <label for="reason_select" class="form-label text-tertiary-dark fw-medium">
            Reason <span class="text-danger">*</span>
          </label>
          <select 
            id="reason_select" 
            v-model="selectedReason" 
            :disabled="loading"
            class="form-select"
            @change="onReasonChange"
          >
            <option value="">Select a reason</option>
            <optgroup label="Stock Increase">
              <option 
                v-for="reason in stockReasons.increase" 
                :key="reason" 
                :value="reason"
              >
                {{ reason }}
              </option>
            </optgroup>
            <optgroup label="Stock Decrease">
              <option 
                v-for="reason in stockReasons.decrease" 
                :key="reason" 
                :value="reason"
              >
                {{ reason }}
              </option>
            </optgroup>
            <optgroup label="Other">
              <option 
                v-for="reason in stockReasons.other" 
                :key="reason" 
                :value="reason"
              >
                {{ reason }}
              </option>
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
            class="form-control mt-2"
          />
        </div>

        <div v-if="form.operation_type === 'remove'" class="alert alert-warning d-flex align-items-start">
          <span class="me-2">⚠️</span>
          <div>
            <strong>Warning:</strong> This will remove {{ form.quantity || 0 }} units from stock.
            <br>Make sure this is correct as this action will be logged.
          </div>
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
            :class="['btn', getSubmitButtonClass()]"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status">
              <span class="visually-hidden">Loading...</span>
            </span>
            {{ loading ? 'Updating...' : getSubmitButtonText() }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { useStockUpdate } from '@/composables/ui/modals/useStockUpdate'
import { onMounted, onBeforeUnmount } from 'vue'

export default {
  name: 'StockUpdateModal',
  emits: ['success'],
  
  setup(props, { emit }) {
    const {
      // State
      show,
      product,
      loading,
      error,
      form,
      selectedReason,
      newStockPreview,
      stockReasons,
      
      // Computed
      isFormValid,
      operationDescription,
      
      // Actions
      openStockModal,
      closeModal,
      submitStockUpdate,
      
      // Form methods
      onOperationChange,
      onReasonChange,
      calculateNewStock,
      
      // Helper methods
      getCategoryName,
      getStockClass,
      getPreviewStockClass,
      getSubmitButtonClass,
      getSubmitButtonText,
      
      // Utility methods
      setupKeyboardListeners,
      cleanupKeyboardListeners
    } = useStockUpdate()
    
    // Setup keyboard listeners on mount
    onMounted(() => {
      setupKeyboardListeners()
    })
    
    // Cleanup on unmount
    onBeforeUnmount(() => {
      cleanupKeyboardListeners()
    })
    
    // Methods
    const handleSubmit = () => {
      submitStockUpdate((result, formData) => {
        const operation = formData.operation_type
        const quantity = formData.quantity
        let message = ''
        
        if (operation === 'add') {
          message = `Added ${quantity} units to "${product.value.product_name}"`
        } else if (operation === 'remove') {
          message = `Removed ${quantity} units from "${product.value.product_name}"`
        } else {
          message = `Set stock to ${quantity} units for "${product.value.product_name}"`
        }
        
        emit('success', {
          message,
          product: result,
          operation: formData
        })
      })
    }
    
    const handleOverlayClick = () => {
      if (!loading.value) {
        closeModal()
      }
    }
    
    // Expose methods for parent component
    const openStock = (productData) => {
      openStockModal(productData)
    }
    
    return {
      // State
      show,
      product,
      loading,
      error,
      form,
      selectedReason,
      newStockPreview,
      stockReasons,
      
      // Computed
      isFormValid,
      operationDescription,
      
      // Methods
      closeModal,
      handleSubmit,
      handleOverlayClick,
      onOperationChange,
      onReasonChange,
      calculateNewStock,
      getCategoryName,
      getStockClass,
      getPreviewStockClass,
      getSubmitButtonClass,
      getSubmitButtonText,
      
      // Exposed methods
      openStock
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

.product-info {
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-details {
  flex: 1;
}

.product-name {
  font-size: 1.125rem;
  margin-bottom: 0.25rem;
}

.product-meta {
  font-size: 0.875rem;
}

.current-stock {
  text-align: right;
}

.stock-label {
  font-size: 0.75rem;
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
}

.stock-form {
  padding: 1.5rem 2rem 2rem 2rem;
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

/* Stock status colors using colors.css variables */
.text-success {
  color: var(--success) !important;
}

.text-warning {
  color: var(--warning, #ffc107) !important;
}

.text-danger {
  color: var(--error) !important;
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