<template>
  <div class="container-fluid pt-2 pb-4 products-page">
    <!-- Header Section -->
    <div class="d-flex justify-content-between align-items-center mb-3 page-header">
      <h1 class="h3 fw-semibold text-primary-dark mb-0">Product Management</h1>
      <div class="d-flex gap-2 flex-wrap">
        <!-- Add Products Dropdown -->
        <div class="dropdown" ref="addDropdown">
          <button 
            class="btn btn-add btn-sm btn-with-icon-sm dropdown-toggle"
            type="button"
            @click="toggleAddDropdown"
            :class="{ 'active': showAddDropdown }"
          >
            <Plus :size="14" />
            Add Products
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
        
        <button 
          class="btn btn-export btn-sm btn-with-icon-sm"
          @click="exportData"
        >
          <Download :size="14" />
          Export
        </button>
        
        <button 
          class="btn btn-refresh btn-sm btn-with-icon-sm"
          @click="refreshData" 
          :disabled="loading"
          :class="{ 'btn-loading': loading }"
        >
          <RefreshCw :size="14" :class="{ 'spin': loading }" />
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Reports Section -->
    <div class="row mb-3" v-if="!loading">
      <div class="col-6 col-md-3 mb-2">
        <CardTemplate
          size="sm"
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
          size="sm"
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
          size="sm"
          border-color="success"
          border-position="start"
          title="Total"
          :value="products.length"
          subtitle="Products"
        />
      </div>
      <div class="col-6 col-md-3 mb-2">
        <CardTemplate
          size="sm"
          border-color="primary"
          border-position="start"
          title="Categories"
          value="3"
          subtitle="Active"
        />
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-6 col-lg-3">
            <label for="categoryFilter" class="form-label text-tertiary-dark fw-medium">Category</label>
            <select id="categoryFilter" class="form-select" v-model="categoryFilter" @change="applyFilters">
              <option value="all">All Categories</option>
              <option value="noodles">Noodles</option>
              <option value="drinks">Drinks</option>
              <option value="toppings">Toppings</option>
            </select>
          </div>
          
          <div class="col-md-6 col-lg-3">
            <label for="statusFilter" class="form-label text-tertiary-dark fw-medium">Status</label>
            <select id="statusFilter" class="form-select" v-model="statusFilter" @change="applyFilters">
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="out-of-stock">Out of Stock</option>
            </select>
          </div>

          <div class="col-md-6 col-lg-3">
            <label for="stockFilter" class="form-label text-tertiary-dark fw-medium">Stock Level</label>
            <select id="stockFilter" class="form-select" v-model="stockFilter" @change="applyFilters">
              <option value="all">All Stock Levels</option>
              <option value="low-stock">Low Stock</option>
              <option value="in-stock">In Stock</option>
              <option value="out-of-stock">Out of Stock</option>
            </select>
          </div>

          <div class="col-md-6 col-lg-3">
            <label for="searchFilter" class="form-label text-tertiary-dark fw-medium">Search</label>
            <input 
              id="searchFilter" 
              v-model="searchFilter" 
              @input="applyFilters"
              type="text" 
              class="form-control"
              placeholder="Search by name, SKU, or barcode..."
            />
          </div>
        </div>
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

    <!-- Success Message -->
    <div v-if="successMessage" class="alert alert-success text-center" role="alert">
      {{ successMessage }}
    </div>

    <!-- Table Controls -->
    <div v-if="!loading || products.length > 0" class="card mb-3">
      <div class="card-body py-3">
        <div class="d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center gap-3">
            <button 
              class="btn btn-filter btn-with-icon-sm"
              @click="showColumnFilter"
            >
              <Columns :size="16" />
              Customize Columns
            </button>
            <button 
              class="btn btn-sm btn-delete-dynamic btn-with-icon-sm"
              @click="deleteSelected" 
              :disabled="selectedProducts.length === 0 || loading"
              :class="selectedProducts.length > 0 ? 'has-items' : 'no-items'"
            >
              <Trash2 :size="16" />
              Delete Selected ({{ selectedProducts.length }})
            </button>
          </div>
          <small class="text-tertiary-medium">
            Showing {{ filteredProducts.length }} of {{ products.length }} products
          </small>
        </div>
      </div>
    </div>

    <!-- Data Table -->
    <DataTable v-if="!loading || products.length > 0">
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
          <th v-if="columnVisibility.id" style="width: 80px;">ID</th>
          <th>Product Name</th>
          <th v-if="columnVisibility.category" style="width: 120px;">Category</th>
          <th v-if="columnVisibility.sku" style="width: 120px;">SKU</th>
          <th v-if="columnVisibility.stock" style="width: 120px;">Stock</th>
          <th v-if="columnVisibility.costPrice" style="width: 100px;">Cost Price</th>
          <th v-if="columnVisibility.sellingPrice" style="width: 100px;">Selling Price</th>
          <th v-if="columnVisibility.status" style="width: 100px;">Status</th>
          <th v-if="columnVisibility.expiryDate" style="width: 140px;">Expiry Date</th>
          <th style="width: 160px;">Actions</th>
        </tr>
      </template>

      <template #body>
        <tr 
          v-for="product in filteredProducts" 
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
          <td v-if="columnVisibility.id" class="font-monospace text-secondary fw-medium">
            {{ product._id.slice(-6) }}
          </td>
          <td>
            <div>
              <div :class="['fw-medium', getProductNameClass(product)]">{{ product.product_name }}</div>
              <small class="text-tertiary-medium">{{ product.unit }}</small>
            </div>
          </td>
          <td v-if="columnVisibility.category">
            <span :class="['badge', 'rounded-pill', getCategoryBadgeClass(product.category_id)]">
              {{ getCategoryName(product.category_id) }}
            </span>
          </td>
          <td v-if="columnVisibility.sku" class="font-monospace fw-semibold text-tertiary-dark">
            {{ product.SKU }}
          </td>
          <td v-if="columnVisibility.stock">
            <div>
              <span :class="['fw-medium', getStockClass(product)]">{{ product.stock }}</span>
              <br>
              <small class="text-tertiary-medium">(Min: {{ product.low_stock_threshold }})</small>
            </div>
          </td>
          <td v-if="columnVisibility.costPrice" class="text-end fw-medium">
            ₱{{ formatPrice(product.cost_price) }}
          </td>
          <td v-if="columnVisibility.sellingPrice" class="text-end fw-medium">
            ₱{{ formatPrice(product.selling_price) }}
          </td>
          <td v-if="columnVisibility.status">
            <span :class="['badge', 'rounded-pill', getStatusBadgeClass(product.status)]">
              {{ formatStatus(product.status) }}
            </span>
          </td>
          <td v-if="columnVisibility.expiryDate">
            <span 
              :class="['badge', 'rounded-pill', getExpiryBadgeClass(product.expiry_date)]"
              :title="getExpiryTooltip(product.expiry_date)"
            >
              {{ formatDate(product.expiry_date) }}
            </span>
          </td>
          <td>
            <div class="d-flex gap-1 justify-content-center">
              <button 
                class="btn btn-outline-secondary btn-icon-only btn-xs action-btn" 
                @click="editProduct(product)"
                data-bs-toggle="tooltip"
                title="Edit Product"
              >
                <Edit :size="12" />
              </button>
              <button 
                class="btn btn-outline-primary btn-icon-only btn-xs action-btn" 
                @click="navigateToProductDetails(product._id)"
                data-bs-toggle="tooltip"
                title="View Details"
              >
                <Eye :size="12" />
              </button>
              <button 
                class="btn btn-outline-info btn-icon-only btn-xs action-btn" 
                @click="restockProduct(product)"
                data-bs-toggle="tooltip"
                title="Update Stock"
              >
                <Package :size="12" />
              </button>
              <button 
                class="btn btn-outline-success btn-icon-only btn-xs action-btn"
                @click="toggleProductStatus(product)"
                data-bs-toggle="tooltip"
                :title="product.status === 'active' ? 'Deactivate Product' : 'Activate Product'"
                :class="{ 'btn-outline-warning': product.status !== 'active' }"
              >
                <Lock v-if="product.status === 'active'" :size="12" />
                <Unlock v-else :size="12" />
              </button>
              <button 
                class="btn btn-outline-danger btn-icon-only btn-xs action-btn" 
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
            class="btn btn-primary-medium btn-with-icon" 
            @click="handleSingleProduct"
          >
            <Plus :size="16" />
            Add First Product
          </button>
          <button 
            v-else 
            class="btn btn-secondary-medium btn-with-icon"
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

    <ColumnFilterModal
      :show="showColumnFilterModal"
      :current-visible-columns="columnVisibility"
      @close="closeColumnFilter"
      @apply="applyColumnFilter"
    />

    <ImportModal
      ref="importModal"
      @import-completed="handleImportSuccess"
      @import-failed="handleImportError"
    />
  </div>
