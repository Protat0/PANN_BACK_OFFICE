<template>
  <div class="container-fluid pt-2 pb-4 products-page">
    <!-- Page Title -->
    <div class="mb-3">
      <h1 class="h3 fw-semibold text-primary-dark mb-0">Product Management</h1>
    </div>

    <!-- Reports Section -->
    <div class="row mb-3" v-if="!loading">
      <div class="col-6 col-md-3 mb-2">
        <CardTemplate
          size="xs"
          border-color="danger"
          border-position="start"
          title="Low Stock"
          :value="lowStockCount"
          subtitle="Critical Items"
          clickable
          @click="showLowStockReport"
        />
      </div>
      <div class="col-6 col-md-3 mb-2">
        <CardTemplate
          size="xs"
          border-color="info"
          border-position="start"
          title="Expiring"
          :value="expiringCount"
          subtitle="30 Days"
          clickable
          @click="showExpiringReport"
        />
      </div>
      <div class="col-6 col-md-3 mb-2">
        <CardTemplate
          size="xs"
          border-color="success"
          border-position="start"
          title="Total"
          :value="products.length"
          subtitle="Products"
        />
      </div>
      <div class="col-6 col-md-3 mb-2">
        <CardTemplate
          size="xs"
          border-color="primary"
          border-position="start"
          title="Categories"
          value="3"
          subtitle="Active"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && products.length === 0" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-tertiary-medium">Loading products...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="alert alert-danger text-center" role="alert">
      <p class="mb-3">{{ error }}</p>
      <button class="btn btn-primary" @click="refreshData">Try Again</button>
    </div>

    <!-- Action Bar and Filters - Separate Section -->
    <div v-if="!loading || products.length > 0" class="action-bar-container mb-3">
      <!-- Integrated Header with Actions and Filters -->
      <div class="action-bar-controls">
        <!-- Action Row: Action Buttons and Filters -->
        <div class="action-row">
          <!-- Left Side: Main Actions (Always visible when no selection) -->
          <div v-if="selectedProducts.length === 0" class="d-flex gap-2">
            <!-- Add Products Dropdown -->
            <div class="dropdown" ref="addDropdown">
              <button 
                class="btn btn-success btn-sm btn-with-icon-sm dropdown-toggle"
                type="button"
                @click="toggleAddDropdown"
                :class="{ 'active': showAddDropdown }"
              >
                <Plus :size="14" />
                ADD ITEM
              </button>
              
              <div 
                class="dropdown-menu custom-dropdown-menu" 
                :class="{ 'show': showAddDropdown }"
              >
                <button class="dropdown-item custom-dropdown-item" @click="handleSingleProduct">
                  <div class="d-flex align-items-center gap-3">
                    <Plus :size="16" class="text-primary" />
                    <div>
                      <div class="fw-semibold">Single Product</div>
                      <small class="text-muted">Add one product manually</small>
                    </div>
                  </div>
                </button>
                
                <button class="dropdown-item custom-dropdown-item" @click="handleBulkAdd">
                  <div class="d-flex align-items-center gap-3">
                    <Package :size="16" class="text-primary" />
                    <div>
                      <div class="fw-semibold">Bulk Entry</div>
                      <small class="text-muted">Add multiple products (5-20 items)</small>
                    </div>
                  </div>
                </button>
                
                <button class="dropdown-item custom-dropdown-item" @click="handleImport">
                  <div class="d-flex align-items-center gap-3">
                    <FileText :size="16" class="text-primary" />
                    <div>
                      <div class="fw-semibold">Import File</div>
                      <small class="text-muted">Upload CSV/Excel (20+ items)</small>
                    </div>
                  </div>
                </button>
              </div>
            </div>

            <button class="btn btn-outline-secondary btn-sm" @click="handleImport">IMPORT</button>
            <button 
              class="btn btn-outline-secondary btn-sm"
              @click="exportData"
            >
              EXPORT
            </button>
          </div>

          <!-- Selection Actions (Visible when items are selected) -->
          <div v-if="selectedProducts.length > 0" class="d-flex gap-2">
            <button 
              class="btn btn-delete btn-sm btn-with-icon-sm"
              @click="deleteSelected"
            >
              <Trash2 :size="14" />
              DELETE
            </button>
          </div>

          <!-- Right Side: Filters and Search -->
          <div class="d-flex align-items-center gap-2">
            <!-- Search Toggle -->
            <button 
              class="btn btn-secondary btn-sm"
              @click="toggleSearchMode"
              :class="{ 'active': searchMode }"
              style="height: calc(1.5em + 0.75rem + 2px); display: flex; align-items: center; justify-content: center; padding: 0 0.75rem;"
            >
              <Search :size="16" />
            </button>

            <!-- Filter Dropdowns (Hidden when search is active) -->
            <template v-if="!searchMode">
              <div class="filter-dropdown">
                <label class="filter-label">Category</label>
                <select 
                  class="form-select form-select-sm" 
                  v-model="categoryFilter" 
                  @change="applyFilters"
                >
                  <option value="all">All items</option>
                  <option value="noodles">Noodles</option>
                  <option value="drinks">Drinks</option>
                  <option value="toppings">Toppings</option>
                </select>
              </div>

              <div class="filter-dropdown">
                <label class="filter-label">Stock alert</label>
                <select 
                  class="form-select form-select-sm" 
                  v-model="stockFilter" 
                  @change="applyFilters"
                >
                  <option value="all">All items</option>
                  <option value="low-stock">Low Stock</option>
                  <option value="in-stock">In Stock</option>
                  <option value="out-of-stock">Out of Stock</option>
                </select>
              </div>
            </template>

            <!-- Search Bar (Visible when search mode is active) -->
            <div v-if="searchMode" class="search-container">
              <div class="position-relative">
                <input 
                  ref="searchInput"
                  v-model="searchFilter" 
                  @input="applyFilters"
                  type="text" 
                  class="form-control form-control-sm search-input"
                  placeholder="Search"
                />
                <button 
                  class="btn btn-sm btn-link position-absolute end-0 top-50 translate-middle-y"
                  @click="clearSearch"
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

    <!-- Data Table - Separate Section -->
    <DataTable
      v-if="!loading || products.length > 0"
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
                @change="selectAll" 
                :checked="allSelected"
                :indeterminate="someSelected"
              />
            </th>
            <th>
              Item name
              <ChevronUp :size="14" class="ms-1" />
            </th>
            <th style="width: 120px;">Category</th>
            <th style="width: 100px;">Price</th>
            <th style="width: 100px;">Cost</th>
            <th style="width: 80px;">Margin</th>
            <th style="width: 100px;">In stock</th>
            <th style="width: 160px;">Actions</th>
          </tr>
        </template>

        <template #body>
          <tr 
            v-for="product in paginatedProducts"
            :key="product._id"
            :class="getRowClass(product)"
          >
            <td>
              <input 
                type="checkbox" 
                class="form-check-input"
                :value="product._id"
                v-model="selectedProducts"
              />
            </td>
            <td>
              <div :class="['fw-medium', getProductNameClass(product)]">
                {{ product.product_name }}
              </div>
            </td>
            <td>
              <span :class="['badge', 'rounded-pill', getCategoryBadgeClass(product.category_id)]">
                {{ getCategoryName(product.category_id) }}
              </span>
            </td>
            <td class="text-end fw-medium">
              ₱{{ formatPrice(product.selling_price) }}
            </td>
            <td class="text-end fw-medium">
              ₱{{ formatPrice(product.cost_price) }}
            </td>
            <td class="text-center fw-medium">
              {{ calculateMargin(product.cost_price, product.selling_price) }}%
            </td>
            <td class="text-end">
              <span :class="getStockDisplayClass(product)">
                {{ product.stock || '—' }}
              </span>
            </td>
            <td>
              <div class="d-flex gap-1 justify-content-center">
                <button 
                  class="btn btn-outline-secondary btn-icon-only btn-lg" 
                  @click="editProduct(product)"
                  data-bs-toggle="tooltip"
                  title="Edit Product"
                >
                  <Edit :size="12" />
                </button>
                <button 
                  class="btn btn-outline-primary btn-icon-only btn-lg" 
                  @click="viewProduct(product)"
                  data-bs-toggle="tooltip"
                  title="View Details"
                >
                  <Eye :size="12" />
                </button>
                <button 
                  class="btn btn-outline-info btn-icon-only btn-lg" 
                  @click="restockProduct(product)"
                  data-bs-toggle="tooltip"
                  title="Update Stock"
                >
                  <Package :size="12" />
                </button>
                <button 
                  class="btn btn-outline-danger btn-icon-only btn-lg" 
                  @click="deleteProduct(product)"
                  data-bs-toggle="tooltip"
                  title="Delete Product"
                >
                  <Trash2 :size="12" />
                </button>
              </div>
            </td>
          </tr>
        </template>
    </DataTable>

    <!-- Empty State -->
    <div v-if="!loading && filteredProducts.length === 0 && !error" class="text-center py-5">
      <div class="card">
        <div class="card-body py-5">
          <Package :size="48" class="text-tertiary-medium mb-3" />
          <p class="text-tertiary-medium mb-3">
            {{ products.length === 0 ? 'No products found' : 'No products match the current filters' }}
          </p>
          <button 
            v-if="products.length === 0" 
            class="btn btn-primary btn-with-icon" 
            @click="handleSingleProduct"
          >
            <Plus :size="16" />
            Add First Product
          </button>
          <button 
            v-else 
            class="btn btn-secondary btn-with-icon"
            @click="clearFilters"
          >
            <RefreshCw :size="16" />
            Clear Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Modular Components -->
    <AddProductModal
      ref="addProductModal"
      @success="handleProductSuccess"
    />

    <StockUpdateModal
      ref="stockUpdateModal"
      @success="handleStockUpdateSuccess"
    />

    <ViewProductModal
      ref="viewProductModal"
      @edit="editProduct"
      @restock="restockProduct"
      @toggle-status="toggleProductStatus"
      @generate-barcode="generateProductBarcode"
    />

    <ReportsModal
      ref="reportsModal"
      @view-product="viewProduct"
      @edit-product="editProduct"
      @restock-product="restockProduct"
    />

    <ImportModal
      ref="importModal"
      @import-completed="handleImportSuccess"
      @import-failed="handleImportError"
    />
  </div>
