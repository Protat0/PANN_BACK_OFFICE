<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content modern-modal">
        <!-- Modal Header -->
        <div class="modal-header border-0 pb-0">
          <div class="d-flex align-items-center">
            <div class="modal-icon me-3">
              <FileText :size="24" />
            </div>
            <div>
              <h4 class="modal-title mb-1">Receipt Details</h4>
              <p class="text-muted mb-0 small">
                Order ID: <strong>{{ receipt?.id }}</strong>
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
          <div v-if="receipt">
            <!-- Receipt Summary -->
            <div class="receipt-header card mb-4">
              <div class="card-body">
                <div class="row">
                  <div class="col-md-6">
                    <h6 class="text-muted mb-3">Receipt Information</h6>
                    <div class="info-row">
                      <span class="label">Receipt ID:</span>
                      <strong>{{ receipt.id }}</strong>
                    </div>
                    <div class="info-row">
                      <span class="label">Order Date:</span>
                      <span>{{ formatDate(receipt.date) }}</span>
                    </div>
                    <div class="info-row">
                      <span class="label">Expected Delivery:</span>
                      <span>{{ formatDate(receipt.expectedDate) }}</span>
                    </div>
                    <div class="info-row">
                      <span class="label">Date Received:</span>
                      <span v-if="receipt.receivedDate" class="text-success">
                        {{ formatDate(receipt.receivedDate) }}
                      </span>
                      <span v-else class="text-warning">
                        <em>Not yet received</em>
                      </span>
                    </div>
                    <div class="info-row">
                      <span class="label">Status:</span>
                      <span :class="['badge', getStatusClass(receipt.status)]">
                        {{ receipt.status }}
                      </span>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <h6 class="text-muted mb-3">Summary</h6>
                    <div class="info-row">
                      <span class="label">Total Items:</span>
                      <strong>{{ receipt.items?.length || 0 }}</strong>
                    </div>
                    <div class="info-row">
                      <span class="label">Total Quantity:</span>
                      <strong>{{ receipt.quantity }}</strong>
                    </div>
                    <div class="info-row">
                      <span class="label">Subtotal:</span>
                      <span>₱{{ formatCurrency(receipt.subtotal || receipt.total) }}</span>
                    </div>
                    <div class="info-row">
                      <span class="label">Total Cost:</span>
                      <strong class="text-primary fs-5">₱{{ formatCurrency(receipt.total) }}</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Items List -->
            <div class="card mb-4">
              <div class="card-header bg-light">
                <h6 class="mb-0">
                  <Package :size="18" class="me-2" />
                  Items Received
                </h6>
              </div>
              <div class="card-body p-0">
                <div class="table-responsive">
                  <table class="table table-hover mb-0">
                    <thead class="table-light">
                      <tr>
                        <th>#</th>
                        <th>Product</th>
                        <th>Batch Number</th>
                        <th>Quantity</th>
                        <th>Unit Price</th>
                        <th>Total Price</th>
                        <th>Expiry Date</th>
                        <th>Remaining</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(item, index) in receipt.items" :key="index">
                        <td>{{ index + 1 }}</td>
                        <td>
                          <strong>{{ item.name }}</strong>
                          <br>
                          <small class="text-muted">{{ item.productId }}</small>
                        </td>
                        <td>
                          <code class="text-primary">{{ item.batchNumber }}</code>
                        </td>
                        <td class="text-center">
                          <span class="badge bg-secondary">{{ item.quantity }}</span>
                        </td>
                        <td>₱{{ formatCurrency(item.unitPrice) }}</td>
                        <td class="fw-bold">₱{{ formatCurrency(item.totalPrice) }}</td>
                        <td>
                          <span v-if="item.expiryDate">
                            {{ formatDate(item.expiryDate) }}
                            <br>
                            <small :class="['text-muted', { 'text-danger': isExpiringSoon(item.expiryDate) }]">
                              {{ getExpiryStatus(item.expiryDate) }}
                            </small>
                          </span>
                          <span v-else class="text-muted">N/A</span>
                        </td>
                        <td class="text-center">
                          <span class="badge" :class="getStockClass(item.quantityRemaining, item.quantity)">
                            {{ item.quantityRemaining || 0 }} / {{ item.quantity }}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                    <tfoot class="table-light">
                      <tr>
                        <td colspan="3" class="text-end"><strong>Total:</strong></td>
                        <td class="text-center">
                          <strong>{{ getTotalQuantity() }}</strong>
                        </td>
                        <td colspan="2" class="text-end">
                          <strong class="text-primary">₱{{ formatCurrency(receipt.total) }}</strong>
                        </td>
                        <td colspan="2"></td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>
            </div>

            <!-- Notes Section -->
            <div v-if="receipt.notes" class="card">
              <div class="card-header bg-light">
                <h6 class="mb-0">
                  <FileText :size="18" class="me-2" />
                  Notes
                </h6>
              </div>
              <div class="card-body">
                <p class="mb-0">{{ receipt.notes }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer border-0">
          <button type="button" class="btn btn-outline-secondary" @click="handleClose">
            Close
          </button>
          <button type="button" class="btn btn-primary" @click="printReceipt">
            <Printer :size="16" class="me-1" />
            Print Receipt
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { FileText, Package, Printer } from 'lucide-vue-next'
import { useToast } from '@/composables/ui/useToast'

export default {
  name: 'BatchDetailsModal',
  components: {
    FileText,
    Package,
    Printer
  },
  emits: ['close'],
  props: {
    show: {
      type: Boolean,
      default: false
    },
    receipt: {
      type: Object,
      default: null
    }
  },
  setup(props, { emit }) {
    const { success: showSuccess } = useToast()
    
    function handleClose() {
      emit('close')
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
    
    function getStatusClass(status) {
      const classes = {
        'Received': 'bg-success',
        'Pending Delivery': 'bg-warning',
        'Partially Received': 'bg-info',
        'Depleted': 'bg-secondary'
      }
      return classes[status] || 'bg-secondary'
    }
    
    function getStockClass(remaining, total) {
      const percentage = (remaining / total) * 100
      if (percentage === 0) return 'bg-secondary'
      if (percentage < 25) return 'bg-danger'
      if (percentage < 50) return 'bg-warning'
      return 'bg-success'
    }
    
    function isExpiringSoon(expiryDate) {
      if (!expiryDate) return false
      const expiry = new Date(expiryDate)
      const today = new Date()
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      return daysUntilExpiry <= 30 && daysUntilExpiry > 0
    }
    
    function getExpiryStatus(expiryDate) {
      if (!expiryDate) return ''
      const expiry = new Date(expiryDate)
      const today = new Date()
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      
      if (daysUntilExpiry < 0) return 'Expired'
      if (daysUntilExpiry === 0) return 'Expires today'
      if (daysUntilExpiry === 1) return 'Expires tomorrow'
      if (daysUntilExpiry <= 30) return `Expires in ${daysUntilExpiry} days`
      return `${daysUntilExpiry} days until expiry`
    }
    
    function getTotalQuantity() {
      return props.receipt?.items?.reduce((sum, item) => sum + (item.quantity || 0), 0) || 0
    }
    
    function printReceipt() {
      showSuccess('Print functionality coming soon')
      // TODO: Implement print functionality
    }
    
    return {
      handleClose,
      formatDate,
      formatCurrency,
      getStatusClass,
      getStockClass,
      isExpiringSoon,
      getExpiryStatus,
      getTotalQuantity,
      printReceipt
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
  background: linear-gradient(135deg, var(--info-light), var(--info));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--info-dark);
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

.receipt-header {
  border: 2px solid var(--neutral-medium);
  border-radius: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--neutral-light);
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  color: var(--tertiary-medium);
  font-size: 0.875rem;
}

code {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.875rem;
}

.table thead th {
  font-weight: 600;
  font-size: 0.875rem;
}

.table tbody td {
  vertical-align: middle;
}
</style>