</template>

<script>
import productsApiService from '../../services/apiProducts.js'
import AddProductModal from '../../components/products/AddProductModal.vue'
import StockUpdateModal from '../../components/products/StockUpdateModal.vue'
import ViewProductModal from '../../components/products/ViewProductModal.vue'
import ReportsModal from '../../components/products/ReportsModal.vue'
import ColumnFilterModal from '../../components/products/ColumnFilterModal.vue'
import DataTable from '@/components/common/TableTemplate.vue'
import CardTemplate from '@/components/common/CardTemplate.vue'
import ImportModal from '../../components/products/ImportModal.vue'
import { 
  Plus, 
  Download, 
  RefreshCw, 
  Edit, 
  Eye, 
  Package, 
  Lock, 
  Unlock, 
  Trash2,
  Columns,
  AlertTriangle,
  Calendar,
  MoreVertical,
  FileText
} from 'lucide-vue-next'

export default {
  name: 'Products',
  components: {
    AddProductModal,
    StockUpdateModal,
    ViewProductModal,
    ColumnFilterModal,
    ImportModal,
    ReportsModal,
    DataTable,
    CardTemplate,
    Plus,
    Download,
    RefreshCw,
    Edit,
    Eye,
    Package,
    Lock,
    Unlock,
    Trash2,
    Columns,
    AlertTriangle,
    Calendar,
    MoreVertical,
    FileText
  },
  data() {
    return {
      products: [],
      filteredProducts: [],
      selectedProducts: [],
      loading: false,
      error: null,
      successMessage: null,
      
      // Dropdown state
      showAddDropdown: false,
      
      // Report data
      lowStockCount: 0,
      expiringCount: 0,
      
      // Filters
      categoryFilter: 'all',
      statusFilter: 'all',
      stockFilter: 'all',
      searchFilter: '',
      
      // Column Filter
      showColumnFilterModal: false,
      columnVisibility: {
        id: false,
        sku: true,
        category: true,
        stock: true,
        costPrice: false,
        sellingPrice: true,
        status: true,
        expiryDate: true,
      }
    }
  },
  computed: {
    allSelected() {
      return this.filteredProducts.length > 0 && this.selectedProducts.length === this.filteredProducts.length
    },
    someSelected() {
      return this.selectedProducts.length > 0 && this.selectedProducts.length < this.filteredProducts.length
    }
  },
  async mounted() {
    console.log('Products component mounted')
    console.log('Bootstrap available:', typeof bootstrap !== 'undefined')
    console.log('Bootstrap Modal:', bootstrap?.Modal)
    this.loadColumnVisibility()
    await this.fetchProducts()
    
    // Close dropdown when clicking outside
    document.addEventListener('click', this.handleClickOutside)
  },
  
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
  },
  
  methods: {
    // Click outside handler for dropdown
    handleClickOutside(event) {
      if (this.$refs.addDropdown && !this.$refs.addDropdown.contains(event.target)) {
        this.showAddDropdown = false
      }
    },

    // Dropdown Methods
    toggleAddDropdown(event) {
      event.stopPropagation()
      this.showAddDropdown = !this.showAddDropdown
    },
    
    closeAddDropdown() {
      this.showAddDropdown = false
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
      console.log('🔍 Import button clicked')
      
      // Check if the modal element exists
      const importModalElement = document.getElementById('importModal')
      console.log('🔍 Modal element found:', importModalElement)
      
      if (importModalElement) {
        console.log('🔍 Creating Bootstrap modal...')
        try {
          const modal = new bootstrap.Modal(importModalElement)
          console.log('🔍 Modal created:', modal)
          modal.show()
          console.log('✅ Modal.show() called')
        } catch (error) {
          console.error('❌ Error creating/showing modal:', error)
        }
      } else {
        console.error('❌ Modal element #importModal not found in DOM')
      }
      
      this.closeAddDropdown()
    },

    handleImportSuccess(result) {
      this.successMessage = `Import completed! ${result.totalSuccessful || 0} products imported successfully.`
      this.fetchProducts() // Refresh the product list
      
      setTimeout(() => {
        this.successMessage = null
      }, 5000)
    },

    handleImportError(error) {
      this.error = `Import failed: ${error.message || 'An unexpected error occurred'}`
      
      setTimeout(() => {
        this.error = null
      }, 5000)
    },

    async fetchProducts() {
      this.loading = true
      this.error = null
      
      try {
        console.log('Fetching products from API...')
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
        console.log('Products loaded:', this.products)
      } catch (error) {
        console.error('Error fetching products:', error)
        this.error = `Failed to load products: ${error.message}`
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
      } catch (error) {
        console.error('Error fetching report counts:', error)
      }
    },

    async showLowStockReport() {
      // ReportsModal exposes showLowStockModal method
      if (this.$refs.reportsModal && this.$refs.reportsModal.showLowStockModal) {
        await this.$refs.reportsModal.showLowStockModal()
      }
    },

    async showExpiringReport() {
      // ReportsModal exposes showExpiringModal method
      if (this.$refs.reportsModal && this.$refs.reportsModal.showExpiringModal) {
        await this.$refs.reportsModal.showExpiringModal()
      }
    },

    async refreshReport() {
      if (this.$refs.reportsModal && this.$refs.reportsModal.refreshReportData) {
        await this.$refs.reportsModal.refreshReportData()
      }
    },

    exportReportData(reportData) {
      const headers = reportData.type === 'low-stock' 
        ? ['Product Name', 'SKU', 'Category', 'Current Stock', 'Threshold']
        : ['Product Name', 'SKU', 'Category', 'Current Stock', 'Expiry Date', 'Days Until Expiry']
      
      const csvContent = [
        headers.join(','),
        ...reportData.data.map(item => {
          const baseData = [
            `"${item.product_name}"`,
            item.SKU,
            this.getCategoryName(item.category_id),
            item.stock
          ]
          
          if (reportData.type === 'low-stock') {
            baseData.push(item.low_stock_threshold)
          } else {
            baseData.push(this.formatDate(item.expiry_date))
            baseData.push(this.getDaysUntilExpiry(item.expiry_date))
          }
          
          return baseData.join(',')
        })
      ].join('\n')

      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${reportData.type}-report_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      window.URL.revokeObjectURL(url)
    },

    applyFilters() {
      let filtered = [...this.products]

      if (this.categoryFilter !== 'all') {
        filtered = filtered.filter(product => product.category_id === this.categoryFilter)
      }

      if (this.statusFilter !== 'all') {
        if (this.statusFilter === 'out-of-stock') {
          filtered = filtered.filter(product => product.stock === 0)
        } else {
          filtered = filtered.filter(product => product.status === this.statusFilter)
        }
      }

      if (this.stockFilter !== 'all') {
        if (this.stockFilter === 'low-stock') {
          filtered = filtered.filter(product => 
            product.stock > 0 && product.stock <= product.low_stock_threshold
          )
        } else if (this.stockFilter === 'in-stock') {
          filtered = filtered.filter(product => product.stock > product.low_stock_threshold)
        } else if (this.stockFilter === 'out-of-stock') {
          filtered = filtered.filter(product => product.stock === 0)
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

      this.filteredProducts = filtered
    },

    clearFilters() {
      this.categoryFilter = 'all'
      this.statusFilter = 'all'
      this.stockFilter = 'all'
      this.searchFilter = ''
      this.applyFilters()
    },

    async refreshData() {
      this.successMessage = null
      await this.fetchProducts()
    },

    selectAll(event) {
      if (event.target.checked) {
        this.selectedProducts = this.filteredProducts.map(product => product._id)
      } else {
        this.selectedProducts = []
      }
    },

    async deleteSelected() {
      if (this.selectedProducts.length === 0) return
      
      const confirmed = confirm(`Are you sure you want to delete ${this.selectedProducts.length} product(s)?`)
      if (!confirmed) return

      this.loading = true
      
      try {
        await productsApiService.bulkDeleteProducts(this.selectedProducts)
        this.successMessage = `Successfully deleted ${this.selectedProducts.length} product(s)`
        this.selectedProducts = []
        await this.fetchProducts()
      } catch (error) {
        console.error('Error deleting products:', error)
        this.error = `Failed to delete products: ${error.message}`
      } finally {
        this.loading = false
      }
      
      setTimeout(() => {
        this.successMessage = null
      }, 3000)
    },

    async deleteProduct(product) {
      const confirmed = confirm(`Are you sure you want to delete "${product.product_name}"?`)
      if (!confirmed) return

      try {
        await productsApiService.deleteProduct(product._id)
        this.successMessage = `Product "${product.product_name}" deleted successfully`
        await this.fetchProducts()
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error deleting product:', error)
        this.error = `Failed to delete product: ${error.message}`
      }
    },

    async toggleProductStatus(product) {
      const newStatus = product.status === 'active' ? 'inactive' : 'active'
      const action = newStatus === 'active' ? 'activate' : 'deactivate'
      
      const confirmed = confirm(`Are you sure you want to ${action} "${product.product_name}"?`)
      if (!confirmed) return

      try {
        await productsApiService.updateProduct(product._id, { status: newStatus })
        this.successMessage = `Product "${product.product_name}" ${action}d successfully`
        await this.fetchProducts()
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error updating product status:', error)
        this.error = `Failed to ${action} product: ${error.message}`
      }
    },

    showAddProductModal() {
      if (this.$refs.addProductModal && this.$refs.addProductModal.openAdd) {
        this.$refs.addProductModal.openAdd()
      }
    },

    editProduct(product) {
      // Close view modal if it's open
      if (this.$refs.viewProductModal && this.$refs.viewProductModal.close) {
        this.$refs.viewProductModal.close()
      }
      // Open edit modal
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
      // StockUpdateModal exposes openStock method
      if (this.$refs.stockUpdateModal && this.$refs.stockUpdateModal.openStock) {
        this.$refs.stockUpdateModal.openStock(product)
      }
    },

    async generateProductBarcode(product) {
      try {
        await productsApiService.generateBarcode(product._id)
        this.successMessage = `Barcode generated for "${product.product_name}"`
        await this.fetchProducts()
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error generating barcode:', error)
        this.error = `Failed to generate barcode: ${error.message}`
      }
    },

    handleProductSuccess(result) {
      this.successMessage = result.message
      this.fetchProducts()
      
      setTimeout(() => {
        this.successMessage = null
      }, 3000)
    },

    handleStockUpdateSuccess(result) {
      this.successMessage = result.message
      this.fetchProducts()
      
      setTimeout(() => {
        this.successMessage = null
      }, 3000)
    },

    async exportData() {
      try {
        const blob = await productsApiService.exportProducts({
          format: 'csv',
          filters: {
            category: this.categoryFilter !== 'all' ? this.categoryFilter : undefined,
            status: this.statusFilter !== 'all' ? this.statusFilter : undefined,
            search: this.searchFilter || undefined
          }
        })
        
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `products_${new Date().toISOString().split('T')[0]}.csv`
        a.click()
        window.URL.revokeObjectURL(url)
      } catch (error) {
        console.error('API export failed, falling back to client-side export:', error)
        
        const headers = ['ID', 'Name', 'SKU', 'Category', 'Stock', 'Cost Price', 'Selling Price', 'Status', 'Expiry Date']
        const csvContent = [
          headers.join(','),
          ...this.filteredProducts.map(product => [
            product._id.slice(-6),
            `"${product.product_name}"`,
            product.SKU,
            this.getCategoryName(product.category_id),
            product.stock,
            product.cost_price,
            product.selling_price,
            product.status,
            this.formatDate(product.expiry_date)
          ].join(','))
        ].join('\n')

        const blob = new Blob([csvContent], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `products_${new Date().toISOString().split('T')[0]}.csv`
        a.click()
        window.URL.revokeObjectURL(url)
      }
    },

    showColumnFilter() {
      // ColumnFilterModal still uses the old pattern with props
      this.showColumnFilterModal = true
    },
    
    closeColumnFilter() {
      this.showColumnFilterModal = false
    },
    
    applyColumnFilter(newColumnVisibility) {
      this.columnVisibility = { ...newColumnVisibility }
      localStorage.setItem('products-column-visibility', JSON.stringify(this.columnVisibility))
      this.successMessage = 'Column visibility updated successfully'
      this.showColumnFilterModal = false
      setTimeout(() => {
        this.successMessage = null
      }, 2000)
    },
    
    loadColumnVisibility() {
      const saved = localStorage.getItem('products-column-visibility')
      if (saved) {
        try {
          this.columnVisibility = { ...this.columnVisibility, ...JSON.parse(saved) }
        } catch (error) {
          console.error('Error loading column visibility:', error)
        }
      }
    },
    
    navigateToProductDetails(productId) {
      console.log('🔄 Navigation triggered!')
      console.log('📦 Product ID:', productId)
      console.log('🌐 Navigating to:', `/products/${productId}`)
      
      if (!productId) {
        console.error('❌ Error: Product ID is null or undefined!')
        return
      }
      
      try {
        this.$router.push(`/products/${productId}`)
        console.log('✅ Router.push executed successfully')
      } catch (error) {
        console.error('❌ Router navigation error:', error)
      }
    },

    getExpiryTooltip(expiryDate) {
      if (!expiryDate) return 'No expiry date set'
      
      const today = new Date()
      const expiry = new Date(expiryDate)
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      
      if (daysUntilExpiry < 0) {
        return `Expired ${Math.abs(daysUntilExpiry)} day${Math.abs(daysUntilExpiry) !== 1 ? 's' : ''} ago - Remove from inventory`
      }
      if (daysUntilExpiry === 0) return 'Expires today - Use immediately'
      if (daysUntilExpiry === 1) return 'Expires tomorrow - Priority sale'
      if (daysUntilExpiry <= 7) return `Expires in ${daysUntilExpiry} days - Urgent attention needed`
      if (daysUntilExpiry <= 30) return `Expires in ${daysUntilExpiry} days - Monitor closely`
      
      return `Expires in ${daysUntilExpiry} days - Good condition`
    },

    getExpiryBadgeClass(expiryDate) {
      if (!expiryDate) return 'text-bg-secondary'
      
      const today = new Date()
      const expiry = new Date(expiryDate)
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      
      if (daysUntilExpiry < 0) return 'text-bg-danger pulsing-badge'
      if (daysUntilExpiry <= 7) return 'text-bg-warning'
      if (daysUntilExpiry <= 30) return 'text-bg-info'
      return 'text-bg-success'
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
      if (product.stock <= product.low_stock_threshold) return 'text-danger fw-semibold'
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

    getStockClass(product) {
      if (product.stock === 0) return 'text-danger fw-bold'
      if (product.stock <= product.low_stock_threshold) return 'text-warning fw-semibold'
      return 'text-success fw-medium'
    },

    getStatusBadgeClass(status) {
      return status === 'active' ? 'text-bg-success' : 'text-bg-danger'
    },

    getDaysUntilExpiry(expiryDate) {
      if (!expiryDate) return 'N/A'
      
      const today = new Date()
      const expiry = new Date(expiryDate)
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      
      if (daysUntilExpiry < 0) return `Expired ${Math.abs(daysUntilExpiry)} days ago`
      if (daysUntilExpiry === 0) return 'Expires today'
      return `${daysUntilExpiry} days`
    },

    formatPrice(price) {
      return parseFloat(price || 0).toFixed(2)
    },

    formatStatus(status) {
      return status.charAt(0).toUpperCase() + status.slice(1).replace('-', ' ')
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
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

/* Custom color classes using colors.css variables */
.text-primary-dark {
  color: var(--primary-dark) !important;
}

.text-tertiary-dark {
  color: var(--tertiary-dark) !important;
}

.text-tertiary-medium {
  color: var(--tertiary-medium) !important;
}

/* Pulsing animation for expired items */
.pulsing-badge {
  animation: pulse-error 2s infinite;
}

@keyframes pulse-error {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

/* Spin animation for refresh button */
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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

/* Products page background */
.products-page {
  background-color: var(--neutral-light);
  min-height: 100vh;
}

/* Action buttons spacing */
.action-btn {
  transition: all 0.2s ease;
}

.action-btn:hover {
  transform: translateY(-1px);
}

/* Responsive adjustments */
@media (max-width: 768px) {
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