</template>

<script>
import { useToast } from '@/composables/useToast.js'
import productsApiService from '../../services/apiProducts.js'
import AddProductModal from '../../components/products/AddProductModal.vue'
import StockUpdateModal from '../../components/products/StockUpdateModal.vue'
import ViewProductModal from '../../components/products/ViewProductModal.vue'
import ReportsModal from '../../components/products/ReportsModal.vue'
import DataTable from '@/components/common/TableTemplate.vue'
import CardTemplate from '@/components/common/CardTemplate.vue'
import ImportModal from '../../components/products/ImportModal.vue'
import { 
  Plus, 
  Search,
  X,
  ChevronUp,
  Package, 
  Trash2,
  RefreshCw,
  FileText,
  Edit,
  Eye,
  Lock,
  Unlock
} from 'lucide-vue-next'

export default {
  name: 'Products',
  components: {
    AddProductModal,
    StockUpdateModal,
    ViewProductModal,
    ImportModal,
    ReportsModal,
    DataTable,
    CardTemplate,
    Plus,
    Search,
    X,
    ChevronUp,
    Package,
    Trash2,
    RefreshCw,
    FileText,
    Edit,
    Eye,
    Lock,
    Unlock
  },
  setup() {
    const { success, error, warning, info } = useToast()
    
    return {
      toast: { success, error, warning, info }
    }
  },
  data() {
    return {
      currentPage: 1,
      itemsPerPage: 10,
      products: [],
      filteredProducts: [],
      selectedProducts: [],
      loading: false,
      error: null,
      
      // UI State
      showAddDropdown: false,
      searchMode: false,
      
      // Report data
      lowStockCount: 0,
      expiringCount: 0,
      
      // Filters
      categoryFilter: 'all',
      stockFilter: 'all',
      searchFilter: ''
    }
  },
  computed: {
    paginatedProducts() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredProducts.slice(start, end)
    },

    allSelected() {
      return this.paginatedProducts.length > 0 && 
            this.selectedProducts.length === this.paginatedProducts.length
    },

    someSelected() {
      return this.selectedProducts.length > 0 && 
            this.selectedProducts.length < this.paginatedProducts.length
    }
  },

  async mounted() {
    await this.fetchProducts()
    document.addEventListener('click', this.handleClickOutside)
  },
  
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
  },

  methods: {
    handleClickOutside(event) {
      if (this.$refs.addDropdown && !this.$refs.addDropdown.contains(event.target)) {
        this.showAddDropdown = false
      }
    },

    toggleAddDropdown(event) {
      event.stopPropagation()
      this.showAddDropdown = !this.showAddDropdown
    },
    
    closeAddDropdown() {
      this.showAddDropdown = false
    },

    toggleSearchMode() {
      this.searchMode = !this.searchMode
      
      if (this.searchMode) {
        this.$nextTick(() => {
          if (this.$refs.searchInput) {
            this.$refs.searchInput.focus()
          }
        })
      } else {
        this.searchFilter = ''
        this.applyFilters()
      }
    },

    clearSearch() {
      this.searchFilter = ''
      this.searchMode = false
      this.applyFilters()
    },
    
    handleSingleProduct(event) {
      if (event) event.stopPropagation()
      this.showAddProductModal()
      this.closeAddDropdown()
    },
    
    handleBulkAdd(event) {
      event.stopPropagation()
      this.$router.push('/products/bulk')
      this.closeAddDropdown()
    },
    
    handleImport(event) {
      event.stopPropagation()
      
      const importModalElement = document.getElementById('importModal')
      
      if (importModalElement) {
        try {
          const modal = new bootstrap.Modal(importModalElement)
          modal.show()
        } catch (error) {
          console.error('❌ Error creating/showing modal:', error)
          this.toast.error('Failed to open import modal')
        }
      } else {
        console.error('❌ Modal element #importModal not found in DOM')
        this.toast.error('Import modal not available')
      }
      
      this.closeAddDropdown()
    },

    async fetchProducts() {
      this.loading = true
      this.error = null
      
      try {
        const data = await productsApiService.getProducts()
        
        if (data.results) {
          this.products = data.results
        } else if (Array.isArray(data)) {
          this.products = data
        } else {
          this.products = data.products || []
        }
        
        this.applyFilters()
        await this.fetchReportCounts()
        
        // Success toast for data loading (optional - only for manual refresh)
        if (!this.loading) {
          this.toast.info(`Loaded ${this.products.length} products`, { duration: 2000 })
        }
      } catch (error) {
        console.error('Error fetching products:', error)
        this.error = `Failed to load products: ${error.message}`
        this.toast.error(`Failed to load products: ${error.message}`, {
          duration: 6000,
          persistent: false
        })
      } finally {
        this.loading = false
      }
    },

    async fetchReportCounts() {
      try {
        const lowStockData = await productsApiService.getLowStockProducts()
        this.lowStockCount = Array.isArray(lowStockData) ? lowStockData.length : (lowStockData.count || 0)
        
        const expiringData = await productsApiService.getExpiringProducts({ days_ahead: 30 })
        this.expiringCount = Array.isArray(expiringData) ? expiringData.length : (expiringData.count || 0)
        
        // Show warnings for critical inventory levels
        if (this.lowStockCount > 0) {
          this.toast.warning(`${this.lowStockCount} items are running low on stock`, {
            duration: 5000
          })
        }
        
        if (this.expiringCount > 0) {
          this.toast.info(`${this.expiringCount} items will expire within 30 days`, {
            duration: 4000
          })
        }
      } catch (error) {
        console.error('Error fetching report counts:', error)
        this.toast.error('Failed to load inventory alerts')
      }
    },

    async showLowStockReport() {
      if (this.$refs.reportsModal && this.$refs.reportsModal.showLowStockModal) {
        await this.$refs.reportsModal.showLowStockModal()
        this.toast.info('Showing low stock report')
      }
    },

    async showExpiringReport() {
      if (this.$refs.reportsModal && this.$refs.reportsModal.showExpiringModal) {
        await this.$refs.reportsModal.showExpiringModal()
        this.toast.info('Showing expiring products report')
      }
    },

    applyFilters() {
      let filtered = [...this.products]

      if (this.categoryFilter !== 'all') {
        filtered = filtered.filter(product => product.category_id === this.categoryFilter)
      }

      if (this.stockFilter !== 'all') {
        if (this.stockFilter === 'out-of-stock') {
          filtered = filtered.filter(product => product.stock === 0)
        } else if (this.stockFilter === 'low-stock') {
          filtered = filtered.filter(product => 
            product.stock > 0 && product.stock <= product.low_stock_threshold
          )
        } else if (this.stockFilter === 'in-stock') {
          filtered = filtered.filter(product => product.stock > product.low_stock_threshold)
        }
      }

      if (this.searchFilter.trim()) {
        const search = this.searchFilter.toLowerCase()
        filtered = filtered.filter(product => 
          product.product_name?.toLowerCase().includes(search) ||
          product.SKU?.toLowerCase().includes(search) ||
          product._id?.toLowerCase().includes(search)
        )
      }

      this.currentPage = 1
      this.selectedProducts = []
      this.filteredProducts = filtered
    },

    clearFilters() {
      this.categoryFilter = 'all'
      this.stockFilter = 'all'
      this.searchFilter = ''
      this.searchMode = false
      this.applyFilters()
      this.toast.info('Filters cleared')
    },

    async refreshData() {
      await this.fetchProducts()
      this.toast.success('Product data refreshed')
    },

    selectAll(event) {
      if (event.target.checked) {
        this.selectedProducts = this.paginatedProducts.map(product => product._id)
        this.toast.info(`Selected ${this.selectedProducts.length} products`)
      } else {
        this.selectedProducts = []
        this.toast.info('Selection cleared')
      }
    },

    async deleteSelected() {
      if (this.selectedProducts.length === 0) {
        this.toast.warning('No products selected')
        return
      }
      
      const confirmed = confirm(`Are you sure you want to delete ${this.selectedProducts.length} product(s)?`)
      if (!confirmed) return

      const loadingToastId = this.toast.loading(`Deleting ${this.selectedProducts.length} product(s)...`)
      
      try {
        await productsApiService.bulkDeleteProducts(this.selectedProducts)
        this.toast.dismiss(loadingToastId)
        this.toast.success(`Successfully deleted ${this.selectedProducts.length} product(s)`)
        this.selectedProducts = []
        await this.fetchProducts()
      } catch (error) {
        console.error('Error deleting products:', error)
        this.toast.dismiss(loadingToastId)
        this.toast.error(`Failed to delete products: ${error.message}`, {
          duration: 6000
        })
      }
    },

    showAddProductModal() {
      if (this.$refs.addProductModal && this.$refs.addProductModal.openAdd) {
        this.$refs.addProductModal.openAdd()
      }
    },

    editProduct(product) {
      if (this.$refs.viewProductModal && this.$refs.viewProductModal.close) {
        this.$refs.viewProductModal.close()
      }
      if (this.$refs.addProductModal && this.$refs.addProductModal.openEdit) {
        this.$refs.addProductModal.openEdit(product)
      }
    },

    viewProduct(product) {
      if (this.$refs.viewProductModal && this.$refs.viewProductModal.open) {
        this.$refs.viewProductModal.open(product)
      }
    },

    restockProduct(product) {
      if (this.$refs.stockUpdateModal && this.$refs.stockUpdateModal.openStock) {
        this.$refs.stockUpdateModal.openStock(product)
      }
    },

    async exportData() {
      const loadingToastId = this.toast.loading('Preparing export...')
      
      try {
        const blob = await productsApiService.exportProducts({
          format: 'csv',
          filters: {
            category: this.categoryFilter !== 'all' ? this.categoryFilter : undefined,
            stock: this.stockFilter !== 'all' ? this.stockFilter : undefined,
            search: this.searchFilter || undefined
          }
        })
        
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `products_${new Date().toISOString().split('T')[0]}.csv`
        a.click()
        window.URL.revokeObjectURL(url)
        
        this.toast.dismiss(loadingToastId)
        this.toast.success(`Export completed! Downloaded ${this.filteredProducts.length} products`)
      } catch (error) {
        console.error('API export failed, falling back to client-side export:', error)
        
        const headers = ['ID', 'Name', 'Category', 'Price', 'Cost', 'Margin', 'Stock']
        const csvContent = [
          headers.join(','),
          ...this.filteredProducts.map(product => [
            product._id.slice(-6),
            `"${product.product_name}"`,
            this.getCategoryName(product.category_id),
            product.selling_price,
            product.cost_price,
            this.calculateMargin(product.cost_price, product.selling_price),
            product.stock
          ].join(','))
        ].join('\n')

        const blob = new Blob([csvContent], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `products_${new Date().toISOString().split('T')[0]}.csv`
        a.click()
        window.URL.revokeObjectURL(url)
        
        this.toast.dismiss(loadingToastId)
        this.toast.warning('Used backup export method - data exported successfully')
      }
    },

    async generateProductBarcode(product) {
      const loadingToastId = this.toast.loading(`Generating barcode for "${product.product_name}"...`)
      
      try {
        await productsApiService.generateBarcode(product._id)
        this.toast.dismiss(loadingToastId)
        this.toast.success(`Barcode generated for "${product.product_name}"`)
        await this.fetchProducts()
      } catch (error) {
        console.error('Error generating barcode:', error)
        this.toast.dismiss(loadingToastId)
        this.toast.error(`Failed to generate barcode: ${error.message}`)
      }
    },

    handleProductSuccess(result) {
      // Show success toast based on the action performed
      if (result.message) {
        this.toast.success(result.message)
      } else {
        this.toast.success('Product saved successfully')
      }
      this.fetchProducts()
    },

    handleStockUpdateSuccess(result) {
      this.toast.success(result.message || 'Stock updated successfully')
      this.fetchProducts()
    },

    handleImportSuccess(result) {
      const successCount = result.totalSuccessful || 0
      const failedCount = result.totalFailed || 0
      
      if (failedCount > 0) {
        this.toast.warning(
          `Import completed with warnings: ${successCount} products imported, ${failedCount} failed`,
          { duration: 8000 }
        )
      } else {
        this.toast.success(
          `Import completed successfully! ${successCount} products imported`,
          { duration: 6000 }
        )
      }
      
      this.fetchProducts()
    },

    handleImportError(error) {
      this.toast.error(
        `Import failed: ${error.message || 'An unexpected error occurred'}`,
        { duration: 8000, persistent: false }
      )
    },

    async deleteProduct(product) {
      const confirmed = confirm(`Are you sure you want to delete "${product.product_name}"?`)
      if (!confirmed) return

      const loadingToastId = this.toast.loading(`Deleting "${product.product_name}"...`)

      try {
        await productsApiService.deleteProduct(product._id)
        this.toast.dismiss(loadingToastId)
        this.toast.success(`Product "${product.product_name}" deleted successfully`)
        await this.fetchProducts()
      } catch (error) {
        console.error('Error deleting product:', error)
        this.toast.dismiss(loadingToastId)
        this.toast.error(`Failed to delete product: ${error.message}`)
      }
    },

    async toggleProductStatus(product) {
      const newStatus = product.status === 'active' ? 'inactive' : 'active'
      const action = newStatus === 'active' ? 'activate' : 'deactivate'
      
      const confirmed = confirm(`Are you sure you want to ${action} "${product.product_name}"?`)
      if (!confirmed) return

      const loadingToastId = this.toast.loading(`${action.charAt(0).toUpperCase() + action.slice(1)}ing product...`)

      try {
        await productsApiService.updateProduct(product._id, { status: newStatus })
        this.toast.dismiss(loadingToastId)
        this.toast.success(`Product "${product.product_name}" ${action}d successfully`)
        await this.fetchProducts()
      } catch (error) {
        console.error('Error updating product status:', error)
        this.toast.dismiss(loadingToastId)
        this.toast.error(`Failed to ${action} product: ${error.message}`)
      }
    },

    getCategoryName(categoryId) {
      const categories = {
        'noodles': 'Noodles',
        'drinks': 'Drinks', 
        'toppings': 'Toppings'
      }
      return categories[categoryId] || categoryId
    },

    getCategoryBadgeClass(categoryId) {
      const classes = {
        'noodles': 'text-bg-secondary',
        'drinks': 'text-bg-primary', 
        'toppings': 'text-bg-info'
      }
      return classes[categoryId] || 'text-bg-light'
    },

    getProductNameClass(product) {
      if (product.stock === 0) return 'text-danger fw-bold'
      if (product.stock <= product.low_stock_threshold) return 'text-warning fw-semibold'
      return 'text-tertiary-dark'
    },

    getRowClass(product) {
      const classes = []
      
      if (this.selectedProducts.includes(product._id)) {
        classes.push('table-primary')
      }
      
      if (product.status === 'inactive') {
        classes.push('text-muted')
      }
      
      return classes.join(' ')
    },

    getStockDisplayClass(product) {
      if (product.stock === 0) return 'text-danger fw-bold'
      if (product.stock <= product.low_stock_threshold) return 'text-warning fw-semibold'
      return 'text-tertiary-medium'
    },

    calculateMargin(costPrice, sellingPrice) {
      if (!costPrice || !sellingPrice) return 0
      const margin = ((sellingPrice - costPrice) / sellingPrice) * 100
      return Math.round(margin)
    },

    formatPrice(price) {
      return parseFloat(price || 0).toFixed(2)
    },

    handlePageChange(page) {
      this.currentPage = page
      this.selectedProducts = []
      
      // Optional: Show page change toast for better UX
      if (this.filteredProducts.length > this.itemsPerPage) {
        this.toast.info(`Page ${page} of ${Math.ceil(this.filteredProducts.length / this.itemsPerPage)}`, {
          duration: 1500
        })
      }
    }
  }
}
</script>

