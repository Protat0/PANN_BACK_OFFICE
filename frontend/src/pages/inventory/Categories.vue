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
          <div class="d-flex gap-2">
            <button 
              class="btn btn-add btn-sm btn-with-icon-sm"
              @click="handleAddCategory"
              :disabled="loading"
            >
              <Plus :size="14" />
              ADD CATEGORY
            </button>
            
            <button 
              class="btn btn-export btn-sm btn-with-icon-sm"
              @click="handleExport" 
              :disabled="loading || filteredCategories.length === 0"
            >
              <FileDown :size="14" />
              EXPORT
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
      <div 
        v-for="category in filteredCategories" 
        :key="category._id"
        class="col-6 col-md-3"
      >
        <CardTemplate
          size="md"
          border-color="primary"
          border-position="start"
          :title="category.category_name"
          :subtitle="getCategorySubtitle(category)"
          shadow="sm"
          clickable
        >
          <template #content>
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <div class="text-primary fw-bold h5 mb-1">
                  {{ getProductCount(category) }}
                </div>
                <small class="text-tertiary-medium">Products</small>
              </div>
              <div class="category-icon surface-primary-light rounded-circle p-2">
                <Package :size="20" class="text-status-primary" />
              </div>
            </div>

            <!-- Action buttons -->
            <div class="d-flex gap-1 mt-2">
              <button 
                class="btn btn-view btn-sm"
                @click.stop="viewCategory(category._id)"
              >
                <Eye :size="14" />
                View
              </button>
              <button 
                class="btn btn-delete btn-sm"
                @click.stop="handleDeleteCategory(category)"
              >
                <Trash2 :size="14" />
                Delete
              </button>
            </div>
          </template>
        </CardTemplate>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && !error && filteredCategories.length === 0" class="text-center py-5">
      <Package :size="64" class="text-tertiary-medium mb-3" />
      <h5 class="text-tertiary-dark">No categories found</h5>
      <p class="text-tertiary-medium mb-3">
        {{ categories.length === 0 ? 'Get started by creating your first category.' : 'No categories match your current filters.' }}
      </p>
      <button 
        v-if="categories.length === 0"
        class="btn btn-add"
        @click="handleAddCategory"
      >
        <Plus :size="16" class="me-1" />
        Add First Category
      </button>
      <button 
        v-else
        class="btn btn-filter"
        @click="handleClearFilters"
      >
        Clear Filters
      </button>
    </div>

    <!-- Add Category Modal -->
    <AddCategoryModal ref="addCategoryModal" @category-added="onCategoryAdded" />
  </div>
</template>

<script>
import { ref, nextTick } from 'vue'
import CardTemplate from '@/components/common/CardTemplate.vue'
import AddCategoryModal from '@/components/categories/AddCategoryModal.vue'
import { useCategories } from '@/composables/ui/categories/useCategories'

export default {
  name: 'Categories',
  components: {
    CardTemplate,
    AddCategoryModal,
  },

  setup() {
    const searchInput = ref(null)
    
    // Use the categories composable
    const {
      // State
      categories,
      filteredCategories,
      loading,
      error,
      successMessage,
      uncategorizedCount,
      
      // UI State
      searchMode,
      
      // Filters
      statusFilter,
      searchFilter,
      
      // Core Methods
      refreshData,
      getProductCount,
      getCategorySubtitle,
      fetchUncategorizedCount,
      softDeleteCategory,
      exportCategories,
      
      // Filter and Search
      applyFilters,
      clearFilters,
      toggleSearchMode,
      clearSearch,
      
      // Success/Error handlers
      handleCategorySuccess,
      handleCategoryError,
      
      // Lifecycle
      initializeCategories,
      cleanupCategories
    } = useCategories()

    // Watch search mode to focus input
    const handleToggleSearchMode = async () => {
      toggleSearchMode()
      if (searchMode.value) {
        await nextTick()
        if (searchInput.value) {
          searchInput.value.focus()
        }
      }
    }

    return {
      // Refs
      searchInput,
      
      // State from composable
      categories,
      filteredCategories,
      loading,
      error,
      successMessage,
      uncategorizedCount,
      searchMode,
      statusFilter,
      searchFilter,
      
      // Methods from composable
      refreshData,
      getProductCount,
      getCategorySubtitle,
      fetchUncategorizedCount,
      softDeleteCategory,
      exportCategories,
      applyFilters,
      clearFilters,
      clearSearch,
      handleCategorySuccess,
      handleCategoryError,
      initializeCategories,
      cleanupCategories,
      
      // Local methods
      toggleSearchMode: handleToggleSearchMode
    }
  },

  async mounted() {
    try {
      // Initialize categories using composable
      await this.initializeCategories()
      await this.fetchUncategorizedCount()
    } catch (error) {
      console.error('Error initializing categories page:', error)
      this.handleCategoryError(error)
    }
  },

  beforeUnmount() {
    // Cleanup using composable
    this.cleanupCategories()
  },

  methods: {
    // Modal handlers
    async handleAddCategory() {
      console.log('Add Category button clicked')
      
      if (this.$refs.addCategoryModal) {
        this.$refs.addCategoryModal.openAddMode()
      } else {
        console.error('AddCategoryModal ref not found')
        this.handleCategoryError({ message: 'Modal component not available' })
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

    // Navigation
    viewCategory(categoryId) {
      console.log('View category:', categoryId)
      
      if (!categoryId) {
        console.error('No valid category ID provided')
        this.handleCategoryError({ message: 'Invalid category ID' })
        return
      }
      
      console.log('Navigating with ID:', categoryId)
      this.$router.push({
        name: 'Category Details',
        params: { id: categoryId }
      })
    },

    // Delete handler
    async handleDeleteCategory(category) {
      try {
        const confirmed = confirm(
          `Are you sure you want to delete "${category.category_name}"?\n\n` +
          `This will move the category to trash. Products will be moved to Uncategorized.`
        )
        
        if (!confirmed) return
        
        console.log('Deleting category:', category._id)
        await this.softDeleteCategory(category._id)
        
        // Refresh uncategorized count since products might be moved there
        await this.fetchUncategorizedCount()
        
      } catch (error) {
        console.error('Error deleting category:', error)
        this.handleCategoryError(error)
      }
    },

    // Export handler
    async handleExport() {
      try {
        console.log('Exporting categories...')
        
        await this.exportCategories({
          format: 'csv',
          include_sales_data: true,
          include_deleted: this.statusFilter === 'deleted'
        })
        
        console.log('Export completed successfully')
        
      } catch (error) {
        console.error('Export failed:', error)
        this.handleCategoryError({ message: `Export failed: ${error.message}` })
      }
    },

    // Filter helper
    handleClearFilters() {
      this.clearFilters()
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

.state-active {
  background-color: var(--state-selected) !important;
  color: var(--text-accent) !important;
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