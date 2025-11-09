<template>
  <div class="page-container p-4">
    <!-- Header Section -->
    <div class="page-header mb-4">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <h1 class="h3 fw-semibold text-primary-dark mb-1">📦 Online Orders</h1>
          <p class="text-secondary mb-0">Manage and track customer online orders</p>
        </div>
        <button
          @click="refreshOrders"
          class="btn btn-outline-primary"
          :disabled="isLoading"
        >
          <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
          🔄 Refresh
        </button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="stat-card surface-card p-3 rounded shadow-sm">
          <div class="stat-icon bg-warning text-white">⏳</div>
          <div class="stat-content">
            <h6 class="stat-label">Pending Orders</h6>
            <p class="stat-value">{{ pendingOrders.length }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="stat-card surface-card p-3 rounded shadow-sm">
          <div class="stat-icon bg-info text-white">📦</div>
          <div class="stat-content">
            <h6 class="stat-label">Processing</h6>
            <p class="stat-value">{{ processingOrders.length }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="stat-card surface-card p-3 rounded shadow-sm">
          <div class="stat-icon bg-success text-white">✅</div>
          <div class="stat-content">
            <h6 class="stat-label">Completed</h6>
            <p class="stat-value">{{ completedOrders.length }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="stat-card surface-card p-3 rounded shadow-sm">
          <div class="stat-icon bg-danger text-white">❌</div>
          <div class="stat-content">
            <h6 class="stat-label">Cancelled</h6>
            <p class="stat-value">{{ cancelledOrders.length }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters Section -->
    <div class="filters-section surface-card p-3 rounded shadow-sm mb-4">
      <div class="row g-3">
        <div class="col-md-3">
          <label for="statusFilter" class="form-label small fw-semibold">Status Filter</label>
          <select
            id="statusFilter"
            v-model="filters.status"
            @change="handleFilterChange"
            class="form-select form-select-sm"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="preparing">Preparing</option>
            <option value="ready">Ready</option>
            <option value="out_for_delivery">Out for Delivery</option>
            <option value="delivered">Delivered</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
        <div class="col-md-3">
          <label for="paymentStatusFilter" class="form-label small fw-semibold">Payment Status</label>
          <select
            id="paymentStatusFilter"
            v-model="filters.payment_status"
            @change="handleFilterChange"
            class="form-select form-select-sm"
          >
            <option value="">All Payment Status</option>
            <option value="pending">Pending</option>
            <option value="paid">Paid</option>
            <option value="failed">Failed</option>
            <option value="refunded">Refunded</option>
          </select>
        </div>
        <div class="col-md-3">
          <label for="searchCustomer" class="form-label small fw-semibold">Search Customer</label>
          <input
            id="searchCustomer"
            v-model="filters.customer_id"
            @input="handleFilterChange"
            type="text"
            class="form-control form-control-sm"
            placeholder="Enter Customer ID..."
          />
        </div>
        <div class="col-md-3">
          <label class="form-label small fw-semibold d-block">&nbsp;</label>
          <button
            @click="clearFilters"
            class="btn btn-outline-secondary btn-sm w-100"
          >
            Clear Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading && !hasOrders" class="text-center py-5">
      <div class="spinner-border text-accent mb-3" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-secondary">Loading orders...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="alert alert-danger" role="alert">
      <strong>Error:</strong> {{ error }}
      <button
        @click="refreshOrders"
        class="btn btn-sm btn-outline-danger ms-2"
      >
        Retry
      </button>
    </div>

    <!-- Orders Table -->
    <div v-if="hasOrders" class="table-container surface-card rounded shadow-sm">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th style="width: 120px;">Order ID</th>
              <th style="width: 120px;">Customer</th>
              <th>Items</th>
              <th style="width: 130px;">Total Amount</th>
              <th style="width: 120px;">Order Status</th>
              <th style="width: 120px;">Payment</th>
              <th style="width: 150px;">Date</th>
              <th style="width: 100px;" class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="order in paginatedOrders"
              :key="order.order_id"
              class="cursor-pointer"
              @click="viewOrderDetails(order)"
            >
              <td>
                <span class="badge bg-light text-dark border font-monospace">
                  {{ order.order_id }}
                </span>
              </td>
              <td>
                <span class="badge bg-info text-white">
                  {{ order.customer_id }}
                </span>
              </td>
              <td>
                <span class="text-secondary small">
                  {{ order.items?.length || 0 }} item(s)
                </span>
              </td>
              <td>
                <span class="fw-semibold text-primary">
                  ₱{{ formatCurrency(order.total_amount) }}
                </span>
              </td>
              <td>
                <span
                  :class="getStatusBadgeClass(order.order_status)"
                  class="badge"
                >
                  {{ formatStatus(order.order_status) }}
                </span>
              </td>
              <td>
                <span
                  :class="getPaymentBadgeClass(order.payment_status)"
                  class="badge"
                >
                  {{ formatPaymentStatus(order.payment_status) }}
                </span>
              </td>
              <td>
                <span class="text-secondary small">
                  {{ formatDate(order.created_at) }}
                </span>
              </td>
              <td class="text-center">
                <button
                  @click.stop="viewOrderDetails(order)"
                  class="btn btn-sm btn-outline-primary"
                  title="View Details"
                >
                  👁️
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination-container p-3 border-top">
        <nav aria-label="Orders pagination">
          <ul class="pagination pagination-sm justify-content-center mb-0">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <button
                class="page-link"
                @click="changePage(currentPage - 1)"
                :disabled="currentPage === 1"
              >
                Previous
              </button>
            </li>
            <li
              v-for="page in displayedPages"
              :key="page"
              class="page-item"
              :class="{ active: currentPage === page }"
            >
              <button class="page-link" @click="changePage(page)">
                {{ page }}
              </button>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <button
                class="page-link"
                @click="changePage(currentPage + 1)"
                :disabled="currentPage === totalPages"
              >
                Next
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-if="!hasOrders && !isLoading && !error"
      class="empty-state text-center py-5 surface-card rounded shadow-sm"
    >
      <div class="empty-icon mb-3">📦</div>
      <h4 class="text-primary">No Orders Found</h4>
      <p class="text-secondary">There are no online orders to display.</p>
      <p class="text-secondary small">Orders will appear here when customers place them.</p>
    </div>

    <!-- Order Details Modal -->
    <OrderDetailsModal
      ref="orderModal"
      :orderId="selectedOrderId"
      @close="handleModalClose"
      @updated="handleOrderUpdated"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useOnlineOrders } from '@/composables/api/useOnlineOrders.js'
import OrderDetailsModal from '@/components/orders/OrderDetailsModal.vue'

// =====================
// COMPOSABLE HOOKS
// =====================
const {
  orders,
  isLoading,
  error,
  hasOrders,
  pendingOrders,
  processingOrders,
  completedOrders,
  cancelledOrders,
  fetchOrders
} = useOnlineOrders()

// =====================
// REACTIVE STATE
// =====================
const orderModal = ref(null)
const selectedOrderId = ref(null)

const currentPage = ref(1)
const itemsPerPage = ref(10)

const filters = ref({
  status: '',
  payment_status: '',
  customer_id: ''
})

// Auto-refresh timer
const autoRefreshTimer = ref(null)

// =====================
// COMPUTED PROPERTIES
// =====================
const filteredOrders = computed(() => {
  let filtered = [...orders.value]

  // Apply status filter
  if (filters.value.status) {
    filtered = filtered.filter(order => order.order_status === filters.value.status)
  }

  // Apply payment status filter
  if (filters.value.payment_status) {
    filtered = filtered.filter(order => order.payment_status === filters.value.payment_status)
  }

  // Apply customer ID filter
  if (filters.value.customer_id) {
    const searchTerm = filters.value.customer_id.toLowerCase()
    filtered = filtered.filter(order => 
      order.customer_id.toLowerCase().includes(searchTerm)
    )
  }

  // Sort by date (newest first)
  return filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const paginatedOrders = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredOrders.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredOrders.value.length / itemsPerPage.value)
})

const displayedPages = computed(() => {
  const pages = []
  const maxPages = 5
  let startPage = Math.max(1, currentPage.value - Math.floor(maxPages / 2))
  let endPage = Math.min(totalPages.value, startPage + maxPages - 1)

  if (endPage - startPage < maxPages - 1) {
    startPage = Math.max(1, endPage - maxPages + 1)
  }

  for (let i = startPage; i <= endPage; i++) {
    pages.push(i)
  }

  return pages
})

// =====================
// METHODS
// =====================
const refreshOrders = async () => {
  await fetchOrders(filters.value)
}

const handleFilterChange = async () => {
  currentPage.value = 1
  await refreshOrders()
}

const clearFilters = async () => {
  filters.value = {
    status: '',
    payment_status: '',
    customer_id: ''
  }
  currentPage.value = 1
  await refreshOrders()
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const viewOrderDetails = (order) => {
  selectedOrderId.value = order.order_id
  orderModal.value?.openModal(order.order_id)
}

const handleModalClose = () => {
  selectedOrderId.value = null
}

const handleOrderUpdated = async () => {
  // Refresh orders list after update
  await refreshOrders()
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    return new Date(dateString).toLocaleString('en-US', {
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
    'ready': 'Ready',
    'out_for_delivery': 'Delivering',
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

const getPaymentBadgeClass = (status) => {
  const classMap = {
    'pending': 'bg-warning text-dark',
    'paid': 'bg-success text-white',
    'failed': 'bg-danger text-white',
    'refunded': 'bg-info text-white'
  }
  return classMap[status] || 'bg-secondary text-white'
}

const setupAutoRefresh = () => {
  // Auto-refresh every 30 seconds
  autoRefreshTimer.value = setInterval(() => {
    console.log('🔄 Auto-refreshing orders...')
    refreshOrders()
  }, 30000)
}

const clearAutoRefresh = () => {
  if (autoRefreshTimer.value) {
    clearInterval(autoRefreshTimer.value)
    autoRefreshTimer.value = null
  }
}

// =====================
// LIFECYCLE
// =====================
onMounted(async () => {
  await refreshOrders()
  setupAutoRefresh()
})

// Cleanup on unmount
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', clearAutoRefresh)
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: var(--surface-primary, #f9fafb);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary, #6b7280);
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary, #111827);
  margin: 0;
}

.filters-section {
  background: var(--surface-card, #ffffff);
}

.table-container {
  background: var(--surface-card, #ffffff);
  overflow: hidden;
}

.table {
  margin-bottom: 0;
}

.table thead th {
  background: var(--surface-secondary, #f3f4f6);
  color: var(--text-primary, #111827);
  font-weight: 600;
  font-size: 0.9rem;
  border-bottom: 2px solid var(--border-color, #e5e7eb);
  padding: 0.75rem;
}

.table tbody tr {
  cursor: pointer;
  transition: background-color 0.2s;
}

.table tbody tr:hover {
  background-color: var(--surface-hover, #f9fafb);
}

.table tbody td {
  padding: 0.75rem;
  vertical-align: middle;
  border-bottom: 1px solid var(--border-subtle, #f3f4f6);
}

.badge {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 0.375rem;
}

.font-monospace {
  font-family: 'Courier New', monospace;
}

.cursor-pointer {
  cursor: pointer;
}

.empty-state {
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 4rem;
  opacity: 0.5;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}

.pagination-container {
  background: var(--surface-secondary, #f9fafb);
}

@media (max-width: 768px) {
  .stat-card {
    flex-direction: column;
    text-align: center;
  }

  .table-responsive {
    font-size: 0.85rem;
  }

  .badge {
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
  }
}
</style>