<style scoped>
.products-page {
  background-color: var(--neutral-light);
  min-height: 100vh;
}

.text-primary-dark {
  color: var(--primary-dark) !important;
}

.text-tertiary-dark {
  color: var(--tertiary-dark) !important;
}

.text-tertiary-medium {
  color: var(--tertiary-medium) !important;
}

/* Table Container */
.table-container {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* Header Controls */
.table-header-controls {
  border-bottom: 1px solid var(--neutral);
  background-color: white;
}

.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
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

/* Search Container */
.search-container {
  min-width: 300px;
}

.search-input {
  padding-right: 2.5rem;
  height: calc(1.5em + 0.75rem + 2px); /* Match form-select height */
}

.search-container .position-relative .btn {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Custom dropdown styling */
.custom-dropdown-menu {
  min-width: 280px;
  border: 1px solid var(--neutral);
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  animation: dropdownSlide 0.2s ease;
}

@keyframes dropdownSlide {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.custom-dropdown-item {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--neutral-light);
  transition: all 0.2s ease;
}

.custom-dropdown-item:last-child {
  border-bottom: none;
}

.custom-dropdown-item:hover {
  background-color: var(--primary-light);
}

/* Button States */
.btn.active {
  background-color: var(--primary);
  border-color: var(--primary);
  color: white;
}

/* Custom hover states for import/export buttons */
.btn.btn-outline-secondary:hover {
  background-color: var(--info-light);
  border-color: var(--info);
  color: var(--info-dark);
}

/* Form controls focus states */
.form-select:focus,
.form-control:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25);
}

/* Table row selection */
.table tbody tr.table-primary {
  background-color: var(--primary-light) !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .action-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-container {
    min-width: 100%;
  }
  
  .custom-dropdown-menu {
    min-width: 250px;
    right: 0;
    left: auto;
  }
  
  .custom-dropdown-item {
    padding: 0.875rem 1rem;
  }
}
</style>