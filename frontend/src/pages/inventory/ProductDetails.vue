<template>
  <div class="flex h-screen surface-secondary">
    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center h-full">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-4 border-accent"></div>
          <p class="text-tertiary">Loading product details...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="flex items-center justify-center h-full">
        <div class="text-center">
          <div class="text-6xl mb-4">❌</div>
          <h2 class="text-2xl font-bold mb-2 text-error">Error Loading Product</h2>
          <p class="text-tertiary">{{ error }}</p>
          <button 
            @click="initializeData" 
            class="mt-4 btn btn-submit"
          >
            Try Again
          </button>
        </div>
      </div>

      <!-- Product Not Found State -->
      <div v-else-if="!currentProduct._id" class="flex items-center justify-center h-full">
        <div class="text-center">
          <div class="text-6xl mb-4">📦</div>
          <h2 class="text-2xl font-bold mb-2 text-primary">Product Not Found</h2>
          <p class="text-tertiary">The product with ID "{{ id }}" could not be found.</p>
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
        <header class="surface-primary px-6 py-3" style="border-bottom: 1px solid var(--border-secondary);">
          <!-- Breadcrumb Navigation -->
          <nav class="breadcrumb-nav">
            <router-link to="/products" class="breadcrumb-link">Inventory</router-link>
            <svg class="breadcrumb-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
            <router-link to="/products" class="breadcrumb-link">Products</router-link>
            <svg class="breadcrumb-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
            <span class="breadcrumb-current">Product Details</span>
          </nav>

          <!-- Product Header -->
          <div class="product-header">
            <div class="product-info">
              <h1 class="product-title text-primary">{{ currentProduct.product_name || 'Product Name' }}</h1>
              <div class="description-and-buttons">
                <p class="product-description text-tertiary">{{ currentProduct.description || 'Product description not available.' }}</p>
                <div class="button-group">
                  <button @click="handleDelete" class="btn btn-delete btn-sm">Delete</button>
                  <button @click="handleEdit" class="btn btn-edit btn-sm">Edit</button>
                  <button @click="handleExport" class="btn btn-outline-secondary btn-sm">Export</button>
                </div>
              </div>
            </div>
          </div>
        </header>

        <!-- Tab Navigation -->
        <div class="surface-primary px-6">
          <nav class="d-flex" style="border-bottom: 1px solid var(--border-secondary);">
            <button
              v-for="tab in tabs"
              :key="tab"
              @click="setActiveTab(tab)"
              class="border-0 bg-transparent py-3 px-0 me-4 shadow-none"
              :style="{
                borderBottom: activeTab === tab ? '2px solid var(--text-accent)' : '2px solid transparent',
                color: activeTab === tab ? 'var(--text-accent)' : 'var(--text-tertiary)',
                fontWeight: activeTab === tab ? '600' : '500'
              }"
            >
              {{ tab }}
            </button>
          </nav>
        </div>

        <!-- Content Area -->
        <div class="flex-1 overflow-auto p-6 surface-secondary">
          <!-- Overview Tab -->
        <!-- Overview Tab -->
        <div v-if="activeTab === 'Overview'" class="row g-4">
          <!-- Left Column - Product Details -->
          <div class="col-lg-8">
            <!-- Primary Details Card -->
            <div class="card-theme p-4 mb-4">
              <h3 class="text-primary mb-3">Primary Details</h3>
              
              <div class="row mb-3">
                <div class="col-6">
                  <small class="text-tertiary d-block">Product Name</small>
                  <span class="text-secondary">{{ currentProduct.product_name || 'N/A' }}</span>
                </div>
                <div class="col-6">
                  <small class="text-tertiary d-block">Product ID</small>
                  <span class="text-secondary">{{ currentProduct._id || 'N/A' }}</span>
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-6">
                  <small class="text-tertiary d-block">Product Category</small>
                  <span class="text-secondary">{{ currentProduct.category_name || 'Uncategorized' }}</span>
                </div>
                <div class="col-6">
                  <small class="text-tertiary d-block">Batch Date</small>
                  <span class="text-secondary">{{ currentProduct.batch_date || currentProduct.created_at }}</span>
                </div>
              </div>
              
              <div class="row">
                <div class="col-6">
                  <small class="text-tertiary d-block">Threshold Value</small>
                  <span class="text-secondary">{{ currentProduct.low_stock_threshold || 0 }}</span>
                </div>
                <div class="col-6">
                  <small class="text-tertiary d-block">Expiry Date</small>
                  <span class="text-secondary">{{ currentProduct.expiry_date }}</span>
                </div>
              </div>
            </div>

            <!-- Supplier Details Card -->
            <div class="card-theme p-4">
              <h3 class="text-primary mb-3">Supplier Details</h3>
              
              <div class="row">
                <div class="col-6">
                  <small class="text-tertiary d-block">Supplier Name</small>
                  <span class="text-secondary">{{ currentProduct.supplier_name || 'Unknown Supplier' }}</span>
                </div>
                <div class="col-6">
                  <small class="text-tertiary d-block">Contact Number</small>
                  <span class="text-secondary">{{ currentProduct.supplier_contact || 'N/A' }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Column - Image and Stock -->
          <div class="col-lg-4">
            <!-- Product Image Card -->
            <div class="card-theme p-3 mb-4">
              <img 
                :src="currentProduct.image_url || currentProduct.image || 'https://via.placeholder.com/300x200?text=No+Image'" 
                :alt="currentProduct.product_name" 
                class="img-fluid rounded"
                style="width: 100%; height: 200px; object-fit: cover;"
              />
              <div class="text-center mt-2">
                <button @click="handleImageUpload" class="btn btn-outline-secondary btn-sm">
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
                <small class="text-tertiary">Opening Stock</small>
                <span class="text-secondary fw-semibold">{{ currentProduct.opening_stock || currentProduct.stock || 0 }}</span>
              </div>
              
              <div class="d-flex justify-content-between align-items-center mb-2">
                <small class="text-tertiary">Current Stock</small>
                <span :class="currentProduct.stock === 0 ? 'text-error' : currentProduct.stock <= currentProduct.low_stock_threshold ? 'text-warning' : 'text-success'" class="fw-semibold">
                  {{ currentProduct.stock || 0 }}
                </span>
              </div>
              
              <div class="d-flex justify-content-between align-items-center mb-2">
                <small class="text-tertiary">On the Way</small>
                <span class="text-secondary fw-semibold">{{ currentProduct.on_the_way || 0 }}</span>
              </div>
              
              <div class="d-flex justify-content-between align-items-center mb-3">
                <small class="text-tertiary">Reserved Stock</small>
                <span class="text-secondary fw-semibold">{{ currentProduct.reserved_stock || 0 }}</span>
              </div>
              
              <hr class="border-theme-subtle">
              
              <div class="d-flex justify-content-between align-items-center mb-2">
                <small class="text-tertiary">Cost Price</small>
                <span class="text-secondary fw-semibold">{{ currentProduct.cost_price }}</span>
              </div>
              
              <div class="d-flex justify-content-between align-items-center mb-2">
                <small class="text-tertiary">Selling Price</small>
                <span class="text-secondary fw-semibold">{{ currentProduct.selling_price }}</span>
              </div>
              
              <div class="d-flex justify-content-between align-items-center">
                <small class="text-tertiary">Unit Type</small>
                <span class="text-accent fw-semibold">{{ currentProduct.unit || 'pcs' }}</span>
              </div>
            </div>
          </div>
        </div>

          <!-- Other Tabs -->
          <div v-else-if="activeTab === 'Purchases'" class="card-theme p-6">
            <h2 class="text-xl font-bold mb-6 text-primary">Purchase History</h2>
            <p class="text-tertiary">Purchase history content will be implemented here.</p>
          </div>

          <div v-else-if="activeTab === 'Adjustments'" class="card-theme p-6">
            <h2 class="text-xl font-bold mb-6 text-primary">Stock Adjustments</h2>
            <p class="text-tertiary">Stock adjustments content will be implemented here.</p>
          </div>

          <div v-else-if="activeTab === 'History'" class="card-theme p-6">
            <h2 class="text-xl font-bold mb-6 text-primary">Product History</h2>
            <p class="text-tertiary">Product history content will be implemented here.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <AddProductModal
      ref="addProductModal"
      :categories="categories"
      @success="handleModalSuccess"
    />

    <StockUpdateModal
      ref="stockUpdateModal"
      @success="handleModalSuccess"
    />
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useProducts } from '@/composables/ui/products/useProducts';
import AddProductModal from '@/components/products/AddProductModal.vue';
import StockUpdateModal from '@/components/products/StockUpdateModal.vue';

