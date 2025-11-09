<template>
  <div
    class="modal fade"
    ref="modalElement"
    tabindex="-1"
    aria-labelledby="orderDetailsModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content">
        <!-- Modal Header -->
        <div class="modal-header border-theme">
          <h5 class="modal-title text-primary fw-semibold" id="orderDetailsModalLabel">
            📦 Order Details
          </h5>
          <button
            type="button"
            class="btn-close"
            @click="closeModal"
            aria-label="Close"
          ></button>
        </div>

        <!-- Modal Body -->
        <div class="modal-body">
          <div v-if="isLoading" class="text-center py-5">
            <div class="spinner-border text-accent" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="text-secondary mt-2">Loading order details...</p>
          </div>

          <div v-else-if="order" class="order-details">
            <!-- Order Header Info -->
            <div class="row mb-4">
              <div class="col-md-6">
                <div class="info-card surface-card p-3 rounded shadow-sm">
                  <h6 class="text-accent fw-semibold mb-3">📋 Order Information</h6>
                  <div class="info-item">
                    <span class="info-label">Order ID:</span>
                    <span class="info-value">{{ order.order_id }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Customer ID:</span>
                    <span class="info-value">{{ order.customer_id }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Order Date:</span>
                    <span class="info-value">{{ formatDate(order.created_at) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Payment Method:</span>
                    <span class="info-value">{{ formatPaymentMethod(order.payment_method) }}</span>
                  </div>
                </div>
              </div>

              <div class="col-md-6">
                <div class="info-card surface-card p-3 rounded shadow-sm">
                  <h6 class="text-accent fw-semibold mb-3">📊 Status Information</h6>
                  <div class="info-item">
                    <span class="info-label">Order Status:</span>
                    <span :class="getStatusBadgeClass(order.order_status)" class="badge">
                      {{ formatStatus(order.order_status) }}
                    </span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Payment Status:</span>
                    <span :class="getPaymentStatusBadgeClass(order.payment_status)" class="badge">
                      {{ formatPaymentStatus(order.payment_status) }}
                    </span>
                  </div>
                  <div v-if="order.cancellation_reason" class="info-item">
                    <span class="info-label">Cancellation Reason:</span>
                    <span class="info-value text-danger">{{ order.cancellation_reason }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Delivery Information -->
            <div class="info-card surface-card p-3 rounded shadow-sm mb-4">
              <h6 class="text-accent fw-semibold mb-3">🚚 Delivery Information</h6>
              <div class="row">
                <div class="col-md-6">
                  <div class="info-item">
                    <span class="info-label">Delivery Type:</span>
                    <span class="info-value">{{ order.delivery_type || 'Delivery' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Delivery Address:</span>
                    <span class="info-value">
                      {{ order.delivery_address?.street || order.delivery_address || 'N/A' }}
                    </span>
                  </div>
                </div>
                <div class="col-md-6">
                  <div v-if="order.notes" class="info-item">
                    <span class="info-label">Special Instructions:</span>
                    <span class="info-value">{{ order.notes }}</span>
                  </div>
                  <div v-if="order.payment_reference" class="info-item">
                    <span class="info-label">Payment Reference:</span>
                    <span class="info-value">{{ order.payment_reference }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Order Items -->
            <div class="info-card surface-card p-3 rounded shadow-sm mb-4">
              <h6 class="text-accent fw-semibold mb-3">🛒 Order Items</h6>
              <div class="table-responsive">
                <table class="table table-sm">
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th class="text-center">Quantity</th>
                      <th class="text-end">Price</th>
                      <th class="text-end">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, index) in order.items" :key="index">
                      <td>{{ item.product_name || item.name }}</td>
                      <td class="text-center">{{ item.quantity }}</td>
                      <td class="text-end">₱{{ formatCurrency(item.price) }}</td>
                      <td class="text-end fw-medium">₱{{ formatCurrency(item.price * item.quantity) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Order Summary -->
            <div class="info-card surface-card p-3 rounded shadow-sm mb-4">
              <h6 class="text-accent fw-semibold mb-3">💰 Order Summary</h6>
              <div class="summary-row">
                <span>Subtotal:</span>
                <span>₱{{ formatCurrency(order.subtotal) }}</span>
              </div>
              <div class="summary-row">
                <span>Delivery Fee:</span>
                <span>₱{{ formatCurrency(order.delivery_fee || 0) }}</span>
              </div>
              <div class="summary-row">
                <span>Service Fee:</span>
                <span>₱{{ formatCurrency(order.service_fee || 0) }}</span>
              </div>
              <div v-if="order.discount_amount > 0" class="summary-row text-success">
                <span>Discount:</span>
                <span>-₱{{ formatCurrency(order.discount_amount) }}</span>
              </div>
              <div class="summary-row fw-bold text-primary border-top pt-2 mt-2">
                <span>Total Amount:</span>
                <span>₱{{ formatCurrency(order.total_amount) }}</span>
              </div>
            </div>

            <!-- Status History -->
            <div v-if="order.status_history && order.status_history.length > 0" class="info-card surface-card p-3 rounded shadow-sm mb-4">
              <h6 class="text-accent fw-semibold mb-3">📅 Status History</h6>
              <div class="timeline">
                <div v-for="(history, index) in order.status_history" :key="index" class="timeline-item">
                  <div class="timeline-marker"></div>
                  <div class="timeline-content">
                    <div class="timeline-status">{{ formatStatus(history.status) }}</div>
                    <div class="timeline-time">{{ formatDate(history.timestamp) }}</div>
                    <div v-if="history.notes" class="timeline-notes">{{ history.notes }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Update Status Section -->
            <div class="info-card surface-card p-3 rounded shadow-sm">
              <h6 class="text-accent fw-semibold mb-3">🔄 Update Order Status</h6>
              <div class="row g-3">
                <div class="col-md-6">
                  <label for="orderStatus" class="form-label">Order Status</label>
                  <select
                    id="orderStatus"
                    v-model="newStatus"
                    class="form-select"
                    :disabled="isUpdating || order.order_status === 'cancelled' || order.order_status === 'completed'"
                  >
                    <option value="pending">Pending</option>
                    <option value="confirmed">Confirmed</option>
                    <option value="preparing">Preparing</option>
                    <option value="ready">Ready for Delivery</option>
                    <option value="out_for_delivery">Out for Delivery</option>
                    <option value="delivered">Delivered</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label for="paymentStatus" class="form-label">Payment Status</label>
                  <select
                    id="paymentStatus"
                    v-model="newPaymentStatus"
                    class="form-select"
                    :disabled="isUpdating"
                  >
                    <option value="pending">Pending</option>
                    <option value="paid">Paid</option>
                    <option value="failed">Failed</option>
                    <option value="refunded">Refunded</option>
                  </select>
                </div>
                <div class="col-12">
                  <label for="statusNotes" class="form-label">Notes (Optional)</label>
                  <textarea
                    id="statusNotes"
                    v-model="statusNotes"
                    class="form-control"
                    rows="2"
                    placeholder="Add notes about this status update..."
                    :disabled="isUpdating"
                  ></textarea>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer border-theme">
          <button
            type="button"
            class="btn btn-secondary"
            @click="closeModal"
            :disabled="isUpdating"
          >
            Close
          </button>
          <button
            v-if="order && order.order_status !== 'cancelled' && order.order_status !== 'completed'"
            type="button"
            class="btn btn-submit"
            @click="handleUpdateStatus"
            :disabled="isUpdating || !hasChanges"
          >
            <span v-if="isUpdating">
              <span class="spinner-border spinner-border-sm me-2" role="status"></span>
              Updating...
            </span>
            <span v-else>
              💾 Save Changes
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Modal } from 'bootstrap'
import { useOnlineOrders } from '@/composables/api/useOnlineOrders.js'

// =====================
// PROPS & EMITS
// =====================
const props = defineProps({
  orderId: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['close', 'updated'])

// =====================
// COMPOSABLE HOOKS
// =====================
const {
  currentOrder: order,
  isLoading,
  fetchOrderById,
  updateOrderStatus,
  updatePaymentStatus
} = useOnlineOrders()

// =====================
// REACTIVE STATE
// =====================
const modalElement = ref(null)
const modalInstance = ref(null)
const isUpdating = ref(false)

const newStatus = ref('')
const newPaymentStatus = ref('')
const statusNotes = ref('')

// =====================
// COMPUTED PROPERTIES
// =====================
const hasChanges = computed(() => {
  if (!order.value) return false
  return (
    newStatus.value !== order.value.order_status ||
    newPaymentStatus.value !== order.value.payment_status
  )
})

// =====================
// METHODS
// =====================
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'Invalid Date'
  }
}

const formatCurrency = (amount) => {
  if (amount == null) return '0.00'
  return parseFloat(amount).toFixed(2)
}

const formatStatus = (status) => {
  const statusMap = {
    'pending': 'Pending',
    'confirmed': 'Confirmed',
    'preparing': 'Preparing',
    'ready': 'Ready for Delivery',
    'out_for_delivery': 'Out for Delivery',
    'delivered': 'Delivered',
    'completed': 'Completed',
    'cancelled': 'Cancelled'
  }
  return statusMap[status] || status
}

const formatPaymentStatus = (status) => {
  const statusMap = {
    'pending': 'Pending',
    'paid': 'Paid',
    'failed': 'Failed',
    'refunded': 'Refunded'
  }
  return statusMap[status] || status
}

const formatPaymentMethod = (method) => {
  const methodMap = {
    'cash': 'Cash on Delivery',
    'cod': 'Cash on Delivery',
    'gcash': 'GCash',
    'paymaya': 'PayMaya',
    'card': 'Credit/Debit Card',
    'grabpay': 'GrabPay'
  }
  return methodMap[method] || method
}

const getStatusBadgeClass = (status) => {
  const classMap = {
    'pending': 'bg-warning text-dark',
    'confirmed': 'bg-info text-white',
    'preparing': 'bg-primary text-white',
    'ready': 'bg-success text-white',
    'out_for_delivery': 'bg-primary text-white',
    'delivered': 'bg-success text-white',
    'completed': 'bg-success text-white',
    'cancelled': 'bg-danger text-white'
  }
  return classMap[status] || 'bg-secondary text-white'
}

const getPaymentStatusBadgeClass = (status) => {
  const classMap = {
    'pending': 'bg-warning text-dark',
    'paid': 'bg-success text-white',
    'failed': 'bg-danger text-white',
    'refunded': 'bg-info text-white'
  }
  return classMap[status] || 'bg-secondary text-white'
}

const handleUpdateStatus = async () => {
  try {
    isUpdating.value = true

    // Update order status if changed
    if (newStatus.value !== order.value.order_status) {
      await updateOrderStatus(
        order.value.order_id,
        newStatus.value,
        statusNotes.value
      )
    }

    // Update payment status if changed
    if (newPaymentStatus.value !== order.value.payment_status) {
      await updatePaymentStatus(
        order.value.order_id,
        newPaymentStatus.value
      )
    }

    // Refresh order data
    await fetchOrderById(order.value.order_id)

    // Reset notes
    statusNotes.value = ''

    emit('updated', order.value)
    alert('✅ Order status updated successfully!')
  } catch (error) {
    console.error('Error updating order:', error)
    alert('❌ Failed to update order status: ' + error.message)
  } finally {
    isUpdating.value = false
  }
}

const openModal = async (orderId) => {
  if (!orderId) return

  try {
    await fetchOrderById(orderId)
    
    // Initialize form fields
    newStatus.value = order.value?.order_status || 'pending'
    newPaymentStatus.value = order.value?.payment_status || 'pending'
    statusNotes.value = ''

    modalInstance.value?.show()
  } catch (error) {
    console.error('Error opening order modal:', error)
    alert('Failed to load order details')
  }
}

const closeModal = () => {
  modalInstance.value?.hide()
  emit('close')
}

// =====================
// WATCHERS
// =====================
watch(() => props.orderId, (newId) => {
  if (newId) {
    openModal(newId)
  }
})

// =====================
// LIFECYCLE
// =====================
defineExpose({ openModal, closeModal })

// Initialize modal on mount
if (import.meta.env.SSR === undefined && typeof window !== 'undefined') {
  setTimeout(() => {
    if (modalElement.value) {
      modalInstance.value = new Modal(modalElement.value)
    }
  }, 100)
}
</script>

<style scoped>
.info-card {
  background: var(--surface-card, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-subtle, #f3f4f6);
}

.info-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.info-label {
  font-weight: 600;
  color: var(--text-secondary, #6b7280);
  font-size: 0.9rem;
}

.info-value {
  color: var(--text-primary, #111827);
  font-size: 0.9rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
}

.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--border-color, #e5e7eb);
}

.timeline-item {
  position: relative;
  margin-bottom: 1.5rem;
}

.timeline-item:last-child {
  margin-bottom: 0;
}

.timeline-marker {
  position: absolute;
  left: -26px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--accent-color, #ff6b35);
  border: 3px solid var(--surface-card, #ffffff);
  box-shadow: 0 0 0 2px var(--accent-color, #ff6b35);
}

.timeline-content {
  background: var(--surface-secondary, #f9fafb);
  padding: 0.75rem;
  border-radius: 0.5rem;
}

.timeline-status {
  font-weight: 600;
  color: var(--text-primary, #111827);
  font-size: 0.95rem;
  margin-bottom: 0.25rem;
}

.timeline-time {
  font-size: 0.85rem;
  color: var(--text-tertiary, #9ca3af);
  margin-bottom: 0.25rem;
}

.timeline-notes {
  font-size: 0.9rem;
  color: var(--text-secondary, #6b7280);
  font-style: italic;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-subtle, #e5e7eb);
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}

.badge {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
  font-weight: 600;
}

@media (max-width: 768px) {
  .modal-dialog {
    margin: 0.5rem;
  }

  .info-item {
    flex-direction: column;
  }

  .info-value {
    margin-top: 0.25rem;
  }
}
</style>

