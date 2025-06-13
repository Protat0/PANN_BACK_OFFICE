<template>
  <div class="products-page">
    <!-- Header Section -->
    <div class="page-header">
      <h1 class="page-title">Product Management</h1>
        <div class="header-actions">
            <button 
                class="btn btn-secondary" 
                @click="deleteSelected" 
                :disabled="selectedProducts.length === 0 || loading"
            >
                Delete Selected ({{ selectedProducts.length }})
            </button>
            <button class="btn btn-success" @click="showAddProductModal">
                Add Product
            </button>
            <button class="btn btn-primary" @click="exportData">
                Export
            </button>
            <button class="btn btn-info" @click="refreshData" :disabled="loading">
                {{ loading ? 'Loading...' : 'Refresh' }}
            </button>
        </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-group">
        <label for="categoryFilter">Filter by Category:</label>
        <select id="categoryFilter" v-model="categoryFilter" @change="applyFilters">
          <option value="all">All Categories</option>
          <option value="noodles">Noodles</option>
          <option value="drinks">Drinks</option>
          <option value="toppings">Toppings</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label for="statusFilter">Filter by Status:</label>
        <select id="statusFilter" v-model="statusFilter" @change="applyFilters">
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="out-of-stock">Out of Stock</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="stockFilter">Stock Level:</label>
        <select id="stockFilter" v-model="stockFilter" @change="applyFilters">
          <option value="all">All Stock Levels</option>
          <option value="low-stock">Low Stock</option>
          <option value="in-stock">In Stock</option>
          <option value="out-of-stock">Out of Stock</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="searchFilter">Search:</label>
        <input 
          id="searchFilter" 
          v-model="searchFilter" 
          @input="applyFilters"
          type="text" 
          placeholder="Search by name, SKU, or barcode..."
        />
      </div>
    </div>

    <!-- Reports Section -->
    <div class="reports-section" v-if="!loading">
      <div class="report-cards">
        <div class="report-card low-stock" @click="showLowStockReport">
          <h3>Low Stock Alert</h3>
          <p class="report-count">{{ lowStockCount }}</p>
          <span class="report-label">Items Below Threshold</span>
        </div>
        <div class="report-card expiring" @click="showExpiringReport">
          <h3>Expiring Soon</h3>
          <p class="report-count">{{ expiringCount }}</p>
          <span class="report-label">Items Expiring in 30 Days</span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && products.length === 0" class="loading-state">
      <p>Loading products...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-state">
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="refreshData">Try Again</button>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>

    <!-- Table Controls Section -->
    <div v-if="!loading || products.length > 0" class="table-controls">
        <div class="table-controls-left">
            <button class="btn btn-info column-filter-btn" @click="showColumnFilter">
            Customize Columns
            </button>
        </div>
        <div class="table-controls-right">
            <div class="table-summary">
            Showing {{ filteredProducts.length }} of {{ products.length }} products
            </div>
        </div>
    </div>

    <!-- Data Table -->
    <DataTable v-if="!loading || products.length > 0">
        <template #header>
            <tr>
            <!-- Always visible columns -->
            <th class="checkbox-column">
                <input 
                type="checkbox" 
                @change="selectAll" 
                :checked="allSelected"
                :indeterminate="someSelected"
                />
            </th>
            <th v-if="columnVisibility.id">ID</th>
            <th>Product Name</th> <!-- Always visible -->
            <th v-if="columnVisibility.category">Category</th>
            <th v-if="columnVisibility.sku">SKU</th>
            <th v-if="columnVisibility.stock">Stock</th>
            <th v-if="columnVisibility.costPrice">Cost Price</th>
            <th v-if="columnVisibility.sellingPrice">Selling Price</th>
            <th v-if="columnVisibility.status">Status</th>
            <th v-if="columnVisibility.expiryDate">Expiry Date</th>
            <th class="actions-column">Actions</th> <!-- Always visible -->
            </tr>
        </template>

        <template #body>
            <tr 
            v-for="product in filteredProducts" 
            :key="product._id"
            :class="getRowClass(product)"
            >
            <!-- Always visible columns -->
            <td class="checkbox-column">
                <input 
                type="checkbox" 
                :value="product._id"
                v-model="selectedProducts"
                />
            </td>
            <td v-if="columnVisibility.id" class="id-column">{{ product._id.slice(-6) }}</td>
            <td class="product-name-column">
                <div class="product-info">
                <span class="product-name">{{ product.product_name }}</span>
                <span class="product-unit">{{ product.unit }}</span>
                </div>
            </td>
            <td v-if="columnVisibility.category" class="category-column">
                <span :class="['category-badge', `category-${getCategorySlug(product.category_id)}`]">
                {{ getCategoryName(product.category_id) }}
                </span>
            </td>
            <td v-if="columnVisibility.sku" class="sku-column">
                <span class="sku-value">{{ product.SKU }}</span>
            </td>
            <td v-if="columnVisibility.stock" class="stock-column">
                <div class="stock-info">
                <span :class="getStockClass(product)">{{ product.stock }}</span>
                <span class="stock-threshold">(Min: {{ product.low_stock_threshold }})</span>
                </div>
            </td>
            <td v-if="columnVisibility.costPrice" class="price-column">₱{{ formatPrice(product.cost_price) }}</td>
            <td v-if="columnVisibility.sellingPrice" class="price-column">₱{{ formatPrice(product.selling_price) }}</td>
            <td v-if="columnVisibility.status" class="status-column">
                <span :class="['status-badge', `status-${product.status}`]">
                {{ formatStatus(product.status) }}
                </span>
            </td>
            <td v-if="columnVisibility.expiryDate" class="expiry-column">
                <span :class="getExpiryClass(product.expiry_date)" :title="getExpiryTooltip(product.expiry_date)">
                {{ formatDate(product.expiry_date) }}
                </span>
            </td>
            <td class="actions-column">
                <div class="action-buttons">
                <button class="action-btn" @click="editProduct(product)" title="Edit">
                    ✏️
                </button>
                <button 
                class="action-btn" @click="navigateToProductDetails(product._id)" title="View Details">
                    👁️
                </button>
                <button class="action-btn" @click="restockProduct(product)" title="Restock">
                    📦
                </button>
                <button 
                    class="action-btn"
                    @click="toggleProductStatus(product)" 
                    :title="product.status === 'active' ? 'Deactivate' : 'Activate'"
                >
                    {{ product.status === 'active' ? '🔒' : '🔓' }}
                </button>
                <button class="action-btn delete" @click="deleteProduct(product)" title="Delete">
                    🗑️
                </button>
                </div>
            </td>
            </tr>
        </template>
    </DataTable>    


    <!-- Empty State -->
    <div v-if="!loading && filteredProducts.length === 0 && !error" class="empty-state">
      <p>{{ products.length === 0 ? 'No products found' : 'No products match the current filters' }}</p>
      <button v-if="products.length === 0" class="btn btn-primary" @click="showAddProductModal">
        Add First Product
      </button>
      <button v-else class="btn btn-secondary" @click="clearFilters">
        Clear Filters
      </button>
    </div>

    <!-- Modular Components -->
    <AddProductModal
      :show="showModal"
      :product="isEditMode ? selectedProduct : null"
      :loading="formLoading"
      :error="formError"
      @close="closeModal"
      @submit="saveProduct"
    />

    <StockUpdateModal
      :show="showStockModal"
      :product="stockProduct"
      :loading="stockFormLoading"
      :error="stockFormError"
      @close="closeStockModal"
      @submit="saveStockUpdate"
    />

    <ViewProductModal
      :show="showViewModal"
      :product="selectedProduct"
      @close="closeViewModal"
      @edit="editProduct"
      @restock="restockProduct"
      @toggle-status="toggleProductStatus"
      @generate-barcode="generateProductBarcode"
    />

    <ReportsModal
      :show="showReportsModal"
      :type="reportType"
      :title="reportTitle"
      :data="reportData"
      :loading="reportsLoading"
      @close="closeReportsModal"
      @export="exportReportData"
      @refresh="refreshReport"
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
  </div>
