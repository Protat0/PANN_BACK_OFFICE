<template>
  <div class="modal fade" :class="{ show: show }" :style="{ display: show ? 'block' : 'none' }" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <TrendingUp :size="20" class="me-2 text-success" />
            Top Performing Suppliers
          </h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <div v-else-if="suppliers.length === 0" class="text-center py-4">
            <TrendingUp :size="48" class="text-tertiary-medium mb-3" />
            <p class="text-tertiary-medium">No top performers found</p>
          </div>
          
          <div v-else class="row g-3">
            <div v-for="(supplier, index) in suppliers" :key="supplier.id" class="col-12">
              <div class="card border-start border-success border-3">
                <div class="card-body">
                  <div class="d-flex align-items-center mb-3">
                    <div class="badge bg-success rounded-circle me-3" style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
                      <span class="fw-bold">#{{ index + 1 }}</span>
                    </div>
                    <div class="flex-grow-1">
                      <h6 class="mb-1 fw-bold">{{ supplier.name }}</h6>
                      <p class="text-tertiary-medium mb-0">{{ supplier.email }}</p>
                    </div>
                    <div class="text-end">
                      <div class="d-flex align-items-center mb-1">
                        <Star :size="16" class="text-warning me-1" :fill="supplier.rating !== 'N/A' ? 'currentColor' : 'none'" />
                        <span class="fw-bold">{{ supplier.rating }}</span>
                      </div>
                      <small class="text-tertiary-medium">{{ supplier.onTimeDelivery }}% on-time</small>
                    </div>
                  </div>
                  
                  <div class="row g-3 mb-3">
                    <div class="col-6 col-md-3">
                      <div class="text-center p-2 bg-light rounded">
                        <div class="h5 mb-0 text-success fw-bold">{{ supplier.totalOrders }}</div>
                        <small class="text-tertiary-medium">Total Orders</small>
                      </div>
                    </div>
                    <div class="col-6 col-md-3">
                      <div class="text-center p-2 bg-light rounded">
                        <div class="h5 mb-0 text-success fw-bold">₱{{ formatCurrency(supplier.totalValue) }}</div>
                        <small class="text-tertiary-medium">Total Value</small>
                      </div>
                    </div>
                    <div class="col-6 col-md-3">
                      <div class="text-center p-2 bg-light rounded">
                        <div class="h5 mb-0 text-success fw-bold">₱{{ formatCurrency(supplier.averageOrderValue, 2) }}</div>
                        <small class="text-tertiary-medium">Avg Order</small>
                      </div>
                    </div>
                    <div class="col-6 col-md-3">
                      <div class="text-center p-2 bg-light rounded">
                        <div class="h5 mb-0 text-primary fw-bold">{{ formatDate(supplier.lastOrder) }}</div>
                        <small class="text-tertiary-medium">Last Order</small>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <small class="text-tertiary-medium">Top Products:</small>
                    <div class="mt-1">
                      <span v-for="(product, pIndex) in supplier.topProducts" :key="pIndex" 
                            class="badge bg-light text-dark me-1 mb-1">
                        {{ getProductDisplayName(product) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal Backdrop -->
  <div v-if="show" class="modal-backdrop fade show" @click="$emit('close')"></div>
</template>

<script>
import { TrendingUp, Star } from 'lucide-vue-next'

export default {
  name: 'TopPerformersModal',
  components: {
    TrendingUp,
    Star
  },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    suppliers: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close'],
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      })
    },

    formatCurrency(amount, decimals = 0) {
      return new Intl.NumberFormat('en-PH', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      }).format(amount || 0)
    },

    getProductDisplayName(product) {
      // Product is already the name from batches, but handle edge cases
      // If it looks like an ID (starts with PROD-), try to extract name
      if (product && product.startsWith && product.startsWith('PROD-')) {
        // This means we got an ID instead of name - should not happen with enrichment
        // But keep as fallback
        return product
      }
      // Return the product name as-is (already enriched from batches)
      return product || 'Unknown Product'
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