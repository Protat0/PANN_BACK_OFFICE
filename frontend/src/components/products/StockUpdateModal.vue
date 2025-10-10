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
            {{ getCurrentStock(product) }} {{ product.unit }}
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
            <option value="add">Add Stock (General)</option>
            <option value="purchase">New Purchase Order</option>
            <option value="remove">Remove Stock</option>
            <option value="set">Set Exact Stock</option>
          </select>
          <div class="form-text text-tertiary-medium">
            {{ operationDescription }}
          </div>
        </div>

        <!-- Batch Information Section - Show for purchases OR when reason is Purchase/Delivery -->
        <div v-if="shouldShowBatchFields" class="batch-section mb-4 p-3 border rounded bg-light">
          <h6 class="text-tertiary-dark mb-3">Batch Information</h6>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="batch_number" class="form-label text-tertiary-dark fw-medium">
                Batch Number
              </label>
              <input 
                id="batch_number"
                v-model="form.batch_number" 
                type="text" 
                :disabled="loading"
                placeholder="Auto-generated if left blank"
                class="form-control"
              />
              <div class="form-text text-tertiary-medium">
                Leave blank to auto-generate batch number
              </div>
            </div>
            
            <div class="col-md-6 mb-3">
              <label for="supplier" class="form-label text-tertiary-dark fw-medium">
                Supplier
              </label>
              <input 
                id="supplier"
                v-model="form.supplier" 
                type="text" 
                :disabled="loading"
                placeholder="Supplier name"
                class="form-control"
              />
            </div>
          </div>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="unit_cost" class="form-label text-tertiary-dark fw-medium">
                Unit Cost <span class="text-danger">*</span>
              </label>
              <div class="input-group">
                <span class="input-group-text">₱</span>
                <input 
                  id="unit_cost"
                  v-model.number="form.unit_cost" 
                  type="number" 
                  min="0"
                  step="0.01"
                  required 
                  :disabled="loading"
                  placeholder="0.00"
                  class="form-control"
                />
              </div>
            </div>
            
            <div class="col-md-6 mb-3">
              <label for="expiry_date" class="form-label text-tertiary-dark fw-medium">
                Expiry Date <span class="text-danger">*</span>
              </label>
              <input 
                id="expiry_date"
                v-model="form.expiry_date" 
                type="date" 
                required
                :disabled="loading"
                class="form-control"
                :min="today"
              />
            </div>
          </div>
          
          <div class="mb-3">
            <label for="purchase_notes" class="form-label text-tertiary-dark fw-medium">
              Purchase Notes
            </label>
            <textarea 
              id="purchase_notes"
              v-model="form.purchase_notes" 
              rows="2"
              :disabled="loading"
              placeholder="Additional notes about this purchase..."
              class="form-control"
            />
          </div>
        </div>

        <div class="mb-3">
          <label for="quantity" class="form-label text-tertiary-dark fw-medium">
            {{ getQuantityLabel() }}
            <span class="text-danger">*</span>
          </label>
          <input 
            id="quantity"
            v-model.number="form.quantity" 
            type="number" 
            :min="1"
            :max="getMaxQuantity()"
            required 
            :disabled="loading"
            :placeholder="getQuantityPlaceholder()"
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
            required
          >
            <option value="">Select a reason</option>
            <optgroup v-if="form.operation_type === 'purchase'" label="Purchase Orders">
              <option value="New Stock Delivery">New Stock Delivery</option>
              <option value="Purchase Order Received">Purchase Order Received</option>
              <option value="Supplier Delivery">Supplier Delivery</option>
              <option value="Inventory Replenishment">Inventory Replenishment</option>
            </optgroup>
            <optgroup v-else-if="form.operation_type === 'add'" label="Stock Increase">
              <option value="Purchase/Delivery">Purchase/Delivery</option>
              <option value="Stock Return">Stock Return</option>
              <option value="Stock Transfer In">Stock Transfer In</option>
              <option value="Manual Recount">Manual Recount</option>
            </optgroup>
            <optgroup v-else-if="form.operation_type === 'remove'" label="Stock Decrease">
              <option value="Sale">Sale</option>
              <option value="Damaged/Expired">Damaged/Expired</option>
              <option value="Stock Transfer Out">Stock Transfer Out</option>
              <option value="Theft/Loss">Theft/Loss</option>
              <option value="Manual Adjustment">Manual Adjustment</option>
            </optgroup>
            <optgroup v-else label="Other">
              <option value="Inventory Correction">Inventory Correction</option>
              <option value="System Migration">System Migration</option>
              <option value="Custom">Custom</option>
            </optgroup>
          </select>
          
          <input 
            v-if="selectedReason === 'Custom' || (selectedReason === '' && form.reason)"
            id="reason"
            v-model="form.reason" 
            type="text" 
            required 
            :disabled="loading"
            placeholder="Enter custom reason for stock update"
            class="form-control mt-2"
          />
        </div>

        <!-- Warning Messages -->
        <div v-if="form.operation_type === 'remove'" class="alert alert-warning d-flex align-items-start">
          <span class="me-2">⚠️</span>
          <div>
            <strong>Warning:</strong> This will remove {{ form.quantity || 0 }} units from stock.
            <br>Make sure this is correct as this action will be logged.
          </div>
        </div>

        <div v-if="shouldShowBatchFields" class="alert alert-info d-flex align-items-start">
          <span class="me-2">ℹ️</span>
          <div>
            <strong>New Batch:</strong> This will create a new batch with {{ form.quantity || 0 }} units.
            <br>The batch will be tracked separately for inventory management.
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
import { useProducts } from '@/composables/api/useProducts'
import { useBatches } from '@/composables/api/useBatches'
import { useCategories } from '@/composables/api/useCategories'
import { useToast } from '@/composables/ui/useToast'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

