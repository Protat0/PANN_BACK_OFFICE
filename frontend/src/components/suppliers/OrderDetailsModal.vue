<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content modern-modal">
        <div class="modal-header">
          <div class="d-flex align-items-center">
            <div class="modal-icon me-3">
              <component :is="isEditMode ? Edit : Eye" :size="24" />
            </div>
            <div>
              <h4 class="modal-title mb-1">
                {{ isEditMode ? 'Edit Order' : 'Order Details' }}
              </h4>
              <p class="text-muted mb-0 small">
                {{ isEditMode ? 'Modify order information' : 'View order information' }}
              </p>
            </div>
          </div>
          <div class="d-flex gap-2">
            <button 
              v-if="!isEditMode && canEdit" 
              type="button" 
              class="btn btn-primary btn-sm"
              @click="toggleEditMode"
            >
              <Edit :size="16" class="me-1" />
              Edit Order
            </button>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
        </div>
        
        <div class="modal-body">
          <!-- Order Header Info -->
          <div class="row mb-4">
            <div class="col-md-6">
              <div class="info-card">
                <h6 class="info-card-title">
                  <FileText :size="16" class="me-2" />
                  Order Information
                </h6>
                <div class="info-item">
                  <label>Order ID:</label>
                  <span class="order-id-text">{{ order.id }}</span>
                </div>
                <div class="info-item">
                  <label>Order Date:</label>
                  <span>{{ formatDate(order.date) }}</span>
                </div>
                <div class="info-item">
                  <label>Expected Date:</label>
                  <div v-if="!isEditMode">
                    <span>{{ formatDate(order.expectedDate) }}</span>
                    <br>
                    <small :class="['text-muted', { 'text-danger': isOverdue(order) }]">
                      {{ getTimeRemaining(order.expectedDate) }}
                    </small>
                  </div>
                  <input 
                    v-else
                    type="date" 
                    class="form-control form-control-sm"
                    v-model="editForm.expectedDate"
                  >
                </div>
                <div class="info-item mb-0">
                  <label>Status:</label>
                  <div v-if="!isEditMode">
                    <span :class="['badge', 'order-status', getOrderStatusClass(order.status)]">
                      {{ order.status }}
                    </span>
                  </div>
                  <select v-else class="form-select form-select-sm" v-model="editForm.status">
                    <option value="Pending">Pending</option>
                    <option value="Active">Active</option>
                    <option value="Received">Received</option>
                    <option value="Cancelled">Cancelled</option>
                  </select>
                </div>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="info-card">
                <h6 class="info-card-title">
                  <DollarSign :size="16" class="me-2" />
                  Financial Summary
                </h6>
                <div class="info-item">
                  <label>Quantity:</label>
                  <div v-if="!isEditMode">
                    <span>{{ order.quantity }} items</span>
                  </div>
                  <input 
                    v-else
                    type="number" 
                    class="form-control form-control-sm"
                    v-model.number="editForm.quantity"
                    min="1"
                  >
                </div>
                <div class="info-item">
                  <label>Total Cost:</label>
                  <div v-if="!isEditMode">
                    <span class="amount-text">₱{{ formatCurrency(order.total) }}</span>
                  </div>
                  <div v-else class="input-group input-group-sm">
                    <span class="input-group-text">₱</span>
                    <input 
                      type="number" 
                      class="form-control"
                      v-model.number="editForm.total"
                      min="0"
                      step="0.01"
                    >
                  </div>
                </div>
                <div class="info-item mb-0">
                  <label>Cost per Item:</label>
                  <span class="text-muted">
                    ₱{{ formatCurrency(getCostPerItem()) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Order Description -->
          <div class="info-card mb-4">
            <h6 class="info-card-title">
              <Package :size="16" class="me-2" />
              Order Description
            </h6>
            <div v-if="!isEditMode" class="description-content">
              {{ order.description || 'No description provided' }}
            </div>
            <textarea 
              v-else
              class="form-control"
              v-model="editForm.description"
              rows="3"
              placeholder="Enter order description..."
            ></textarea>
          </div>

          <!-- Order Items (if available) -->
          <div v-if="orderItems && orderItems.length > 0" class="info-card mb-4">
            <h6 class="info-card-title">
              <List :size="16" class="me-2" />
              Order Items
              <span class="badge bg-secondary ms-2">{{ orderItems.length }}</span>
            </h6>
            <div class="table-responsive">
              <table class="table table-sm items-table">
                <thead>
                  <tr>
                    <th>Item Name</th>
                    <th>Quantity</th>
                    <th>Unit Price</th>
                    <th>Total</th>
                    <th v-if="isEditMode">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in editableItems" :key="index">
                    <td>
                      <input 
                        v-if="isEditMode"
                        type="text" 
                        class="form-control form-control-sm"
                        v-model="item.name"
                        placeholder="Item name"
                      >
                      <span v-else>{{ item.name }}</span>
                    </td>
                    <td>
                      <input 
                        v-if="isEditMode"
                        type="number" 
                        class="form-control form-control-sm"
                        v-model.number="item.quantity"
                        min="1"
                        @input="calculateItemTotal(item)"
                      >
                      <span v-else>{{ item.quantity }}</span>
                    </td>
                    <td>
                      <div v-if="isEditMode" class="input-group input-group-sm">
                        <span class="input-group-text">₱</span>
                        <input 
                          type="number" 
                          class="form-control"
                          v-model.number="item.unitPrice"
                          min="0"
                          step="0.01"
                          @input="calculateItemTotal(item)"
                        >
                      </div>
                      <span v-else>₱{{ formatCurrency(item.unitPrice) }}</span>
                    </td>
                    <td>
                      <span class="fw-bold">₱{{ formatCurrency(item.total) }}</span>
                    </td>
                    <td v-if="isEditMode">
                      <button 
                        type="button" 
                        class="btn btn-outline-danger btn-sm"
                        @click="removeItem(index)"
                        :disabled="editableItems.length <= 1"
                      >
                        <Trash2 :size="14" />
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div v-if="isEditMode" class="mt-3">
              <button type="button" class="btn btn-outline-primary btn-sm" @click="addNewItem">
                <Plus :size="16" class="me-1" />
                Add Item
              </button>
            </div>
          </div>

          <!-- Order Notes -->
          <div class="info-card mb-4">
            <h6 class="info-card-title">
              <MessageSquare :size="16" class="me-2" />
              Order Notes
            </h6>
            <div v-if="!isEditMode" class="notes-content">
              {{ order.notes || 'No notes available' }}
            </div>
            <textarea 
              v-else
              class="form-control"
              v-model="editForm.notes"
              rows="3"
              placeholder="Add notes about this order..."
            ></textarea>
          </div>

          <!-- Order Timeline/History -->
          <div v-if="orderHistory && orderHistory.length > 0" class="info-card">
            <h6 class="info-card-title">
              <Clock :size="16" class="me-2" />
              Order History
            </h6>
            <div class="timeline">
              <div v-for="event in orderHistory" :key="event.id" class="timeline-item">
                <div class="timeline-marker" :class="getEventMarkerClass(event.type)">
                  <component :is="getEventIcon(event.type)" :size="12" />
                </div>
                <div class="timeline-content">
                  <div class="timeline-header">
                    <strong>{{ event.title }}</strong>
                    <small class="text-muted ms-auto">{{ formatTimeAgo(event.date) }}</small>
                  </div>
                  <p class="mb-1 text-muted">{{ event.description }}</p>
                  <small class="text-muted">by {{ event.user }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <div class="d-flex justify-content-between w-100">
            <div>
              <button 
                v-if="!isEditMode" 
                type="button" 
                class="btn btn-outline-primary"
                @click="printOrder"
              >
                <Printer :size="16" class="me-1" />
                Print
              </button>
            </div>
            <div class="d-flex gap-2">
              <button type="button" class="btn btn-secondary" @click="handleCancel">
                {{ isEditMode ? 'Cancel' : 'Close' }}
              </button>
              <button 
                v-if="isEditMode" 
                type="button" 
                class="btn btn-primary" 
                @click="saveOrder"
                :disabled="saving || !isFormValid"
              >
                <div v-if="saving" class="spinner-border spinner-border-sm me-2"></div>
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
import {
  Eye,
  Edit,
  FileText,
  DollarSign,
  Package,
  List,
  MessageSquare,
  Clock,
  Plus,
  Trash2,
  Printer,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Activity
} from 'lucide-vue-next'

export default {
  name: 'OrderDetailsModal',
  components: {
    Eye,
    Edit,
    FileText,
    DollarSign,
    Package,
    List,
    MessageSquare,
    Clock,
    Plus,
    Trash2,
    Printer,
    AlertTriangle,
    CheckCircle,
    XCircle,
    Activity
  },
  props: {
    show: {
        type: Boolean,
        default: false
    },
    order: {
        type: Object,
        required: true
    },
    canEdit: {
        type: Boolean,
        default: true
    },
    // Add this new prop
    initialMode: {
        type: String,
        default: 'view', // 'view' or 'edit'
        validator: value => ['view', 'edit'].includes(value)
    }
  },
  emits: ['close', 'save', 'edit-mode-changed'],
  data() {
    return {
      isEditMode: false,
      saving: false,
      editForm: {
        expectedDate: '',
        status: '',
        quantity: 0,
        total: 0,
        description: '',
        notes: ''
      },
      editableItems: [],
      orderItems: [],
      orderHistory: []
    }
  },
  computed: {
    isFormValid() {
      return this.editForm.quantity > 0 && 
             this.editForm.total > 0 && 
             this.editForm.expectedDate && 
             this.editForm.status
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        this.initializeModal()
      }
    },
    order: {
      handler() {
        if (this.show) {
          this.initializeModal()
        }
      },
      deep: true
    }
  },
  methods: {
    initializeModal() {
        this.isEditMode = this.initialMode === 'edit'
        this.resetEditForm()
        this.loadOrderData()
    },

    resetEditForm() {
      this.editForm = {
        expectedDate: this.order.expectedDate || '',
        status: this.order.status || 'Pending',
        quantity: this.order.quantity || 0,
        total: this.order.total || 0,
        description: this.order.description || '',
        notes: this.order.notes || ''
      }
    },

    loadOrderData() {
      // Mock order items data
      this.orderItems = [
        {
          name: 'Rice (Premium)',
          quantity: 5,
          unitPrice: 150.00,
          total: 750.00
        },
        {
          name: 'Cooking Oil (1L)',
          quantity: 10,
          unitPrice: 85.00,
          total: 850.00
        },
        {
          name: 'Sugar (1kg)',
          quantity: 8,
          unitPrice: 75.00,
          total: 600.00
        }
      ]

      // Mock order history
      this.orderHistory = [
        {
          id: 1,
          type: 'created',
          title: 'Order Created',
          description: 'Purchase order was created',
          user: 'Admin User',
          date: this.order.date
        },
        {
          id: 2,
          type: 'updated',
          title: 'Order Updated',
          description: 'Order details were modified',
          user: 'Admin User',
          date: '2024-12-11T10:00:00Z'
        }
      ]

      this.editableItems = [...this.orderItems]
    },

    toggleEditMode() {
      this.isEditMode = !this.isEditMode
      if (this.isEditMode) {
        this.resetEditForm()
        this.editableItems = [...this.orderItems]
      }
      this.$emit('edit-mode-changed', this.isEditMode)
    },

    handleCancel() {
      if (this.isEditMode) {
        this.isEditMode = false
        this.resetEditForm()
        this.editableItems = [...this.orderItems]
      } else {
        this.closeModal()
      }
    },

    closeModal() {
      this.isEditMode = false
      this.$emit('close')
    },

    async saveOrder() {
      this.saving = true
      
      try {
        // Calculate total from items if available
        if (this.editableItems.length > 0) {
          this.editForm.total = this.editableItems.reduce((sum, item) => sum + item.total, 0)
          this.editForm.quantity = this.editableItems.reduce((sum, item) => sum + item.quantity, 0)
        }

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000))

        const updatedOrder = {
          ...this.order,
          ...this.editForm,
          items: [...this.editableItems]
        }

        this.$emit('save', updatedOrder)
        this.isEditMode = false
        
      } catch (error) {
        console.error('Error saving order:', error)
        alert('Failed to save order. Please try again.')
      } finally {
        this.saving = false
      }
    },

    addNewItem() {
      this.editableItems.push({
        name: '',
        quantity: 1,
        unitPrice: 0,
        total: 0
      })
    },

    removeItem(index) {
      if (this.editableItems.length > 1) {
        this.editableItems.splice(index, 1)
      }
    },

    calculateItemTotal(item) {
      item.total = (item.quantity || 0) * (item.unitPrice || 0)
    },

    printOrder() {
      window.print()
    },

    // Utility methods
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },

    formatTimeAgo(dateString) {
      const date = new Date(dateString)
      const now = new Date()
      const diffTime = Math.abs(now - date)
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
      const diffHours = Math.floor(diffTime / (1000 * 60 * 60))

      if (diffDays > 0) {
        return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
      } else if (diffHours > 0) {
        return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
      } else {
        return 'Just now'
      }
    },

    formatCurrency(amount) {
      return new Intl.NumberFormat('en-PH', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(amount || 0)
    },

    getCostPerItem() {
      return this.isEditMode 
        ? (this.editForm.total || 0) / (this.editForm.quantity || 1)
        : (this.order.total || 0) / (this.order.quantity || 1)
    },

    isOverdue(order) {
      const expectedDate = new Date(order.expectedDate)
      const today = new Date()
      return expectedDate < today && (order.status === 'Pending' || order.status === 'Active')
    },

    getTimeRemaining(dateString) {
      const expectedDate = new Date(dateString)
      const today = new Date()
      const diffTime = expectedDate - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays < 0) {
        return `${Math.abs(diffDays)} days overdue`
      } else if (diffDays === 0) {
        return 'Due today'
      } else if (diffDays === 1) {
        return 'Due tomorrow'
      } else {
        return `${diffDays} days remaining`
      }
    },

    getOrderStatusClass(status) {
      const classes = {
        'Received': 'bg-success',
        'Pending': 'bg-warning',
        'Cancelled': 'bg-danger',
        'Active': 'bg-primary'
      }
      return classes[status] || 'bg-secondary'
    },

    getEventIcon(type) {
      const icons = {
        created: Plus,
        updated: Edit,
        cancelled: XCircle,
        received: CheckCircle
      }
      return icons[type] || Activity
    },

    getEventMarkerClass(type) {
      const classes = {
        created: 'bg-primary',
        updated: 'bg-info',
        cancelled: 'bg-danger',
        received: 'bg-success'
      }
      return classes[type] || 'bg-secondary'
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

.modal-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--primary-light), var(--primary));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-dark);
}

