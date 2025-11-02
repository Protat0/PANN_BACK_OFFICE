<template>
  <div class="overview-container">
    <!-- Loading State -->
    <div v-if="isLoading && !currentProduct" class="text-center py-5" style="grid-column: 1 / -1;">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-tertiary-medium mt-2">Loading product details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage && !currentProduct" class="alert alert-danger" role="alert" style="grid-column: 1 / -1;">
      <strong>Error:</strong> {{ errorMessage }}
      <button @click="retryLoad" class="btn btn-sm btn-primary ms-3">Retry</button>
    </div>

    <!-- Content -->
    <template v-else-if="currentProduct">
      <!-- Left Column - Product Details (2/3 width) -->
      <div class="details-column">
        <!-- Primary Details -->
        <div class="card-theme p-4">
          <h3 class="text-primary mb-3">Primary Details</h3>
          
          <div class="row mb-3">
            <div class="col-6">
              <div class="mb-2">
                <small class="text-tertiary d-block">Product Name</small>
                <span class="text-secondary">{{ currentProduct.product_name }}</span>
              </div>
            </div>
            <div class="col-6">
              <div class="mb-2">
                <small class="text-tertiary d-block">SKU</small>
                <span class="text-secondary">{{ currentProduct.SKU || 'N/A' }}</span>
              </div>
            </div>
          </div>
          
          <div class="row mb-3">
            <div class="col-6">
              <div class="mb-2">
                <small class="text-tertiary d-block">Category</small>
                <span class="text-secondary">{{ categoryName }}</span>
              </div>
            </div>
            <div class="col-6">
              <div class="mb-2">
                <small class="text-tertiary d-block">Subcategory</small>
                <span class="text-secondary">{{ currentProduct.subcategory_name || 'General' }}</span>
              </div>
            </div>
          </div>
          
          <div class="row mb-3">
            <div class="col-6">
              <div class="mb-2">
                <small class="text-tertiary d-block">Threshold Value</small>
                <span class="text-secondary">{{ currentProduct.low_stock_threshold || 0 }}</span>
              </div>
            </div>
            <div class="col-6">
              <div class="mb-2">
                <small class="text-tertiary d-block">Expiry Date</small>
                <span class="text-secondary">{{ formatDate(nearestExpiryDate) }}</span>
              </div>
            </div>
          </div>
          
          <div class="row">
            <div class="col-6">
              <div class="mb-2">
                <small class="text-tertiary d-block">Created</small>
                <span class="text-secondary">{{ formatDate(currentProduct.createdAt) }}</span>
              </div>
            </div>
            <div class="col-6">
              <div class="mb-2">
                <small class="text-tertiary d-block">Status</small>
                <span :class="getStatusBadgeClass(currentProduct.status)">
                  {{ formatStatus(currentProduct.status) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Supplier Details -->
        <div class="card-theme p-4">
          <h3 class="text-primary mb-3">Supplier Details</h3>
          
          <div class="row">
            <div class="col-6">
              <div class="mb-2">
                <small class="text-tertiary d-block">Supplier Name</small>
                <span class="text-secondary">{{ supplierName }}</span>
              </div>
            </div>
            <div class="col-6">
              <div class="mb-2">
                <small class="text-tertiary d-block">Barcode</small>
                <span class="text-secondary">{{ currentProduct.barcode || 'No barcode' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Image & Stock Info (1/3 width) -->
      <div class="sidebar-column">
        <!-- Product Image -->
        <div class="card-theme p-3 text-center">
          <div v-if="currentProduct.image" class="image-wrapper">
            <img 
              :src="currentProduct.image" 
              :alt="currentProduct.product_name"
              class="product-image"
            />
          </div>
          <div v-else class="image-placeholder">
            <Package :size="48" class="opacity-50" />
            <p class="text-tertiary-medium mt-2 mb-0">{{ currentProduct.product_name }}</p>
          </div>
          <button 
            class="btn btn-sm btn-outline-primary mt-3 w-100"
            @click="$emit('change-image')"
          >
            Change Image
          </button>
        </div>

        <!-- Stock Information -->
        <div class="card-theme p-4 position-relative">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="text-primary mb-0">Stock Information</h5>
            <button 
              class="btn btn-sm btn-edit"
              @click="$emit('adjust-stock')"
              title="Adjust Stock"
            >
              Adjust Stock
            </button>
          </div>
          
          <div class="d-flex justify-content-between align-items-center mb-2">
            <small class="text-tertiary">Current Stock</small>
            <span :class="getStockClass(currentStock)" class="fw-semibold fs-5">
              {{ currentStock }}
            </span>
          </div>
          
          <div class="d-flex justify-content-between align-items-center mb-2">
            <small class="text-tertiary">Low Stock Threshold</small>
            <span class="text-secondary fw-semibold">{{ currentProduct.low_stock_threshold || 10 }}</span>
          </div>
          
          <div class="d-flex justify-content-between align-items-center mb-2">
            <small class="text-tertiary">Cost Price</small>
            <span class="text-secondary fw-semibold">₱{{ formatPrice(averageCostPrice) }}</span>
          </div>
          
          <div class="d-flex justify-content-between align-items-center mb-2">
            <small class="text-tertiary">Selling Price</small>
            <div class="d-flex flex-column align-items-end">
              <span v-if="hasActivePromotion" class="text-tertiary text-decoration-line-through small">
                ₱{{ formatPrice(currentProduct.selling_price) }}
              </span>
              <span class="text-secondary fw-semibold">₱{{ formatPrice(effectiveSellingPrice) }}</span>
            </div>
          </div>
          
          <!-- Active Promotion Badge -->
          <div v-if="hasActivePromotion" class="promotion-badge mb-2">
            <CheckCircle :size="14" class="me-1" />
            {{ activePromotion.name }}
          </div>
          
          <div class="d-flex justify-content-between align-items-center mb-2">
            <small class="text-tertiary">Profit Margin</small>
            <span :class="profitMarginClass" class="fw-semibold">
              {{ profitMargin }}%
            </span>
          </div>
          
          <div class="d-flex justify-content-between align-items-center">
            <small class="text-tertiary">Unit Type</small>
            <span class="text-accent fw-semibold">{{ currentProduct.unit || 'bottle' }}</span>
          </div>

          <!-- Stock Alert -->
          <div v-if="isLowStock" class="alert alert-warning mt-3 mb-0 py-2">
            <div class="d-flex align-items-center">
              <AlertTriangle :size="16" class="me-2" />
              <small>Low stock alert!</small>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- No Product Found -->
    <div v-else class="text-center py-5" style="grid-column: 1 / -1;">
      <Package :size="64" class="opacity-50 mb-3" />
      <h5 class="text-tertiary">Product not found</h5>
      <p class="text-tertiary-medium">The requested product could not be loaded.</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useProducts } from '@/composables/api/useProducts.js'
import { useBatches } from '@/composables/api/useBatches.js'
import { useCategories } from '@/composables/api/useCategories.js'
import { Package, CheckCircle, AlertTriangle } from 'lucide-vue-next'

export default {
  name: 'ProductOverview',
  components: {
    Package,
    CheckCircle,
    AlertTriangle
  },
  props: {
    productId: {
      type: String,
      required: true
    }
  },
  emits: ['adjust-stock', 'change-image', 'reorder', 'view-history'],
  setup(props) {
    // ================ COMPOSABLES ================
    
    const { 
      currentProduct,
      loading: productLoading,
      error: productError,
      fetchProductById
    } = useProducts()
    
    const {
      batches,
      loading: batchLoading,
      error: batchError,
      fetchBatchesByProduct
    } = useBatches()
    
    const {
      currentCategory,
      fetchCategoryById
    } = useCategories()
    
    // ================ LOCAL STATE ================
    
    const activePromotion = ref(null)
    const isInitialized = ref(false)
    
    // ================ COMPUTED - LOADING & ERRORS ================
    
    const isLoading = computed(() => 
      productLoading.value || batchLoading.value
    )
    
    const errorMessage = computed(() => {
      if (productError.value && !productError.value.includes('aborted')) {
        return productError.value
      }
      if (batchError.value && !batchError.value.includes('aborted')) {
        return batchError.value
      }
      return null
    })
    
    // ================ COMPUTED - STOCK CALCULATIONS ================
    
    const currentStock = computed(() => {
      const activeBatches = batches.value.filter(batch => batch.status === 'active')
      return activeBatches.reduce((sum, batch) => sum + (batch.quantity_remaining || 0), 0)
    })
    
    // ================ COMPUTED - PRICING ================
    
    const averageCostPrice = computed(() => {
      const activeBatches = batches.value.filter(b => b.status === 'active')
      
      if (activeBatches.length === 0 || currentStock.value === 0) {
        const sortedBatches = [...batches.value].sort((a, b) => 
          new Date(b.date_received) - new Date(a.date_received)
        )
        return sortedBatches[0]?.cost_price || currentProduct.value?.cost_price || 0
      }
      
      const totalCost = activeBatches.reduce((sum, batch) => {
        return sum + ((batch.cost_price || 0) * (batch.quantity_remaining || 0))
      }, 0)
      
      return totalCost / currentStock.value
    })
    
    const hasActivePromotion = computed(() => activePromotion.value !== null)
    
    const effectiveSellingPrice = computed(() => {
      const basePrice = currentProduct.value?.selling_price || 0
      
      if (hasActivePromotion.value && activePromotion.value.discount_percentage) {
        const discount = (basePrice * activePromotion.value.discount_percentage) / 100
        return basePrice - discount
      }
      
      return basePrice
    })
    
    const profitMargin = computed(() => {
      if (averageCostPrice.value === 0 || effectiveSellingPrice.value === 0) {
        return '0.00'
      }
      
      const profit = effectiveSellingPrice.value - averageCostPrice.value
      const margin = (profit / effectiveSellingPrice.value) * 100
      
      return margin.toFixed(2)
    })
    
    const profitMarginClass = computed(() => {
      const margin = parseFloat(profitMargin.value)
      if (margin < 0) return 'text-error'
      if (margin < 10) return 'text-warning'
      return 'text-success'
    })
    
    // ================ COMPUTED - BATCH INFO ================
    
    const nearestExpiryDate = computed(() => {
      const activeBatches = batches.value.filter(b => 
        b.status === 'active' && b.expiry_date
      )
      
      if (activeBatches.length === 0) return null
      
      const sorted = [...activeBatches].sort((a, b) => 
        new Date(a.expiry_date) - new Date(b.expiry_date)
      )
      
      return sorted[0]?.expiry_date
    })
    
    // ================ COMPUTED - SUPPLIER INFO ================
    
    const supplierName = computed(() => {
      if (batches.value.length === 0) return 'No supplier specified'
      
      const sorted = [...batches.value].sort((a, b) => 
        new Date(b.date_received) - new Date(a.date_received)
      )
      
      const supplier = sorted[0]?.supplier_id
      return supplier?.supplier_name || 'No supplier specified'
    })
    
    // ================ COMPUTED - CATEGORY INFO ================
    
    const categoryName = computed(() => {
      if (!currentProduct.value?.category_id) return 'Uncategorized'
      return currentCategory.value?.category_name || currentProduct.value.category_id
    })
    
    // ================ COMPUTED - STATUS CHECKS ================
    
    const isLowStock = computed(() => {
      const threshold = currentProduct.value?.low_stock_threshold || 0
      return currentStock.value > 0 && currentStock.value <= threshold
    })
    
    // ================ METHODS - FORMATTING ================
    
    const formatPrice = (price) => {
      return parseFloat(price || 0).toFixed(2)
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
    
    const formatStatus = (status) => {
      if (!status) return 'Unknown'
      return status.charAt(0).toUpperCase() + status.slice(1)
    }
    
    // ================ METHODS - STYLING ================
    
    const getStatusBadgeClass = (status) => {
      const statusClasses = {
        'active': 'badge bg-success',
        'inactive': 'badge bg-secondary',
        'discontinued': 'badge bg-danger'
      }
      return statusClasses[status] || 'badge bg-secondary'
    }
    
    const getStockClass = (stock) => {
      const threshold = currentProduct.value?.low_stock_threshold || 0
      
      if (stock === 0) return 'text-error'
      if (stock <= threshold) return 'text-warning'
      return 'text-success'
    }
    
    // ================ METHODS - DATA LOADING ================
    
    const loadProductData = async () => {
      if (!props.productId || isInitialized.value) return
      
      try {
        const [productResult, batchesResult] = await Promise.allSettled([
          fetchProductById(props.productId),
          fetchBatchesByProduct(props.productId)
        ])
        
        if (currentProduct.value?.category_id) {
          fetchCategoryById(currentProduct.value.category_id).catch(() => {
            // Silently handle category fetch errors
          })
        }
        
        checkActivePromotions()
        isInitialized.value = true
      } catch (err) {
        // Error is handled by composables and displayed via errorMessage computed
      }
    }
    
    const retryLoad = () => {
      isInitialized.value = false
      loadProductData()
    }
    
    const checkActivePromotions = () => {
      activePromotion.value = currentProduct.value?.active_promotion || null
    }
    
    // ================ LIFECYCLE ================
    
    let productIdWatcher = null
    
    onMounted(() => {
      if (props.productId) {
        loadProductData()
      }
    })
    
    onBeforeUnmount(() => {
      if (productIdWatcher) {
        productIdWatcher()
      }
    })
    
    productIdWatcher = watch(
      () => props.productId,
      (newId, oldId) => {
        if (newId && newId !== oldId) {
          isInitialized.value = false
          loadProductData()
        }
      }
    )
    
    return {
      // State
      currentProduct,
      batches,
      currentCategory,
      activePromotion,
      
      // Loading & Errors
      isLoading,
      errorMessage,
      
      // Stock
      currentStock,
      
      // Pricing
      averageCostPrice,
      effectiveSellingPrice,
      profitMargin,
      profitMarginClass,
      hasActivePromotion,
      
      // Batch Info
      nearestExpiryDate,
      
      // Supplier
      supplierName,
      
      // Category
      categoryName,
      
      // Status
      isLowStock,
      
      // Methods
      formatPrice,
      formatDate,
      formatStatus,
      getStatusBadgeClass,
      getStockClass,
      retryLoad
    }
  }
}
</script>

<style scoped>
.overview-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  max-width: 1400px;
}

.details-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sidebar-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Image Styles */
.image-wrapper {
  width: 100%;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--surface-secondary);
  border-radius: 0.5rem;
  overflow: hidden;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 0.5rem;
}

.image-placeholder {
  width: 100%;
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: var(--surface-secondary);
  border: 2px dashed var(--border-primary);
  border-radius: 0.5rem;
  color: var(--text-tertiary);
  padding: 1rem;
}

/* Promotion Badge */
.promotion-badge {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  background-color: var(--success-light);
  color: var(--success-dark);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .overview-container {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

@media (max-width: 768px) {
  .overview-container {
    gap: 1rem;
  }
  
  .details-column,
  .sidebar-column {
    gap: 1rem;
  }
  
  .row > .col-6 {
    flex: 0 0 100%;
    max-width: 100%;
  }
}

/* Utility Classes */
.opacity-50 {
  opacity: 0.5;
}

.fs-5 {
  font-size: 1.25rem;
}
</style>