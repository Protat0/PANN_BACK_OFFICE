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
      :show="showEditModal"
      :product="currentProduct"
      @close="closeEditModal"
      @success="handleModalSuccess"
    />

    <StockUpdateModal
      :show="showStockModal"
      :product="currentProduct"
      @close="closeStockModal"
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
    console.log('ProductDetails component mounted!');
    console.log('Product ID from route:', props.id);

    const router = useRouter();
    
    // Use the products composable - only retrieve methods
    const {
      products,
      categories,
      loading,
      error,
      successMessage,
      fetchProducts,
      fetchCategories,
      getCategoryName,
    } = useProducts();

    // Local state for this component
    const activeTab = ref('Overview');
    const tabs = ['Overview', 'Purchases', 'Adjustments', 'History'];

    // Modal states
    const showEditModal = ref(false);
    const showStockModal = ref(false);

    // Current product computed from the products list
    const currentProduct = computed(() => {
      return products.value.find(product => product._id === props.id) || {};
    });

    // Transform the product data for ProductOverview component
    const transformedProductData = computed(() => {
        console.log('Current product:', currentProduct.value); // Debug line
        console.log('Products array:', products.value.length); 
      if (!currentProduct.value || Object.keys(currentProduct.value).length === 0) {
        return {
          name: '',
          id: props.id,
          category: '',
          batchDate: '',
          expiryDate: '',
          thresholdValue: 0,
          description: '',
          tags: [],
          supplier: {
            name: '',
            contact: '',
            email: '',
            address: ''
          },
          stock: {
            opening: 0,
            remaining: 0,
            onTheWay: 0,
            reserved: 0
          },
          pricing: {
            cost: 0,
            selling: 0,
            unitType: ''
          },
          image: ''
        };
      }

      return {
        name: currentProduct.value.product_name || '',
        id: currentProduct.value._id || props.id,
        category: currentProduct.value.category_name || getCategoryName(currentProduct.value.category_id),
        batchDate: currentProduct.value.batch_date || currentProduct.value.created_at || '',
        expiryDate: currentProduct.value.expiry_date || '',
        thresholdValue: currentProduct.value.low_stock_threshold || 0,
        description: currentProduct.value.description || 'Product description not available.',
        tags: currentProduct.value.tags || [],
        supplier: {
          name: currentProduct.value.supplier_name || 'Unknown Supplier',
          contact: currentProduct.value.supplier_contact || '',
          email: currentProduct.value.supplier_email || '',
          address: currentProduct.value.supplier_address || ''
        },
        stock: {
          opening: currentProduct.value.opening_stock || currentProduct.value.stock || 0,
          remaining: currentProduct.value.stock || 0,
          onTheWay: currentProduct.value.on_the_way || 0,
          reserved: currentProduct.value.reserved_stock || 0
        },
        pricing: {
          cost: currentProduct.value.cost_price || 0,
          selling: currentProduct.value.selling_price || 0,
          unitType: currentProduct.value.unit || 'pcs'
        },
        image: currentProduct.value.image_url || currentProduct.value.image || ''
      };
    });

    // Methods
    const setActiveTab = (tab) => {
      console.log('Tab changed to:', tab);
      activeTab.value = tab;
    };

    // Modal trigger methods - no logic, just open modals
    const handleDelete = () => {
      console.log('Delete button clicked for product:', props.id);
      if (!currentProduct.value || !currentProduct.value.product_name) {
        error.value = 'Product data not available for deletion';
        return;
      }
      // Open delete confirmation modal (you'll need to create this)
      // For now, just log - the modal will handle the actual deletion
    };

    const handleEdit = () => {
      console.log('Edit button clicked for product:', props.id);
      if (currentProduct.value && Object.keys(currentProduct.value).length > 0) {
        showEditModal.value = true;
      }
    };

    const handleUpdateStock = () => {
      console.log('Update Stock button clicked for product:', props.id);
      if (currentProduct.value && Object.keys(currentProduct.value).length > 0) {
        showStockModal.value = true;
      }
    };

    const handleExport = () => {
      console.log('Export button clicked for product:', props.id);
      // Export functionality can be handled here or in a modal
    };

    // Modal close handlers
    const closeEditModal = () => {
      showEditModal.value = false;
    };

    const closeStockModal = () => {
      showStockModal.value = false;
    };

    // Modal success handlers - refresh data when modals complete successfully
    const handleModalSuccess = async (message) => {
      if (message) {
        successMessage.value = message;
        setTimeout(() => {
          successMessage.value = null;
        }, 3000);
      }
      // Refresh the products data to get updated information
      await fetchProducts();
    };

    // ProductOverview event handlers - just trigger modals
    const handleStockAdjustment = () => {
      handleUpdateStock();
    };

    const handleReorder = (product) => {
      console.log('Reorder requested for:', product);
      // Could open a reorder modal
    };

    const handleViewHistory = () => {
      setActiveTab('History');
    };

    const handleImageUpload = () => {
      console.log('Image upload requested');
      // Could open an image upload modal
    };

    // Initialize data
    const initializeData = async () => {
      await fetchCategories();
      await fetchProducts();
    };

    // Watch for prop changes
    watch(() => props.id, (newId, oldId) => {
      console.log('Product ID changed from', oldId, 'to', newId);
      if (newId && !currentProduct.value) {
        // If product not found in current products list, refresh
        fetchProducts();
      }
    });

    // Lifecycle
    onMounted(() => {
      console.log('Component mounted, initializing data...');
      initializeData();
    });

    return {
      // State from composable
      loading,
      error,
      successMessage,
      
      // Local state
      currentProduct,
      transformedProductData,
      activeTab,
      tabs,
      showEditModal,
      showStockModal,
      router,
      
      // Methods
      setActiveTab,
      handleDelete,
      handleEdit,
      handleUpdateStock,
      handleExport,
      closeEditModal,
      closeStockModal,
      handleModalSuccess,
      handleStockAdjustment,
      handleReorder,
      handleViewHistory,
      handleImageUpload
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