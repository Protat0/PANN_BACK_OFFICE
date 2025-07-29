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
          value="3"
          subtitle="Active"
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

    <!-- Success Message -->
    <div v-if="successMessage" class="alert alert-success text-center" role="alert">
      {{ successMessage }}
    </div>

    <!-- Action Bar and Filters -->
    <div v-if="!loading || products.length > 0" class="action-bar-container mb-3">
      <div class="action-bar-controls">
        <div class="action-row">
          <!-- Left Side: Main Actions -->
          <div v-if="selectedProducts.length === 0" class="d-flex gap-2">
            <!-- Add Products Dropdown -->
            <div class="dropdown" ref="addDropdown">
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
                class="dropdown-menu custom-dropdown-menu" 
                :class="{ 'show': showAddDropdown }"
              >
                <button class="dropdown-item custom-dropdown-item" @click="handleSingleProduct">
                  <div class="d-flex align-items-center gap-3">
                    <Plus :size="16" class="text-accent" />
                    <div>
                      <div class="fw-semibold">Single Product</div>
                      <small class="text-tertiary">Add one product manually</small>
                    </div>
                  </div>
                </button>
                
                <button class="dropdown-item custom-dropdown-item" @click="handleBulkAdd">
                  <div class="d-flex align-items-center gap-3">
                    <Package :size="16" class="text-accent" />
                    <div>
                      <div class="fw-semibold">Bulk Entry</div>
                      <small class="text-tertiary">Add multiple products (5-20 items)</small>
                    </div>
                  </div>
                </button>
                
                <button class="dropdown-item custom-dropdown-item" @click="handleImport">
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
            <button 
              class="btn btn-export btn-sm"
              @click="exportData"
            >
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
              DELETE
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
                  class="form-select form-select-sm input-theme" 
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
                  class="form-select form-select-sm input-theme" 
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
                  class="form-control form-control-sm input-theme search-input"
                  placeholder="Search"
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

    <!-- Data Table -->
    <DataTable
      v-if="!loading || products.length > 0"
      :total-items="filteredProducts.length"
      :current-page="currentPage"
      :items-per-page="itemsPerPage"
      @page-changed="handlePageChange"
    >
      <template #header>
        <tr>
          <!-- Checkbox Column -->
          <th style="width: 40px;">
            <input 
              type="checkbox" 
              class="form-check-input" 
              @change="selectAll" 
              :checked="allSelected"
              :indeterminate="someSelected"
            />
          </th>
          
          <!-- Product Name Column -->
          <th>
            Item name
            <ChevronUp :size="14" class="ms-1" />
          </th>
          
          <!-- SKU Column -->
          <th v-if="isColumnVisible('sku')" style="width: 100px;">
            SKU
          </th>
          
          <!-- Category Column -->
          <th v-if="isColumnVisible('category')" style="width: 120px;">
            Category
          </th>
          
          <!-- Selling Price Column -->
          <th v-if="isColumnVisible('sellingPrice')" style="width: 100px;">
            Price
          </th>
          
          <!-- Cost Price Column -->
          <th v-if="isColumnVisible('costPrice')" style="width: 100px;">
            Cost
          </th>
          
          <!-- Margin Column -->
          <th style="width: 80px;">
            Margin
          </th>
          
          <!-- Stock Column -->
          <th v-if="isColumnVisible('stock')" style="width: 100px;">
            In stock
          </th>
          
          <!-- Status Column -->
          <th v-if="isColumnVisible('status')" style="width: 80px;">
            Status
          </th>
          
          <!-- Expiry Date Column -->
          <th v-if="isColumnVisible('expiryDate')" style="width: 110px;">
            Expiry Date
          </th>
          
          <!-- Actions Column -->
          <th style="width: 160px;">
            Actions
          </th>
        </tr>
      </template>

      <template #body>
        <tr 
          v-for="product in paginatedProducts"
          :key="product._id"
          :class="getRowClass(product)"
        >
          <!-- Checkbox Column -->
          <td>
            <input 
              type="checkbox" 
              class="form-check-input"
              :value="product._id"
              v-model="selectedProducts"
            />
          </td>
          
          <!-- Product Name Column -->
          <td>
            <div :class="['fw-medium', getProductNameClass(product)]">
              {{ product.product_name }}
            </div>
          </td>
          
          <!-- SKU Column -->
          <td v-if="isColumnVisible('sku')" class="text-center">
            <code class="text-primary surface-tertiary px-2 py-1 rounded">
              {{ product.SKU || '—' }}
            </code>
          </td>
          
          <!-- Category Column -->
          <td v-if="isColumnVisible('category')">
            <span :class="['badge', 'rounded-pill', getCategoryBadgeClass(product.category_id)]">
              {{ getCategoryName(product.category_id) }}
            </span>
          </td>
          
          <!-- Selling Price Column -->
          <td v-if="isColumnVisible('sellingPrice')" class="text-end fw-medium">
            ₱{{ formatPrice(product.selling_price) }}
          </td>
          
          <!-- Cost Price Column -->
          <td v-if="isColumnVisible('costPrice')" class="text-end fw-medium">
            ₱{{ formatPrice(product.cost_price) }}
          </td>
          
          <!-- Margin Column -->
          <td class="text-center fw-medium">
            <span :class="getMarginClass(product.cost_price, product.selling_price)">
              {{ calculateMargin(product.cost_price, product.selling_price) }}%
            </span>
          </td>
          
          <!-- Stock Column -->
          <td v-if="isColumnVisible('stock')" class="text-end">
            <span :class="getStockDisplayClass(product)">
              {{ product.stock || '—' }}
            </span>
          </td>
          
          <!-- Status Column -->
          <td v-if="isColumnVisible('status')" class="text-center">
            <span :class="getStatusBadgeClass(product.status)">
              {{ getStatusText(product.status) }}
            </span>
          </td>
          
          <!-- Expiry Date Column -->
          <td v-if="isColumnVisible('expiryDate')" class="text-center">
            <small :class="getExpiryDateClass(product.expiry_date)">
              {{ formatExpiryDate(product.expiry_date) }}
            </small>
          </td>
          
          <!-- Actions Column -->
          <td>
            <div class="d-flex gap-1 justify-content-center">
              <button 
                class="btn btn-outline-secondary btn-icon-only btn-xs action-btn action-btn-edit" 
                @click="editProduct(product)"
                data-bs-toggle="tooltip"
                title="Edit Product"
              >
                <Edit :size="12" />
              </button>
              <button 
                class="btn btn-outline-primary btn-icon-only btn-xs action-btn action-btn-view" 
                @click="viewProduct(product)"
                data-bs-toggle="tooltip"
                title="View Details"
              >
                <Eye :size="12" />
              </button>
              <button 
                class="btn btn-outline-info btn-icon-only btn-xs action-btn action-btn-stock" 
                @click="restockProduct(product)"
                data-bs-toggle="tooltip"
                title="Update Stock"
              >
                <Package :size="12" />
              </button>
              <button 
                class="btn btn-outline-success btn-icon-only btn-xs action-btn action-btn-status"
                @click="toggleProductStatus(product)"
                data-bs-toggle="tooltip"
                :title="product.status === 'active' ? 'Deactivate Product' : 'Activate Product'"
                :class="{ 'action-btn-status-inactive': product.status !== 'active' }"
              >
                <Lock v-if="product.status === 'active'" :size="12" />
                <Unlock v-else :size="12" />
              </button>
              <button 
                class="btn btn-outline-danger btn-icon-only btn-xs action-btn action-btn-delete" 
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
      <div class="card card-theme">
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
import { onMounted, onBeforeUnmount } from 'vue'
import { useProducts } from '../../composables/ui/products/useProducts'
import AddProductModal from '../../components/products/AddProductModal.vue'
import StockUpdateModal from '../../components/products/StockUpdateModal.vue'
import ViewProductModal from '../../components/products/ViewProductModal.vue'
import ReportsModal from '../../components/products/ReportsModal.vue'
import DataTable from '@/components/common/TableTemplate.vue'
import CardTemplate from '@/components/common/CardTemplate.vue'
import ImportModal from '../../components/products/ImportModal.vue'
import ColumnFilterModal from '@/components/products/ColumnFilterModal.vue'
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
  Unlock,
  Settings
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
    Unlock,
    Settings
  },
  
  setup() {
    const productsComposable = useProducts()
    
    // Lifecycle hooks
    onMounted(() => {
      productsComposable.initializeProducts()
    })
    
    onBeforeUnmount(() => {
      productsComposable.cleanupProducts()
    })
    
    return {
      ...productsComposable
    }
  },
  
  methods: {
    // Modal-specific methods (these stay in the component)
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
    
    async showLowStockReport() {
      if (this.$refs.reportsModal && this.$refs.reportsModal.showLowStockModal) {
        await this.$refs.reportsModal.showLowStockModal()
      }
    },
    
    async showExpiringReport() {
      if (this.$refs.reportsModal && this.$refs.reportsModal.showExpiringModal) {
        await this.$refs.reportsModal.showExpiringModal()
      }
    },
    
    // Override composable methods to handle modal triggers
    handleSingleProduct(event) {
      if (event) event.stopPropagation()
      this.showAddProductModal()
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
        }
      } else {
        console.error('❌ Modal element #importModal not found in DOM')
      }
      
      this.closeAddDropdown()
    },
    
    // Handle selectAll event from template
    selectAll(event) {
      // Call the composable's selectAll with the checkbox state
      this.$options.setup().selectAll(event.target.checked)
    }
  }
}
</script>