.info-card {
  background: var(--neutral-light);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.info-card:last-child {
  margin-bottom: 0;
}

.info-card-title {
  color: var(--tertiary-dark);
  font-weight: 600;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--neutral);
  padding-bottom: 0.5rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--neutral);
}

.info-item:last-child {
  margin-bottom: 0;
  border-bottom: none;
  padding-bottom: 0;
}

.info-item label {
  font-weight: 500;
  color: var(--tertiary-medium);
  font-size: 0.875rem;
  margin-bottom: 0;
  flex-shrink: 0;
  width: 120px;
}

.info-item span, .info-item div {
  color: var(--tertiary-dark);
  font-weight: 500;
  text-align: right;
  flex-grow: 1;
}

.order-id-text {
  font-family: 'Monaco', 'Menlo', monospace;
  color: var(--primary) !important;
  font-weight: 600;
}

.amount-text {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--success) !important;
}

.description-content, .notes-content {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid var(--neutral);
  min-height: 60px;
  color: var(--tertiary-dark);
  line-height: 1.6;
}

.items-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.items-table th {
  background: var(--primary-light);
  color: var(--primary-dark);
  font-weight: 600;
  border: none;
  padding: 0.75rem;
}

.items-table td {
  padding: 0.75rem;
  border-top: 1px solid var(--neutral);
  vertical-align: middle;
}

.timeline {
  position: relative;
}

.timeline-item {
  display: flex;
  margin-bottom: 1.5rem;
  position: relative;
}

.timeline-item:last-child {
  margin-bottom: 0;
}

.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 30px;
  bottom: -24px;
  width: 2px;
  background-color: var(--neutral-medium);
}

.timeline-marker {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 1rem;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.timeline-content {
  flex-grow: 1;
}

.timeline-header {
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.order-status {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

/* Form controls in edit mode */
.form-control:focus,
.form-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .info-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .info-item label {
    width: auto;
    margin-bottom: 0.25rem;
  }
  
  .info-item span, .info-item div {
    text-align: left;
  }
}
</style>