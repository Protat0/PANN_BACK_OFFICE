<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-xl modal-dialog-centered">
      <div class="modal-content modern-order-modal">
        <!-- Modal Header -->
        <div class="modal-header border-0 pb-0">
          <div class="d-flex align-items-center">
            <div class="modal-icon me-3">
              <ShoppingCart :size="24" />
            </div>
            <div>
              <h4 class="modal-title mb-1">Create Purchase Order</h4>
              <p class="text-muted mb-0 small">
                Create a new purchase order for <strong>{{ supplier?.name }}</strong>
              </p>
            </div>
          </div>
          <button 
            type="button" 
            class="btn-close" 
            @click="$emit('close')"
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
                    <label for="expectedDate" class="form-label">Expected Delivery</label>
                    <input 
                      type="date" 
                      class="form-control" 
                      id="expectedDate"
                      v-model="orderData.expectedDate"
                      :min="orderData.orderDate"
                    >
                  </div>
                  
                  <div class="col-md-6">
                    <label for="priority" class="form-label">Priority</label>
                    <select class="form-select" id="priority" v-model="orderData.priority">
                      <option value="low">Low</option>
                      <option value="normal">Normal</option>
                      <option value="high">High</option>
                      <option value="urgent">Urgent</option>
                    </select>
                  </div>
                  
                  <div class="col-12">
                    <label for="description" class="form-label">Order Description</label>
                    <textarea 
                      class="form-control" 
                      id="description"
                      v-model="orderData.description"
                      rows="3"
                      placeholder="Brief description of this purchase order..."
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
              <div class="d-flex gap-2">
                <button 
                  class="btn btn-outline-success btn-sm"
                  @click="addOrderItem"
                >
                  <Plus :size="16" class="me-1" />
                  Add Item
                </button>
                <button 
                  class="btn btn-outline-primary btn-sm"
                  @click="loadSampleItems"
                >
                  <Lightbulb :size="16" class="me-1" />
                  Load Sample
                </button>
              </div>
            </div>

            <!-- Items Table -->
            <div class="table-responsive">
              <table class="table table-bordered order-items-table">
                <thead class="table-light">
                  <tr>
                    <th style="width: 40px;">#</th>
                    <th style="width: 250px;">Item Name / Description <span class="text-danger">*</span></th>
                    <th style="width: 80px;">Quantity <span class="text-danger">*</span></th>
                    <th style="width: 100px;">Unit</th>
                    <th style="width: 120px;">Unit Price</th>
                    <th style="width: 120px;">Total Price</th>
                    <th style="width: 100px;">Notes</th>
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
                    
                    <!-- Item Name -->
                    <td>
                      <input 
                        type="text" 
                        class="form-control form-control-sm"
                        :class="{ 'is-invalid': item.errors?.name }"
                        v-model="item.name"
                        @input="validateOrderItem(index)"
                        placeholder="Enter item name or description"
                      >
                      <div v-if="item.errors?.name" class="invalid-feedback">
                        {{ item.errors.name }}
                      </div>
                    </td>
                    
                    <!-- Quantity -->
                    <td>
                      <input 
                        type="number" 
                        class="form-control form-control-sm"
                        :class="{ 'is-invalid': item.errors?.quantity }"
                        v-model.number="item.quantity"
                        @input="validateOrderItem(index); calculateItemTotal(index)"
                        min="1"
                        step="1"
                        placeholder="0"
                      >
                      <div v-if="item.errors?.quantity" class="invalid-feedback">
                        {{ item.errors.quantity }}
                      </div>
                    </td>
                    
                    <!-- Unit -->
                    <td>
                      <select 
                        class="form-select form-select-sm" 
                        v-model="item.unit"
                      >
                        <option value="">Select</option>
                        <option value="pcs">Pieces</option>
                        <option value="kg">Kilograms</option>
                        <option value="lbs">Pounds</option>
                        <option value="box">Box</option>
                        <option value="case">Case</option>
                        <option value="liter">Liter</option>
                        <option value="gallon">Gallon</option>
                        <option value="pack">Pack</option>
                        <option value="dozen">Dozen</option>
                        <option value="other">Other</option>
                      </select>
                    </td>
                    
                    <!-- Unit Price -->
                    <td>
                      <div class="input-group input-group-sm">
                        <span class="input-group-text">₱</span>
                        <input 
                          type="number" 
                          class="form-control"
                          v-model.number="item.unitPrice"
                          @input="calculateItemTotal(index)"
                          min="0"
                          step="0.01"
                          placeholder="0.00"
                        >
                      </div>
                    </td>
                    
                    <!-- Total Price -->
                    <td>
                      <div class="total-price">
                        ₱{{ formatCurrency(item.totalPrice || 0) }}
                      </div>
                    </td>
                    
                    <!-- Notes -->
                    <td>
                      <input 
                        type="text" 
                        class="form-control form-control-sm"
                        v-model="item.notes"
                        placeholder="Notes"
                      >
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
                <!-- Additional Notes -->
                <div class="additional-notes">
                  <label for="orderNotes" class="form-label">
                    <MessageSquare :size="16" class="me-2" />
                    Additional Notes
                  </label>
                  <textarea 
                    class="form-control" 
                    id="orderNotes"
                    v-model="orderData.notes"
                    rows="3"
                    placeholder="Any special instructions, delivery requirements, or additional notes..."
                  ></textarea>
                </div>
              </div>
              
              <div class="col-md-4">
                <!-- Order Totals -->
                <div class="order-totals">
                  <h6 class="mb-3">Order Summary</h6>
                  
                  <div class="summary-row">
                    <span>Total Items:</span>
                    <span class="fw-bold">{{ totalQuantity }}</span>
                  </div>
                  
                  <div class="summary-row">
                    <span>Subtotal:</span>
                    <span>₱{{ formatCurrency(subtotal) }}</span>
                  </div>
                  
                  <div class="summary-row">
                    <span>Tax ({{ taxRate }}%):</span>
                    <span>₱{{ formatCurrency(taxAmount) }}</span>
                  </div>
                  
                  <div class="summary-row">
                    <span>Shipping:</span>
                    <div class="input-group input-group-sm">
                      <span class="input-group-text">₱</span>
                      <input 
                        type="number" 
                        class="form-control form-control-sm"
                        v-model.number="orderData.shippingCost"
                        @input="calculateTotals"
                        min="0"
                        step="0.01"
                        placeholder="0.00"
                      >
                    </div>
                  </div>
                  
                  <hr>
                  
                  <div class="summary-row total-row">
                    <span class="fw-bold">Total Amount:</span>
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
            <div class="d-flex align-items-center">
              <div class="form-check">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  id="sendToSupplier" 
                  v-model="orderData.sendToSupplier"
                >
                <label class="form-check-label text-muted" for="sendToSupplier">
                  Send order details to supplier via email
                </label>
              </div>
            </div>
            
            <div class="d-flex gap-3">
              <button 
                type="button" 
                class="btn btn-outline-secondary px-4"
                @click="$emit('close')"
              >
                Cancel
              </button>
              <div class="btn-group">
                <button 
                  type="button" 
                  class="btn btn-success px-4"
                  @click="saveOrder('pending')"
                  :disabled="!isOrderValid || saving"
                  :class="{ 'btn-loading': saving }"
                >
                  <div v-if="saving" class="spinner-border spinner-border-sm me-2"></div>
                  <ShoppingCart :size="16" class="me-1" />
                  Create Order
                </button>
                <button 
                  type="button" 
                  class="btn btn-success dropdown-toggle dropdown-toggle-split"
                  data-bs-toggle="dropdown"
                  :disabled="!isOrderValid || saving"
                >
                  <span class="visually-hidden">Toggle Dropdown</span>
                </button>
                <ul class="dropdown-menu">
                  <li>
                    <a class="dropdown-item" href="#" @click.prevent="saveOrder('draft')">
                      <FileText :size="16" class="me-2" />
                      Save as Draft
                    </a>
                  </li>
                  <li>
                    <a class="dropdown-item" href="#" @click.prevent="saveOrder('pending')">
                      <Clock :size="16" class="me-2" />
                      Create & Send
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { 
  ShoppingCart,
  FileText,
  Building,
  Package,
  Plus,
  Trash2,
  Lightbulb,
  MessageSquare,
  Clock
} from 'lucide-vue-next'

