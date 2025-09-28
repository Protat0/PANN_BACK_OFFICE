<template>
  <div class="container-fluid pt-2 pb-4 products-page">
    <!-- Reports Section -->
    <div class="row mb-3" v-if="!loading">
      <div class="col-6 col-md-3 mb-2">
        <CardTemplate
          size="xs"
          border-color="error"
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
          border-color="accent"
          border-position="start"
          title="Categories"
          :value="totalCategories"
          subtitle="Total"
          :loading="categoryStatsLoading"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && products.length === 0" class="text-center py-5">
      <div class="spinner-border text-accent" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-tertiary">Loading products...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="alert alert-danger text-center" role="alert">
      <p class="mb-3">{{ error }}</p>
      <button class="btn btn-submit" @click="refreshData">Try Again</button>
    </div>

    <!-- Action Bar and Filters -->
    <div v-if="!loading || products.length > 0" class="action-bar mb-3">
      <div class="action-controls">
        <div class="action-row">
          <!-- Left Side: Main Actions -->
          <div v-if="selectedProducts.length === 0" class="d-flex gap-2">
            <!-- Add Products Dropdown - FIXED -->
            <div class="dropdown dropdown-container" ref="addDropdown">
              <button 
                class="btn btn-add btn-sm btn-with-icon-sm dropdown-toggle"
                type="button"
                @click="toggleAddDropdown"
                :class="{ 'active': showAddDropdown }"
              >
                <Plus :size="14" />
                ADD ITEM
              </button>
              
              <div 
                class="dropdown-menu add-dropdown-menu" 
                :class="{ 'show': showAddDropdown }"
              >
                <button class="dropdown-item" @click="handleSingleProduct">
                  <div class="d-flex align-items-center gap-3">
                    <Plus :size="16" class="text-accent" />
                    <div>
                      <div class="fw-semibold">Single Product</div>
                      <small class="text-tertiary">Add one product manually</small>
                    </div>
                  </div>
                </button>
                
                <button class="dropdown-item" @click="handleBulkAdd">
                  <div class="d-flex align-items-center gap-3">
                    <Package :size="16" class="text-accent" />
                    <div>
                      <div class="fw-semibold">Bulk Entry</div>
                      <small class="text-tertiary">Add multiple products (5-20 items)</small>
                    </div>
                  </div>
                </button>
                
                <button class="dropdown-item" @click="handleImport">
                  <div class="d-flex align-items-center gap-3">
                    <FileText :size="16" class="text-accent" />
                    <div>
                      <div class="fw-semibold">Import File</div>
                      <small class="text-tertiary">Upload CSV/Excel (20+ items)</small>
                    </div>
                  </div>
                </button>
              </div>
            </div>

            <button class="btn btn-filter btn-sm" @click="toggleColumnFilter">
              <Settings :size="14" class="me-1" />
              COLUMNS
            </button>
            <button class="btn btn-export btn-sm" @click="exportData">
              EXPORT
            </button>
          </div>

          <!-- Selection Actions -->
          <div v-if="selectedProducts.length > 0" class="d-flex gap-2">
            <button 
              class="btn btn-delete btn-sm btn-with-icon-sm"
              @click="deleteSelected"
            >
              <Trash2 :size="14" />
              DELETE ({{ selectedProducts.length }})
            </button>
          </div>

          <!-- Right Side: Filters and Search -->
          <div class="d-flex align-items-center gap-2">
            <!-- Search Toggle -->
            <button 
              class="btn btn-filter btn-sm search-toggle"
              @click="toggleSearchMode"
              :class="{ 'active': searchMode }"
            >
              <Search :size="16" />
            </button>

            <!-- Filter Dropdowns -->
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

            <!-- Search Bar -->
            <div v-if="searchMode" class="search-container">
              <div class="position-relative">
                <input 
                  ref="searchInput"
                  v-model="searchFilter" 
                  @input="applyFilters"
                  type="text" 
                  class="form-control form-control-sm search-input"
                  placeholder="Search products..."
                />
                <button 
                  class="btn btn-sm btn-link position-absolute end-0 top-50 translate-middle-y text-tertiary"
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

    <!-- Data Table with fixed overflow -->
    <div class="table-wrapper">
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
            <th>Item name <ChevronUp :size="14" class="ms-1" /></th>
            <th v-if="isColumnVisible('sku')" style="width: 200px;">SKU</th>
            <th v-if="isColumnVisible('category')" style="width: 120px;">Category</th>
            <th v-if="isColumnVisible('sellingPrice')" style="width: 100px; text-align: right;">Price</th>
            <th v-if="isColumnVisible('costPrice')" style="width: 100px; text-align: right;">Cost</th>
            <th style="width: 80px;">Margin</th>
            <th v-if="isColumnVisible('stock')" style="width: 100px;">In stock</th>
            <th v-if="isColumnVisible('status')" style="width: 80px;">Status</th>
            <th v-if="isColumnVisible('expiryDate')" style="width: 130px;">Expiry Date</th>
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
            <td v-if="isColumnVisible('sku')" class="text-left">
              <code class="text-primary">
                {{ product.SKU || '—' }}
              </code>
            </td>
            <td v-if="isColumnVisible('category')">
              <span :class="['badge', 'rounded-pill', getCategoryBadgeClass(product.category_id)]">
                {{ getCategoryName(product.category_id) }}
              </span>
            </td>
            <td v-if="isColumnVisible('sellingPrice')" class="text-end fw-medium">
              ₱{{ formatPrice(product.selling_price) }}
            </td>
            <td v-if="isColumnVisible('costPrice')" class="text-end fw-medium">
              ₱{{ formatPrice(product.cost_price) }}
            </td>
            <td class="text-center fw-medium">
              <span :class="getMarginClass(product.cost_price, product.selling_price)">
                {{ calculateMargin(product.cost_price, product.selling_price) }}%
              </span>
            </td>
            <td v-if="isColumnVisible('stock')" class="text-end">
              <span :class="getStockDisplayClass(product)">
                {{ product.stock || '—' }}
              </span>
            </td>
            <td v-if="isColumnVisible('status')" class="text-center">
              <span :class="getStatusBadgeClass(product.status)">
                {{ getStatusText(product.status) }}
              </span>
            </td>
            <td v-if="isColumnVisible('expiryDate')" class="text-center">
              <small :class="getExpiryDateClass(product.expiry_date)">
                {{ formatExpiryDate(product.expiry_date) }}
              </small>
            </td>
            <td>
              <div class="d-flex gap-1 justify-content-center">
                <button 
                  class="btn btn-outline-secondary btn-icon-only btn-xs action-btn action-btn-edit" 
                  @click="editProduct(product)"
                  title="Edit"
                >
                  <Edit :size="12" />
                </button>
                <button 
                  class="btn btn-outline-primary btn-icon-only btn-xs action-btn action-btn-view" 
                  @click="viewProduct(product)"
                  title="View"
                >
                  <Eye :size="12" />
                </button>
                <button 
                  class="btn btn-outline-info btn-icon-only btn-xs action-btn action-btn-stock" 
                  @click="restockProduct(product)"
                  title="Stock"
                >
                  <Package :size="12" />
                </button>
                <button 
                  class="btn btn-outline-danger btn-icon-only btn-xs action-btn action-btn-delete" 
                  @click="deleteProduct(product)"
                  title="Delete"
                >
                  <Trash2 :size="12" />
                </button>
              </div>
            </td>
          </tr>
        </template>
      </DataTable>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && filteredProducts.length === 0 && !error" class="text-center py-5">
      <div class="card">
        <div class="card-body py-5">
          <Package :size="48" class="text-tertiary mb-3" />
          <p class="text-tertiary mb-3">
            {{ products.length === 0 ? 'No products found' : 'No products match the current filters' }}
          </p>
          <button 
            v-if="products.length === 0" 
            class="btn btn-add btn-with-icon" 
            @click="handleSingleProduct"
          >
            <Plus :size="16" />
            Add First Product
          </button>
          <button 
            v-else 
            class="btn btn-refresh btn-with-icon"
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
      :categories="categories"
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

    <ColumnFilterModal
      :show="showColumnFilter"
      :current-visible-columns="visibleColumns"
      @close="showColumnFilter = false"
      @apply="handleColumnChanges"
    />
  </div>
