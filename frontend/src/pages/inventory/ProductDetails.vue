<template>
  <div class="flex h-screen surface-secondary">
    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center h-full">
        <div class="text-center">
          <div class="spinner-border text-accent" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-3 text-tertiary-medium">Loading product details...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="flex items-center justify-center h-full">
        <div class="text-center">
          <div class="text-6xl mb-4">❌</div>
          <h2 class="text-2xl font-bold mb-2 text-error">Error Loading Product</h2>
          <p class="text-tertiary-medium">{{ error }}</p>
          <button 
            @click="initializeData" 
            class="mt-4 btn btn-submit"
          >
            Try Again
          </button>
        </div>
      </div>

      <!-- Product Not Found State -->
      <div v-else-if="!currentProduct || !currentProduct._id" class="flex items-center justify-center h-full">
        <div class="text-center">
          <div class="text-6xl mb-4">📦</div>
          <h2 class="text-2xl font-bold mb-2 text-primary">Product Not Found</h2>
          <p class="text-tertiary-medium">The product with ID "{{ id }}" could not be found.</p>
          <button 
            @click="router.push('/products')" 
            class="mt-4 btn btn-submit"
          >
            Back to Products
          </button>
        </div>
      </div>

      <!-- Product Content - Only show when we have a valid product -->
      <div v-else-if="currentProduct._id" class="h-full">
        <!-- Success Message -->
        <div v-if="successMessage" class="mx-6 mt-4 status-success rounded-md">
          {{ successMessage }}
        </div>

        <!-- Header -->
        <header class="surface-primary px-6 py-3 border-bottom-theme">
          <!-- Breadcrumb Navigation -->
          <nav class="breadcrumb-nav">
            <router-link to="/products" class="breadcrumb-link">Inventory</router-link>
            <ChevronRight :size="12" class="breadcrumb-icon" />
            <router-link to="/products" class="breadcrumb-link">Products</router-link>
            <ChevronRight :size="12" class="breadcrumb-icon" />
            <span class="breadcrumb-current">Product Details</span>
          </nav>

          <!-- Product Header -->
          <div class="product-header">
            <div class="product-info">
              <h1 class="product-title text-primary">{{ currentProduct.product_name || 'Product Name' }}</h1>
              <div class="description-and-buttons">
                <p class="product-description text-tertiary-medium">{{ currentProduct.description || 'Product description not available.' }}</p>
                <div class="button-group">
                  <button @click="handleDelete" class="btn btn-delete btn-sm">Delete</button>
                  <button @click="handleEdit" class="btn btn-edit btn-sm">Edit</button>
                  <button @click="handleExport" class="btn btn-export btn-sm">Export</button>
                </div>
              </div>
            </div>
          </div>
        </header>

        <!-- Tab Navigation -->
        <div class="surface-primary px-6">
          <nav class="d-flex border-bottom-theme">
            <button
              v-for="tab in tabs"
              :key="tab"
              @click="setActiveTab(tab)"
              class="tab-button"
              :class="{ 'tab-active': activeTab === tab }"
            >
              {{ tab }}
            </button>
          </nav>
        </div>

        <!-- Content Area -->
        <div class="flex-1 overflow-auto p-6 surface-secondary">
          <!-- Overview Tab -->
          <div v-if="activeTab === 'Overview'" class="row g-4">
            <!-- Left Column - Product Details -->
            <div class="col-lg-8">
              <!-- Primary Details Card -->
              <div class="card-theme p-4 mb-4">
                <h3 class="text-primary mb-3">Primary Details</h3>
                
                <div class="row mb-3">
                  <div class="col-6">
                    <small class="text-tertiary-medium d-block">Product Name</small>
                    <span class="text-secondary">{{ currentProduct.product_name || 'N/A' }}</span>
                  </div>
                  <div class="col-6">
                    <small class="text-tertiary-medium d-block">SKU</small>
                    <span class="text-secondary">{{ currentProduct.SKU || 'N/A' }}</span>
                  </div>
                </div>
                
                <div class="row mb-3">
                  <div class="col-6">
                    <small class="text-tertiary-medium d-block">Category</small>
                    <span class="text-secondary">{{ getCategoryDisplayName(currentProduct.category_id) }}</span>
                  </div>
                  <div class="col-6">
                    <small class="text-tertiary-medium d-block">Subcategory</small>
                    <span class="text-secondary">{{ currentProduct.subcategory_name || 'General' }}</span>
                  </div>
                </div>
                
                <div class="row mb-3">
                  <div class="col-6">
                    <small class="text-tertiary-medium d-block">Threshold Value</small>
                    <span class="text-secondary">{{ currentProduct.low_stock_threshold || 0 }}</span>
                  </div>
                  <div class="col-6">
                    <small class="text-tertiary-medium d-block">Expiry Date</small>
                    <span class="text-secondary">{{ formatDate(currentProduct.expiry_date) }}</span>
                  </div>
                </div>

                <div class="row">
                  <div class="col-6">
                    <small class="text-tertiary-medium d-block">Status</small>
                    <span :class="currentProduct.status === 'active' ? 'badge bg-success' : 'badge bg-secondary'">
                      {{ currentProduct.status || 'active' }}
                    </span>
                  </div>
                  <div class="col-6">
                    <small class="text-tertiary-medium d-block">Created</small>
                    <span class="text-secondary">{{ formatDate(currentProduct.created_at) }}</span>
                  </div>
                </div>
              </div>

              <!-- Supplier Details Card -->
              <div class="card-theme p-4">
                <h3 class="text-primary mb-3">Supplier Details</h3>
                
                <div class="row">
                  <div class="col-6">
                    <small class="text-tertiary-medium d-block">Supplier Name</small>
                    <span class="text-secondary">{{ currentProduct.supplier || 'No supplier specified' }}</span>
                  </div>
                  <div class="col-6">
                    <small class="text-tertiary-medium d-block">Barcode</small>
                    <span class="text-secondary">{{ currentProduct.barcode || 'No barcode' }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Right Column - Image and Stock -->
            <div class="col-lg-4">
              <!-- Product Image Card -->
              <div class="card-theme p-3 mb-4">
                <img 
                  :src="currentProduct.image_url || 'https://via.placeholder.com/300x200?text=No+Image'" 
                  :alt="currentProduct.product_name" 
                  class="img-fluid rounded"
                  style="width: 100%; height: 200px; object-fit: cover;"
                />
                <div class="text-center mt-2">
                  <button @click="handleImageUpload" class="btn btn-filter btn-sm">
                    Change Image
                  </button>
                </div>
              </div>

              <!-- Stock Information Card -->
              <div class="card-theme p-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h5 class="text-primary mb-0">Stock Information</h5>
                  <button @click="handleStockAdjustment" class="btn btn-edit btn-sm">
                    Adjust Stock
                  </button>
                </div>
                
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <small class="text-tertiary-medium">Current Stock</small>
                  <span :class="getStockClass(currentProduct)" class="fw-semibold">
                    {{ currentProduct.stock || 0 }}
                  </span>
                </div>
                
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <small class="text-tertiary-medium">Low Stock Threshold</small>
                  <span class="text-secondary fw-semibold">{{ currentProduct.low_stock_threshold || 0 }}</span>
                </div>
                
                <div class="divider-theme my-3"></div>
                
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <small class="text-tertiary-medium">Cost Price</small>
                  <span class="text-secondary fw-semibold">₱{{ formatPrice(currentProduct.cost_price) }}</span>
                </div>
                
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <small class="text-tertiary-medium">Selling Price</small>
                  <span class="text-secondary fw-semibold">₱{{ formatPrice(currentProduct.selling_price) }}</span>
                </div>

                <div class="d-flex justify-content-between align-items-center mb-2">
                  <small class="text-tertiary-medium">Profit Margin</small>
                  <span :class="getMarginClass(currentProduct)" class="fw-semibold">
                    {{ calculateMargin(currentProduct) }}%
                  </span>
                </div>
                
                <div class="d-flex justify-content-between align-items-center">
                  <small class="text-tertiary-medium">Unit Type</small>
                  <span class="text-accent fw-semibold">{{ currentProduct.unit || 'piece' }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Other Tabs -->
          <div v-else-if="activeTab === 'Purchases'">
            <ProductPurchases :product-id="id" />
          </div>

          <div v-else-if="activeTab === 'Adjustments'">
            <ProductAdjustments :product-id="id" />
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <AddProductModal
      ref="addProductModal"
      :categories="activeCategories"
      @success="handleModalSuccess"
    />

    <StockUpdateModal
      ref="stockUpdateModal"
      @success="handleModalSuccess"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useProducts } from '@/composables/api/useProducts'
import { useCategories } from '@/composables/api/useCategories'
import AddProductModal from '@/components/products/AddProductModal.vue'
import StockUpdateModal from '@/components/products/StockUpdateModal.vue'
import ProductPurchases from '@/components/products/ProductPurchases.vue'
import ProductAdjustments from '@/components/products/ProductAdjustments.vue'

export default {
  name: 'ProductDetails',
  components: {
    AddProductModal,
    StockUpdateModal,
    ProductPurchases,
    ProductAdjustments 
  },
  props: {
    id: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const router = useRouter()
    
    // Template refs
    const addProductModal = ref(null)
    const stockUpdateModal = ref(null)
    
    // Use composables
    const {
      currentProduct,
      loading,
      error,
      fetchProductById,
      updateProduct,
      deleteProduct,
      exportProducts
    } = useProducts()

    const {
      activeCategories,
      initializeCategories
    } = useCategories()

    // Local state
    const activeTab = ref('Overview')
    const tabs = ['Overview', 'Purchases', 'Adjustments']
    const successMessage = ref('')

    // Utility functions
    const formatDate = (date) => {
      if (!date) return 'Not set'
      return new Date(date).toLocaleDateString()
    }

    const formatPrice = (price) => {
      return parseFloat(price || 0).toFixed(2)
    }

    const getCategoryDisplayName = (categoryId) => {
      if (!categoryId) return 'Uncategorized'
      const category = activeCategories.value.find(c => c._id === categoryId)
      return category?.category_name || 'Unknown Category'
    }

    const getStockClass = (product) => {
      if (product.stock === 0) return 'text-error'
      if (product.stock <= (product.low_stock_threshold || 15)) return 'text-warning'
      return 'text-success'
    }

    const getMarginClass = (product) => {
      const margin = calculateMargin(product)
      if (margin >= 40) return 'text-success'
      if (margin >= 20) return 'text-warning'
      return 'text-error'
    }

    const calculateMargin = (product) => {
      const { cost_price, selling_price } = product
      if (!cost_price || !selling_price || cost_price >= selling_price) return 0
      return Math.round(((selling_price - cost_price) / selling_price) * 100)
    }

    // Methods
    const handleEdit = () => {
      if (currentProduct.value && currentProduct.value._id) {
        addProductModal.value?.openEdit?.(currentProduct.value)
      }
    }

    const handleStockAdjustment = () => {
      if (currentProduct.value && currentProduct.value._id) {
        stockUpdateModal.value?.openStock?.(currentProduct.value)
      }
    }

    const handleImageUpload = () => {
      if (currentProduct.value && currentProduct.value._id) {
        addProductModal.value?.openEdit?.(currentProduct.value)
      }
    }

    const handleDelete = async () => {
      if (!currentProduct.value || !currentProduct.value.product_name) {
        return
      }
      
      const confirmed = confirm(`Are you sure you want to delete "${currentProduct.value.product_name}"?`)
      if (confirmed) {
        try {
          await deleteProduct(currentProduct.value._id)
          router.push('/products')
        } catch (err) {
          console.error('Error deleting product:', err)
        }
      }
    }

    const handleExport = async () => {
      try {
        // Export single product
        const filters = { _id: currentProduct.value._id }
        await exportProducts(filters)
      } catch (err) {
        console.error('Error exporting:', err)
      }
    }

    const handleModalSuccess = async (result) => {
      if (result?.message) {
        successMessage.value = result.message
        setTimeout(() => {
          successMessage.value = ''
        }, 3000)
      }
      // Refresh the current product
      await fetchProductById(props.id)
    }

    const setActiveTab = (tab) => {
      activeTab.value = tab
    }

    // Initialize data
    const initializeData = async () => {
      try {
        await Promise.all([
          initializeCategories(),
          fetchProductById(props.id)
        ])
      } catch (err) {
        console.error('Failed to initialize data:', err)
      }
    }

    onMounted(() => {
      initializeData()
    })

    return {
      // State
      loading,
      error,
      successMessage,
      currentProduct,
      activeTab,
      tabs,
      router,
      activeCategories,
      
      // Template refs
      addProductModal,
      stockUpdateModal,
      
      // Methods
      setActiveTab,
      handleDelete,
      handleEdit,
      handleStockAdjustment,
      handleImageUpload,
      handleExport,
      handleModalSuccess,
      initializeData,
      formatDate,
      formatPrice,
      getCategoryDisplayName,
      getStockClass,
      getMarginClass,
      calculateMargin
    }
  }
}
</script>

<style scoped>
/* Breadcrumb Navigation Styles */
.breadcrumb-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 12px;
  line-height: 1;
}

