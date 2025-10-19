<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content modern-modal">
        <!-- Modal Header -->
        <div class="modal-header border-0 pb-0">
          <div class="d-flex align-items-center">
            <div class="modal-icon me-3">
              <Package :size="24" />
            </div>
            <div>
              <h4 class="modal-title mb-1">Receive Pending Stock</h4>
              <p class="text-muted mb-0 small">
                Select pending orders from <strong>{{ supplier?.name }}</strong> to receive
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
          <!-- Loading State -->
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 text-muted">Loading pending stock...</p>
          </div>

          <!-- Pending Stock List -->
          <div v-else-if="pendingBatches.length > 0">
            <div class="alert alert-info mb-4">
              <Clock :size="16" class="me-2" />
              <strong>{{ pendingBatches.length }}</strong> pending batch(es) awaiting receipt
            </div>

            <div class="table-responsive">
              <table class="table table-hover">
                <thead class="table-light">
                  <tr>
                    <th style="width: 40px;">
                      <input 
                        type="checkbox" 
                        class="form-check-input" 
                        v-model="selectAll"
                        @change="toggleSelectAll"
                      >
                    </th>
                    <th>Batch Number</th>
                    <th>Product</th>
                    <th>Order Date</th>
                    <th>Expected Date</th>
                    <th>Quantity</th>
                    <th>Est. Cost</th>
                    <th>Total</th>
                    <th>Days Pending</th>
                  </tr>
                </thead>
                <tbody>
                  <tr 
                    v-for="batch in pendingBatches" 
                    :key="batch._id"
                    :class="{ 'table-warning': isOverdue(batch), 'table-active': selectedBatches.includes(batch._id) }"
                  >
                    <td>
                      <input 
                        type="checkbox" 
                        class="form-check-input" 
                        :value="batch._id"
                        v-model="selectedBatches"
                      >
                    </td>
                    <td>
                      <code class="text-primary">{{ batch.batch_number }}</code>
                    </td>
                    <td>
                      <div>
                        <strong>{{ getProductName(batch) }}</strong>
                        <br>
                        <small class="text-muted">{{ batch.product_id }}</small>
                      </div>
                    </td>
                    <td>{{ formatDate(batch.created_at) }}</td>
                    <td>
                      <div>
                        {{ formatDate(batch.expected_delivery_date) }}
                        <br>
                        <small v-if="isOverdue(batch)" class="text-danger">
                          <AlertTriangle :size="12" class="me-1" />
                          Overdue
                        </small>
                        <small v-else class="text-muted">
                          {{ getDaysUntil(batch.expected_delivery_date) }}
                        </small>
                      </div>
                    </td>
                    <td class="text-center">
                      <span class="badge bg-secondary">{{ batch.quantity_received }}</span>
                    </td>
                    <td>₱{{ formatCurrency(batch.cost_price || 0) }}</td>
                    <td class="fw-bold">₱{{ formatCurrency((batch.cost_price || 0) * batch.quantity_received) }}</td>
                    <td class="text-center">
                      <span class="badge" :class="getDaysPendingClass(batch)">
                        {{ getDaysPending(batch) }} days
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="text-center py-5">
            <Package :size="64" class="text-muted mb-3" />
            <h5 class="text-muted">No Pending Stock</h5>
            <p class="text-muted">All orders from this supplier have been received.</p>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer border-0 pt-4">
          <div class="d-flex justify-content-between align-items-center w-100">
            <div class="text-muted small">
              <span v-if="selectedBatches.length > 0">
                {{ selectedBatches.length }} batch(es) selected
              </span>
            </div>
            
            <div class="d-flex gap-3">
              <button 
                type="button" 
                class="btn btn-outline-secondary px-4"
                @click="handleClose"
              >
                Cancel
              </button>
              <button 
                type="button" 
                class="btn btn-success px-4"
                @click="receiveSelected"
                :disabled="selectedBatches.length === 0 || receiving"
              >
                <div v-if="receiving" class="spinner-border spinner-border-sm me-2"></div>
                <Package :size="16" class="me-1" />
                Receive {{ selectedBatches.length }} Batch(es)
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
  Package,
  Clock,
  AlertTriangle
} from 'lucide-vue-next'
import { useToast } from '@/composables/ui/useToast'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export default {
  name: 'ReceiveStockModal',
  components: {
    Package,
    Clock,
    AlertTriangle
  },
  emits: ['close', 'received'],
  props: {
    show: {
      type: Boolean,
      default: false
    },
    supplier: {
      type: Object,
      required: true
    }
  },
  setup(props, { emit }) {
    const { success: showSuccess, error: showError } = useToast()
    
    const loading = ref(false)
    const receiving = ref(false)
    const pendingBatches = ref([])
    const selectedBatches = ref([])
    const selectAll = ref(false)
    
    // ================ COMPUTED ================
    
    const selectedBatchObjects = computed(() => {
      return pendingBatches.value.filter(batch => selectedBatches.value.includes(batch._id))
    })
    
    // ================ METHODS ================
    
    async function loadPendingBatches() {
      loading.value = true
      
      try {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken')
        
        const response = await axios.get(
          `${API_BASE_URL}/batches/by-supplier/${props.supplier.id}/`,
          {
            params: { status: 'pending' },
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        )
        
        console.log('📦 Raw response:', response.data)
        
        // Handle response structure: {success: true, data: [...]}
        if (response.data.success && response.data.data) {
          pendingBatches.value = response.data.data
        } else if (Array.isArray(response.data)) {
          pendingBatches.value = response.data
        } else {
          pendingBatches.value = []
        }
        
        console.log('📦 Loaded pending batches:', pendingBatches.value.length)
        
        if (pendingBatches.value.length > 0) {
          console.log('📦 Sample batch:', pendingBatches.value[0])
        }
        
      } catch (error) {
        console.error('Error loading pending batches:', error)
        showError('Failed to load pending stock')
      } finally {
        loading.value = false
      }
    }
    
    function toggleSelectAll() {
      if (selectAll.value) {
        selectedBatches.value = pendingBatches.value.map(b => b._id)
      } else {
        selectedBatches.value = []
      }
    }
    
    async function receiveSelected() {
      if (selectedBatches.value.length === 0) return
      
      receiving.value = true
      
      try {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken')
        const results = {
          successful: [],
          failed: []
        }
        
        // Activate each selected batch
        for (const batch of selectedBatchObjects.value) {
          try {
            const response = await axios.post(
              `${API_BASE_URL}/batches/activate/`,
              {
                batch_number: batch.batch_number,
                product_id: batch.product_id,
                supplier_id: props.supplier.id,
                // date_received will be set automatically by backend to current time
                notes: `Received via batch activation on ${new Date().toLocaleDateString()}`
              },
              {
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                }
              }
            )
            
            results.successful.push({
              batch: batch.batch_number,
              product: batch.product_id
            })
            
          } catch (error) {
            console.error('Error activating batch:', batch.batch_number, error)
            results.failed.push({
              batch: batch.batch_number,
              error: error.message
            })
          }
        }
        
        // ✅ Don't show toast here - let parent handle it to avoid duplicates
        // Parent (SupplierDetails) will show the success/error toast
        
        // Emit event
        emit('received', results)
        
        // Close modal
        handleClose()
        
      } catch (error) {
        console.error('Error receiving batches:', error)
        showError('Failed to process stock receipt')
      } finally {
        receiving.value = false
      }
    }
    
    function getProductName(batch) {
      // Try to get product name from batch data
      // Check various possible field names
      if (batch.product_name) return batch.product_name
      if (batch.productName) return batch.productName
      if (batch.product_info && batch.product_info.product_name) return batch.product_info.product_name
      if (batch.product_id) return batch.product_id
      return 'Unknown Product'
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
    
    function isOverdue(batch) {
      if (!batch.expected_delivery_date) return false
      const expectedDate = new Date(batch.expected_delivery_date)
      const today = new Date()
      return expectedDate < today
    }
    
    function getDaysUntil(dateString) {
      if (!dateString) return 'No date set'
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
    }
    
    function getDaysPending(batch) {
      const createdDate = new Date(batch.created_at)
      const today = new Date()
      const diffTime = Math.abs(today - createdDate)
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    }
    
    function getDaysPendingClass(batch) {
      const days = getDaysPending(batch)
      if (days <= 3) return 'bg-success'
      if (days <= 7) return 'bg-warning'
      return 'bg-danger'
    }
    
    function handleClose() {
      emit('close')
      selectedBatches.value = []
      selectAll.value = false
    }
    
    // ================ LIFECYCLE ================
    
    watch(() => props.show, (newVal) => {
      if (newVal) {
        loadPendingBatches()
      }
    })
    
    onMounted(() => {
      if (props.show) {
        loadPendingBatches()
      }
    })
    
    return {
      loading,
      receiving,
      pendingBatches,
      selectedBatches,
      selectAll,
      toggleSelectAll,
      receiveSelected,
      getProductName,
      formatDate,
      formatCurrency,
      isOverdue,
      getDaysUntil,
      getDaysPending,
      getDaysPendingClass,
      handleClose
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

.modal-header {
  padding: 2rem 2rem 1rem 2rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.modal-body {
  padding: 1.5rem 2rem;
  max-height: 65vh;
  overflow-y: auto;
}

.table-hover tbody tr {
  cursor: pointer;
  transition: all 0.2s ease;
}

.table-hover tbody tr:hover {
  background-color: var(--neutral-light);
}

.table-active {
  background-color: rgba(115, 146, 226, 0.1) !important;
}

.table-warning {
  background-color: rgba(255, 193, 7, 0.1) !important;
}

code {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.875rem;
}
</style>