<style scoped>
/* ==========================================================================
   PRODUCTS PAGE - SEMANTIC THEME SYSTEM
   ========================================================================== */

.products-page {
  min-height: 100vh;
  @apply page-container;
}

/* ==========================================================================
   ACTION BAR - SEMANTIC STYLING
   ========================================================================== */

.action-bar-container {
  @apply card-theme shadow-sm;
  border-radius: 0.75rem;
  overflow: hidden;
}

.action-bar-controls {
  @apply border-bottom-theme surface-primary transition-theme;
}

.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

/* ==========================================================================
   FILTERS - SEMANTIC STYLING
   ========================================================================== */

.filter-dropdown {
  min-width: 120px;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  display: block;
  @apply text-tertiary;
}

.search-container {
  min-width: 300px;
}

.search-input {
  padding-right: 2.5rem;
  height: calc(1.5em + 0.75rem + 2px);
}

.search-toggle {
  height: calc(1.5em + 0.75rem + 2px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 0.75rem;
}

/* ==========================================================================
   DROPDOWN MENU - SEMANTIC STYLING
   ========================================================================== */

.custom-dropdown-menu {
  min-width: 280px;
  border-radius: 0.75rem;
  animation: dropdownSlide 0.2s ease;
  @apply surface-elevated border-theme shadow-lg;
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
  @apply border-bottom-theme transition-theme;
}

.custom-dropdown-item:last-child {
  border-bottom: none;
}

.custom-dropdown-item:hover {
  @apply hover-surface;
}

/* ==========================================================================
   BUTTON STATES - SEMANTIC
   ========================================================================== */

.btn.active {
  @apply text-inverse;
  background-color: var(--secondary);
  border-color: var(--secondary);
}

/* ==========================================================================
   RESPONSIVE DESIGN
   ========================================================================== */

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
}</style>