</template>

<script>
import productsApiService from '../../services/apiProducts.js'
import DataTable from '../../components/TableTemplate.vue'
import AddProductModal from '../../components/products/AddProductModal.vue'
import StockUpdateModal from '../../components/products/StockUpdateModal.vue'
import ViewProductModal from '../../components/products/ViewProductModal.vue'
import ReportsModal from '../../components/products/ReportsModal.vue'
import ColumnFilterModal from '../../components/products/ColumnFilterModal.vue'

export default {
  name: 'Products',
  components: {
    DataTable,
    AddProductModal,
    StockUpdateModal,
    ViewProductModal,
    ColumnFilterModal,
    ReportsModal
  },
  data() {
    return {
      products: [],
      filteredProducts: [],
      selectedProducts: [],
      loading: false,
      error: null,
      successMessage: null,
      
      // Report data
      lowStockCount: 0,
      expiringCount: 0,
      reportData: [],
      reportType: '',
      reportTitle: '',
      showReportsModal: false,
      reportsLoading: false,
      
      // Filters
      categoryFilter: 'all',
      statusFilter: 'all',
      stockFilter: 'all',
      searchFilter: '',
      
      // Modal states
      showModal: false,
      showViewModal: false,
      showStockModal: false,
      isEditMode: false,
      formLoading: false,
      formError: null,
      selectedProduct: null,
      
      // Stock update form
      stockProduct: null,
      stockFormLoading: false,
      stockFormError: null,

        // Column Filter Modal
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
  methods: {
    async fetchProducts() {
      this.loading = true
      this.error = null
      
      try {
        console.log('Fetching products from API...')
        const data = await productsApiService.getProducts()
        
        // Handle different response formats
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
        // Get low stock count
        const lowStockData = await productsApiService.getLowStockProducts()
        this.lowStockCount = Array.isArray(lowStockData) ? lowStockData.length : (lowStockData.count || 0)
        
        // Get expiring products count (next 30 days)
        const expiringData = await productsApiService.getExpiringProducts({ days_ahead: 30 })
        this.expiringCount = Array.isArray(expiringData) ? expiringData.length : (expiringData.count || 0)
      } catch (error) {
        console.error('Error fetching report counts:', error)
        // Don't show error for report counts, just log it
      }
    },

    async showLowStockReport() {
      this.reportsLoading = true
      try {
        this.reportData = await productsApiService.getLowStockProducts()
        this.reportType = 'low-stock'
        this.reportTitle = 'Low Stock Report'
        this.showReportsModal = true
      } catch (error) {
        console.error('Error fetching low stock report:', error)
        this.error = `Failed to load low stock report: ${error.message}`
      } finally {
        this.reportsLoading = false
      }
    },

    async showExpiringReport() {
      this.reportsLoading = true
      try {
        this.reportData = await productsApiService.getExpiringProducts({ days_ahead: 30 })
        this.reportType = 'expiring'
        this.reportTitle = 'Products Expiring in 30 Days'
        this.showReportsModal = true
      } catch (error) {
        console.error('Error fetching expiring products report:', error)
        this.error = `Failed to load expiring products report: ${error.message}`
      } finally {
        this.reportsLoading = false
      }
    },

    closeReportsModal() {
      this.showReportsModal = false
      this.reportData = []
      this.reportType = ''
      this.reportTitle = ''
      this.reportsLoading = false
    },

    async refreshReport() {
      if (this.reportType === 'low-stock') {
        await this.showLowStockReport()
      } else if (this.reportType === 'expiring') {
        await this.showExpiringReport()
      }
    },

    exportReportData(reportData) {
      // Handle export from ReportsModal
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

      // Category filter
      if (this.categoryFilter !== 'all') {
        filtered = filtered.filter(product => product.category_id === this.categoryFilter)
      }

      // Status filter
      if (this.statusFilter !== 'all') {
        if (this.statusFilter === 'out-of-stock') {
          filtered = filtered.filter(product => product.stock === 0)
        } else {
          filtered = filtered.filter(product => product.status === this.statusFilter)
        }
      }

      // Stock filter
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

      // Search filter
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
      this.isEditMode = false
      this.selectedProduct = null
      this.formError = null
      this.showModal = true
    },

    editProduct(product) {
      this.isEditMode = true
      this.selectedProduct = product
      this.formError = null
      this.showViewModal = false
      this.showModal = true
    },

    viewProduct(product) {
      this.selectedProduct = product
      this.showViewModal = true
    },

    restockProduct(product) {
      this.stockProduct = product
      this.stockFormError = null
      this.showStockModal = true
    },

    closeStockModal() {
      this.showStockModal = false
      this.stockProduct = null
      this.stockFormError = null
    },

    async saveStockUpdate(stockData) {
      this.stockFormLoading = true
      this.stockFormError = null

      try {
        await productsApiService.updateProductStock(this.stockProduct._id, stockData)
        
        const operation = stockData.operation_type
        const quantity = stockData.quantity
        let message = ''
        
        if (operation === 'add') {
          message = `Added ${quantity} units to "${this.stockProduct.product_name}"`
        } else if (operation === 'remove') {
          message = `Removed ${quantity} units from "${this.stockProduct.product_name}"`
        } else {
          message = `Set stock to ${quantity} units for "${this.stockProduct.product_name}"`
        }
        
        this.successMessage = message
        this.closeStockModal()
        await this.fetchProducts()
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error updating stock:', error)
        this.stockFormError = error.message
      } finally {
        this.stockFormLoading = false
      }
    },

    closeModal() {
      this.showModal = false
      this.isEditMode = false
      this.selectedProduct = null
      this.formError = null
    },

    closeViewModal() {
      this.showViewModal = false
      this.selectedProduct = null
    },

    async saveProduct(productData) {
      this.formLoading = true
      this.formError = null

      try {
        if (this.isEditMode) {
          await productsApiService.updateProduct(this.selectedProduct._id, productData)
          this.successMessage = `Product "${productData.product_name}" updated successfully`
        } else {
          await productsApiService.createProduct(productData)
          this.successMessage = `Product "${productData.product_name}" created successfully`
        }

        this.closeModal()
        await this.fetchProducts()
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error saving product:', error)
        this.formError = error.message
      } finally {
        this.formLoading = false
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

    async exportData() {
      try {
        // Try to use the API export function first
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
        
        // Fallback to client-side export
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

    // Column Filter Methods
    showColumnFilter() {
      this.showColumnFilterModal = true
    },
    
    closeColumnFilter() {
      this.showColumnFilterModal = false
    },
    
    applyColumnFilter(newColumnVisibility) {
      this.columnVisibility = { ...newColumnVisibility }
      
      // Save to localStorage for persistence
      localStorage.setItem('products-column-visibility', JSON.stringify(this.columnVisibility))
      
      // Optional: Show success message
      this.successMessage = 'Column visibility updated successfully'
      setTimeout(() => {
        this.successMessage = null
      }, 2000)
    },
    
    loadColumnVisibility() {
      // Load saved column visibility from localStorage
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
      console.log('🔄 Navigation triggered!');
      console.log('📦 Product ID:', productId);
      console.log('🌐 Navigating to:', `/products/${productId}`);
      
      // Check if productId exists and is valid
      if (!productId) {
        console.error('❌ Error: Product ID is null or undefined!');
        return;
      }
      
      try {
        this.$router.push(`/products/${productId}`);
        console.log('✅ Router.push executed successfully');
      } catch (error) {
        console.error('❌ Router navigation error:', error);
      }
    },

    // Enhanced tooltip method for expiry dates
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

    // Enhanced expiry class method
    getExpiryClass(expiryDate) {
      if (!expiryDate) return 'no-expiry'
      
      const today = new Date()
      const expiry = new Date(expiryDate)
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      
      if (daysUntilExpiry < 0) return 'expired'
      if (daysUntilExpiry <= 7) return 'expiring-soon'
      if (daysUntilExpiry <= 30) return 'expiring-month'
      return 'fresh'
    },

    // Utility methods
    getCategoryName(categoryId) {
      const categories = {
        'noodles': 'Noodles',
        'drinks': 'Drinks',
        'toppings': 'Toppings'
      }
      return categories[categoryId] || categoryId
    },

    getCategorySlug(categoryId) {
      return categoryId?.toLowerCase().replace(/\s+/g, '-') || 'unknown'
    },

    getRowClass(product) {
      const classes = []
      
      if (this.selectedProducts.includes(product._id)) {
        classes.push('selected')
      }
      
      if (product.status === 'inactive') {
        classes.push('inactive')
      }
      
      if (product.stock === 0) {
        classes.push('out-of-stock')
      } else if (product.stock <= product.low_stock_threshold) {
        classes.push('low-stock')
      }
      
      return classes.join(' ')
    },

    getStockClass(product) {
      if (product.stock === 0) return 'stock-zero'
      if (product.stock <= product.low_stock_threshold) return 'stock-low'
      return 'stock-normal'
    },

    getExpiryClass(expiryDate) {
      if (!expiryDate) return ''
      
      const today = new Date()
      const expiry = new Date(expiryDate)
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      
      if (daysUntilExpiry < 0) return 'expired'
      if (daysUntilExpiry <= 7) return 'expiring-soon'
      if (daysUntilExpiry <= 30) return 'expiring-month'
      return ''
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
  },

  async mounted() {
    console.log('Products component mounted')
    this.loadColumnVisibility()
    await this.fetchProducts()
  }
}
</script>

<style scoped>
.products-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  background-color: var(--neutral-light);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: var(--primary-dark);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.reports-section {
  margin-bottom: 1.5rem;
}

.report-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.report-card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 4px solid var(--primary);
}

.report-card.low-stock {
  border-left-color: var(--error);
}

.report-card.expiring {
  border-left-color: var(--info);
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.15);
}

.report-card h3 {
  margin: 0 0 0.5rem 0;
  color: var(--tertiary-dark);
  font-size: 1rem;
  font-weight: 500;
}

.report-count {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary);
  margin: 0;
}

.report-card.low-stock .report-count {
  color: var(--error);
}

.report-card.expiring .report-count {
  color: var(--info);
}

.report-label {
  color: var(--tertiary);
  font-size: 0.875rem;
}

.filters-section {
  background: white;
  padding: 1.5rem;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: var(--tertiary-dark);
  font-size: 0.875rem;
}

.filter-group select,
.filter-group input {
  padding: 0.5rem;
  border: 1px solid var(--neutral);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
  color: var(--tertiary-dark);
}

.filter-group select:focus,
.filter-group input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(115, 146, 226, 0.1);
}

.btn {
  padding: 0.5rem 1.25rem;
  border-radius: 0.5rem;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  white-space: nowrap;
}

.btn-primary {
  background-color: var(--primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.btn-secondary {
  background-color: var(--neutral-medium);
  color: var(--tertiary-dark);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--neutral-dark);
}

.btn-success {
  background-color: var(--success);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: var(--success-dark);
}

.btn-info {
  background-color: var(--info);
  color: white;
}

.btn-info:hover:not(:disabled) {
  background-color: var(--info-dark);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-state, .error-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.error-state {
  color: var(--error);
}

.success-message {
  background-color: var(--success-light);
  border: 1px solid var(--success);
  color: var(--success-dark);
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
  text-align: center;
}

.checkbox-column {
  width: 40px;
  text-align: center;
}

.id-column {
  width: 80px;
  font-weight: 500;
  color: var(--secondary);
  font-family: monospace;
}

.product-name-column {
  min-width: 200px;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.product-name {
  font-weight: 500;
  color: var(--tertiary-dark);
}

.product-unit {
  font-size: 0.75rem;
  color: var(--tertiary);
}

.category-column {
  width: 120px;
}

.category-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.category-badge.category-noodles {
  background-color: var(--secondary-light);
  color: var(--secondary-dark);
}

.category-badge.category-drinks {
  background-color: var(--primary-light);
  color: var(--primary-dark);
}

.category-badge.category-toppings {
  background-color: var(--info-light);
  color: var(--info-dark);
}

.category-badge.category-unknown {
  background-color: var(--neutral-medium);
  color: var(--tertiary-dark);
}

.sku-column {
  width: 120px;
  font-family: monospace;
  font-size: 0.8125rem;
}

.stock-column {
  width: 120px;
}

.stock-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stock-threshold {
  font-size: 0.75rem;
  color: var(--tertiary);
}

.stock-zero {
  color: var(--error);
  font-weight: 600;
}

.stock-low {
  color: var(--error-medium);
  font-weight: 500;
}

.stock-normal {
  color: var(--success);
  font-weight: 500;
}

.price-column {
  width: 100px;
  text-align: right;
  font-weight: 500;
  color: var(--tertiary-dark);
}

.status-column {
  width: 100px;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.status-badge.status-active {
  background-color: var(--success-light);
  color: var(--success-dark);
}

.status-badge.status-inactive {
  background-color: var(--error-light);
  color: var(--error-dark);
}

.expiry-column {
  width: 120px;
  font-size: 0.8125rem;
}

.expired {
  color: var(--error);
  font-weight: 600;
}

.expiring-soon {
  color: var(--error-medium);
  font-weight: 500;
}

.expiring-month {
  color: var(--info);
}

.actions-column {
  width: 160px;
  text-align: center;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
  justify-content: center;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
  font-size: 1rem;
}

.action-btn:hover {
  background-color: var(--neutral-medium);
}

.action-btn.delete:hover {
  background-color: var(--error-light);
}

/* Row styling */
:deep(.data-table tbody tr.inactive) {
  opacity: 0.6;
}

:deep(.data-table tbody tr.out-of-stock) {
  background-color: var(--error-light);
}

:deep(.data-table tbody tr.low-stock) {
  background-color: var(--secondary-light);
}

:deep(.data-table tbody tr.selected) {
  background-color: var(--primary-light);
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--tertiary);
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

/* Custom checkbox styling */
input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--primary);
  cursor: pointer;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .products-page {
    padding: 1rem;
  }

  .filters-section {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .page-title {
    font-size: 1.5rem;
    text-align: center;
  }
  
  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.8125rem;
  }

  .filters-section {
    grid-template-columns: 1fr;
    padding: 1rem;
  }

  .action-buttons {
    flex-direction: column;
    gap: 0.125rem;
  }

  .report-cards {
    grid-template-columns: 1fr;
  }
}

.sku-column {
  width: 120px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--primary-dark);
  background-color: var(--primary-light);
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  border: 1px solid var(--primary-medium);
}

/* Expiry Date Column - Enhanced visibility with better color coding */
.expiry-column {
  width: 140px;
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.5rem;
}

/* Default expiry date styling */
.expiry-column span {
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  font-weight: 600;
  background-color: var(--neutral-light);
  color: var(--tertiary-dark);
  border: 1px solid var(--neutral-medium);
}

/* Expired items - High priority alert */
.expired {
  background-color: var(--error-light) !important;
  color: var(--error-dark) !important;
  border: 1px solid var(--error) !important;
  font-weight: 700;
  animation: pulse-error 2s infinite;
}

/* Expiring soon (within 7 days) - Warning state */
.expiring-soon {
  background-color: #FEF3C7 !important;
  color: #92400E !important;
  border: 1px solid #F59E0B !important;
  font-weight: 600;
}

/* Expiring within a month - Info state */
.expiring-month {
  background-color: var(--info-light) !important;
  color: var(--info-dark) !important;
  border: 1px solid var(--info) !important;
  font-weight: 500;
}

/* Fresh items (more than 30 days) */
.expiry-column span:not(.expired):not(.expiring-soon):not(.expiring-month) {
  background-color: var(--success-light);
  color: var(--success-dark);
  border: 1px solid var(--success);
}

/* Add pulse animation for expired items */
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

/* Hover effects for better interactivity */
.sku-column:hover {
  background-color: var(--primary-medium);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(115, 146, 226, 0.3);
  transition: all 0.2s ease;
}

.expiry-column span:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

/* Improve table cell padding for these columns */
:deep(.data-table td.sku-column),
:deep(.data-table td.expiry-column) {
  padding: 0.75rem;
  vertical-align: middle;
}

/* Add tooltip-like styling for better UX */
.sku-column::before {
  content: "SKU: ";
  font-size: 0.7rem;
  color: var(--primary-medium);
  font-weight: 400;
  display: block;
  margin-bottom: 0.25rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .sku-column {
    font-size: 0.8rem;
    padding: 0.5rem;
  }
  
  .expiry-column {
    width: 120px;
    font-size: 0.8rem;
  }
  
  .expiry-column span {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
  }
}
</style>