export default {
  name: 'CreateOrderModal',
  components: {
    ShoppingCart,
    FileText,
    Building,
    Package,
    Plus,
    Trash2,
    Lightbulb,
    MessageSquare,
    Clock
  },
  emits: ['close', 'save'],
  props: {
    show: {
      type: Boolean,
      default: false
    },
    supplier: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      saving: false,
      taxRate: 12, // 12% VAT in Philippines
      
      orderData: {
        orderId: this.generateOrderId(),
        orderDate: new Date().toISOString().split('T')[0],
        expectedDate: this.getDefaultExpectedDate(),
        priority: 'normal',
        description: '',
        notes: '',
        shippingCost: 0,
        sendToSupplier: true,
        items: [
          this.createEmptyItem()
        ]
      }
    }
  },
  computed: {
    totalQuantity() {
      return this.orderData.items.reduce((sum, item) => sum + (item.quantity || 0), 0)
    },
    
    subtotal() {
      return this.orderData.items.reduce((sum, item) => sum + (item.totalPrice || 0), 0)
    },
    
    taxAmount() {
      return (this.subtotal * this.taxRate) / 100
    },
    
    grandTotal() {
      return this.subtotal + this.taxAmount + (this.orderData.shippingCost || 0)
    },
    
    isOrderValid() {
      return this.orderData.items.some(item => 
        item.name && 
        item.name.trim() && 
        item.quantity && 
        item.quantity > 0 &&
        (!item.errors || Object.keys(item.errors).length === 0)
      )
    }
  },
  methods: {
    generateOrderId() {
      const prefix = 'PO'
      const timestamp = Date.now().toString().slice(-6)
      const random = Math.floor(Math.random() * 100).toString().padStart(2, '0')
      return `${prefix}-${timestamp}${random}`
    },
    
    getDefaultExpectedDate() {
      const date = new Date()
      date.setDate(date.getDate() + 7) // Default to 7 days from now
      return date.toISOString().split('T')[0]
    },
    
    createEmptyItem() {
      return {
        name: '',
        quantity: null,
        unit: '',
        unitPrice: null,
        totalPrice: 0,
        notes: '',
        errors: {}
      }
    },
    
    addOrderItem() {
      this.orderData.items.push(this.createEmptyItem())
    },
    
    removeOrderItem(index) {
      if (this.orderData.items.length > 1) {
        this.orderData.items.splice(index, 1)
      }
    },
    
    loadSampleItems() {
      this.orderData.items = [
        {
          name: 'Premium Rice 25kg',
          quantity: 10,
          unit: 'bag',
          unitPrice: 1200.00,
          totalPrice: 12000.00,
          notes: 'Jasmine rice',
          errors: {}
        },
        {
          name: 'Cooking Oil 1L',
          quantity: 24,
          unit: 'bottle',
          unitPrice: 85.00,
          totalPrice: 2040.00,
          notes: 'Palm oil',
          errors: {}
        },
        {
          name: 'All Purpose Flour 1kg',
          quantity: 15,
          unit: 'pack',
          unitPrice: 45.00,
          totalPrice: 675.00,
          notes: 'For baking',
          errors: {}
        }
      ]
      
      this.validateAllItems()
      this.calculateTotals()
    },
    
    validateOrderItem(index) {
      const item = this.orderData.items[index]
      const errors = {}
      
      // Name validation
      if (!item.name || !item.name.trim()) {
        errors.name = 'Item name is required'
      } else if (item.name.trim().length < 2) {
        errors.name = 'Item name must be at least 2 characters'
      }
      
      // Quantity validation
      if (!item.quantity || item.quantity <= 0) {
        errors.quantity = 'Quantity must be greater than 0'
      } else if (!Number.isInteger(item.quantity)) {
        errors.quantity = 'Quantity must be a whole number'
      }
      
      item.errors = errors
    },
    
    validateAllItems() {
      this.orderData.items.forEach((item, index) => {
        this.validateOrderItem(index)
      })
    },
    
    calculateItemTotal(index) {
      const item = this.orderData.items[index]
      const quantity = item.quantity || 0
      const unitPrice = item.unitPrice || 0
      item.totalPrice = quantity * unitPrice
      this.calculateTotals()
    },
    
    calculateTotals() {
      // Totals are computed properties, so this just triggers reactivity
      this.$nextTick(() => {
        this.$forceUpdate()
      })
    },
    
    async saveOrder(status = 'pending') {
      this.saving = true
      
      try {
        this.validateAllItems()
        
        if (!this.isOrderValid) {
          alert('Please fix validation errors before saving')
          return
        }
        
        // Prepare order data
        const orderToSave = {
          ...this.orderData,
          id: this.orderData.orderId,
          supplierId: this.supplier?.id,
          supplierName: this.supplier?.name,
          status: status,
          totalItems: this.totalQuantity,
          subtotal: this.subtotal,
          tax: this.taxAmount,
          total: this.grandTotal,
          createdAt: new Date().toISOString(),
          items: this.orderData.items.filter(item => 
            item.name && item.name.trim() && item.quantity > 0
          )
        }
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        this.$emit('save', orderToSave)
        this.$emit('close')
        
      } catch (error) {
        console.error('Error saving order:', error)
        alert('Failed to save order. Please try again.')
      } finally {
        this.saving = false
      }
    },
    
    emailSupplier() {
      if (this.supplier?.email) {
        const subject = `Purchase Order ${this.orderData.orderId}`
        const body = `Dear ${this.supplier.contactPerson || 'Team'},\n\nWe would like to place a purchase order with your company.\n\nBest regards`
        window.open(`mailto:${this.supplier.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`)
      }
    },
    
    getSupplierTypeLabel(type) {
      const labels = {
        'food': 'Food & Beverages',
        'packaging': 'Packaging Materials',
        'equipment': 'Equipment & Tools',
        'services': 'Services',
        'raw_materials': 'Raw Materials',
        'other': 'Other'
      }
      return labels[type] || 'Not specified'
    },
    
    formatCurrency(amount) {
      return new Intl.NumberFormat('en-PH', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(amount || 0)
    }
  },
  
  watch: {
    show(newVal) {
      if (newVal) {
        // Reset modal state when opened
        this.orderData = {
          orderId: this.generateOrderId(),
          orderDate: new Date().toISOString().split('T')[0],
          expectedDate: this.getDefaultExpectedDate(),
          priority: 'normal',
          description: '',
          notes: '',
          shippingCost: 0,
          sendToSupplier: true,
          items: [this.createEmptyItem()]
        }
        this.saving = false
      }
    }
  }
}
</script>

