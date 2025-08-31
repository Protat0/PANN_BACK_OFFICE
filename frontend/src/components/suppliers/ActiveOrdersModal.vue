<template>
  <div class="modal fade" :class="{ show: show }" :style="{ display: show ? 'block' : 'none' }" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <Package :size="20" class="me-2 text-warning" />
            Active Purchase Orders
          </h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <div v-else-if="orders.length === 0" class="text-center py-4">
            <Package :size="48" class="text-tertiary-medium mb-3" />
            <p class="text-tertiary-medium">No active orders found</p>
          </div>
          
          <div v-else class="row g-3">
            <div v-for="order in orders" :key="order.id" class="col-12">
              <div class="card border-start border-warning border-3">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start mb-3">
                    <div>
                      <h6 class="mb-1 fw-bold">{{ order.id }}</h6>
                      <p class="text-tertiary-medium mb-1">{{ order.supplier }}</p>
                      <small class="text-tertiary-medium">Ordered: {{ formatDate(order.orderDate) }}</small>
                    </div>
                    <div class="text-end">
                      <h5 class="mb-1 text-warning fw-bold">₱{{ formatCurrency(order.totalAmount) }}</h5>
                      <span :class="getStatusBadgeClass(order.status)" class="badge">
                        {{ getStatusText(order.status) }}
                      </span>
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <small class="text-tertiary-medium">Expected Delivery:</small>
                    <div class="fw-semibold">{{ formatDate(order.expectedDelivery) }}</div>
                  </div>
                  
                  <div class="border-top pt-2">
                    <small class="text-tertiary-medium">Items ({{ order.items?.length || 0 }}):</small>
                    <div class="mt-1">
                      <div v-for="(item, index) in order.items" :key="index" class="d-flex justify-content-between small">
                        <span>{{ item.name }} ({{ item.quantity }}x)</span>
                        <span>₱{{ formatCurrency(item.quantity * item.unitPrice) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Close</button>
          <button type="button" class="btn btn-warning" @click="handleViewAllOrders">View All Orders</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal Backdrop -->
  <div v-if="show" class="modal-backdrop fade show" @click="$emit('close')"></div>
</template>

<script>
import { Package } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

export default {
  name: 'ActiveOrdersModal',
  components: {
    Package
  },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    orders: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const router = useRouter()

    const handleViewAllOrders = () => {
      // Close the modal first
      emit('close')
      
      // Navigate to the orders history page
      router.push({ name: 'OrdersHistory' })
    }

    return {
      handleViewAllOrders
    }
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      })
    },

    formatCurrency(amount) {
      return new Intl.NumberFormat('en-PH').format(amount)
    },

    getStatusBadgeClass(status) {
      const statusClasses = {
        'pending': 'bg-warning text-dark',
        'confirmed': 'bg-info text-white',
        'in_transit': 'bg-primary text-white',
        'delivered': 'bg-success text-white',
        'cancelled': 'bg-danger text-white'
      }
      return statusClasses[status] || 'bg-secondary text-white'
    },

    getStatusText(status) {
      const statusTexts = {
        'pending': 'Pending',
        'confirmed': 'Confirmed',
        'in_transit': 'In Transit',
        'delivered': 'Delivered',
        'cancelled': 'Cancelled'
      }
      return statusTexts[status] || status
    }
  }
}
</script>

<style scoped>
@import '@/assets/styles/colors.css';

.text-tertiary-medium {
  color: var(--tertiary-medium) !important;
}

/* Modal styling */
.modal-backdrop.show {
  opacity: 0.5;
  background-color: rgba(0, 0, 0, 0.5);
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1040;
}

.modal.show {
  z-index: 1055;
}

.modal.show .modal-dialog {
  transform: none;
}

.modal-content {
  border-radius: 0.75rem;
  border: none;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25);
}

.modal-header {
  border-bottom: 1px solid var(--neutral-light);
  padding: 1.5rem;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  border-top: 1px solid var(--neutral-light);
  padding: 1rem 1.5rem;
}
</style>