export default {
  name: 'ProductDetails',
  components: {
    AddProductModal,
    StockUpdateModal
  },
  props: {
    id: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const router = useRouter();
    
    // Template refs
    const addProductModal = ref(null);
    const stockUpdateModal = ref(null);
    
    // Use the products composable
    const {
      products,
      categories,
      loading,
      error,
      successMessage,
      fetchProducts,
      fetchCategories,
      getCategoryName,
      deleteProduct,
      exportData
    } = useProducts();

    // Local state
    const activeTab = ref('Overview');
    const tabs = ['Overview', 'Purchases', 'Adjustments', 'History'];

    // Current product computed
    const currentProduct = computed(() => {
      return products.value.find(product => product._id === props.id) || {};
    });

    // Fixed methods
    const handleEdit = () => {
      if (currentProduct.value && Object.keys(currentProduct.value).length > 0) {
        addProductModal.value?.openEdit?.(currentProduct.value);
      }
    };

    const handleStockAdjustment = () => {
      if (currentProduct.value && Object.keys(currentProduct.value).length > 0) {
        stockUpdateModal.value?.openStock?.(currentProduct.value);
      }
    };

    const handleImageUpload = () => {
      // Open the edit modal which has image upload functionality
      if (currentProduct.value && Object.keys(currentProduct.value).length > 0) {
        addProductModal.value?.openEdit?.(currentProduct.value);
      }
    };

    const handleDelete = async () => {
      if (!currentProduct.value || !currentProduct.value.product_name) {
        return;
      }
      
      const confirmed = confirm(`Are you sure you want to delete "${currentProduct.value.product_name}"?`);
      if (confirmed) {
        try {
          await deleteProduct(currentProduct.value);
          router.push('/products');
        } catch (err) {
          console.error('Error deleting product:', err);
        }
      }
    };

    const handleExport = async () => {
      try {
        await exportData();
      } catch (err) {
        console.error('Error exporting:', err);
      }
    };

    const handleModalSuccess = async (result) => {
      if (result?.message) {
        successMessage.value = result.message;
        setTimeout(() => {
          successMessage.value = null;
        }, 3000);
      }
      await fetchProducts();
    };

    const setActiveTab = (tab) => {
      activeTab.value = tab;
    };

    // Initialize data
    const initializeData = async () => {
      await fetchCategories();
      await fetchProducts();
    };

    onMounted(() => {
      initializeData();
    });

    return {
      // State
      loading,
      error,
      successMessage,
      currentProduct,
      activeTab,
      tabs,
      router,
      categories,
      
      // Template refs
      addProductModal,
      stockUpdateModal,
      handleImageUpload,
      
      // Methods
      setActiveTab,
      handleDelete,
      handleEdit,
      handleStockAdjustment,
      handleExport,
      handleModalSuccess,
      initializeData
    };
  }
};
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
  color: var(--text-accent);
  font-size: 12px;
  font-weight: 500;
}

.breadcrumb-icon {
  width: 12px;
  height: 12px;
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

.tab-item {
  border-bottom: 1px solid transparent !important;
  background: transparent !important;
  transition: all 0.2s ease;
  font-weight: 500;
  font-size: 0.875rem;
}

.tab-item.active {
  font-weight: 600;
  border-bottom: 2px solid var(--border-accent) !important;
}

.tab-item:hover:not(.active) {
  opacity: 0.7;
}

.border-bottom-accent {
  border-bottom-color: var(--border-accent) !important;
}

.border-bottom-transparent {
  border-bottom-color: transparent !important;
}
</style>