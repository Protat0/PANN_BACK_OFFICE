<template>
  <div class="container-fluid pt-2 pb-4 uncategorized-page">
    <!-- Breadcrumb Navigation -->
    <nav aria-label="breadcrumb" class="mb-3">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link to="/inventory" class="text-tertiary-medium">Inventory</router-link>
        </li>
        <li class="breadcrumb-item">
          <router-link to="/categories" class="text-tertiary-medium">Categories</router-link>
        </li>
        <li class="breadcrumb-item active text-primary" aria-current="page">Uncategorized Products</li>
      </ol>
    </nav>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading uncategorized products...</span>
      </div>
      <p class="mt-2 text-muted">Loading uncategorized products...</p>
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
          <h1 class="h2 fw-bold text-primary mb-1">Uncategorized Products</h1>
          <p class="text-muted mb-0">Manage products that need to be categorized</p>
        </div>
        <div class="d-flex gap-2">
          <!-- Export button -->
          <button 
            class="btn btn-export btn-sm btn-with-icon-sm" 
            type="button" 
            :disabled="isExporting || products.length === 0"
            @click="exportUncategorizedProducts()"
            title="Export uncategorized products as CSV"
          >
            <Download :size="14" />
            {{ isExporting ? 'Exporting...' : `Export (${products.length})` }}
          </button>
        </div>
      </div>

      <!-- Summary Card -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card shadow-sm">
            <div class="card-body">
              <div class="row">
                <div class="col-md-3">
                  <div class="text-center">
                    <div class="h2 fw-bold text-warning mb-1">{{ products.length }}</div>
                    <small class="text-muted">Total Uncategorized</small>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="text-center">
                    <div class="h2 fw-bold text-info mb-1">{{ selectedProducts.length }}</div>
                    <small class="text-muted">Selected</small>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="text-center">
                    <div class="h2 fw-bold text-success mb-1">{{ availableCategories.length }}</div>
                    <small class="text-muted">Available Categories</small>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="text-center">
                    <div class="h2 fw-bold text-primary mb-1">{{ totalValue.toFixed(2) }}</div>
                    <small class="text-muted">Total Value (₱)</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Bar -->
      <div class="action-bar-container mb-3">
        <div class="action-bar-controls">
          <div class="action-row">
            <div class="d-flex align-items-center gap-3 flex-wrap">
              <!-- Bulk Categorization -->
              <div v-if="selectedProducts.length > 0" class="d-flex align-items-center gap-2">
                <span class="text-muted">Move {{ selectedProducts.length }} product(s) to:</span>
                <select 
                  class="form-select form-select-sm" 
                  v-model="bulkTargetCategory"
                  style="min-width: 200px;"
                >
                  <option value="">Choose Category</option>
                  <option 
                    v-for="category in availableCategories" 
                    :key="category._id" 
                    :value="category._id"
                  >
                    {{ category.category_name }}
                  </option>
                </select>
                <button 
                  class="btn btn-success btn-sm"
                  @click="moveSelectedToCategory"
                  :disabled="!bulkTargetCategory || isMoving"
                >
                  <div v-if="isMoving" class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Moving...</span>
                  </div>
                  {{ isMoving ? 'Moving...' : 'Move' }}
                </button>
                <button 
                  class="btn btn-outline-secondary btn-sm"
                  @click="clearSelection"
                >
                  Clear
                </button>
              </div>

              <!-- Search -->
              <div class="search-container ms-auto">
                <div class="position-relative">
                  <input 
                    v-model="searchFilter" 
                    type="text" 
                    class="form-control form-control-sm search-input"
                    placeholder="Search products..."
                    style="min-width: 250px;"
                  />
                  <button 
                    v-if="searchFilter"
                    class="btn btn-sm btn-link position-absolute end-0 top-50 translate-middle-y"
                    @click="searchFilter = ''"
                    style="border: none; padding: 0.25rem;"
                  >
                    <X :size="16" />
                  </button>
                </div>
              </div>
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
            <th style="width: 200px;">Move to Category</th>
            <th style="width: 120px;">Stock</th>
            <th style="width: 120px;">Selling Price</th>
            <th style="width: 120px;">Supplier</th>
            <th style="width: 100px;">Date Added</th>
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
                @change="moveProductToCategory(product._id, $event.target.value)"
                :disabled="isMoving"
              >
                <option value="">Select Category</option>
                <option 
                  v-for="category in availableCategories" 
                  :key="category._id" 
                  :value="category._id"
                >
                  {{ category.category_name }}
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
            <td class="text-tertiary-dark">
              {{ formatDate(product.date_created || product.created_at) }}
            </td>
          </tr>
        </template>
      </DataTable>

      <!-- Empty State -->
      <div v-if="filteredProducts.length === 0" class="text-center py-5">
        <div class="card">
          <div class="card-body py-5">
            <Package :size="64" class="text-success mb-3" />
            <h5 class="text-success">All Products Categorized!</h5>
            <p class="text-muted mb-3">
              {{ products.length === 0 ? 
                'No uncategorized products found. All products have been properly categorized.' :
                'No products match your search criteria.' }}
            </p>
            <router-link to="/categories" class="btn btn-primary">
              <ArrowLeft :size="16" class="me-1" />
              Back to Categories
            </router-link>
          </div>
        </div>
      </div>
    </div>
    <!-- Success/Error Messages -->
    <div 
      v-if="successMessage" 
      class="alert alert-success alert-dismissible fade show fixed-top mt-3 mx-3" 
      style="z-index: 1060;"
    >
      {{ successMessage }}
      <button type="button" class="btn-close" @click="successMessage = ''"></button>
    </div>

    <div 
      v-if="errorMessage" 
      class="alert alert-danger alert-dismissible fade show fixed-top mt-3 mx-3" 
      style="z-index: 1060;"
    >
      {{ errorMessage }}
      <button type="button" class="btn-close" @click="errorMessage = ''"></button>
    </div>
  </div>