<style scoped>
/* Modern Modal styling */
.modern-order-modal {
  border-radius: 16px;
  border: none;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.modal-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--success-light), var(--success));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--success-dark);
}

.modal-title {
  color: var(--primary-dark);
  font-weight: 600;
  margin: 0;
}

.modal-header {
  padding: 2rem 2rem 1rem 2rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.modal-body {
  padding: 1.5rem 2rem;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-footer {
  padding: 1rem 2rem 2rem 2rem;
  background-color: #f8f9fa;
}

/* Info Cards */
.order-info-card,
.supplier-info-card {
  padding: 1.5rem;
  background: var(--neutral-light);
  border-radius: 12px;
  border: 1px solid var(--neutral-medium);
  height: 100%;
}

.order-info-card h5,
.supplier-info-card h5 {
  color: var(--tertiary-dark);
  font-weight: 600;
  display: flex;
  align-items: center;
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

.quick-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Order Items Section */
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

.order-items-table .form-control,
.order-items-table .form-select {
  font-size: 0.875rem;
}

.total-price {
  font-weight: 600;
  color: var(--success);
  text-align: right;
  padding: 0.5rem;
  background: var(--success-light);
  border-radius: 4px;
}

/* Order Summary */
.order-summary-section {
  background: var(--neutral-light);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--neutral-medium);
}

.additional-notes .form-label {
  color: var(--tertiary-dark);
  font-weight: 500;
  display: flex;
  align-items: center;
}

.order-totals {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid var(--neutral-medium);
}

.order-totals h6 {
  color: var(--tertiary-dark);
  font-weight: 600;
  margin-bottom: 1rem;
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

.total-row span {
  font-size: 1.1rem;
}

/* Form styling */
.form-label {
  color: var(--tertiary-dark);
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.form-control,
.form-select {
  border: 2px solid var(--neutral-medium);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.form-control:focus,
.form-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.15);
}

.form-control.is-invalid {
  border-color: var(--error);
}

/* Priority styling */
select#priority option[value="urgent"] {
  color: var(--error);
  font-weight: 600;
}

select#priority option[value="high"] {
  color: #f59e0b;
  font-weight: 600;
}

select#priority option[value="normal"] {
  color: var(--primary);
}

