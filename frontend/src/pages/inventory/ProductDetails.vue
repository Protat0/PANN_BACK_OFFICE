<template>
  <div class="flex h-screen bg-gray-50">
    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center h-full">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-4" style="border-color: var(--primary);"></div>
          <p style="color: var(--tertiary-medium);">Loading product details...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="flex items-center justify-center h-full">
        <div class="text-center">
          <div class="text-6xl mb-4">❌</div>
          <h2 class="text-2xl font-bold mb-2" style="color: var(--error);">Error Loading Product</h2>
          <p style="color: var(--tertiary-medium);">{{ error }}</p>
          <button 
            @click="fetchProductData" 
            class="mt-4 px-4 py-2 rounded-lg font-medium"
            style="background-color: var(--primary); color: white;"
          >
            Try Again
          </button>
        </div>
      </div>

      <!-- Product Content -->
      <div v-else class="h-full">
        <!-- Success Message -->
        <div v-if="successMessage" class="mx-6 mt-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
          {{ successMessage }}
        </div>
        <!-- Header -->
        <header class="bg-white border-b border-gray-200 px-6 py-3">
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
              <h1 class="product-title">{{ productData.product_name || 'Product Name' }}</h1>
              <div class="description-and-buttons">
                <p class="product-description">{{ productData.description || 'Spicy Korean instant noodles known for their bold flavor and heat.' }}</p>
                <div class="button-group">
                  <button @click="handleUpdateStock" class="action-button btn-stock">Update Stock</button>
                  <button @click="handleDelete" class="action-button btn-delete">Delete</button>
                  <button @click="handleEdit" class="action-button btn-edit">Edit</button>
                  <button @click="handleExport" class="action-button btn-export">Export</button>
                </div>
              </div>
            </div>
          </div>
        </header>

        <!-- Tab Navigation -->
        <div class="bg-white border-b border-gray-200 px-6">
          <nav class="tab-nav">
            <button
              v-for="tab in tabs"
              :key="tab"
              @click="setActiveTab(tab)"
              :class="['tab-button', { 'active': activeTab === tab }]"
            >
              {{ tab }}
            </button>
          </nav>
        </div>

        <!-- Content Area -->
        <div class="flex-1 overflow-auto p-6 bg-gray-50">
          <!-- Overview Tab -->
          <ProductOverview 
            v-if="activeTab === 'Overview'"
            :product-data="transformedProductData"
            @stock-adjustment="handleStockAdjustment"
            @reorder="handleReorder"
            @view-history="handleViewHistory"
            @image-upload="handleImageUpload"
          />

          <!-- Other Tabs - Placeholder content for now -->
          <div v-else-if="activeTab === 'Purchases'" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-xl font-bold mb-6" style="color: var(--primary);">Purchase History</h2>
            <p style="color: var(--tertiary-medium);">Purchase history content will be implemented here.</p>
          </div>

          <div v-else-if="activeTab === 'Adjustments'" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-xl font-bold mb-6" style="color: var(--primary);">Stock Adjustments</h2>
            <p style="color: var(--tertiary-medium);">Stock adjustments content will be implemented here.</p>
          </div>

          <div v-else-if="activeTab === 'History'" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-xl font-bold mb-6" style="color: var(--primary);">Product History</h2>
            <p style="color: var(--tertiary-medium);">Product history content will be implemented here.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Product Modal for Editing -->
    <AddProductModal
      :show="showEditModal"
      :product="productData"
      :loading="formLoading"
      :error="formError"
      @close="closeEditModal"
      @submit="saveProduct"
    />

    <!-- Stock Update Modal -->
    <StockUpdateModal
      :show="showStockModal"
      :product="productData"
      :loading="stockLoading"
      :error="stockError"
      @close="closeStockModal"
      @submit="updateStock"
    />
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
    console.log('📋 Received props:', props);
    console.log('🆔 Product ID from route:', props.id);

    const router = useRouter();
    const productData = ref({});
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

    // Transform the API data to match ProductOverview component expectations
    const transformedProductData = computed(() => {
      if (!productData.value || Object.keys(productData.value).length === 0) {
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
        name: productData.value.product_name || '',
        id: productData.value._id || props.id,
        category: productData.value.category_name || productData.value.category_id || '',
        batchDate: productData.value.batch_date || productData.value.created_at || '',
        expiryDate: productData.value.expiry_date || '',
        thresholdValue: productData.value.low_stock_threshold || 0,
        description: productData.value.description || 'Spicy Korean instant noodles known for their bold flavor and heat.',
        tags: productData.value.tags || [],
        supplier: {
          name: productData.value.supplier_name || 'John Doe',
          contact: productData.value.supplier_contact || '09999999999',
          email: productData.value.supplier_email || '',
          address: productData.value.supplier_address || ''
        },
        stock: {
          opening: productData.value.opening_stock || productData.value.stock || 0,
          remaining: productData.value.stock || 0,
          onTheWay: productData.value.on_the_way || 0,
          reserved: productData.value.reserved_stock || 0
        },
        pricing: {
          cost: productData.value.cost_price || 0,
          selling: productData.value.selling_price || 0,
          unitType: productData.value.unit || 'pcs'
        },
        image: productData.value.image_url || productData.value.image || 'https://images.unsplash.com/photo-1617093727343-374698b1b08d?w=200&h=150&fit=crop&crop=center'
      };
    });

    const fetchProductData = async () => {
      console.log('🔄 Fetching product data for ID:', props.id);
      
      loading.value = true;
      error.value = null;
      
      try {
        console.log('📡 Calling API...');
        const response = await productsApiService.getProduct(props.id);
        console.log('✅ API Response:', response);
        
        productData.value = response || {};
        console.log('📦 Product data set:', productData.value);
        
      } catch (err) {
        console.error('❌ Error fetching product:', err);
        error.value = `Failed to load product: ${err.message}`;
      } finally {
        loading.value = false;
        console.log('🏁 Fetch completed. Loading:', loading.value);
      }
    };

    const setActiveTab = (tab) => {
      console.log('📑 Tab changed to:', tab);
      activeTab.value = tab;
    };

    const handleDelete = async () => {
      console.log('🗑️ Delete button clicked for product:', props.id);
      
      if (!productData.value || !productData.value.product_name) {
        error.value = 'Product data not available for deletion';
        return;
      }

      const productName = productData.value.product_name;
      const confirmed = confirm(`Are you sure you want to delete "${productName}"?\n\nThis action cannot be undone.`);
      
      if (!confirmed) return;

      formLoading.value = true;
      error.value = null;

      try {
        console.log('🔄 Deleting product with ID:', props.id);
        await productsApiService.deleteProduct(props.id);
        
        console.log('✅ Product deleted successfully');
        successMessage.value = `Product "${productName}" has been deleted successfully`;
        
        // Navigate back to products list after successful deletion
        setTimeout(() => {
          console.log('🔄 Navigating back to products list');
          try {
            router.push('/products');
          } catch (routerError) {
            console.error('Router navigation failed:', routerError);
            window.location.href = '/products'; // Fallback navigation
          }
        }, 1500);
        
      } catch (err) {
        console.error('❌ Error deleting product:', err);
        error.value = `Failed to delete product: ${err.message}`;
      } finally {
        formLoading.value = false;
      }
    };

    const handleEdit = () => {
      console.log('✏️ Edit button clicked for product:', props.id);
      if (productData.value && Object.keys(productData.value).length > 0) {
        showEditModal.value = true;
        formError.value = null;
      }
    };

    const closeEditModal = () => {
      showEditModal.value = false;
      formError.value = null;
    };

    const saveProduct = async (updatedProductData) => {
      formLoading.value = true;
      formError.value = null;

      try {
        await productsApiService.updateProduct(props.id, updatedProductData);
        successMessage.value = `Product "${updatedProductData.product_name}" updated successfully`;
        
        closeEditModal();
        await fetchProductData(); // Refetch the updated data
        
        setTimeout(() => {
          successMessage.value = null;
        }, 3000);
      } catch (err) {
        console.error('Error updating product:', err);
        formError.value = err.message;
      } finally {
        formLoading.value = false;
      }
    };

    const handleExport = () => {
      console.log('📤 Export button clicked for product:', props.id);
      // Add export functionality here
    };

    // Stock modal handlers
    const handleUpdateStock = () => {
      console.log('📦 Update Stock button clicked for product:', props.id);
      if (productData.value && Object.keys(productData.value).length > 0) {
        showStockModal.value = true;
        stockError.value = null;
      }
    };

    const closeStockModal = () => {
      showStockModal.value = false;
      stockError.value = null;
    };

    const updateStock = async (stockData) => {
      stockLoading.value = true;
      stockError.value = null;

      try {
        console.log('📦 Updating stock with data:', stockData);
        
        // Here you would call your API service to update stock
        // await productsApiService.updateProductStock(props.id, stockData);
        
        // For now, we'll simulate the API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        successMessage.value = `Stock updated successfully: ${stockData.operation_type} ${stockData.quantity} units`;
        
        closeStockModal();
        await fetchProductData(); // Refetch the updated data
        
        setTimeout(() => {
          successMessage.value = null;
        }, 3000);
      } catch (err) {
        console.error('Error updating stock:', err);
        stockError.value = err.message || 'Failed to update stock';
      } finally {
        stockLoading.value = false;
      }
    };

    // ProductOverview event handlers
    const handleStockAdjustment = (product) => {
      console.log('📦 Stock adjustment requested for:', product);
      // Open the stock modal when stock adjustment is requested from overview
      handleUpdateStock();
    };

    const handleReorder = (product) => {
      console.log('🔄 Reorder requested for:', product);
      // Implement reorder functionality
    };

    const handleViewHistory = (product) => {
      console.log('📜 View history requested for:', product);
      setActiveTab('History');
    };

    const handleImageUpload = (product) => {
      console.log('🖼️ Image upload requested for:', product);
      // Implement image upload functionality
    };

    // Watch for prop changes
    watch(() => props.id, (newId, oldId) => {
      console.log('🔄 Product ID changed from', oldId, 'to', newId);
      if (newId) {
        fetchProductData();
      }
    });

    // Fetch data when component mounts
    onMounted(() => {
      console.log('🚀 Component mounted, fetching data...');
      if (props.id) {
        fetchProductData();
      }
    });

    return {
      productData,
      transformedProductData,
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
      handleImageUpload,
      fetchProductData
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
  font-size: 12px !important;
  line-height: 1 !important;
}

