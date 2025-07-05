<template>
  <div class="container-fluid pt-2 pb-4 category-details-page">
    <!-- Breadcrumb Navigation -->
    <nav aria-label="breadcrumb" class="mb-3">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link to="/inventory" class="text-tertiary-medium">Inventory</router-link>
        </li>
        <li class="breadcrumb-item">
          <router-link to="/inventory/categories" class="text-tertiary-medium">Categories</router-link>
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

    <!-- Main Content (Only show when not loading and no error) -->
    <div v-if="!loading && !error">
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

    <!-- Main Content (Only show when not loading and no error) -->
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
          <button class="btn btn-export btn-sm btn-with-icon-sm">
            <Download :size="14" />
            Export
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
                    <p class="mb-0 text-tertiary-dark">{{ products.length }}</p>
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
                  <option value="all">All Products</option>
                  <option v-for="subCat in categoryData.sub_categories" :key="subCat.id || subCat.name" :value="subCat.id || subCat.name">
                    {{ subCat.name }}
                  </option>
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
              <!-- UPDATED: Show actual subcategory with editing capability -->
              <select 
                class="form-select form-select-sm"
                :value="product.subcategory || ''"
                @change="updateProductSubcategory(product._id, $event.target.value)"
              >
                <option value="">None</option>
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
                  title="Remove from Category"
                >
                  <Trash2 :size="12" />
                </button>
              </div>
            </td>
          </tr>
        </template>
      </DataTable>

      <!-- Empty State -->
      <div v-if="products.length === 0" class="text-center py-5">
        <div class="card">
          <div class="card-body py-5">
            <Package :size="48" class="text-tertiary-medium mb-3" />
            <p class="text-tertiary-medium mb-3">No products found in this category</p>
            <button class="btn btn-primary btn-with-icon">
              <Plus :size="16" />
              Add First Product
            </button>
          </div>
        </div>
      </div>
    </div>
</div>
    <!-- Edit Category Modal -->
    <AddCategoryModal ref="editCategoryModal" @category-updated="onCategoryUpdated" />
  </div>
</template>

