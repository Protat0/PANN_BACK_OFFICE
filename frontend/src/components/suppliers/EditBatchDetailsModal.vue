<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content modern-modal">
        <!-- Modal Header -->
        <div class="modal-header border-0 pb-0">
          <div class="d-flex align-items-center">
            <div class="modal-icon me-3">
              <Edit :size="24" />
            </div>
            <div>
              <h4 class="modal-title mb-1">Edit Purchase Order</h4>
              <p class="text-muted mb-0 small">
                Order ID: <strong>{{ editForm.id }}</strong>
              </p>
            </div>
          </div>
          <button 
            type="button" 
            class="btn-close" 
            @click="handleClose"
            aria-label="Close"
          ></button>
        </div>

        <!-- Modal Body -->
        <div class="modal-body pt-4">
          <!-- Order Information -->
          <div class="card mb-4">
            <div class="card-header bg-light">
              <h6 class="mb-0">
                <Calendar :size="18" class="me-2" />
                Order Information
              </h6>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-4">
                  <label class="form-label">Order Date (Read-only)</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    :value="formatDate(editForm.date)"
                    readonly
                    disabled
                  >
                </div>
                <div class="col-md-4">
                  <label class="form-label">Expected Delivery <span class="text-danger">*</span></label>
                  <div v-if="!isEditingExpectedDate" 
                       class="form-control clickable-field" 
                       @click="isEditingExpectedDate = true"
                       title="Click to edit">
                    <span v-if="editForm.expectedDate">
                      {{ formatDate(editForm.expectedDate) }}
                    </span>
                    <span v-else class="text-muted">
                      Click to set expected delivery date
                    </span>
                    <small class="float-end text-primary">
                      <Edit :size="14" />
                    </small>
                  </div>
                  <input 
                    v-else
                    type="date" 
                    class="form-control" 
                    v-model="editForm.expectedDate"
                    :min="editForm.date"
                    @blur="isEditingExpectedDate = false"
                    ref="expectedDateInput"
                  >
                </div>
                <div class="col-md-4">
                  <label class="form-label">Status</label>
                  <select class="form-select" v-model="editForm.status" disabled>
                    <option value="Pending Delivery">Pending Delivery</option>
                    <option value="Partially Received">Partially Received</option>
                    <option value="Received">Received</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Items Section -->
          <div class="card mb-4">
            <div class="card-header bg-light d-flex justify-content-between align-items-center">
              <h6 class="mb-0">
                <Package :size="18" class="me-2" />
                Order Items
                <span class="badge bg-primary ms-2">{{ editForm.items.length }}</span>
              </h6>
              <button 
                type="button" 
                class="btn btn-sm btn-outline-primary"
                @click="addItem"
              >
                <Plus :size="16" class="me-1" />
                Add Item
              </button>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table table-borderless mb-0 edit-items-table">
                  <thead class="table-light">
                    <tr>
                      <th style="width: 40px;">#</th>
                      <th style="width: 160px;">Category <span class="text-danger">*</span></th>
                      <th style="width: 160px;">Subcategory <span class="text-danger">*</span></th>
                      <th style="width: 180px;">Product <span class="text-danger">*</span></th>
                      <th style="width: 120px;">Batch Number</th>
                      <th style="width: 100px;">Quantity <span class="text-danger">*</span></th>
                      <th style="width: 120px;">Unit Price (₱) <span class="text-danger">*</span></th>
                      <th style="width: 120px;">Total Price</th>
                      <th style="width: 120px;">Expiry Date</th>
                      <th style="width: 60px;"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, index) in editForm.items" :key="index" class="item-row">
                      <td class="text-center">{{ index + 1 }}</td>
                      
                      <!-- Category (Dropdown for new, Text for existing) -->
                      <td>
                        <select 
                          v-if="item.isNew"
                          class="form-select form-select-sm"
                          :class="{ 'is-invalid': item.errors?.category }"
                          v-model="item.categoryId"
                          @change="onCategoryChange(index)"
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
                        <div v-else class="text-muted small">
                          {{ getCategoryName(item) || 'N/A' }}
                        </div>
                      </td>
                      
                      <!-- Subcategory (Dropdown for new, Text for existing) -->
                      <td>
                        <select 
                          v-if="item.isNew"
                          class="form-select form-select-sm"
                          :class="{ 'is-invalid': item.errors?.subcategory }"
                          v-model="item.subcategoryName"
                          @change="onSubcategoryChange(index)"
                          :disabled="!item.categoryId"
                        >
                          <option value="">Select Subcategory</option>
                          <option 
                            v-for="subcategory in getSubcategoriesForItem(item)" 
                            :key="subcategory.name"
                            :value="subcategory.name"
                          >
                            {{ subcategory.name }} ({{ subcategory.product_count }})
                          </option>
                        </select>
                        <div v-else class="text-muted small">
                          {{ item.subcategoryName || 'N/A' }}
                        </div>
                      </td>
                      
                      <!-- Product Dropdown (for new items) or Product Name (for existing items) -->
                      <td>
                        <select 
                          v-if="item.isNew"
                          class="form-select form-select-sm"
                          :class="{ 'is-invalid': item.errors?.product }"
                          v-model="item.productId"
                          @change="onProductChange(index)"
                          :disabled="!item.subcategoryName"
                        >
                          <option value="">Select Product</option>
                          <option 
                            v-for="product in getProductsForItem(item)" 
                            :key="product._id"
                            :value="product._id"
                          >
                            {{ product.product_name }} - {{ product.SKU }}
                          </option>
                        </select>
                        <div v-else>
                          <strong>{{ item.name }}</strong>
                          <br>
                          <small class="text-muted">{{ item.productId }}</small>
                        </div>
                      </td>
                      
                      <!-- Batch Number -->
                      <td>
                        <input 
                          type="text" 
                          class="form-control form-control-sm" 
                          v-model="item.batchNumber"
                          readonly
                          disabled
                        >
                      </td>
                      <td>
                        <input 
                          type="number" 
                          class="form-control form-control-sm" 
                          v-model.number="item.quantity"
                          @input="calculateItemTotal(index)"
                          min="1"
                          step="1"
                        >
                      </td>
                      <td>
                        <input 
                          type="number" 
                          class="form-control form-control-sm" 
                          v-model.number="item.unitPrice"
                          @input="calculateItemTotal(index)"
                          min="0"
                          step="0.01"
                        >
                      </td>
                      <td>
                        <div class="fw-bold text-primary">
                          ₱{{ formatCurrency(item.totalPrice) }}
                        </div>
                      </td>
                      <td>
                        <input 
                          type="date" 
                          class="form-control form-control-sm" 
                          v-model="item.expiryDate"
                          :min="new Date().toISOString().split('T')[0]"
                        >
                      </td>
                      <td>
                        <button 
                          type="button" 
                          class="btn btn-sm btn-outline-danger"
                          @click="removeItem(index)"
                          :disabled="editForm.items.length === 1"
                          title="Remove item"
                        >
                          <Trash2 :size="14" />
                        </button>
                      </td>
                    </tr>
                  </tbody>
                  <tfoot class="table-light">
                    <tr>
                      <td colspan="3" class="text-end"><strong>Total Items:</strong></td>
                      <td class="text-center"><strong>{{ getTotalQuantity() }}</strong></td>
                      <td colspan="2" class="text-end">
                        <strong class="text-primary fs-5">₱{{ formatCurrency(getGrandTotal()) }}</strong>
                      </td>
                      <td></td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          </div>

          <!-- Notes Section -->
          <div class="card">
            <div class="card-header bg-light">
              <h6 class="mb-0">
                <FileText :size="18" class="me-2" />
                Order Notes
              </h6>
            </div>
            <div class="card-body">
              <textarea 
                class="form-control" 
                v-model="editForm.notes"
                rows="3"
                placeholder="Add any notes about this purchase order..."
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer border-0 pt-4">
          <div class="d-flex justify-content-between align-items-center w-100">
            <div class="text-muted small">
              <AlertCircle :size="16" class="me-1" />
              Changes will update all related batches
            </div>
            <div class="d-flex gap-2">
              <button 
                type="button" 
                class="btn btn-outline-secondary px-4"
                @click="handleClose"
                :disabled="saving"
              >
                Cancel
              </button>
              <button 
                type="button" 
                class="btn btn-primary px-4"
                @click="saveChanges"
                :disabled="saving || !isFormValid"
              >
                <div v-if="saving" class="spinner-border spinner-border-sm me-2"></div>
                <Save :size="16" class="me-1" />
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { 
  Edit, 
  Calendar, 
  Package, 
  FileText, 
  Plus, 
  Trash2, 
  Save, 
  AlertCircle 
} from 'lucide-vue-next'
import { useToast } from '@/composables/ui/useToast'
import { useCategories } from '@/composables/api/useCategories'
import { useProducts } from '@/composables/api/useProducts'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export default {
  name: 'EditBatchDetailsModal',
  components: {
    Edit,
    Calendar,
    Package,
    FileText,
    Plus,
    Trash2,
    Save,
    AlertCircle
  },
  emits: ['close', 'saved'],
  props: {
    show: {
      type: Boolean,
      default: false
    },
    receipt: {
      type: Object,
      default: null
    },
    supplier: {
      type: Object,
      default: null
    }
  },
  setup(props, { emit }) {
    const { success: showSuccess, error: showError } = useToast()
    const { categories, fetchCategories } = useCategories()
    const { fetchProductsByCategory } = useProducts()
    
    const saving = ref(false)
    const isEditingExpectedDate = ref(false)
    const expectedDateInput = ref(null)
    const productsByCategory = ref({})
    const editForm = ref({
      id: '',
      date: '',
      expectedDate: '',
      status: 'Pending Delivery',
      items: [],
      notes: '',
      total: 0
    })
    
    // Define initializeFormData function first
    function initializeFormData(receipt) {
      if (!receipt) {
        console.warn('EditBatchDetailsModal: No receipt data provided')
        return
      }
      
      // Ensure expectedDate is in YYYY-MM-DD format for date input
      let expectedDate = receipt.expectedDate
      if (expectedDate && typeof expectedDate === 'string' && expectedDate.includes('T')) {
        expectedDate = expectedDate.split('T')[0]
      }
      
      editForm.value = {
        id: receipt.id,
        date: receipt.date,  // Order date (created_at)
        expectedDate: expectedDate,
        status: receipt.status,
        items: (receipt.items || []).map((item) => {
          return {
            productId: item.productId,
            name: item.name,
            batchNumber: item.batchNumber,
            batchId: item.batchId,
            quantity: item.quantity,
            unitPrice: item.unitPrice,
            totalPrice: item.totalPrice,
            expiryDate: item.expiryDate ? new Date(item.expiryDate).toISOString().split('T')[0] : '',
            quantityRemaining: item.quantityRemaining,
            categoryId: item.categoryId || '',
            categoryName: item.categoryName || '',
            subcategoryName: item.subcategoryName || '',
            selectedProduct: null,
            isNew: false,
            errors: {}
          }
        }),
        notes: receipt.notes || '',
        total: receipt.total
      }
      
      // Reset editing state
      isEditingExpectedDate.value = false
      
    }
    
    // Initialize form immediately if receipt is already available
    if (props.receipt) {
      initializeFormData(props.receipt)
    }
    
    // Watch for editing state change to auto-focus input
    watch(isEditingExpectedDate, (newVal) => {
      if (newVal) {
        // Focus input on next tick
        setTimeout(() => {
          if (expectedDateInput.value) {
            expectedDateInput.value.focus()
          }
        }, 100)
      }
    })
    
    const isFormValid = computed(() => {
      if (!editForm.value.expectedDate) return false
      if (editForm.value.items.length === 0) return false
      
      return editForm.value.items.every(item => 
        item.productId && 
        item.quantity > 0 && 
        item.unitPrice >= 0
      )
    })
    
    function addItem() {
      // Find existing batch number from current items to reuse the same batch_number
      const existingItem = editForm.value.items.find(item => item.batchNumber)
      let sharedBatchNumber = null
      
      if (existingItem?.batchNumber) {
        // Reuse the existing batch number for grouping
        sharedBatchNumber = existingItem.batchNumber
      } else {
        // Generate new batch number in format BATCH-0001
        const timestamp = Date.now().toString().slice(-6)
        const random = Math.floor(Math.random() * 100).toString().padStart(2, '0')
        sharedBatchNumber = `BATCH-${timestamp}${random}`
      }
      
      editForm.value.items.push({
        categoryId: '',
        subcategoryName: '',
        productId: '',
        name: '',
        selectedProduct: null,
        batchNumber: sharedBatchNumber, // ✅ Same batch number for grouping
        batchId: null, // Will be set by backend when created
        quantity: 1,
        unitPrice: 0,
        totalPrice: 0,
        expiryDate: '',
        quantityRemaining: 0,
        isNew: true,
        errors: {}
      })
    }
    
    // Category/Product Selection Functions
    function getCategoryName(item) {
      if (!item.categoryId) return item.categoryName || 'N/A'
      
      const category = categories.value.find(c => c._id === item.categoryId)
      return category?.category_name || item.categoryName || 'N/A'
    }
    
    function getSubcategoriesForItem(item) {
      if (!item.categoryId) return []
      
      const category = categories.value.find(c => c._id === item.categoryId)
      return category?.sub_categories || []
    }
    
    function getProductsForItem(item) {
      if (!item.categoryId || !item.subcategoryName) return []
      
      const key = `${item.categoryId}-${item.subcategoryName}`
      const products = productsByCategory.value[key]
      
      if (!Array.isArray(products)) {
        return []
      }
      
      return products
    }
    
    async function onCategoryChange(index) {
      const item = editForm.value.items[index]
      
      // Reset dependent fields
      item.subcategoryName = ''
      item.productId = ''
      item.name = ''
      item.selectedProduct = null
      
      // Clear errors
      if (item.errors?.category) {
        delete item.errors.category
      }
    }
    
    async function onSubcategoryChange(index) {
      const item = editForm.value.items[index]
      
      // Reset product selection
      item.productId = ''
      item.name = ''
      item.selectedProduct = null
      
      // Clear errors
      if (item.errors?.subcategory) {
        delete item.errors.subcategory
      }
      
      // Load products for this category-subcategory combination
      if (item.categoryId && item.subcategoryName) {
        await loadProductsForCategorySubcategory(item.categoryId, item.subcategoryName)
      }
    }
    
    async function onProductChange(index) {
      const item = editForm.value.items[index]
      
      // Find and store the selected product
      const products = getProductsForItem(item)
      
      if (!Array.isArray(products)) {
        console.error('Products is not an array:', products)
        item.selectedProduct = null
        return
      }
      
      item.selectedProduct = products.find(p => p._id === item.productId)
      
      // Set product name and default cost if available
      if (item.selectedProduct) {
        item.name = item.selectedProduct.product_name
        if (!item.unitPrice) {
          item.unitPrice = item.selectedProduct.cost_price || item.selectedProduct.selling_price || 0
        }
      }
      
      // Clear errors
      if (item.errors?.product) {
        delete item.errors.product
      }
      
      calculateItemTotal(index)
    }
    
    async function loadProductsForCategorySubcategory(categoryId, subcategoryName) {
      const key = `${categoryId}-${subcategoryName}`
      
      // Skip if already loaded
      if (productsByCategory.value[key]) {
        return
      }
      
      try {
        const response = await fetchProductsByCategory(categoryId, subcategoryName)
        
        let productsArray = []
        
        if (Array.isArray(response)) {
          productsArray = response
        } else if (response && Array.isArray(response.data)) {
          productsArray = response.data
        } else if (response && Array.isArray(response.products)) {
          productsArray = response.products
        } else {
          console.warn('Unexpected response format:', response)
          productsArray = []
        }
        
        productsByCategory.value[key] = productsArray
        
      } catch (error) {
        console.error('Error loading products:', error)
        productsByCategory.value[key] = []
      }
    }
    
    function removeItem(index) {
      if (editForm.value.items.length > 1) {
        editForm.value.items.splice(index, 1)
      }
    }
    
    function calculateItemTotal(index) {
      const item = editForm.value.items[index]
      item.totalPrice = (item.quantity || 0) * (item.unitPrice || 0)
    }
    
    function getTotalQuantity() {
      return editForm.value.items.reduce((sum, item) => sum + (item.quantity || 0), 0)
    }
    
    function getGrandTotal() {
      return editForm.value.items.reduce((sum, item) => sum + (item.totalPrice || 0), 0)
    }
    
    async function saveChanges() {
      if (!isFormValid.value) {
        showError('Please fill in all required fields')
        return
      }
      
      saving.value = true
      
      try {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken')
        
        // Update each batch with new details
        const updates = []
        for (const item of editForm.value.items) {
          if (!item.isNew && item.batchId) {
            // Update existing batch
            const updateData = {
              quantity_received: item.quantity,
              cost_price: item.unitPrice,
              expiry_date: item.expiryDate || null,
              expected_delivery_date: editForm.value.expectedDate,
              notes: editForm.value.notes
            }
            
            updates.push(
              axios.put(
                `${API_BASE_URL}/batches/${item.batchId}/`,
                updateData,
                {
                  headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                  }
                }
              ).catch(error => {
                console.error(`❌ Failed to update batch ${item.batchId}:`, error.response?.data || error.message)
                throw error
              })
            )
           } else if (item.isNew) {
             // Create new batch - Use /batches/create/ endpoint
             const createData = {
               product_id: item.productId,
               batch_number: item.batchNumber, // ✅ Same batch_number for grouping
               quantity_received: item.quantity,
               cost_price: item.unitPrice,
               expiry_date: item.expiryDate || null,
               expected_delivery_date: editForm.value.expectedDate,
               supplier_id: props.supplier?._id || props.supplier?.id,
               status: 'pending',
               notes: editForm.value.notes
             }
             
             updates.push(
               axios.post(
                 `${API_BASE_URL}/batches/create/`,
                 createData,
                 {
                   headers: {
                     'Authorization': `Bearer ${token}`,
                     'Content-Type': 'application/json'
                   }
                 }
               ).catch(error => {
                 console.error(`❌ Failed to create new batch:`, error.response?.data || error.message)
                 throw error
               })
             )
           }
        }
        
        await Promise.all(updates)
        
        showSuccess('Purchase order updated successfully')
        emit('saved', {
          ...editForm.value,
          total: getGrandTotal()
        })
        handleClose()
        
      } catch (error) {
        console.error('❌ Error saving changes:', error)
        console.error('Error details:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status
        })
        
        // Provide more specific error message
        let errorMessage = 'Failed to save changes. Please try again.'
        if (error.response?.data?.error) {
          errorMessage = `Error: ${error.response.data.error}`
        } else if (error.response?.data?.message) {
          errorMessage = `Error: ${error.response.data.message}`
        }
        
        showError(errorMessage)
      } finally {
        saving.value = false
      }
    }
    
    function formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
    
    function formatCurrency(amount) {
      return new Intl.NumberFormat('en-PH', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(amount || 0)
    }
    
    function handleClose() {
      emit('close')
    }
    
    // Watch for show prop changes
    watch(() => props.show, (newVal) => {
      if (newVal && props.receipt) {
        initializeFormData(props.receipt)
      }
    })
    
    // Also watch for receipt changes
    watch(() => props.receipt, (newVal) => {
      if (newVal && props.show) {
        initializeFormData(newVal)
      }
    })
    
    // Load categories on mount
    onMounted(async () => {
      try {
        await fetchCategories()
      } catch (error) {
        console.error('Error loading categories:', error)
        showError('Failed to load categories')
      }
    })
    
    return {
      saving,
      editForm,
      isFormValid,
      isEditingExpectedDate,
      expectedDateInput,
      categories,
      addItem,
      removeItem,
      calculateItemTotal,
      getTotalQuantity,
      getGrandTotal,
      saveChanges,
      formatDate,
      formatCurrency,
      handleClose,
      // Category/Product selection
      getCategoryName,
      getSubcategoriesForItem,
      getProductsForItem,
      onCategoryChange,
      onSubcategoryChange,
      onProductChange
    }
  }
}
</script>