export default {
  name: 'StockUpdateModal',
  emits: ['success'],
  
  setup(props, { emit }) {
    // Composables
    const { updateProductStock, error: productError, loading: productLoading } = useProducts()
    const { createBatch, error: batchError, loading: batchLoading } = useBatches()
    const { activeCategories } = useCategories()
    const { toast } = useToast()
    
    // State
    const show = ref(false)
    const product = ref(null)
    const selectedReason = ref('')
    const newStockPreview = ref(null)
    
    // Form data - properly initialized
    const form = ref({
      operation_type: 'add',
      quantity: null,
      reason: '',
      batch_number: '',
      supplier: '',
      unit_cost: null,
      expiry_date: '',
      purchase_notes: ''
    })
    
    // Computed properties
    const loading = computed(() => productLoading.value || batchLoading.value)
    const error = computed(() => productError.value || batchError.value)
    
    const today = computed(() => {
      return new Date().toISOString().split('T')[0]
    })
        
    const shouldShowBatchFields = computed(() => {
      return form.value.operation_type === 'purchase' || 
            (form.value.operation_type === 'add' && selectedReason.value === 'Purchase/Delivery')
    })
    
    const isFormValid = computed(() => {
      const hasQuantity = form.value.quantity != null && Number(form.value.quantity) > 0
      const hasReason = selectedReason.value || form.value.reason
      
      if (shouldShowBatchFields.value) {
        const hasUnitCost = form.value.unit_cost != null && Number(form.value.unit_cost) > 0
        const hasExpiryDate = form.value.expiry_date
        return hasQuantity && hasReason && hasUnitCost && hasExpiryDate
      }
      
      return hasQuantity && hasReason
    })
    
    const operationDescription = computed(() => {
      if (!form.value) return ''
      
      switch (form.value.operation_type) {
        case 'add':
          return 'Add the specified quantity to current stock'
        case 'purchase':
          return 'Create a new batch from purchase order'
        case 'remove':
          return 'Remove the specified quantity from stock'
        case 'set':
          return 'Set stock to exact quantity specified'
        default:
          return ''
      }
    })
    
    // Helper functions
    const getCurrentStock = (product) => {
      return product?.total_stock ?? product?.stock ?? 0
    }
    
    const getCategoryName = (categoryId) => {
      if (!categoryId) return 'Uncategorized'
      const category = activeCategories.value.find(c => c._id === categoryId)
      return category?.category_name || 'Unknown'
    }
    
    const getStockClass = (product) => {
      const stock = getCurrentStock(product)
      if (stock === 0) return 'text-danger'
      if (stock <= (product?.low_stock_threshold || 15)) return 'text-warning'
      return 'text-success'
    }
    
    const getPreviewStockClass = (newStock) => {
      if (newStock === 0) return 'text-danger'
      if (newStock <= (product.value?.low_stock_threshold || 15)) return 'text-warning'
      return 'text-success'
    }
    
    const getSubmitButtonClass = () => {
      if (form.value.operation_type === 'remove') return 'btn-delete'
      if (shouldShowBatchFields.value) return 'btn-add'
      return 'btn-submit'
    }
    
    const getSubmitButtonText = () => {
      if (form.value.operation_type === 'purchase') return 'Create Batch'
      if (shouldShowBatchFields.value) return 'Add Batch'
      return 'Update Stock'
    }
    
    const getQuantityLabel = () => {
      if (!form.value) return 'Quantity'
      
      switch (form.value.operation_type) {
        case 'purchase':
          return 'Quantity Received'
        case 'add':
          return selectedReason.value === 'Purchase/Delivery' ? 'Quantity Received' : 'Quantity to Add'
        case 'remove':
          return 'Quantity to Remove'
        case 'set':
          return 'New Stock Quantity'
        default:
          return 'Quantity'
      }
    }
    
    const getQuantityPlaceholder = () => {
      if (!form.value) return 'Enter quantity'
      
      switch (form.value.operation_type) {
        case 'purchase':
          return 'Enter received quantity'
        case 'add':
          return selectedReason.value === 'Purchase/Delivery' ? 'Enter received quantity' : 'Enter quantity to add'
        case 'remove':
          return 'Enter quantity to remove'
        case 'set':
          return 'Enter new stock level'
        default:
          return 'Enter quantity'
      }
    }
    
    const getMinQuantity = () => {
      return 1
    }
    
    const getMaxQuantity = () => {
      if (!form.value || !product.value) return undefined
      return form.value.operation_type === 'remove' ? getCurrentStock(product.value) : undefined
    }
    
    const generateBatchNumber = () => {
      const now = new Date()
      const year = now.getFullYear()
      const month = String(now.getMonth() + 1).padStart(2, '0')
      const day = String(now.getDate()).padStart(2, '0')
      const timestamp = now.getTime().toString().slice(-4)
      
      return `BTH-${year}${month}${day}-${timestamp}`
    }
    
    const calculateNewStock = () => {
      if (!product.value || !form.value) return
      
      const currentStock = getCurrentStock(product.value)
      const quantity = form.value.quantity || 0
      
      switch (form.value.operation_type) {
        case 'add':
        case 'purchase':
          newStockPreview.value = currentStock + quantity
          break
        case 'remove':
          newStockPreview.value = Math.max(0, currentStock - quantity)
          break
        case 'set':
          newStockPreview.value = quantity
          break
        default:
          newStockPreview.value = null
      }
    }
    
    // Event handlers
    const onOperationChange = () => {
      selectedReason.value = ''
      form.value.reason = ''
      form.value.quantity = null
      newStockPreview.value = null
      
      // Clear batch fields when not needed
      if (!shouldShowBatchFields.value) {
        form.value.batch_number = ''
        form.value.supplier = ''
        form.value.unit_cost = null
        form.value.expiry_date = ''
        form.value.purchase_notes = ''
      }
    }
    
    const onReasonChange = () => {
      if (selectedReason.value !== 'Custom') {
        form.value.reason = selectedReason.value
      } else {
        form.value.reason = ''
      }
    }
    
    // Modal actions
    const openStockModal = (productData) => {
      product.value = productData
      show.value = true
      resetForm()
    }
    
    const closeModal = () => {
      show.value = false
      product.value = null
      resetForm()
    }
    
    const resetForm = () => {
      form.value = {
        operation_type: 'add',
        quantity: null,
        reason: '',
        batch_number: '',
        supplier: '',
        unit_cost: null,
        expiry_date: '',
        purchase_notes: ''
      }
      selectedReason.value = ''
      newStockPreview.value = null
    }
    
    const handleSubmit = async () => {
      try {
        // Validate form data before submission
        const quantityValue = Number(form.value.quantity)
        if (!quantityValue || quantityValue <= 0) {
          toast.error('Quantity must be greater than 0')
          return
        }

        // Auto-generate batch number if creating batch and field is empty
        if (shouldShowBatchFields.value && !form.value.batch_number) {
          form.value.batch_number = generateBatchNumber()
        }
        
        let result
        
        if (shouldShowBatchFields.value) {
          // Create new batch - use the correct field names that match your backend
          const batchData = {
            product_id: product.value._id,
            batch_number: form.value.batch_number,
            quantity_received: quantityValue, // Backend expects this field name
            cost_price: Number(form.value.unit_cost), // Backend expects this field name
            expiry_date: form.value.expiry_date,
            supplier_id: form.value.supplier || null, // Backend might expect supplier_id
            reason: form.value.reason || selectedReason.value
          }
          
          // Add optional fields if they exist in your backend
          if (form.value.purchase_notes) {
            batchData.notes = form.value.purchase_notes
          }
          
          console.log('Sending batch data with correct field names:', batchData)
          result = await createBatch(batchData)
        } else {
          // Regular stock update
          const stockData = {
            operation_type: form.value.operation_type,
            quantity: quantityValue,
            reason: form.value.reason || selectedReason.value
          }
          
          console.log('Sending stock data:', stockData)
          result = await updateProductStock(product.value._id, stockData)
        }
        
        const operation = form.value.operation_type
        const quantity = form.value.quantity
        let message = ''
        
        if (operation === 'purchase') {
          message = `New batch created: ${quantity} units of "${product.value.product_name}"`
        } else if (operation === 'add' && selectedReason.value === 'Purchase/Delivery') {
          message = `New batch added: ${quantity} units of "${product.value.product_name}"`
        } else if (operation === 'add') {
          message = `Added ${quantity} units to "${product.value.product_name}"`
        } else if (operation === 'remove') {
          message = `Removed ${quantity} units from "${product.value.product_name}"`
        } else {
          message = `Set stock to ${quantity} units for "${product.value.product_name}"`
        }
        
        toast.success(message)
        
        emit('success', {
          message,
          product: result,
          operation: form.value
        })
        
        closeModal()
        
      } catch (err) {
        console.error('Stock update failed:', err)
        console.error('Error details:', err.response?.data)
        
        // More specific error handling
        if (err.response?.data?.message) {
          toast.error(err.response.data.message)
        } else if (err.response?.data?.error) {
          toast.error(err.response.data.error)
        } else if (err.message) {
          toast.error(err.message)
        } else {
          toast.error('Failed to update stock')
        }
      }
    }
    
    const handleOverlayClick = () => {
      if (!loading.value) {
        closeModal()
      }
    }
    
    // Keyboard shortcuts
    const handleKeydown = (event) => {
      if (show.value && event.key === 'Escape' && !loading.value) {
        closeModal()
      }
    }
    
    onMounted(() => {
      document.addEventListener('keydown', handleKeydown)
    })
    
    onBeforeUnmount(() => {
      document.removeEventListener('keydown', handleKeydown)
    })
    
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
      today,
      shouldShowBatchFields,
      
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
      getCurrentStock,
      getQuantityLabel,
      getQuantityPlaceholder,
      getMinQuantity,
      getMaxQuantity,
      generateBatchNumber,
      
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
  max-width: 600px;
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

.batch-section {
  background-color: var(--neutral-light);
  border-color: var(--primary-light) !important;
}

.batch-section h6 {
  color: var(--primary-dark);
  font-weight: 600;
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

/* Input group styling */
.input-group-text {
  background-color: var(--neutral-light);
  border-color: var(--neutral-medium);
  color: var(--tertiary-dark);
}

/* Responsive Design */
@media (max-width: 768px) {
  .modal-content {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
    max-width: 500px;
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

  .batch-section {
    padding: 1rem;
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

  .batch-section {
    padding: 0.75rem;
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