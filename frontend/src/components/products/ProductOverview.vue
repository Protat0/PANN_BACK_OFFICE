<template>
  <div class="overview-container">
    <!-- Left Column - Product Details (2/3 width) -->
    <div class="details-column">
      <!-- Primary Details -->
      <div class="card-theme p-4">
        <h3 class="text-primary mb-3">Primary Details</h3>
        
        <div class="row mb-3">
          <div class="col-6">
            <div class="mb-2">
              <small class="text-tertiary d-block">Product Name</small>
              <span class="text-secondary">Ansung Noodles Anseongtangmyeon</span>
            </div>
          </div>
          <div class="col-6">
            <div class="mb-2">
              <small class="text-tertiary d-block">Product ID</small>
              <span class="text-secondary">45f04c</span>
            </div>
          </div>
        </div>
        
        <div class="row mb-3">
          <div class="col-6">
            <div class="mb-2">
              <small class="text-tertiary d-block">Product Category</small>
              <span class="text-secondary">685e5dd708ecae83aea0aadf</span>
            </div>
          </div>
          <div class="col-6">
            <div class="mb-2">
              <small class="text-tertiary d-block">Batch Date</small>
              <span class="text-secondary">07/03/2025</span>
            </div>
          </div>
        </div>
        
        <div class="row">
          <div class="col-6">
            <div class="mb-2">
              <small class="text-tertiary d-block">Threshold Value</small>
              <span class="text-secondary">5</span>
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
              <span class="text-secondary">John Doe</span>
            </div>
          </div>
          <div class="col-6">
            <div class="mb-2">
              <small class="text-tertiary d-block">Contact Number</small>
              <span class="text-secondary">09999999999</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Column - Image & Stock Info (1/3 width) -->
    <div class="sidebar-column">
      <!-- Product Image -->
      <div class="card-theme p-3">
        <img 
          :src="productData.image" 
          :alt="productData.name"
          class="product-image"
        />
      </div>

      <!-- Stock Information -->
      <div class="card-theme p-4">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <small class="text-tertiary">Opening Stock</small>
          <span class="text-secondary fw-semibold">41</span>
        </div>
        
        <div class="d-flex justify-content-between align-items-center mb-2">
          <small class="text-tertiary">Remaining Stock</small>
          <span class="text-success fw-semibold">41</span>
        </div>
        
        <div class="d-flex justify-content-between align-items-center mb-2">
          <small class="text-tertiary">On the Way</small>
          <span class="text-error fw-semibold">0</span>
        </div>
        
        <div class="d-flex justify-content-between align-items-center mb-2">
          <small class="text-tertiary">Cost Price</small>
          <span class="text-secondary fw-semibold">52.50</span>
        </div>
        
        <div class="d-flex justify-content-between align-items-center mb-2">
          <small class="text-tertiary">Selling Price</small>
          <span class="text-secondary fw-semibold">70.00</span>
        </div>
        
        <div class="d-flex justify-content-between align-items-center">
          <small class="text-tertiary">Unit Type</small>
          <span class="text-accent fw-semibold">pc</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import productsApiService from '@/services/apiProducts.js';
import ProductOverview from '@/components/products/ProductOverview.vue';
import AddProductModal from '@/components/products/AddProductModal.vue';
import StockUpdateModal from '@/components/products/StockUpdateModal.vue';

export default {
  name: 'ProductDetails',
  components: {
    ProductOverview,
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
    console.log('🎯 ProductDetails component mounted!');
    console.log('🆔 Product ID from route:', props.id);

    const router = useRouter();
    // Remove productData ref - will be handled by composable
    const loading = ref(false);
    const error = ref(null);
    const activeTab = ref('Overview');
    const tabs = ['Overview', 'Purchases', 'Adjustments', 'History'];

    // Modal states
    const showEditModal = ref(false);
    const formLoading = ref(false);
    const formError = ref(null);
    const successMessage = ref(null);

    // Stock modal states
    const showStockModal = ref(false);
    const stockLoading = ref(false);
    const stockError = ref(null);

    // Remove transformedProductData computed property - will come from composable

    // Remove fetchProductData function - will come from composable

    const setActiveTab = (tab) => {
      console.log('📑 Tab changed to:', tab);
      activeTab.value = tab;
    };

    const handleDelete = async () => {
      console.log('🗑️ Delete button clicked for product:', props.id);
      // Will be implemented with composable
    };

    const handleEdit = () => {
      console.log('✏️ Edit button clicked for product:', props.id);
      // Will be implemented with composable
    };

    const closeEditModal = () => {
      showEditModal.value = false;
      formError.value = null;
    };

    const saveProduct = async (updatedProductData) => {
      // Will be implemented with composable
    };

    const handleExport = () => {
      console.log('📤 Export button clicked for product:', props.id);
      // Will be implemented with composable
    };

    // Stock modal handlers
    const handleUpdateStock = () => {
      console.log('📦 Update Stock button clicked for product:', props.id);
      // Will be implemented with composable
    };

    const closeStockModal = () => {
      showStockModal.value = false;
      stockError.value = null;
    };

    const updateStock = async (stockData) => {
      // Will be implemented with composable
    };

    // ProductOverview event handlers
    const handleStockAdjustment = (product) => {
      console.log('📦 Stock adjustment requested for:', product);
      handleUpdateStock();
    };

    const handleReorder = (product) => {
      console.log('🔄 Reorder requested for:', product);
      // Will be implemented with composable
    };

    const handleViewHistory = (product) => {
      console.log('📜 View history requested for:', product);
      setActiveTab('History');
    };

    const handleImageUpload = (product) => {
      console.log('🖼️ Image upload requested for:', product);
      // Will be implemented with composable
    };

    // Watch for prop changes - will be handled by composable
    // onMounted will be handled by composable

    return {
      loading,
      error,
      activeTab,
      tabs,
      showEditModal,
      formLoading,
      formError,
      showStockModal,
      stockLoading,
      stockError,
      successMessage,
      setActiveTab,
      handleDelete,
      handleEdit,
      closeEditModal,
      saveProduct,
      handleExport,
      handleUpdateStock,
      closeStockModal,
      updateStock,
      handleStockAdjustment,
      handleReorder,
      handleViewHistory,
      handleImageUpload
    };
  }
};
</script>

<style scoped>
.overview-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  max-width: 1200px;
}

.details-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.details-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 1.5rem;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--tertiary-medium);
}

.detail-value {
  font-size: 1rem;
  font-weight: 500;
  color: var(--tertiary-dark);
  margin: 0;
}

.sidebar-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.image-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
  border: 2px dashed var(--primary-light);
  text-align: center;
}

.product-image {
  width: 100%;
  height: 150px;
  object-fit: contain;
  border-radius: 4px;
}

.stock-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--tertiary-medium);
}

.stock-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--tertiary-dark);
}

.stock-info {
  color: var(--info) !important;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .overview-container {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .overview-container {
    gap: 1rem;
  }
  
  .details-card,
  .image-container,
  .stock-container {
    padding: 1rem;
  }
  
  .section-title {
    font-size: 1.125rem;
    margin-bottom: 1rem;
  }
}
</style>