<style scoped>
@import '@/assets/styles/colors.css';

.modern-modal {
  border-radius: 16px;
  border: none;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.clickable-field {
  cursor: pointer;
  background-color: #f8f9fa;
  transition: all 0.2s ease;
  position: relative;
  padding-right: 30px;
}

.clickable-field:hover {
  background-color: #e9ecef;
  border-color: var(--primary);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.15);
}

.modal-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--warning-light), var(--warning));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--warning-dark);
}

.modal-header {
  padding: 2rem 2rem 1rem 2rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.modal-body {
  padding: 1.5rem 2rem;
  max-height: 70vh;
  overflow-y: auto;
}

.edit-items-table {
  font-size: 0.875rem;
}

.edit-items-table th {
  font-weight: 600;
  font-size: 0.875rem;
  background-color: #f8f9fa;
  padding: 0.75rem 0.5rem;
}

.edit-items-table td {
  vertical-align: middle;
  padding: 0.75rem 0.5rem;
}

.item-row {
  border-bottom: 1px solid var(--neutral-light);
}

.item-row:hover {
  background-color: rgba(115, 146, 226, 0.05);
}

.form-control-sm {
  font-size: 0.875rem;
}

.form-label {
  font-weight: 500;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.text-danger {
  color: var(--error) !important;
}

code {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.875rem;
}
</style>