select#priority option[value="low"] {
  color: var(--tertiary-medium);
}

/* Button styling */
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

.btn-success {
  background: linear-gradient(135deg, var(--success), var(--success-dark));
  border: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-success:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(94, 180, 136, 0.3);
}

.btn-outline-secondary {
  border: 2px solid var(--neutral-medium);
  color: var(--tertiary-dark);
  border-radius: 8px;
  font-weight: 500;
}

.btn-outline-secondary:hover {
  background-color: var(--neutral-medium);
  border-color: var(--neutral-dark);
  color: white;
}

/* Color classes */
.text-primary-dark {
  color: var(--primary-dark) !important;
}

.text-tertiary-dark {
  color: var(--tertiary-dark) !important;
}

.text-tertiary-medium {
  color: var(--tertiary-medium) !important;
}

/* Form check styling */
.form-check-label {
  color: var(--tertiary-dark);
  margin-left: 0.5rem;
}

.form-check-input:checked {
  background-color: var(--primary);
  border-color: var(--primary);
}

/* Loading state */
.btn-loading {
  position: relative;
}

.btn-loading .spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

/* Input group styling */
.input-group-text {
  background-color: var(--neutral-light);
  border-color: var(--neutral-medium);
  color: var(--tertiary-dark);
  font-weight: 500;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .modal-body {
    padding: 1rem;
    max-height: 85vh;
  }
  
  .modal-footer {
    padding: 1rem;
  }
  
  .order-info-card,
  .supplier-info-card {
    padding: 1rem;
    margin-bottom: 1rem;
  }
  
  .order-items-table {
    font-size: 0.8rem;
  }
  
  .order-items-table th,
  .order-items-table td {
    padding: 0.5rem 0.25rem;
  }
  
  .quick-actions {
    margin-top: 1rem;
  }
  
  .d-flex.justify-content-between.align-items-center.w-100 {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .btn-group {
    width: 100%;
  }
}

@media (max-width: 576px) {
  .order-items-section {
    padding: 1rem;
  }
  
  .order-summary-section {
    padding: 1rem;
  }
  
  .order-totals {
    padding: 1rem;
  }
  
  .table-responsive {
    font-size: 0.75rem;
  }
  
  .btn-sm {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
  }
}

/* Table row error state */
.table-danger {
  background-color: rgba(220, 53, 69, 0.1) !important;
}

/* Validation styling */
.invalid-feedback {
  font-size: 0.75rem;
  margin-top: 0.25rem;
}
</style>