<script>
import DataTable from '@/components/common/TableTemplate.vue'
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
      
      // Store the category ID from route
      categoryId: null,
      
      // Initialize as empty - will be populated by API
      categoryData: {},
      
      // Products array - will be extracted from sub_categories
      products: []
    }
  },
  computed: {
  // Filter products based on categoryFilter
    filteredProducts() {
      if (this.categoryFilter === 'all') {
        return this.products
      }
      return this.products.filter(product => {
        const productSubcategory = product.subcategory || product.subcategory_id || product.subcategory_name
        return productSubcategory === this.categoryFilter
      })
    },
    
    paginatedProducts() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredProducts.slice(start, end)
    },

    isAllSelected() {
      // FIX: Use _id instead of id
      const currentPageProductIds = this.paginatedProducts.map(p => p._id)
      return currentPageProductIds.length > 0 && 
            currentPageProductIds.every(id => this.selectedProducts.includes(id))
    },

    isIndeterminate() {
      // FIX: Use _id instead of id
      const currentPageProductIds = this.paginatedProducts.map(p => p._id)
      const selectedOnPage = currentPageProductIds.filter(id => this.selectedProducts.includes(id))
      return selectedOnPage.length > 0 && selectedOnPage.length < currentPageProductIds.length
    }
  },
  methods: {
        // ==========================================
        // API METHODS
        // ==========================================
        
        // Fetch specific category data from API using the category ID
      async fetchCategoryData(categoryId) {
        this.loading = true
        this.error = null
        
        try {
          console.log('Fetching category with ID:', categoryId)
          
          const response = await categoryApiService.FindCategoryData({ id: categoryId })
          console.log('API Response:', response)
          
          // Handle the specific response structure from your API
          if (response.category && typeof response.category === 'object') {
            this.categoryData = response.category
            console.log('Using response.category')
          } else if (response.data && typeof response.data === 'object') {
            this.categoryData = response.data
            console.log('Using response.data')
          } else if (response && typeof response === 'object' && !Array.isArray(response) && !response.message) {
            // Only use response directly if it doesn't have a message field (meaning it's the actual category data)
            this.categoryData = response
            console.log('Using response directly')
          } else {
            console.warn('Unexpected response structure:', response)
            this.categoryData = {}
          }
          
          console.log('Final categoryData:', this.categoryData)
          console.log('Category name:', this.categoryData.category_name)
          console.log('Sub-categories:', this.categoryData.sub_categories)
          
          // Extract products from sub_categories
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
        
        // Use your FindProdcategory API method
        const completeProducts = await categoryApiService.FindProdcategory({ id: categoryId })
        console.log('Complete products fetched:', completeProducts)
        
        // Simply assign the complete products
        this.products = completeProducts
        
        console.log('Final products:', this.products)
        console.log('Total products:', this.products.length)
        
      } catch (error) {
        console.error('Error fetching complete products:', error)
        // Fallback to empty products array
        this.products = []
        throw error
      }
    },
    // Load all category data
    async loadCategoryData(categoryId) {
      if (!categoryId) {
        console.error('No category ID provided')
        this.error = 'No category ID provided'
        return
      }
      
      await this.fetchCategoryData(categoryId)
    },

    // Retry loading data
    async retryLoad() {
      const categoryId = this.$route.query.id || this.$route.params.id
      if (categoryId) {
        await this.loadCategoryData(categoryId)
      } else {
        this.error = 'No category ID available for retry'
      }
    },

    // Refresh category data when updated
    onCategoryUpdated() {
      const categoryId = this.$route.query.id || this.$route.params.id
      if (categoryId) {
        this.loadCategoryData(categoryId)
      }
    },

    // ==========================================
    // DATA PROCESSING METHODS
    // ==========================================
    
    // Extract products from sub_categories
    extractProductsFromSubcategories() {
      this.products = []
      
      if (this.categoryData.sub_categories && Array.isArray(this.categoryData.sub_categories)) {
        this.categoryData.sub_categories.forEach(subCategory => {
          if (subCategory.products && Array.isArray(subCategory.products)) {
            // Add subcategory info to each product
            const productsWithSubcategory = subCategory.products.map(product => ({
              ...product,
              subcategory: subCategory.name,
              subcategory_id: subCategory._id || subCategory.id || subCategory.name,
              subcategory_name: subCategory.name
            }))
            
            this.products.push(...productsWithSubcategory)
          }
        })
      }
      
      console.log('Extracted products:', this.products)
    },

    // ==========================================
    // UI INTERACTION METHODS
    // ==========================================
    
    // Apply filter when subcategory filter changes
    applyFilter() {
      this.currentPage = 1 // Reset to first page when filter changes
    },

    // Handle page change
    handlePageChange(page) {
      this.currentPage = page
    },

    // Handle edit category button click
    handleEditCategory() {
      console.log('Edit category button clicked')
      
      // Call the modal's openEditMode method with category data
      if (this.$refs.editCategoryModal) {
        this.$refs.editCategoryModal.openEditMode(this.categoryData)
      } else {
        console.error('EditCategoryModal ref not found')
      }
    },

    // Handle add sub-category button click
    handleAddSubCategory() {
      console.log('Add sub-category button clicked')
      // TODO: Implement add sub-category functionality
      // This could open a separate modal or allow inline editing
    },

    // ==========================================
    // PRODUCT SELECTION METHODS
    // ==========================================
    
    // Toggle select all products on current page
    toggleSelectAll() {
      const currentPageProductIds = this.paginatedProducts.map(p => p.id)
      
      if (this.isAllSelected) {
        // Deselect all products on current page
        this.selectedProducts = this.selectedProducts.filter(id => !currentPageProductIds.includes(id))
      } else {
        // Select all products on current page
        const newSelections = currentPageProductIds.filter(id => !this.selectedProducts.includes(id))
        this.selectedProducts = [...this.selectedProducts, ...newSelections]
      }
    },

    // ==========================================
    // PRODUCT MANAGEMENT METHODS
    // ==========================================
    
    // Update product subcategory
    updateProductSubcategory(productId, newSubcategory) {
      const product = this.products.find(p => p.id === productId)
      if (product) {
        product.subcategory = newSubcategory || null
        product.subcategory_id = newSubcategory || null
        product.subcategory_name = newSubcategory || null
        console.log(`Updated ${productId} subcategory to:`, newSubcategory || 'None')
        // TODO: Call API to update product subcategory
        // Example: await productsApi.updateProduct(productId, { subcategory: newSubcategory })
      }
    },

    // Remove single product from category
    removeProductFromCategory(product) {
      const confirmed = confirm(`Are you sure you want to remove "${product.name || product.product_name}" from the "${this.categoryData.category_name}" category?\n\nThe product will become uncategorized.`)
      if (!confirmed) return
      
      console.log('Remove product from category:', product.id)
      // TODO: Implement removing product from category (make it uncategorized)
      // Example: await productsApi.updateProduct(product.id, { category: null, subcategory: null })
      
      // For now, remove from local array
      const index = this.products.findIndex(p => p.id === product.id)
      if (index > -1) {
        this.products.splice(index, 1)
      }
    },

    // Remove selected products from category
    removeSelectedFromCategory() {
      if (this.selectedProducts.length === 0) return
      
      const productNames = this.selectedProducts
        .map(id => {
          const product = this.products.find(p => p.id === id)
          return product?.name || product?.product_name
        })
        .filter(Boolean)
        .slice(0, 3) // Show first 3 names
      
      let confirmMessage = `Are you sure you want to remove ${this.selectedProducts.length} product(s) from the "${this.categoryData.category_name}" category?\n\nThe products will become uncategorized.`
      
      if (productNames.length > 0) {
        confirmMessage += `\n\nProducts to be removed:\n${productNames.join(', ')}`
        if (this.selectedProducts.length > 3) {
          confirmMessage += `\n...and ${this.selectedProducts.length - 3} more`
        }
      }
      
      const confirmed = confirm(confirmMessage)
      if (!confirmed) return
      
      console.log('Remove selected products from category:', this.selectedProducts)
      // TODO: Implement bulk removal from category
      
      // For now, remove from local array
      this.products = this.products.filter(product => !this.selectedProducts.includes(product.id))
      
      // Clear selection after removal
      this.selectedProducts = []
    },

    // ==========================================
    // UTILITY METHODS
    // ==========================================
    
    // Format price for display
    formatPrice(price) {
      return parseFloat(price || 0).toFixed(2)
    },

    // Format date for display
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },

    // Get status class for badge styling
    getStatusClass(status) {
      if (status === 'active') {
        return 'badge bg-success text-white'
      } else if (status === 'inactive') {
        return 'badge bg-danger text-white'
      }
      return 'badge bg-secondary text-white'
    },
    
    // Get stock class for color coding
    getStockClass(stock) {
      if (stock === 0) return 'text-danger fw-bold'
      if (stock <= 15) return 'text-warning fw-semibold'
      return 'text-success fw-medium'
    }
  },
  
  async mounted() {
    // Debug: Check what we have in the route
    console.log('Route params:', this.$route.params)
    console.log('Route query:', this.$route.query)
    
    // Get category ID from query or params
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

.text-primary-dark {
  color: var(--primary-dark) !important;
}

.bg-primary-light {
  background-color: var(--primary-light) !important;
}

.bg-neutral-light {
  background-color: var(--neutral-light) !important;
}

/* Loading and empty states */
.spinner-border {
  width: 2rem;
  height: 2rem;
}

/* Breadcrumb Styling */
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

/* Action Bar Controls */
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

/* Filter Dropdown */
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

/* Category Image Placeholder */
.category-image-placeholder {
  width: 100%;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed var(--neutral);
}

/* Card styling */
.card {
  border: 1px solid var(--neutral);
  border-radius: 0.75rem;
}

.card-body {
  padding: 1.5rem;
}

.card-header {
  border-bottom: 1px solid var(--neutral);
  border-top-left-radius: 0.75rem;
  border-top-right-radius: 0.75rem;
}

/* Badge styling for sub-categories */
.badge {
  font-size: 0.875rem;
  font-weight: 500;
}

/* Form controls focus states */
.form-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25);
}

/* Responsive adjustments */
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
/* Loading and empty states */
.spinner-border {
  width: 2rem;
  height: 2rem;
}
</style>