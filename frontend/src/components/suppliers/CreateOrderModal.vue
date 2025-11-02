<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content modern-order-modal">
        <!-- Modal Header -->
        <div class="modal-header border-0 pb-0">
          <div class="d-flex align-items-center">
            <div class="modal-icon modal-icon-pending me-3">
              <ShoppingCart :size="24" />
            </div>
            <div>
              <h4 class="modal-title mb-1">Create Purchase Order</h4>
              <p class="text-muted mb-0 small">
                Order stock from <strong>{{ supplier?.name }}</strong> (Status: Pending)
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
          <div class="row mb-4">
            <!-- Left Column - Order Details -->
            <div class="col-md-6">
              <div class="order-info-card">
                <h5 class="mb-3">
                  <FileText :size="18" class="me-2" />
                  Order Information
                </h5>
                
                <div class="row g-3">
                  <div class="col-md-6">
                    <label for="orderId" class="form-label">Order ID</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="orderId"
                      v-model="orderData.orderId"
                      readonly
                      style="background-color: #f8f9fa;"
                    >
                  </div>
                  
                  <div class="col-md-6">
                    <label for="orderDate" class="form-label">Order Date</label>
                    <input 
                      type="date" 
                      class="form-control" 
                      id="orderDate"
                      v-model="orderData.orderDate"
                    >
                  </div>
                  
                  <div class="col-md-6">
                    <label for="expectedDeliveryDate" class="form-label">Expected Delivery <span class="text-danger">*</span></label>
                    <input 
                      type="date" 
                      class="form-control" 
                      id="expectedDeliveryDate"
                      v-model="orderData.expectedDeliveryDate"
                      :min="orderData.orderDate"
                    >
                  </div>
                  
                  <div class="col-md-6">
                    <label for="referenceNumber" class="form-label">Reference #</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="referenceNumber"
                      v-model="orderData.referenceNumber"
                      placeholder="Optional"
                    >
                  </div>
                  
                  <div class="col-12">
                    <label for="orderNotes" class="form-label">Order Notes</label>
                    <textarea 
                      class="form-control" 
                      id="orderNotes"
                      v-model="orderData.notes"
                      rows="3"
                      placeholder="Any notes about this order..."
                    ></textarea>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Right Column - Supplier Info -->
            <div class="col-md-6">
              <div class="supplier-info-card">
                <h5 class="mb-3">
                  <Building :size="18" class="me-2" />
                  Supplier Information
                </h5>
                
                <div class="supplier-details">
                  <div class="detail-row">
                    <strong>Company:</strong>
                    <span>{{ supplier?.name }}</span>
                  </div>
                  <div class="detail-row">
                    <strong>Contact:</strong>
                    <span>{{ supplier?.contactPerson || 'Not specified' }}</span>
                  </div>
                  <div class="detail-row">
                    <strong>Email:</strong>
                    <span>{{ supplier?.email || 'Not provided' }}</span>
                  </div>
                  <div class="detail-row">
                    <strong>Phone:</strong>
                    <span>{{ supplier?.phone || 'Not provided' }}</span>
                  </div>
                  <div class="detail-row">
                    <strong>Type:</strong>
                    <span>{{ getSupplierTypeLabel(supplier?.type) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Order Items Section -->
          <div class="order-items-section">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="mb-0">
                <Package :size="18" class="me-2" />
                Order Items
              </h5>
              <button 
                class="btn btn-outline-primary btn-sm"
                @click="addOrderItem"
              >
                <Plus :size="16" class="me-1" />
                Add Item
              </button>
            </div>

            <!-- Items Table -->
            <div class="table-responsive">
              <table class="table table-bordered order-items-table">
                <thead class="table-light">
                  <tr>
                    <th style="width: 40px;">#</th>
                    <th style="width: 180px;">Category <span class="text-danger">*</span></th>
                    <th style="width: 180px;">Subcategory <span class="text-danger">*</span></th>
                    <th style="width: 200px;">Product <span class="text-danger">*</span></th>
                    <th style="width: 100px;">Quantity <span class="text-danger">*</span></th>
                    <th style="width: 120px;">Est. Unit Cost (₱)</th>
                    <th style="width: 100px;">Expected Expiry</th>
                    <th style="width: 120px;">Total Cost</th>
                    <th style="width: 60px;">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr 
                    v-for="(item, index) in orderData.items" 
                    :key="`item-${index}`"
                    :class="{ 'table-danger': item.errors && Object.keys(item.errors).length > 0 }"
                  >
                    <td class="text-center">{{ index + 1 }}</td>
                    
                    <!-- Category Dropdown -->
                    <td>
                      <select 
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
                      <div v-if="item.errors?.category" class="invalid-feedback">
                        {{ item.errors.category }}
                      </div>
                    </td>
                    
                    <!-- Subcategory Dropdown -->
                    <td>
                      <select 
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
                      <div v-if="item.errors?.subcategory" class="invalid-feedback">
                        {{ item.errors.subcategory }}
                      </div>
                    </td>
                    
                    <!-- Product Dropdown -->
                    <td>
                      <select 
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
                      <div v-if="item.errors?.product" class="invalid-feedback">
                        {{ item.errors.product }}
                      </div>
                      <small v-if="item.selectedProduct" class="text-muted d-block mt-1">
                        Current stock: {{ item.selectedProduct.total_stock || 0 }}
                      </small>
                    </td>
                    
                    <!-- Quantity -->
                    <td>
                      <input 
                        type="number" 
                        class="form-control form-control-sm"
                        :class="{ 'is-invalid': item.errors?.quantity }"
                        v-model.number="item.quantity"
                        @input="validateItem(index); calculateItemTotal(index)"
                        min="1"
                        step="1"
                        placeholder="0"
                      >
                      <div v-if="item.errors?.quantity" class="invalid-feedback">
                        {{ item.errors.quantity }}
                      </div>
                    </td>
                    
                    <!-- Unit Cost -->
                    <td>
                      <input 
                        type="number" 
                        class="form-control form-control-sm"
                        v-model.number="item.estimatedCost"
                        @input="calculateItemTotal(index)"
                        min="0"
                        step="0.01"
                        placeholder="0.00"
                      >
                    </td>
                    
                    <!-- Expected Expiry Date -->
                    <td>
                      <input 
                        type="date" 
                        class="form-control form-control-sm"
                        v-model="item.expectedExpiryDate"
                        :min="orderData.expectedDeliveryDate"
                      >
                    </td>
                    
                    <!-- Total Cost -->
                    <td>
                      <div class="total-price">
                        ₱{{ formatCurrency(item.totalCost || 0) }}
                      </div>
                    </td>
                    
                    <!-- Actions -->
                    <td class="text-center">
                      <button 
                        class="btn btn-outline-danger btn-sm"
                        @click="removeOrderItem(index)"
                        :disabled="orderData.items.length <= 1"
                        title="Remove item"
                      >
                        <Trash2 :size="14" />
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Add Item Button (if no items) -->
            <div v-if="orderData.items.length === 0" class="text-center py-4">
              <Package :size="48" class="text-muted mb-3" />
              <p class="text-muted mb-3">No items added yet</p>
              <button class="btn btn-primary" @click="addOrderItem">
                <Plus :size="16" class="me-1" />
                Add First Item
              </button>
            </div>
          </div>

          <!-- Order Summary -->
          <div class="order-summary-section mt-4">
            <div class="row">
              <div class="col-md-8">
                <div class="alert alert-info">
                  <Clock :size="16" class="me-2" />
                  <strong>Purchase Order (Pending Delivery):</strong> Batches will be created with "pending" status. 
                  Use "Receive Stock" button to activate them when delivery arrives.
                </div>
              </div>
              
              <div class="col-md-4">
                <!-- Order Totals -->
                <div class="order-totals">
                  <h6 class="mb-3">Order Summary</h6>
                  
                  <div class="summary-row">
                    <span>Total Items:</span>
                    <span class="fw-bold">{{ validItemsCount }}</span>
                  </div>
                  
                  <div class="summary-row">
                    <span>Total Quantity:</span>
                    <span class="fw-bold">{{ totalQuantity }}</span>
                  </div>
                  
                  <div class="summary-row">
                    <span>Total Products:</span>
                    <span class="fw-bold">{{ uniqueProductsCount }}</span>
                  </div>
                  
                  <hr>
                  
                  <div class="summary-row total-row">
                    <span class="fw-bold">Estimated Total:</span>
                    <span class="fw-bold text-primary fs-5">₱{{ formatCurrency(grandTotal) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer border-0 pt-4">
          <div class="d-flex justify-content-between align-items-center w-100">
            <div class="text-muted small">
              <Clock :size="16" class="me-1" />
              {{ validItemsCount }} pending batch(es) will be created
            </div>
            
            <div class="d-flex gap-3">
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
                @click="saveOrder"
                :disabled="!isOrderValid || saving"
                :class="{ 'btn-loading': saving }"
              >
                <div v-if="saving" class="spinner-border spinner-border-sm me-2"></div>
                <ShoppingCart :size="16" class="me-1" />
                Create Pending Order
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { 
  Package,
  FileText,
  Building,
  Plus,
  Trash2,
  ShoppingCart,
  Clock
} from 'lucide-vue-next'
import { useCategories } from '@/composables/api/useCategories'
import { useProducts } from '@/composables/api/useProducts'
import { useBatches } from '@/composables/api/useBatches'
import { useToast } from '@/composables/ui/useToast'

export default {
  name: 'CreateOrderModal',
  components: {
    Package,
    FileText,
    Building,
    Plus,
    Trash2,
    ShoppingCart,
    Clock
  },
  emits: ['close', 'saved'],
  props: {
    show: {
      type: Boolean,
      default: false
    },
    supplier: {
      type: Object,
      required: false,
      default: null
    }
  },
  setup(props, { emit }) {
    const { success: showSuccess, error: showError } = useToast()
    const { categories, fetchCategories } = useCategories()
    const { fetchProductsByCategory } = useProducts()
    const { createBatch } = useBatches()
    
    const saving = ref(false)
    const productsByCategory = ref({})
    
    const orderData = ref({
      orderId: generateOrderId(),
      orderDate: new Date().toISOString().split('T')[0],
      expectedDeliveryDate: '',
      referenceNumber: '',
      notes: '',
      items: [createEmptyItem()]
    })
    
    // ================ HELPER FUNCTIONS ================
    
    function generateOrderId() {
      const prefix = 'PO'
      const timestamp = Date.now().toString().slice(-6)
      const random = Math.floor(Math.random() * 100).toString().padStart(2, '0')
      return `${prefix}-${timestamp}${random}`
    }
    
    function generateBatchNumber() {
      // Generate a unique batch number in format BATCH-0001
      // All items in the same purchase order will share this batch number
      const timestamp = Date.now().toString().slice(-6)
      const random = Math.floor(Math.random() * 100).toString().padStart(2, '0')
      return `BATCH-${timestamp}${random}`
    }
    
    function createEmptyItem() {
      return {
        categoryId: '',
        subcategoryName: '',
        productId: '',
        selectedProduct: null,
        quantity: null,
        estimatedCost: null,
        expectedExpiryDate: '',
        totalCost: 0,
        errors: {}
      }
    }
    
    function getSupplierTypeLabel(type) {
      const labels = {
        'food': 'Food & Beverages',
        'packaging': 'Packaging Materials',
        'equipment': 'Equipment & Tools',
        'services': 'Services',
        'raw_materials': 'Raw Materials',
        'other': 'Other'
      }
      return labels[type] || 'Not specified'
    }
    
    function formatCurrency(amount) {
      return new Intl.NumberFormat('en-PH', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(amount || 0)
    }
    
    // ================ COMPUTED PROPERTIES ================
    
    const validItems = computed(() => {
      return orderData.value.items.filter(item => 
        item.productId && 
        item.quantity && 
        item.quantity > 0 &&
        (!item.errors || Object.keys(item.errors).length === 0)
      )
    })
    
    const validItemsCount = computed(() => validItems.value.length)
    
    const totalQuantity = computed(() => {
      return validItems.value.reduce((sum, item) => sum + (item.quantity || 0), 0)
    })
    
    const uniqueProductsCount = computed(() => {
      const uniqueProducts = new Set(validItems.value.map(item => item.productId))
      return uniqueProducts.size
    })
    
    const grandTotal = computed(() => {
      return validItems.value.reduce((sum, item) => sum + (item.totalCost || 0), 0)
    })
    
    const isOrderValid = computed(() => {
      return validItems.value.length > 0 && 
             orderData.value.expectedDeliveryDate
    })
    
    // ================ CASCADE DROPDOWN METHODS ================
    
    function getSubcategoriesForItem(item) {
      if (!item.categoryId) return []
      
      const category = categories.value.find(cat => cat._id === item.categoryId)
      return category?.sub_categories || []
    }
    
    function getProductsForItem(item) {
      if (!item.categoryId || !item.subcategoryName) return []
      
      const key = `${item.categoryId}-${item.subcategoryName}`
      const products = productsByCategory.value[key] || []
      
      // ✅ SAFETY CHECK
      if (!Array.isArray(products)) {
        console.error('Products for key is not an array:', key, products)
        return []
      }
      
      return products
    }
    
    async function onCategoryChange(index) {
      const item = orderData.value.items[index]
      
      // Reset dependent fields
      item.subcategoryName = ''
      item.productId = ''
      item.selectedProduct = null
      
      // Clear errors
      if (item.errors?.category) {
        delete item.errors.category
      }
      
      validateItem(index)
    }
    
    async function onSubcategoryChange(index) {
      const item = orderData.value.items[index]
      
      // Reset product selection
      item.productId = ''
      item.selectedProduct = null
      
      // Clear errors
      if (item.errors?.subcategory) {
        delete item.errors.subcategory
      }
      
      // Load products for this category-subcategory combination
      if (item.categoryId && item.subcategoryName) {
        await loadProductsForCategorySubcategory(item.categoryId, item.subcategoryName)
      }
      
      validateItem(index)
    }
    
    async function onProductChange(index) {
      const item = orderData.value.items[index]
      
      // Find and store the selected product
      const products = getProductsForItem(item)
      
      // ✅ ADD SAFETY CHECK
      if (!Array.isArray(products)) {
        console.error('Products is not an array:', products)
        item.selectedProduct = null
        return
      }
      
      item.selectedProduct = products.find(p => p._id === item.productId)
      
      // Set default cost if available
      if (item.selectedProduct && !item.estimatedCost) {
        item.estimatedCost = item.selectedProduct.cost_price || item.selectedProduct.selling_price || 0
      }
      
      // Clear errors
      if (item.errors?.product) {
        delete item.errors.product
      }
      
      validateItem(index)
      calculateItemTotal(index)
    }
    
    async function loadProductsForCategorySubcategory(categoryId, subcategoryName) {
      const key = `${categoryId}-${subcategoryName}`
      
      // Skip if already loaded
      if (productsByCategory.value[key]) {
        return
      }
      
      try {
        console.log('Loading products for:', categoryId, subcategoryName)
        const response = await fetchProductsByCategory(categoryId, subcategoryName)
        
        console.log('Products response:', response)
        
        // ✅ HANDLE DIFFERENT RESPONSE FORMATS
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
        
        console.log('Parsed products array:', productsArray)
        productsByCategory.value[key] = productsArray
        
      } catch (error) {
        console.error('Error loading products:', error)
        productsByCategory.value[key] = []
      }
    }
    
    // ================ ITEM MANAGEMENT ================
    
    function addOrderItem() {
      orderData.value.items.push(createEmptyItem())
    }
    
    function removeOrderItem(index) {
      if (orderData.value.items.length > 1) {
        orderData.value.items.splice(index, 1)
      }
    }
    
    function validateItem(index) {
      const item = orderData.value.items[index]
      const errors = {}
      
      if (!item.categoryId) {
        errors.category = 'Category is required'
      }
      
      if (!item.subcategoryName) {
        errors.subcategory = 'Subcategory is required'
      }
      
      if (!item.productId) {
        errors.product = 'Product is required'
      }
      
      if (!item.quantity || item.quantity <= 0) {
        errors.quantity = 'Quantity must be greater than 0'
      } else if (!Number.isInteger(item.quantity)) {
        errors.quantity = 'Quantity must be a whole number'
      }
      
      item.errors = errors
    }
    
    function validateAllItems() {
      orderData.value.items.forEach((item, index) => {
        validateItem(index)
      })
    }
    
    function calculateItemTotal(index) {
      const item = orderData.value.items[index]
      const quantity = item.quantity || 0
      const unitPrice = item.estimatedCost || 0
      item.totalCost = quantity * unitPrice
    }
    
    // ================ SAVE ORDER ================
    
    async function saveOrder() {
      saving.value = true
      
      try {
        validateAllItems()
        
        if (!isOrderValid.value) {
          showError('Please fix validation errors before saving')
          return
        }
        
        const itemsToProcess = validItems.value
        const results = {
          successful: [],
          failed: []
        }
        
        // Generate a single batch number for all items in this purchase order
        const sharedBatchNumber = generateBatchNumber()
        console.log(`📦 Using shared batch number for all items: ${sharedBatchNumber}`)
        
        // Validate supplier exists
        if (!props.supplier?.id) {
          showError('Supplier information is required to create an order')
          return
        }

        // Create a batch for each valid item with the same batch number
        for (const item of itemsToProcess) {
          try {
            const batchData = {
              product_id: item.productId,
              supplier_id: props.supplier.id,
              batch_number: sharedBatchNumber, // ✅ Same batch number for all items in this order
              quantity_received: item.quantity,
              cost_price: item.estimatedCost || 0,
              expiry_date: item.expectedExpiryDate || null,
              expected_delivery_date: orderData.value.expectedDeliveryDate, // ✅ Expected delivery date (for pending orders)
              // date_received will be null until stock is actually received/activated
              status: 'pending', // ✅ CREATE AS PENDING (on-going delivery)
              notes: `Receipt: ${orderData.value.orderId}${orderData.value.referenceNumber ? ` | Ref: ${orderData.value.referenceNumber}` : ''}${orderData.value.notes ? ` | ${orderData.value.notes}` : ''}`
            }
            
            const response = await createBatch(batchData)
            
            results.successful.push({
              product: item.selectedProduct?.product_name,
              batch: response
            })
            
          } catch (error) {
            console.error('Error creating batch for item:', item, error)
            results.failed.push({
              product: item.selectedProduct?.product_name,
              error: error.message
            })
          }
        }
        
        // ✅ Don't show toast here - let parent handle it to avoid duplicates
        // Parent (SupplierDetails) will show the success/error toast
        
        // Emit saved event with results
        emit('saved', {
          orderId: orderData.value.orderId,
          supplierId: props.supplier?.id,
          supplierName: props.supplier?.name,
          results
        })
        
        // Close modal
        handleClose()
        
      } catch (error) {
        console.error('Error saving order:', error)
        showError('Failed to process order. Please try again.')
      } finally {
        saving.value = false
      }
    }
    
    // ================ MODAL CONTROLS ================
    
    function handleClose() {
      emit('close')
      resetForm()
    }
    
    function resetForm() {
      orderData.value = {
        orderId: generateOrderId(),
        orderDate: new Date().toISOString().split('T')[0],
        expectedDeliveryDate: '',
        referenceNumber: '',
        notes: '',
        items: [createEmptyItem()]
      }
      productsByCategory.value = {}
      saving.value = false
    }
    
    // ================ LIFECYCLE ================
    
    onMounted(async () => {
      try {
        await fetchCategories()
      } catch (error) {
        console.error('Error loading categories:', error)
        showError('Failed to load categories')
      }
    })
    
    watch(() => props.show, (newVal) => {
      if (newVal) {
        resetForm()
      }
    })
    
    return {
      // Data
      orderData,
      saving,
      categories,
      
      // Computed
      validItemsCount,
      totalQuantity,
      uniqueProductsCount,
      grandTotal,
      isOrderValid,
      
      // Methods
      getSupplierTypeLabel,
      formatCurrency,
      getSubcategoriesForItem,
      getProductsForItem,
      onCategoryChange,
      onSubcategoryChange,
      onProductChange,
      addOrderItem,
      removeOrderItem,
      validateItem,
      calculateItemTotal,
      saveOrder,
      handleClose
    }
  }
}
</script>

<style scoped>
/* Keep all existing styles from CreateOrderModal */
.modern-order-modal {
  border-radius: 16px;
  border: none;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.modal-icon-pending {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--primary-light), var(--primary));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-dark);
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

.order-info-card,
.supplier-info-card {
  padding: 1.5rem;
  background: var(--neutral-light);
  border-radius: 12px;
  border: 1px solid var(--neutral-medium);
  height: 100%;
}

.supplier-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--neutral-light);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row strong {
  color: var(--tertiary-dark);
  min-width: 80px;
}

.detail-row span {
  color: var(--tertiary-medium);
  text-align: right;
  flex: 1;
}

.order-items-section {
  background: white;
  border-radius: 12px;
  border: 1px solid var(--neutral-medium);
  padding: 1.5rem;
}

.order-items-table {
  margin-bottom: 0;
}

.order-items-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: var(--tertiary-dark);
  border-bottom: 2px solid var(--neutral-medium);
  font-size: 0.875rem;
}

.order-items-table td {
  vertical-align: middle;
  padding: 0.75rem 0.5rem;
}

.total-price {
  font-weight: 600;
  color: var(--primary);
  text-align: right;
  padding: 0.5rem;
  background: var(--primary-light);
  border-radius: 4px;
}

.order-summary-section {
  background: var(--neutral-light);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--neutral-medium);
}

.order-totals {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid var(--neutral-medium);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--neutral-light);
}

.summary-row:last-child {
  border-bottom: none;
}

.total-row {
  margin-top: 0.5rem;
  padding-top: 1rem;
  border-top: 2px solid var(--neutral-medium);
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  border: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(115, 146, 226, 0.3);
}

.table-danger {
  background-color: rgba(220, 53, 69, 0.1) !important;
}
</style>