<template>
  <div class="container-fluid pt-2 pb-4 category-details-page">
    <!-- Breadcrumb Navigation -->
    <nav aria-label="breadcrumb" class="mb-3">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link to="/inventory" class="text-tertiary-medium">Inventory</router-link>
        </li>
        <li class="breadcrumb-item">
          <router-link to="/categories" class="text-tertiary-medium">Categories</router-link>
        </li>
        <li class="breadcrumb-item active text-primary" aria-current="page">Category Details</li>
      </ol>
    </nav>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading category details...</span>
      </div>
      <p class="mt-2 text-muted">Loading category details...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="alert alert-danger" role="alert">
      <strong>Error:</strong> {{ error }}
      <button @click="retryLoad" class="btn btn-sm btn-outline-danger ms-2">
        Retry
      </button>
    </div>

    <!-- Main Content -->
    <div v-if="!loading && !error">
      <!-- Page Header -->
      <div class="d-flex justify-content-between align-items-start mb-4">
        <div>
          <h1 class="h2 fw-bold text-primary mb-1">{{ categoryData.category_name || 'Category Details' }}</h1>
        </div>
        <div class="d-flex gap-2">
          <button 
            class="btn btn-edit btn-sm btn-with-icon-sm"
            @click="handleEditCategory"
          >
            <Edit :size="14" />
            Edit
          </button>
          
          <!-- Export button -->
          <button 
            class="btn btn-export btn-sm btn-with-icon-sm" 
            type="button" 
            :disabled="isExporting"
            @click="exportFilteredProducts()"
            :title="getExportTooltip()"
          >
            <Download :size="14" />
            {{ isExporting ? 'Exporting...' : getExportButtonText() }}
          </button>
        </div>
      </div>

      <!-- Category Information Card -->
      <div class="row mb-4">
        <div class="col-md-8">
          <div class="card shadow-sm h-100">
            <div class="card-body">
              <div class="row">
                <div class="col-6">
                  <div class="mb-3">
                    <label class="form-label text-tertiary-dark fw-semibold">Category Name:</label>
                    <p class="mb-0 text-tertiary-dark">{{ categoryData.category_name || 'N/A' }}</p>
                  </div>
                  <div class="mb-3">
                    <label class="form-label text-tertiary-dark fw-semibold">Sub-Categories:</label>
                    <p class="mb-0 text-tertiary-dark">{{ categoryData.sub_categories?.length || 0 }}</p>
                  </div>
                  <div class="mb-3">
                    <label class="form-label text-tertiary-dark fw-semibold">Description:</label>
                    <p class="mb-0 text-tertiary-dark">{{ categoryData.description || 'No description available' }}</p>
                  </div>
                </div>
                <div class="col-6">
                  <div class="mb-3">
                    <label class="form-label text-tertiary-dark fw-semibold">Total Products:</label>
                    <p class="mb-0 text-tertiary-dark">{{ categoryData.sub_categories ? 
       categoryData.sub_categories.reduce((total, sub) => total + (sub.products?.length || 0), 0) : 0  }}</p>
                  </div>
                  <div class="mb-3">
                    <label class="form-label text-tertiary-dark fw-semibold">Status:</label>
                    <span :class="getStatusClass(categoryData.status)">
                      {{ categoryData.status?.charAt(0).toUpperCase() + categoryData.status?.slice(1) || 'N/A' }}
                    </span>
                  </div>
                  <div class="mb-3">
                    <label class="form-label text-tertiary-dark fw-semibold">Last Updated:</label>
                    <p class="mb-0 text-tertiary-dark">{{ formatDate(categoryData.last_updated) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card shadow-sm h-100">
            <div class="card-body d-flex align-items-center justify-content-center">
              <div class="text-center">
                <div v-if="categoryData.image_url" class="category-image mb-3">
                  <img :src="categoryData.image_url" alt="Category image" class="img-fluid rounded" style="max-height: 120px;" />
                </div>
                <div v-else class="category-image-placeholder bg-neutral-light rounded p-4 mb-3">
                  <Package :size="64" class="text-tertiary-medium" />
                </div>
                <small class="text-tertiary-medium">Category Image</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Bar -->
      <div class="action-bar-container mb-3">
        <div class="action-bar-controls">
          <div class="action-row">
            <div class="d-flex align-items-end gap-2">
              <div class="filter-dropdown">
                <label class="filter-label">Filter</label>
                <select class="form-select form-select-sm" v-model="categoryFilter" @change="applyFilter">
                  <option value="all">All Products ({{ products.length }})</option>
                  <option 
                    v-for="subCat in categoryData.sub_categories" 
                    :key="subCat.id || subCat.name" 
                    :value="subCat.name"
                  >
                    {{ subCat.name }} ({{ getSubcategoryProductCount(subCat.name) }})
                  </option>
                  <!-- REMOVED: Special "None" option - now treated as regular subcategory -->
                </select>
              </div>
              
              <!-- Show Add Sub Category button when no products are selected -->
              <button 
                v-if="selectedProducts.length === 0"
                class="btn btn-add btn-sm btn-with-icon-sm" 
                @click="handleAddSubCategory"
              >
                <Plus :size="14" />
                Add Sub Category
              </button>
              
              <!-- Show Remove from Category button when products are selected -->
              <button 
                v-if="selectedProducts.length > 0"
                class="btn btn-delete btn-sm btn-with-icon-sm" 
                @click="removeSelectedFromCategory"
              >
                <Trash2 :size="14" />
                Remove ({{ selectedProducts.length }})
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Products Table -->
      <DataTable
        :total-items="filteredProducts.length"
        :current-page="currentPage"
        :items-per-page="itemsPerPage"
        @page-changed="handlePageChange"
      >
        <template #header>
          <tr>
            <th style="width: 40px;">
              <input 
                type="checkbox" 
                class="form-check-input" 
                :checked="isAllSelected"
                @change="toggleSelectAll"
                :indeterminate.prop="isIndeterminate"
              />
            </th>
            <th style="width: 120px;">Product ID</th>
            <th>Product Name</th>
            <th style="width: 140px;">Sub-Category</th>
            <th style="width: 120px;">Remaining Stock</th>
            <th style="width: 120px;">Selling Price</th>
            <th style="width: 120px;">Supplier</th>
            <th style="width: 100px;">Actions</th>
          </tr>
        </template>

        <template #body>
          <tr v-for="product in paginatedProducts" :key="product._id">
            <td>
              <input 
                type="checkbox" 
                class="form-check-input" 
                :value="product._id"
                v-model="selectedProducts"
              />
            </td>
            <td>
              <code class="text-tertiary-dark bg-neutral-light px-2 py-1 rounded">
                {{ product._id }}
              </code>
            </td>
            <td>
              <div class="fw-medium text-tertiary-dark">{{ product.product_name }}</div>
            </td>
            <td>
               <select 
                  class="form-select form-select-sm"
                  :value="product.subcategory || 'None'"  
                  @change="updateProductSubcategory(product._id, $event.target.value)"
                >
                  <option 
                    v-for="subCat in categoryData.sub_categories" 
                    :key="subCat.name" 
                    :value="subCat.name"
                  >
                    {{ subCat.name }}
                  </option>
                </select>
            </td>
            <td class="text-center">
              <span :class="getStockClass(product.stock)">
                {{ product.stock || 0 }}
              </span>
            </td>
            <td class="text-end fw-medium text-tertiary-dark">
              ₱{{ formatPrice(product.selling_price) }}
            </td>
            <td class="text-tertiary-dark">{{ product.supplier || 'N/A' }}</td>
            <td>
              <div class="d-flex gap-1 justify-content-center">
                <button 
                  class="btn btn-outline-danger btn-icon-only btn-xs action-btn action-btn-delete"
                  @click="removeProductFromCategory(product)"
                  data-bs-toggle="tooltip"
                  title="Set to None Subcategory"
                >
                  <Trash2 :size="12" />
                </button>
              </div>
            </td>
          </tr>
        </template>
      </DataTable>

      <!-- Empty State -->
      <div v-if="filteredProducts.length === 0" class="text-center py-5">
        <div class="card">
          <div class="card-body py-5">
            <Package :size="48" class="text-tertiary-medium mb-3" />
            <p class="text-tertiary-medium mb-3">
              {{ categoryFilter === 'all' ? 'No products found in this category' : 
                 `No products found in "${categoryFilter}" subcategory` }}
            </p>
            <button class="btn btn-primary btn-with-icon" v-if="categoryFilter === 'all'">
              <Plus :size="16" />
              Add First Product
            </button>
          </div>
        </div>
      </div>
    </div>

     <!-- Edit Category Modal -->
    <AddCategoryModal ref="editCategoryModal" @category-updated="onCategoryUpdated" />
    
    <!-- Add Subcategory Modal -->
    <AddSubcategoryModal ref="addSubcategoryModal" @subcategory-added="onSubcategoryAdded" />
  </div>
</template>

<script>
import DataTable from '@/components/common/TableTemplate.vue'
import AddSubcategoryModal from '@/components/categories/AddSubCategoryModal.vue'
import AddCategoryModal from '@/components/categories/AddCategoryModal.vue'
import categoryApiService from '@/services/apiCategory'
import { 
  Edit,
  Download,
  Package,
  Plus,
  Trash2
} from 'lucide-vue-next'

export default {
  name: 'CategoryDetails',
  components: {
    DataTable,
    AddCategoryModal,
    AddSubcategoryModal,
    Edit,
    Download,
    Package,
    Plus,
    Trash2
  },
  data() {
    return {
      currentPage: 1,
      itemsPerPage: 10,
      categoryFilter: 'all',
      selectedProducts: [],
      loading: false,
      error: null,
      categoryId: null,
      categoryData: {},
      products: [],
      isExporting: false
    }
  },
  computed: {
    filteredProducts() {
      if (this.categoryFilter === 'all') {
        return this.products
      } else {
        // Now treat "None" as a regular subcategory, not a special case
        return this.products.filter(product => {
          const productSubcategory = product.subcategory || product.subcategory_id || product.subcategory_name
          return productSubcategory === this.categoryFilter
        })
      }
    },
    
    // REMOVED: productsWithoutSubcategory computed property
    // No longer needed since all products should have a subcategory
    
    paginatedProducts() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredProducts.slice(start, end)
    },

    isAllSelected() {
      const currentPageProductIds = this.paginatedProducts.map(p => p._id)
      return currentPageProductIds.length > 0 && 
            currentPageProductIds.every(id => this.selectedProducts.includes(id))
    },

    isIndeterminate() {
      const currentPageProductIds = this.paginatedProducts.map(p => p._id)
      const selectedOnPage = currentPageProductIds.filter(id => this.selectedProducts.includes(id))
      return selectedOnPage.length > 0 && selectedOnPage.length < currentPageProductIds.length
    }
  },
  methods: {
    // API METHODS
    async fetchCategoryData(categoryId) {
      this.loading = true
      this.error = null
      
      try {
        console.log('Fetching category with ID:', categoryId)
        
        const response = await categoryApiService.FindCategoryData({ id: categoryId })
        console.log('API Response:', response)
        
        if (response.category && typeof response.category === 'object') {
          this.categoryData = response.category
        } else if (response.data && typeof response.data === 'object') {
          this.categoryData = response.data
        } else if (response && typeof response === 'object' && !Array.isArray(response) && !response.message) {
          this.categoryData = response
        } else {
          console.warn('Unexpected response structure:', response)
          this.categoryData = {}
        }
        
        await this.fetchCompleteProducts(categoryId)
        
      } catch (error) {
        console.error('Error fetching category data:', error)
        this.error = error.message || 'Failed to fetch category data'
        this.categoryData = {}
        this.products = []
      } finally {
        this.loading = false
      }
    },

    async fetchCompleteProducts(categoryId) {
      try {
        console.log('Fetching complete products for category:', categoryId)
        
        const completeProducts = await categoryApiService.FindProdcategory({ id: categoryId })
        console.log('Complete products fetched:', completeProducts)
        
        this.products = completeProducts
        
      } catch (error) {
        console.error('Error fetching complete products:', error)
        this.products = []
        throw error
      }
    },

    async loadCategoryData(categoryId) {
      if (!categoryId) {
        console.error('No category ID provided')
        this.error = 'No category ID provided'
        return
      }
      
      await this.fetchCategoryData(categoryId)
    },

    async retryLoad() {
      const categoryId = this.$route.query.id || this.$route.params.id
      if (categoryId) {
        await this.loadCategoryData(categoryId)
      } else {
        this.error = 'No category ID available for retry'
      }
    },

    onCategoryUpdated() {
      const categoryId = this.$route.query.id || this.$route.params.id
      if (categoryId) {
        this.loadCategoryData(categoryId)
      }
    },

    // UI INTERACTION METHODS
    applyFilter() {
      this.currentPage = 1
    },

    handlePageChange(page) {
      this.currentPage = page
    },

    handleEditCategory() {
      console.log('Edit category button clicked')
      
      if (this.$refs.editCategoryModal) {
        this.$refs.editCategoryModal.openEditMode(this.categoryData)
      } else {
        console.error('EditCategoryModal ref not found')
      }
    },

    handleAddSubCategory() {
      console.log('Add sub-category button clicked')
      
      // Check if we have category data
      if (!this.categoryData._id) {
        this.showErrorMessage('Category not loaded. Please refresh the page.')
        return
      }
      
      // Open the modal
      if (this.$refs.addSubcategoryModal) {
        this.$refs.addSubcategoryModal.openModal(
          this.categoryData._id,
          this.categoryData.category_name || 'Unknown Category'
        )
      } else {
        console.error('AddSubcategoryModal ref not found')
        this.showErrorMessage('Modal component not available')
      }
    },

    // PRODUCT SELECTION METHODS
    toggleSelectAll() {
      const currentPageProductIds = this.paginatedProducts.map(p => p._id)
      
      if (this.isAllSelected) {
        this.selectedProducts = this.selectedProducts.filter(id => !currentPageProductIds.includes(id))
      } else {
        const newSelections = currentPageProductIds.filter(id => !this.selectedProducts.includes(id))
        this.selectedProducts = [...this.selectedProducts, ...newSelections]
      }
    },

    // PRODUCT MANAGEMENT METHODS
    async updateProductSubcategory(productId, newSubcategory) {
      try {
        console.log(`Updating ${productId} subcategory to:`, newSubcategory || 'None');
        
        // When user selects "None", set subcategory to "None" (the actual subcategory)
        const result = await categoryApiService.SubCatChangeTab({
          product_id: productId,
          new_subcategory: newSubcategory || "None", // Use "None" subcategory instead of null
          category_id: this.categoryData._id // Keep in CURRENT category
        });
        
        if (result.result.success) {
          console.log(`✅ ${result.result.message}`);
          
          const product = this.products.find(p => p._id === productId);
          if (product) {
            // Update local product data
            product.subcategory = newSubcategory || "None";
            product.subcategory_name = newSubcategory || "None";
            product.subcategory_id = newSubcategory || "None";
            
            console.log(`📝 Product "${product.product_name}" moved to "${newSubcategory || 'None'}" subcategory`);
          }
          
        } else {
          console.error('❌ Update failed:', result);
          this.showErrorMessage('Failed to update subcategory');
        }
      } catch (error) {
        console.error('❌ Failed to update subcategory:', error);
        this.showErrorMessage(`Failed to update subcategory: ${error.message}`);
      }
    },

    async onSubcategoryAdded(eventData) {
      try {
        console.log('Subcategory added event received:', eventData)
        
        // Refresh the category data to show the new subcategory
        await this.loadCategoryData(this.categoryData._id)
        
        // Log success
        console.log(`✅ Category data refreshed after adding "${eventData.subcategory.name}"`)
        
      } catch (error) {
        console.error('❌ Error refreshing data after subcategory addition:', error)
        this.showErrorMessage('Subcategory added but failed to refresh data. Please refresh the page.')
      }
    },

    async removeProductFromCategory(product) {
      try {
        // Updated confirmation message
        const confirmed = confirm(
          `Are you sure you want to remove "${product.name || product.product_name}" from the "${this.categoryData.category_name}" category?\n\n` +
          `The product will be moved back to the "Uncategorized" category.`
        );
        
        if (!confirmed) return;
        
        console.log('Moving product back to Uncategorized category:', product._id);
        
        // Use the dedicated API method for moving to uncategorized
        const result = await categoryApiService.MoveProductToUncategorized({
          product_id: product._id,
          current_category_id: this.categoryData._id
        });
        
        console.log('✅ Product moved to Uncategorized successfully:', result);
        
        // Remove from local products array since it's no longer in this category
        const productIndex = this.products.findIndex(p => p._id === product._id);
        if (productIndex > -1) {
          this.products.splice(productIndex, 1);
        }
        
        // Clear from selection if selected
        this.selectedProducts = this.selectedProducts.filter(id => id !== product._id);
        
        this.showSuccessMessage(
          `"${product.product_name}" has been moved to the Uncategorized category.`
        );
        
      } catch (error) {
        console.error('❌ Error moving product to Uncategorized:', error);
        this.showErrorMessage(`Failed to move product: ${error.message}`);
      }
    },

    async removeSelectedFromCategory() {
      if (this.selectedProducts.length === 0) return
      
      const productNames = this.selectedProducts
        .map(id => {
          const product = this.products.find(p => p._id === id)
          return product?.name || product?.product_name
        })
        .filter(Boolean)
        .slice(0, 3)
      
      let confirmMessage = `Are you sure you want to remove ${this.selectedProducts.length} product(s) from the "${this.categoryData.category_name}" category?\n\n` +
                          `The products will be moved back to the "Uncategorized" category.`
      
      if (productNames.length > 0) {
        confirmMessage += `\n\nProducts to be removed:\n${productNames.join(', ')}`
        if (this.selectedProducts.length > 3) {
          confirmMessage += `\n...and ${this.selectedProducts.length - 3} more`
        }
      }
      
      const confirmed = confirm(confirmMessage)
      if (!confirmed) return
      
      try {
        console.log('Bulk moving selected products to Uncategorized:', this.selectedProducts)
        
        // Use the bulk move API method
        const result = await categoryApiService.BulkMoveProductsToUncategorized({
          product_ids: this.selectedProducts,
          current_category_id: this.categoryData._id
        });
        
        console.log('✅ Products bulk moved to Uncategorized successfully:', result);
        
        // Remove all selected products from local array
        this.products = this.products.filter(product => 
          !this.selectedProducts.includes(product._id)
        );
        
        // Clear selections
        this.selectedProducts = []
        
        this.showSuccessMessage(
          `${this.selectedProducts.length} product(s) moved to Uncategorized category successfully!`
        );
        
      } catch (error) {
        console.error('Error in bulk move to Uncategorized:', error)
        this.showErrorMessage(`Bulk move failed: ${error.message}`)
      }
    },

    // EXPORT METHODS
    async exportFilteredProducts() {
      try {
        this.isExporting = true;
        console.log(`🚀 Exporting filtered products (${this.filteredProducts.length} items)`);
        
        const csvContent = this.convertFilteredProductsToCSV();
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        const timestamp = new Date().toISOString().split('T')[0];
        const categoryName = this.categoryData.category_name?.replace(/[^a-z0-9]/gi, '_').toLowerCase() || 'category';
        const filterText = this.categoryFilter === 'all' ? 'all' : 
                          this.categoryFilter.replace(/[^a-z0-9]/gi, '_').toLowerCase();
        
        link.download = `${categoryName}_${filterText}_${timestamp}.csv`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        console.log('✅ Filtered products export completed!');
        this.showSuccessMessage(`${this.filteredProducts.length} products exported successfully as CSV`);
        
      } catch (error) {
        console.error('❌ Filtered export failed:', error);
        this.showErrorMessage(`Export failed: ${error.message}`);
      } finally {
        this.isExporting = false;
      }
    },

    convertFilteredProductsToCSV() {
      if (!this.filteredProducts || this.filteredProducts.length === 0) {
        return 'No products found with current filter settings\n';
      }
      
      const headers = [
        'Product ID',
        'Product Name', 
        'Category',
        'Sub-Category',
        'Stock',
        'Selling Price (₱)',
        'Supplier',
        'Last Updated'
      ];
      
      const categoryName = this.categoryData.category_name || 'Unknown';
      const filterInfo = this.getFilterDescription();
      const timestamp = new Date().toISOString();
      
      const csvComments = [
        `# Category: ${categoryName}`,
        `# Filter: ${filterInfo}`,
        `# Total Products: ${this.filteredProducts.length}`,
        `# Exported: ${timestamp}`,
        ''
      ];
      
      const rows = this.filteredProducts.map(product => [
        product._id,
        `"${product.product_name || 'Unknown'}"`,
        `"${categoryName}"`,
        `"${product.subcategory || 'None'}"`,
        product.stock || 0,
        product.selling_price || 0,
        `"${product.supplier || 'N/A'}"`,
        this.formatDate(product.updated_at || product.last_updated) || 'N/A'
      ]);
      
      const csvContent = [
        ...csvComments,
        headers.join(','),
        ...rows.map(row => row.join(','))
      ].join('\n');
      
      return csvContent;
    },

    getFilterDescription() {
      if (this.categoryFilter === 'all') {
        return 'All products';
      } else {
        return `Products in "${this.categoryFilter}" subcategory`;
      }
    },

    // UTILITY METHODS
    formatPrice(price) {
      return parseFloat(price || 0).toFixed(2)
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },

    getStatusClass(status) {
      if (status === 'active') {
        return 'badge bg-success text-white'
      } else if (status === 'inactive') {
        return 'badge bg-danger text-white'
      }
      return 'badge bg-secondary text-white'
    },
    
    getStockClass(stock) {
      if (stock === 0) return 'text-danger fw-bold'
      if (stock <= 15) return 'text-warning fw-semibold'
      return 'text-success fw-medium'
    },

    getSubcategoryProductCount(subcategoryName) {
      return this.products.filter(product => {
        const productSubcategory = product.subcategory || product.subcategory_id || product.subcategory_name
        return productSubcategory === subcategoryName
      }).length
    },

    showSuccessMessage(message) {
      console.log('✅ Success:', message);
    },

    showErrorMessage(message) {
      alert(message);
      console.error('❌ Error:', message);
    },

    getExportButtonText() {
      const count = this.filteredProducts.length;
      if (this.categoryFilter === 'all') {
        return `Export All (${count})`;
      } else {
        return `Export ${this.categoryFilter} (${count})`;
      }
    },

    getExportTooltip() {
      const filterText = this.getFilterDescription();
      return `Export ${filterText} as CSV file`;
    }
  },
  
  async mounted() {
    console.log('Route params:', this.$route.params)
    console.log('Route query:', this.$route.query)
    
    const categoryId = this.$route.query.id || this.$route.params.id
    
    console.log('Category ID:', categoryId)
    
    if (categoryId) {
      console.log('Fetching category with ID:', categoryId)
      await this.loadCategoryData(categoryId)
    } else {
      console.error('No category ID found in route')
      this.error = 'No category ID found'
    }
  }
}
</script>

<style scoped>
.category-details-page {
  background-color: var(--neutral-light);
  min-height: 100vh;
}

.text-primary {
  color: var(--primary) !important;
}

.text-tertiary-dark {
  color: var(--tertiary-dark) !important;
}

.text-tertiary-medium {
  color: var(--tertiary-medium) !important;
}

.bg-neutral-light {
  background-color: var(--neutral-light) !important;
}

.spinner-border {
  width: 2rem;
  height: 2rem;
}

.breadcrumb {
  background: none;
  padding: 0;
  margin: 0;
}

.breadcrumb-item + .breadcrumb-item::before {
  content: ">";
  color: var(--tertiary-medium);
}

.breadcrumb-item a {
  text-decoration: none;
}

.breadcrumb-item a:hover {
  text-decoration: underline;
}

.action-bar-controls {
  border-bottom: 1px solid var(--neutral);
  background-color: white;
  border-radius: 0.75rem;
}

.action-row {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.action-row .d-flex {
  align-items: center;
}

.action-row .btn {
  flex-shrink: 0;
  height: auto;
}

.filter-dropdown {
  min-width: 120px;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--tertiary-medium);
  margin-bottom: 0.25rem;
  display: block;
}

.category-image-placeholder {
  width: 100%;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed var(--neutral);
}

.card {
  border: 1px solid var(--neutral);
  border-radius: 0.75rem;
}

.card-body {
  padding: 1.5rem;
}

.badge {
  font-size: 0.875rem;
  font-weight: 500;
}

.form-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .action-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .d-flex.gap-2 {
    flex-direction: column;
    gap: 0.5rem !important;
  }
  
  .filter-dropdown {
    min-width: 100%;
  }
}
</style>