</template>

<script>
import { useToast } from '@/composables/useToast.js'
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { useProducts } from '../../composables/ui/products/useProducts'
import AddProductModal from '../../components/products/AddProductModal.vue'
import StockUpdateModal from '../../components/products/StockUpdateModal.vue'
import ViewProductModal from '../../components/products/ViewProductModal.vue'
import ReportsModal from '../../components/products/ReportsModal.vue'
import DataTable from '@/components/common/TableTemplate.vue'
import CardTemplate from '@/components/common/CardTemplate.vue'
import ImportModal from '../../components/products/ImportModal.vue'
import ColumnFilterModal from '@/components/products/ColumnFilterModal.vue'
import productsApiService from '../../services/apiProducts.js'
import { 
  Plus, Search, X, ChevronUp, Package, Trash2,
  RefreshCw, FileText, Edit, Eye, Lock, Unlock, Settings
} from 'lucide-vue-next'

export default {
  name: 'Products',
  components: {
    AddProductModal, StockUpdateModal, ViewProductModal,
    ColumnFilterModal, ImportModal, ReportsModal,
    DataTable, CardTemplate,
    Plus, Search, X, ChevronUp, Package, Trash2,
    RefreshCw, FileText, Edit, Eye, Lock, Unlock, Settings
  },
  
  setup() {
    const productsComposable = useProducts()
    const { success, error, warning, info, loading, dismiss } = useToast()
    
    // Simple category stats state
    const totalCategories = ref(0)
    const categoryStatsLoading = ref(false)
    
    // Fetch category stats using the API service
    const fetchCategoryStats = async () => {
      try {
        categoryStatsLoading.value = true
        const result = await productsApiService.getCategoryStats()
        
        if (result.success) {
          totalCategories.value = result.stats.category_overview.total_categories || 0
        }
      } catch (err) {
        console.error('Error fetching category stats:', err)
      } finally {
        categoryStatsLoading.value = false
      }
    }
    
    onMounted(async () => {
      productsComposable.initializeProducts()
      await fetchCategoryStats()
    })
    
    onBeforeUnmount(() => {
      productsComposable.cleanupProducts()
    })
    
    return { 
      ...productsComposable,
      totalCategories,
      categoryStatsLoading,
      toast: { success, error, warning, info, loading, dismiss }
    }
  },

  methods: {
    showAddProductModal() {
      this.$refs.addProductModal?.openAdd?.()
    },
    
    editProduct(product) {
      const enrichedProduct = {
        ...product,
        category_id: product.category_id || ''
      }
      
      this.$refs.viewProductModal?.close?.()
      this.$refs.addProductModal?.openEdit?.(enrichedProduct)
    },
    
    viewProduct(product) {
      this.$router.push(`/products/${product._id}`)
    },
        
    restockProduct(product) {
      this.$refs.stockUpdateModal?.openStock?.(product)
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
    
    async showLowStockReport() {
      await this.$refs.reportsModal?.showLowStockModal?.()
    },
    
    async showExpiringReport() {
      await this.$refs.reportsModal?.showExpiringModal?.()
    },
    
    handleSingleProduct(event) {
      event?.stopPropagation()
      this.showAddProductModal()
      this.closeAddDropdown()
    },
    
    handleImport(event) {
      event?.stopPropagation()
      
      const importModalElement = document.getElementById('importModal')
      if (importModalElement) {
        try {
          const modal = new bootstrap.Modal(importModalElement)
          modal.show()
        } catch (error) {
          console.error('Error showing modal:', error)
        }
      }
      
      this.closeAddDropdown()
    },
    
    selectAll(event) {
      this.$options.setup().selectAll(event.target.checked)
      const count = event.target.checked ? this.paginatedProducts.length : 0
      if (count > 0) {
        this.toast.info(`Selected ${count} products`)
      } else {
        this.toast.info('Selection cleared')
      }
    },

    handleProductSuccess(result) {
      if (result.message) {
        this.toast.success(result.message)
      } else {
        this.toast.success('Item added') // The exact toast you wanted
      }
    },

    handleStockUpdateSuccess(result) {
      this.toast.success(result.message || 'Stock updated successfully')
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
    },

    handleImportError(error) {
      this.toast.error(
        `Import failed: ${error.message || 'An unexpected error occurred'}`,
        { duration: 8000 }
      )
    }
  }
}
</script>

<style scoped>
/* Page Container */
.products-page {
  min-height: 100vh;
  background-color: var(--surface-secondary);
  color: var(--text-secondary);
  position: relative; /* Establish positioning context */
}

/* Action Bar */
.action-bar {
  background-color: var(--surface-primary);
  border: 1px solid var(--border-secondary);
  box-shadow: var(--shadow-sm);
  border-radius: 0.75rem;
  /* Remove overflow: hidden to allow dropdown to escape */
  position: relative;
  z-index: 100; /* Ensure action bar is above other content */
}

.action-controls {
  background-color: var(--surface-primary);
  border-bottom: 1px solid var(--border-primary);
  transition: background-color 0.3s ease, color 0.3s ease;
}

.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

/* Dropdown Container - Ensures dropdown can overflow */
.dropdown-container {
  position: relative;
  z-index: 1050; /* Bootstrap's dropdown z-index */
}

.dropdown {
  position: relative;
}

.add-dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 1055; /* Higher than Bootstrap's default dropdown z-index */
  min-width: 280px;
  margin-top: 0.25rem;
  background-color: var(--surface-elevated);
  border: 1px solid var(--border-primary);
  border-radius: 0.75rem;
  box-shadow: var(--shadow-xl); /* Enhanced shadow for better visibility */
  animation: dropdownSlide 0.2s ease;
  /* Ensure dropdown is not clipped */
  transform: translateZ(0); /* Create new stacking context */
}