</template>

<script>
import DataTable from '@/components/common/TableTemplate.vue'
import categoryApiService from '@/services/apiCategory'
import { 
  Download,
  Package,
  X,
  ArrowLeft
} from 'lucide-vue-next'

export default {
  name: 'UncategorizedProducts',
  components: {
    DataTable,
    Download,
    Package,
    X,
    ArrowLeft
  },
  data() {
    return {
      currentPage: 1,
      itemsPerPage: 10,
      selectedProducts: [],
      loading: false,
      error: null,
      isExporting: false,
      isMoving: false,
      
      // Data
      products: [],
      availableCategories: [],
      
      // Filters
      searchFilter: '',
      
      // Bulk operations
      bulkTargetCategory: '',
      
      successMessage: '',
      errorMessage: '',

      // Constants
      UNCATEGORIZED_CATEGORY_ID: '686a4de143821e2b21f725c6'
    }
  },
  computed: {
    filteredProducts() {
      if (!this.searchFilter.trim()) {
        return this.products
      }
      
      const searchTerm = this.searchFilter.toLowerCase().trim()
      return this.products.filter(product => 
        (product.product_name || '').toLowerCase().includes(searchTerm) ||
        (product.supplier || '').toLowerCase().includes(searchTerm) ||
        (product._id || '').toLowerCase().includes(searchTerm)
      )
    },
    
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
    },

    totalValue() {
      return this.products.reduce((total, product) => {
        return total + (parseFloat(product.selling_price) || 0) * (parseInt(product.stock) || 0)
      }, 0)
    }
  },
  methods: {
    // DATA LOADING METHODS
    async loadUncategorizedProducts() {
      this.loading = true
      this.error = null
      
      try {
        console.log('Loading uncategorized products...')
        
        // Load uncategorized products from the Uncategorized category
        const products = await categoryApiService.FindProdcategory({ 
          id: this.UNCATEGORIZED_CATEGORY_ID 
        })
        
        this.products = Array.isArray(products) ? products : []
        console.log(`Loaded ${this.products.length} uncategorized products`)
        
      } catch (error) {
        console.error('Error loading uncategorized products:', error)
        this.error = error.message || 'Failed to load uncategorized products'
        this.products = []
      } finally {
        this.loading = false
      }
    },

    async loadAvailableCategories() {
      try {
        console.log('🔄 Loading available categories...')
        
        const response = await categoryApiService.CategoryData()
        
        // Handle different response structures
        let allCategories = []
        if (response.data && Array.isArray(response.data)) {
          allCategories = response.data
        } else if (response.categories && Array.isArray(response.categories)) {
          allCategories = response.categories
        } else if (Array.isArray(response)) {
          allCategories = response
        }
        
        // Filter out Uncategorized category
        this.availableCategories = allCategories.filter(category => 
          category.category_name !== "Uncategorized" && 
          category._id !== this.UNCATEGORIZED_CATEGORY_ID &&
          !category.isDeleted
        )
        
        console.log(`✅ Loaded ${this.availableCategories.length} available categories`)

      } catch (error) {
        console.error('❌ Error loading categories:', error)
        this.availableCategories = []
      }
    },

    // PRODUCT MOVEMENT METHODS
    async moveProductToCategory(productId, categoryId) {
      if (!categoryId) return
      
      try {
        this.isMoving = true
        
        const product = this.products.find(p => p._id === productId)
        const category = this.availableCategories.find(c => c._id === categoryId)
        
        if (!product || !category) {
          throw new Error('Product or category not found')
        }
        
        console.log(`Moving product ${product.product_name} to category ${category.category_name}`)
        
        // FIXED: Explicitly set subcategory to "None" instead of null
        await categoryApiService.SubCatChangeTab({
          product_id: productId,
          new_subcategory: "None", // ← Changed from null to "None"
          category_id: categoryId // The target category
        })
        
        // Remove from local uncategorized array since it's now categorized
        this.products = this.products.filter(p => p._id !== productId)
        
        // Clear from selection if selected
        this.selectedProducts = this.selectedProducts.filter(id => id !== productId)
        
        this.showSuccessMessage(
          `"${product.product_name}" moved to "${category.category_name}" category (subcategory: None)`
        )
        
      } catch (error) {
        console.error('Error moving product:', error)
        this.showErrorMessage(`Failed to move product: ${error.message}`)
      } finally {
        this.isMoving = false
      }
    },

    async moveSelectedToCategory() {
      if (this.selectedProducts.length === 0 || !this.bulkTargetCategory) return
      
      try {
        this.isMoving = true
        
        const category = this.availableCategories.find(c => c._id === this.bulkTargetCategory)
        if (!category) {
          throw new Error('Target category not found')
        }
        
        console.log(`Bulk moving ${this.selectedProducts.length} products to ${category.category_name}`)
        
        // FIXED: Explicitly set subcategory to "None" for all products
        const movePromises = this.selectedProducts.map(productId => 
          categoryApiService.SubCatChangeTab({
            product_id: productId,
            new_subcategory: "None", // ← Changed from null to "None"
            category_id: this.bulkTargetCategory
          })
        )
        
        const results = await Promise.allSettled(movePromises)
        
        // Count successes
        const successful = results.filter(r => r.status === 'fulfilled').length
        const failed = results.filter(r => r.status === 'rejected').length
        
        // Remove successfully moved products
        const failedProductIds = results
          .map((result, index) => result.status === 'rejected' ? this.selectedProducts[index] : null)
          .filter(Boolean)
        
        this.products = this.products.filter(product => 
          !this.selectedProducts.includes(product._id) || failedProductIds.includes(product._id)
        )
        
        // Clear selections and reset form
        this.selectedProducts = []
        this.bulkTargetCategory = ''
        
        // Show results
        if (successful > 0) {
          this.showSuccessMessage(
            `${successful} product(s) moved to "${category.category_name}" (subcategory: None) successfully!` +
            (failed > 0 ? ` ${failed} failed.` : '')
          )
        }
        
        if (failed > 0 && successful === 0) {
          this.showErrorMessage(`Failed to move ${failed} product(s)`)
        }
        
      } catch (error) {
        console.error('Error in bulk move:', error)
        this.showErrorMessage(`Bulk move failed: ${error.message}`)
      } finally {
        this.isMoving = false
      }
    },

    // SELECTION METHODS
    toggleSelectAll() {
      const currentPageProductIds = this.paginatedProducts.map(p => p._id)
      
      if (this.isAllSelected) {
        this.selectedProducts = this.selectedProducts.filter(id => !currentPageProductIds.includes(id))
      } else {
        const newSelections = currentPageProductIds.filter(id => !this.selectedProducts.includes(id))
        this.selectedProducts = [...this.selectedProducts, ...newSelections]
      }
    },

    clearSelection() {
      this.selectedProducts = []
      this.bulkTargetCategory = ''
    },

    handlePageChange(page) {
      this.currentPage = page
    },

    // EXPORT METHODS
    async exportUncategorizedProducts() {
      try {
        this.isExporting = true
        
        const csvContent = this.convertProductsToCSV()
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        const timestamp = new Date().toISOString().split('T')[0]
        link.download = `uncategorized_products_${timestamp}.csv`
        
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        this.showSuccessMessage(`${this.products.length} uncategorized products exported successfully`)
        
      } catch (error) {
        console.error('Export failed:', error)
        this.showErrorMessage(`Export failed: ${error.message}`)
      } finally {
        this.isExporting = false
      }
    },

    convertProductsToCSV() {
      const headers = [
        'Product ID',
        'Product Name',
        'Stock',
        'Selling Price (₱)',
        'Supplier',
        'Date Added'
      ]
      
      const csvComments = [
        '# Uncategorized Products Report',
        `# Generated: ${new Date().toISOString()}`,
        `# Total Products: ${this.products.length}`,
        `# Total Value: ₱${this.totalValue.toFixed(2)}`,
        ''
      ]
      
      const rows = this.products.map(product => [
        product._id,
        `"${product.product_name || 'Unknown'}"`,
        product.stock || 0,
        product.selling_price || 0,
        `"${product.supplier || 'N/A'}"`,
        this.formatDate(product.date_created || product.created_at) || 'N/A'
      ])
      
      return [
        ...csvComments,
        headers.join(','),
        ...rows.map(row => row.join(','))
      ].join('\n')
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

    getStockClass(stock) {
      if (stock === 0) return 'text-danger fw-bold'
      if (stock <= 15) return 'text-warning fw-semibold'
      return 'text-success fw-medium'
    },

    showSuccessMessage(message) {
      console.log('✅ Success:', message)
      this.successMessage = message
      this.errorMessage = ''
      
      // Auto-hide after 5 seconds
      setTimeout(() => {
        this.successMessage = ''
      }, 5000)
    },

    showErrorMessage(message) {
      console.error('❌ Error:', message)
      this.errorMessage = message
      this.successMessage = ''
      
      // Auto-hide after 7 seconds
      setTimeout(() => {
        this.errorMessage = ''
      }, 7000)
    },
    async retryLoad() {
      await Promise.all([
        this.loadUncategorizedProducts(),
        this.loadAvailableCategories()
      ])
    }
  },
  
  async mounted() {
    await Promise.all([
      this.loadUncategorizedProducts(),
      this.loadAvailableCategories()
    ])
  }
}
</script>

<style scoped>
.uncategorized-page {
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

.search-input {
  padding-right: 2.5rem;
}

.card {
  border: 1px solid var(--neutral);
  border-radius: 0.75rem;
}

.card-body {
  padding: 1.5rem;
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
  
  .search-container {
    margin-left: 0 !important;
    margin-top: 1rem;
  }
}

.alert {
  border-radius: 0.5rem;
  border: none;
}

.alert-success {
  background-color: #d1edff;
  color: #0f5132;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.btn-close {
  filter: brightness(0.8);
}

.btn-close:hover {
  filter: brightness(0.6);
}
</style>