.breadcrumb-link {
  color: var(--primary) !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  text-decoration: none !important;
  transition: opacity 0.2s ease !important;
}

.breadcrumb-link:hover {
  opacity: 0.8 !important;
}

.breadcrumb-current {
  color: var(--primary) !important;
  font-size: 12px !important;
  font-weight: 500 !important;
}

.breadcrumb-icon {
  width: 12px !important;
  height: 12px !important;
  color: var(--tertiary-medium) !important;
  flex-shrink: 0 !important;
}

/* Product Header Styles */
.product-header {
  width: 100% !important;
}

.product-info {
  width: 100% !important;
}

.product-title {
  font-size: 1.5rem !important;
  font-weight: 700 !important;
  margin-bottom: 0.5rem !important;
  color: var(--tertiary-dark) !important;
}

.description-and-buttons {
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  width: 100% !important;
  gap: 20px !important;
}

.product-description {
  font-size: 0.875rem !important;
  color: var(--tertiary-medium) !important;
  margin: 0 !important;
  flex: 1 !important;
}

/* Button Group Styles */
.button-group {
  display: flex !important;
  gap: 12px !important;
  align-items: center !important;
  flex-shrink: 0 !important;
}

/* Button Styles */
.action-button {
  padding: 8px 16px !important;
  font-size: 0.875rem !important;
  font-weight: 500 !important;
  border-radius: 6px !important;
  border: none !important;
  cursor: pointer !important;
  transition: opacity 0.2s ease !important;
  white-space: nowrap !important;
  
  /* Button size constraints for uniformity */
  min-width: 80px !important;
  max-width: 120px !important;
  min-height: 36px !important;
  max-height: 40px !important;
  
  /* Center text within button */
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
}

.action-button:hover {
  opacity: 0.9 !important;
}

.btn-stock {
  background-color: var(--primary) !important;
  color: white !important;
}

.btn-delete {
  background-color: var(--error) !important;
  color: white !important;
}

.btn-edit {
  background-color: var(--secondary) !important;
  color: white !important;
}

.btn-export {
  background-color: transparent !important;
  color: var(--tertiary-dark) !important;
  border: 1px solid var(--tertiary) !important;
}

/* Tab Navigation Styles */
.tab-nav {
  display: flex !important;
  gap: 32px !important;
}

.tab-button {
  padding: 16px 4px !important;
  border-bottom: 2px solid transparent !important;
  font-size: 0.875rem !important;
  font-weight: 500 !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
  background: none !important;
  border-left: none !important;
  border-right: none !important;
  border-top: none !important;
}

.tab-button.active {
  border-bottom-color: var(--primary) !important;
  color: var(--primary) !important;
  font-weight: 600 !important;
}

.tab-button:not(.active) {
  color: var(--tertiary-medium) !important;
}

.tab-button:not(.active):hover {
  opacity: 0.7 !important;
}

/* Override any global styles that might interfere */
nav, nav *, div, div *, span, span *, a, a * {
  font-size: inherit !important;
}
</style>