.add-dropdown-menu.show {
  display: block;
}

/* Table Wrapper - Controls overflow separately from action bar */
.table-wrapper {
  position: relative;
  z-index: 1; /* Lower than dropdown */
}

/* Override table container if needed */
.table-wrapper :deep(.table-container) {
  position: relative;
  z-index: 1;
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

.dropdown-item {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-primary);
  background: transparent;
  border-left: none;
  border-right: none;
  border-top: none;
  transition: background-color 0.2s ease;
  cursor: pointer;
  width: 100%;
  text-align: left;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background-color: var(--state-hover);
}

/* Filters */
.filter-dropdown {
  min-width: 120px;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  display: block;
  color: var(--text-tertiary);
}

.form-select {
  background-color: var(--input-bg);
  border-color: var(--input-border);
  color: var(--input-text);
}

.form-select:focus {
  border-color: var(--border-accent);
  box-shadow: 0 0 0 0.2rem rgba(160, 123, 227, 0.25);
}

/* Search */
.search-container {
  min-width: 300px;
}

.search-input {
  padding-right: 2.5rem;
  height: calc(1.5em + 0.75rem + 2px);
  background-color: var(--input-bg);
  border-color: var(--input-border);
  color: var(--input-text);
}

.search-toggle {
  height: calc(1.5em + 0.75rem + 2px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 0.75rem;
}

/* Button States */
.btn.active {
  color: var(--text-inverse);
  background-color: var(--secondary);
  border-color: var(--secondary);
}

/* Card Styling */
.card {
  background-color: var(--surface-primary);
  border: 1px solid var(--border-secondary);
  color: var(--text-primary);
  box-shadow: var(--shadow-md);
}

/* Ensure proper stacking context for modals */
.modal,
.modal-backdrop {
  z-index: 1060; /* Higher than dropdown */
}

/* Responsive */
@media (max-width: 768px) {
  .action-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-container {
    min-width: 100%;
  }
  
  .add-dropdown-menu {
    min-width: 250px;
    right: 0;
    left: auto;
  }
  
  .dropdown-item {
    padding: 0.875rem 1rem;
  }
}
</style>