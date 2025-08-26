<template>
  <div class="container-fluid pt-2 pb-4 categories-page surface-secondary">
    <!-- Page Title and Uncategorized Link -->
    <div class="d-flex justify-content-between align-items-start mb-3">
      <div>
        <h1 class="h3 fw-semibold text-primary mb-0">Category Management</h1>
      </div>
      <div>
        <router-link 
          to="/uncategorized" 
          class="btn btn-filter btn-sm btn-with-icon-sm"
        >
          <Package :size="14" class="me-1" />
          Uncategorized ({{ uncategorizedCount }})
        </router-link>
      </div>
    </div>

    <!-- Action Bar and Filters -->
    <div class="action-bar-container mb-3">
      <div class="action-bar-controls surface-card border-theme">
        <div class="action-row">
          <!-- Left Side: Main Actions -->
          <div v-if="selectedCategories.length === 0" class="d-flex gap-2">
            <button 
              class="btn btn-add btn-sm btn-with-icon-sm"
              @click="handleAddCategory"
              :disabled="loading"
            >
              <div v-if="loading" class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <Plus v-else :size="14" />
              {{ loading ? 'CREATING...' : 'ADD CATEGORY' }}
            </button>

            <button 
              class="btn btn-export btn-sm btn-with-icon-sm"
              @click="handleExport" 
              :disabled="loading || categories.length === 0"
            >
              <FileDown :size="14" />
              EXPORT
            </button>
          </div>

          <!-- Bulk Actions for Selected Items -->
          <div v-else class="d-flex gap-2">
            <span class="text-tertiary-medium">{{ selectedCategories.length }} selected</span>
            <button 
              class="btn btn-delete btn-sm btn-with-icon-sm"
              @click="deleteSelected"
              :disabled="loading"
            >
              <Trash2 :size="14" />
              Delete Selected
            </button>
          </div>

          <!-- Right Side: Filters and Search -->
          <div class="d-flex align-items-center gap-2">
            <button 
              class="btn btn-filter btn-sm"
              @click="toggleSearchMode"
              :class="{ 'state-active': searchMode }"
              style="height: calc(1.5em + 0.75rem + 2px); display: flex; align-items: center; justify-content: center; padding: 0 0.75rem;"
            >
              <Search :size="16" />
            </button>

            <!-- Filter Dropdowns -->
            <template v-if="!searchMode">
              <div class="filter-dropdown">
                <label class="filter-label text-tertiary-medium">Status</label>
                <select 
                  class="form-select form-select-sm input-theme" 
                  v-model="statusFilter" 
                  @change="applyFilters"
                >
                  <option value="all">All categories</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="deleted">Deleted</option>
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
                  class="form-control form-control-sm search-input input-theme"
                  placeholder="Search categories..."
                />
                <button 
                  class="btn btn-sm btn-link position-absolute end-0 top-50 translate-middle-y text-tertiary-medium"
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

    <!-- Loading State -->
    <div v-if="loading && categories.length === 0" class="text-center py-4">
      <div class="spinner-border text-accent" role="status">
        <span class="visually-hidden">Loading categories...</span>
      </div>
      <p class="mt-2 text-tertiary-medium">Loading categories...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="status-error" role="alert">
      <strong>Error:</strong> {{ error }}
      <button @click="refreshData" class="btn btn-sm btn-export ms-2">
        Retry
      </button>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="status-success">
      {{ successMessage }}
    </div>

    <!-- Category Cards Section -->
    <div v-if="!loading && !error" class="row g-3 mb-4">
      <!-- Sample Categories Data -->
      <div class="col-6 col-md-3">
        <CardTemplate
          size="md"
          border-color="primary"
          border-position="start"
          title="Drinks"
          subtitle="Hot and cold drinks that are available for all the customers"
          shadow="sm"
          clickable

        >
          <template #content>
            <!-- Selection Checkbox -->
            <div class="position-absolute top-0 start-0 p-2">
              <input 
                type="checkbox" 
                class="form-check-input"
                @click.stop
              />
            </div>

            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <div class="text-primary fw-bold h5 mb-1">55</div>
                <small class="text-tertiary-medium">Products</small>
              </div>
              <div class="category-icon surface-primary-light rounded-circle p-2">
                <Coffee :size="20" class="text-status-primary" />
              </div>
            </div>

            <!-- Sales Data -->
            <div class="mb-2">
              <small class="text-tertiary-medium">Sales: </small>
              <span class="text-success fw-semibold">₱313,882.67</span>
            </div>

            <!-- Action buttons -->
            <div class="d-flex gap-1 mt-2">
              <button 
                class="btn btn-view btn-sm btn-with-icon-sm"
                data-bs-toggle="tooltip"
                title="View Category Details"
              >
                <Eye :size="14" />
                <span class="btn-text">View</span>
              </button>

              <button 
                class="btn btn-delete btn-sm btn-with-icon-sm"
                data-bs-toggle="tooltip"
                title="Delete Category"
              >
                <Trash2 :size="14" />
                Delete
              </button>
            </div>
          </template>
        </CardTemplate>
      </div>

      <div class="col-6 col-md-3">
        <CardTemplate
          size="md"
          border-color="secondary"
          border-position="start"
          title="Noodles"
          subtitle="Different Types of Noodles for customers to eat"
          shadow="sm"
          clickable

        >
          <template #content>
            <!-- Selection Checkbox -->
            <div class="position-absolute top-0 start-0 p-2">
              <input 
                type="checkbox" 
                class="form-check-input"
                @click.stop
              />
            </div>

            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <div class="text-primary fw-bold h5 mb-1">102</div>
                <small class="text-tertiary-medium">Products</small>
              </div>
              <div class="category-icon surface-secondary-light rounded-circle p-2">
                <Utensils :size="20" class="text-status-info" />
              </div>
            </div>

            <!-- Sales Data -->
            <div class="mb-2">
              <small class="text-tertiary-medium">Sales: </small>
              <span class="text-success fw-semibold">₱793,417.04</span>
            </div>

            <!-- Action buttons -->
            <div class="d-flex gap-1 mt-2">
              <button 
                class="btn btn-view btn-sm btn-with-icon-sm"
                data-bs-toggle="tooltip"
                title="View Category Details"
              >
                <Eye :size="14" />
                <span class="btn-text">View</span>
              </button>

              <button 
                class="btn btn-delete btn-sm btn-with-icon-sm"
                data-bs-toggle="tooltip"
                title="Delete Category"
              >
                <Trash2 :size="14" />
                Delete
              </button>
            </div>
          </template>
        </CardTemplate>
      </div>

      <div class="col-6 col-md-3">
        <CardTemplate
          size="md"
          border-color="info"
          border-position="start"
          title="Toppings"
          subtitle="Different Types of Toppings to add to the meals"
          shadow="sm"
          clickable

        >
          <template #content>
            <!-- Selection Checkbox -->
            <div class="position-absolute top-0 start-0 p-2">
              <input 
                type="checkbox" 
                class="form-check-input"
                @click.stop
              />
            </div>

            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <div class="text-primary fw-bold h5 mb-1">40</div>
                <small class="text-tertiary-medium">Products</small>
              </div>
              <div class="category-icon surface-info-light rounded-circle p-2">
                <Star :size="20" class="text-status-info" />
              </div>
            </div>

            <!-- Sales Data -->
            <div class="mb-2">
              <small class="text-tertiary-medium">Sales: </small>
              <span class="text-success fw-semibold">₱533,301.06</span>
            </div>

            <!-- Action buttons -->
            <div class="d-flex gap-1 mt-2">
              <button 
                class="btn btn-view btn-sm btn-with-icon-sm"
                data-bs-toggle="tooltip"
                title="View Category Details"
              >
                <Eye :size="14" />
                <span class="btn-text">View</span>
              </button>

              <button 
                class="btn btn-delete btn-sm btn-with-icon-sm"
                data-bs-toggle="tooltip"
                title="Delete Category"
              >
                <Trash2 :size="14" />
                Delete
              </button>
            </div>
          </template>
        </CardTemplate>
      </div>

      <div class="col-6 col-md-3">
        <CardTemplate
          size="md"
          border-color="success"
          border-position="start"
          title="Others"
          subtitle="These items are the different items available in the menu"
          shadow="sm"
          clickable

        >
          <template #content>
            <!-- Selection Checkbox -->
            <div class="position-absolute top-0 start-0 p-2">
              <input 
                type="checkbox" 
                class="form-check-input"
                @click.stop
              />
            </div>

            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <div class="text-primary fw-bold h5 mb-1">42</div>
                <small class="text-tertiary-medium">Products</small>
              </div>
              <div class="category-icon surface-success-light rounded-circle p-2">
                <ShoppingBag :size="20" class="text-status-success" />
              </div>
            </div>

            <!-- Sales Data -->
            <div class="mb-2">
              <small class="text-tertiary-medium">Sales: </small>
              <span class="text-success fw-semibold">₱182,981.72</span>
            </div>

            <!-- Action buttons -->
            <div class="d-flex gap-1 mt-2">
              <button 
                class="btn btn-view btn-sm btn-with-icon-sm"
                data-bs-toggle="tooltip"
                title="View Category Details"
              >
                <Eye :size="14" />
                <span class="btn-text">View</span>
              </button>

              <button 
                class="btn btn-delete btn-sm btn-with-icon-sm"
                data-bs-toggle="tooltip"
                title="Delete Category"
              >
                <Trash2 :size="14" />
                Delete
              </button>
            </div>
          </template>
        </CardTemplate>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="filteredCategories.length > itemsPerPage" class="d-flex justify-content-center">
      <nav aria-label="Categories pagination">
        <ul class="pagination pagination-sm">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <button 
              class="page-link" 
              @click="handlePageChange(currentPage - 1)" 
              :disabled="currentPage === 1"
            >
              Previous
            </button>
          </li>
          
          <li 
            v-for="page in Math.ceil(filteredCategories.length / itemsPerPage)" 
            :key="page"
            class="page-item" 
            :class="{ active: page === currentPage }"
          >
            <button class="page-link" @click="handlePageChange(page)">
              {{ page }}
            </button>
          </li>
          
          <li class="page-item" :class="{ disabled: currentPage === Math.ceil(filteredCategories.length / itemsPerPage) }">
            <button 
              class="page-link" 
              @click="handlePageChange(currentPage + 1)" 
              :disabled="currentPage === Math.ceil(filteredCategories.length / itemsPerPage)"
            >
              Next
            </button>
          </li>
        </ul>
      </nav>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && !error && filteredCategories.length === 0" class="text-center py-5">
      <Package :size="64" class="text-tertiary-medium mb-3" />
      <h5 class="text-tertiary-dark">No categories found</h5>
      <p class="text-tertiary-medium mb-3">
        {{ getEmptyStateMessage() }}
      </p>
      <button 
        v-if="categories.length === 0 && statusFilter !== 'deleted'"
        class="btn btn-add"
        @click="handleAddCategory"
      >
        <Plus :size="16" class="me-1" />
        Add First Category
      </button>
      <button 
        v-else-if="searchFilter || statusFilter !== 'all'"
        class="btn btn-filter"
        @click="clearFilters"
      >
        Clear Filters
      </button>
    </div>

    <!-- Add Category Modal -->
    <AddCategoryModal ref="addCategoryModal" @category-added="onCategoryAdded" />
  </div>