.breadcrumb-link {
  color: var(--text-accent);
  font-size: 12px;
  font-weight: 500;
  text-decoration: none;
  transition: opacity 0.2s ease;
}

.breadcrumb-link:hover {
  opacity: 0.8;
}

.breadcrumb-current {
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;
}

.breadcrumb-icon {
  color: var(--text-tertiary);
  flex-shrink: 0;
}

/* Product Header Styles */
.product-header {
  width: 100%;
}

.product-info {
  width: 100%;
}

.product-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.description-and-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 20px;
}

.product-description {
  font-size: 0.875rem;
  margin: 0;
  flex: 1;
}

/* Button Group Styles */
.button-group {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-shrink: 0;
}

/* Tab Styles */
.tab-button {
  border: none;
  background: transparent;
  padding: 1rem 0;
  margin-right: 2rem;
  border-bottom: 2px solid transparent;
  color: var(--text-tertiary);
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  cursor: pointer;
}

.tab-button:hover {
  color: var(--text-accent);
}

.tab-button.tab-active {
  color: var(--text-accent);
  border-bottom-color: var(--border-accent);
  font-weight: 600;
}

/* Responsive Design */
@media (max-width: 768px) {
  .description-and-buttons {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .button-group {
    width: 100%;
    justify-content: flex-start;
  }

  .tab-button {
    margin-right: 1rem;
    font-size: 0.8rem;
  }
}
</style>