</template>

<script>
import CardTemplate from '@/components/common/CardTemplate.vue'
import AddCategoryModal from '@/components/categories/AddCategoryModal.vue'
import { useCategories } from '@/composables/ui/categories/useCategories'
import { 
  Plus, 
  Search,
  X,
  Package, 
  Trash2,
  Eye,
  Coffee,
  Star,
  Zap,
  Utensils,
  ShoppingBag,
  Grid3x3,
  RotateCcw,
  FileDown
} from 'lucide-vue-next'

export default {
  name: 'Categories',
  components: {
    CardTemplate,
    AddCategoryModal,
    Plus,
    Search,
    X,
    Package,
    Trash2,
    Eye,
    Coffee,
    Star,
    Zap,
    Utensils,
    ShoppingBag,
    Grid3x3,
    RotateCcw,
    FileDown
  },

  setup() {
    // Use the categories composable
    const {
      // State
      categories,
      filteredCategories,
      selectedCategories,
      loading,
      error,
      successMessage,
      
      // UI State
      searchMode,
      
      // Pagination
      currentPage,
      itemsPerPage,
      paginatedCategories,
      
      // Filters
      statusFilter,
      searchFilter,
      includeDeleted,
      
      // Computed
      allSelected,
      someSelected,
      activeCategories,
      
      // Core Methods
      fetchCategoriesWithSalesData,
      createCategory,
      updateCategory,
      softDeleteCategory,
      hardDeleteCategory,
      restoreCategory,
      getCategoryDeleteInfo,
      refreshData,
      
      // Filter and Search
      applyFilters,
      clearFilters,
      
      // Selection Methods
      selectAll,
      deleteSelected,
      
      // UI Methods
      toggleSearchMode,
      clearSearch,
      
      // Pagination
      handlePageChange,
      
      // Formatting Methods
      formatDate,
      formatSalesData,
      getCategoryStatusClass,
      getCategoryStatusText,
      getRowClass,
      
      // Success/Error handlers
      handleCategorySuccess,
      handleCategoryError,
      
      // Lifecycle
      initializeCategories,
      cleanupCategories
    } = useCategories()

    return {
      // Export all useCategories functionality
      categories,
      filteredCategories,
      selectedCategories,
      loading,
      error,
      successMessage,
      searchMode,
      currentPage,
      itemsPerPage,
      paginatedCategories,
      statusFilter,
      searchFilter,
      includeDeleted,
      allSelected,
      someSelected,
      activeCategories,
      fetchCategoriesWithSalesData,
      createCategory,
      updateCategory,
      softDeleteCategory,
      hardDeleteCategory,
      restoreCategory,
      getCategoryDeleteInfo,
      refreshData,
      applyFilters,
      clearFilters,
      selectAll,
      deleteSelected,
      toggleSearchMode,
      clearSearch,
      handlePageChange,
      formatDate,
      formatSalesData,
      getCategoryStatusClass,
      getCategoryStatusText,
      getRowClass,
      handleCategorySuccess,
      handleCategoryError,
      initializeCategories,
      cleanupCategories
    }
  },

  data() {
    return {
      isAdmin: true, // TODO: Get from auth composable
      
      // Uncategorized tracking
      uncategorizedCount: 0,
      UNCATEGORIZED_CATEGORY_ID: '686a4de143821e2b21f725c6'
    }
  },

  computed: {
    // Override paginatedCategories to exclude Uncategorized category
    displayedCategories() {
      return this.paginatedCategories.filter(category => 
        category._id !== this.UNCATEGORIZED_CATEGORY_ID
      )
    }
  },

  async mounted() {
    // Initialize categories using composable
    await this.initializeCategories()
    await this.fetchUncategorizedCount()
  },

  beforeUnmount() {
    // Cleanup using composable
    this.cleanupCategories()
  },

  methods: {
    // Fetch uncategorized products count (category-specific logic)
    async fetchUncategorizedCount() {
      try {
        console.log('Fetching uncategorized products count...')
        
        // Use composable's fetchCategoryProducts method
        const products = await this.$options.setup().fetchCategoryProducts(this.UNCATEGORIZED_CATEGORY_ID)
        
        this.uncategorizedCount = Array.isArray(products) ? products.length : 0
        console.log(`Found ${this.uncategorizedCount} uncategorized products`)
        
      } catch (error) {
        console.error('Error fetching uncategorized count:', error)
        this.uncategorizedCount = 0
      }
    },

    // Modal handlers (keeping existing modal integration)
    async handleAddCategory() {
      console.log('Add Category button clicked')
      
      if (this.$refs.addCategoryModal) {
        this.$refs.addCategoryModal.openAddMode()
      } else {
        console.error('AddCategoryModal ref not found')
      }
    },

    async onCategoryAdded(newCategory) {
      try {
        console.log('New category added:', newCategory)
        
        // Use composable's refresh method
        await this.refreshData()
        await this.fetchUncategorizedCount()
        
        // Use composable's success handler
        this.handleCategorySuccess({
          message: `Category "${newCategory.category_name}" added successfully!`
        })
      } catch (error) {
        console.error('Error refreshing categories after add:', error)
        this.handleCategoryError(error)
      }
    },

    // Navigation (keeping existing logic)
    viewCategory(category) {
      console.log('View category:', category)
      
      const categoryId = category._id || category.id || category.category_id
      
      if (!categoryId) {
        console.error('No valid ID found in category object')
        return
      }
      
      console.log('Navigating with ID:', categoryId)
      this.$router.push({
        name: 'Category Details',
        params: { id: categoryId }
      })
    },

    // Enhanced delete methods using composable
    async handleSoftDelete(category) {
      try {
        const deleteInfo = await this.getCategoryDeleteInfo(category._id)
        
        const categoryName = category.category_name || 'this category'
        const productCount = deleteInfo.delete_info?.products_count || 0
        const subcategoryCount = deleteInfo.delete_info?.subcategories_count || 0
        
        let confirmMessage = `Are you sure you want to delete "${categoryName}"?`
        
        if (productCount > 0 || subcategoryCount > 0) {
          confirmMessage += `\n\nThis category contains:`
          if (subcategoryCount > 0) confirmMessage += `\n• ${subcategoryCount} subcategory`
          if (productCount > 0) confirmMessage += `\n• ${productCount} product(s)`
          confirmMessage += `\n\nProducts will be moved to Uncategorized.`
        }
        
        const confirmed = confirm(confirmMessage)
        if (!confirmed) return

        await this.softDeleteCategory(category._id)
        await this.fetchUncategorizedCount() // Refresh uncategorized count
        
      } catch (error) {
        console.error('Error soft deleting category:', error)
        this.handleCategoryError(error)
      }
    },

    async handleRestore(category) {
      try {
        const confirmed = confirm(`Are you sure you want to restore "${category.category_name}"?`)
        if (!confirmed) return

        await this.restoreCategory(category._id)
        await this.fetchUncategorizedCount() // Refresh uncategorized count
        
      } catch (error) {
        console.error('Error restoring category:', error)
        this.handleCategoryError(error)
      }
    },

    async handleHardDelete(category) {
      try {
        const categoryName = category.category_name || 'this category'
        
        const confirmed = confirm(
          `⚠️ PERMANENT DELETE WARNING ⚠️\n\n` +
          `Are you sure you want to PERMANENTLY delete "${categoryName}"?\n\n` +
          `This action:\n` +
          `• CANNOT be undone\n` +
          `• Will permanently remove all data\n` +
          `• Requires admin permissions\n\n` +
          `Type "DELETE" to confirm this permanent action.`
        )
        
        if (!confirmed) return

        const confirmText = prompt('Please type "DELETE" to confirm permanent deletion:')
        if (confirmText !== 'DELETE') {
          this.handleCategoryError({ message: 'Confirmation text did not match. Operation cancelled.' })
          return
        }

        await this.hardDeleteCategory(category._id)
        await this.fetchUncategorizedCount() // Refresh uncategorized count
        
      } catch (error) {
        console.error('Error hard deleting category:', error)
        this.handleCategoryError(error)
      }
    },

    // Export using composable
    async handleExport() {
      try {
        const exportParams = {
          format: 'csv',
          include_sales_data: true,
          include_deleted: this.includeDeleted
        }
        
        await this.exportCategories(exportParams)
        
      } catch (error) {
        console.error('Export error:', error)
        this.handleCategoryError(error)
      }
    },

    // Utility methods (enhanced with composable integration)
    getCategorySubtitle(category) {
      if (category.isDeleted) {
        return `Deleted ${this.formatDate(category.deleted_at)}`
      }
      return category.description || category.subtitle || `${category.category_name} products`
    },

    getProductCount(category) {
      // Handle different data structures
      if (category.subcategories) {
        return category.subcategories.reduce((total, sub) => total + (sub.product_count || 0), 0)
      }
      return category.product_count || 0
    },

    getEmptyStateMessage() {
      if (this.statusFilter === 'deleted') {
        return 'No deleted categories found.'
      } else if (this.categories.length === 0) {
        return 'Get started by creating your first category.'
      } else if (this.searchFilter) {
        return `No categories match "${this.searchFilter}". Try a different search term.`
      } else {
        return 'Try adjusting your search or filters.'
      }
    },

    // ICON AND STYLING METHODS (keeping existing visual logic)
    getCategoryIcon(category, index) {
      const categoryName = (category.category_name || '').toLowerCase()
      
      if (categoryName.includes('noodles') || categoryName.includes('pasta')) {
        return 'Utensils'
      } else if (categoryName.includes('drink') || categoryName.includes('beverage')) {
        return 'Coffee'
      } else if (categoryName.includes('topping') || categoryName.includes('extra')) {
        return 'Star'
      } else if (categoryName.includes('snack') || categoryName.includes('side')) {
        return 'Zap'
      } else if (categoryName.includes('food') || categoryName.includes('meal')) {
        return 'Package'
      } else if (categoryName.includes('bag') || categoryName.includes('shop')) {
        return 'ShoppingBag'
      }
      
      const icons = ['Package', 'Coffee', 'Star', 'Zap', 'Utensils', 'ShoppingBag', 'Grid3x3']
      return icons[index % icons.length]
    },

    getCategoryBorderColor(category, index) {
      const categoryName = (category.category_name || '').toLowerCase()
      
      if (categoryName.includes('noodle') || categoryName.includes('pasta')) {
        return 'secondary'
      } else if (categoryName.includes('drink') || categoryName.includes('beverage')) {
        return 'primary'
      } else if (categoryName.includes('topping') || categoryName.includes('extra')) {
        return 'info'
      } else if (categoryName.includes('snack') || categoryName.includes('side')) {
        return 'success'
      }
      
      const colors = ['secondary', 'primary', 'info', 'success']
      return colors[index % colors.length]
    },

    getCategoryIconClass(category, index) {
      const borderColor = this.getCategoryBorderColor(category, index)
      return `category-icon surface-${borderColor}-light rounded-circle p-2`
    },

    getCategoryIconColor(category, index) {
      const borderColor = this.getCategoryBorderColor(category, index)
      return `text-status-${borderColor === 'secondary' ? 'info' : borderColor}`
    }
  }
}
</script>


<style scoped>
.categories-page {
  min-height: 100vh;
}

.action-bar-controls {
  border-radius: 0.75rem;
}

.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-dropdown {
  min-width: 120px;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  display: block;
}

.search-container {
  min-width: 300px;
}

.search-input {
  padding-right: 2.5rem;
  height: calc(1.5em + 0.75rem + 2px);
}

.search-container .position-relative .btn {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.category-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
}

@media (max-width: 768px) {
  .action-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-container {
    min-width: 100%;
  }
  
  .col-6 {
    flex: 0 0 100%;
    max-width: 100%;
  }
}

@media (max-width: 576px) {
  .categories-page {
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
  }
}
</style>