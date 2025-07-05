<template>
  <div class="container-fluid pt-2 pb-4 categories-page">
    <!-- Page Title -->
    <div class="mb-3">
      <h1 class="h3 fw-semibold text-primary-dark mb-0">Category Management</h1>
    </div>

    <!-- Action Bar and Filters -->
    <div class="action-bar-container mb-3">
      <div class="action-bar-controls">
        <div class="action-row">
          <!-- Left Side: Main Actions (Always visible when no selection) -->
          <div v-if="selectedCategories.length === 0" class="d-flex gap-2">
            <!-- Add Category Button -->
           <button 
              class="btn btn-success btn-sm btn-with-icon-sm"
              @click="handleAddCategory"
              :disabled="isCreatingCategory"
            >
              <!-- Show spinner when creating category -->
              <div v-if="isCreatingCategory" class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <Plus v-else :size="14" />
              {{ isCreatingCategory ? 'CREATING...' : 'ADD CATEGORY' }}
            </button>

            <button 
              class="btn btn-outline-secondary btn-sm"
              @click="exportData" :disabled="exporting || categories.length === 0"
            >
              
              <div v-if="exporting" class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">Exporting...</span>
              </div>
              {{ exporting ? 'EXPORTING...' : 'EXPORT' }}
            </button>
          </div>

          <!-- Selection Actions (Visible when items are selected) -->
          <div v-if="selectedCategories.length > 0" class="d-flex gap-2">
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
                <label class="filter-label">Status</label>
                <select 
                  class="form-select form-select-sm" 
                  v-model="statusFilter" 
                  @change="applyFilters"
                >
                  <option value="all">All categories</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>

              <div class="filter-dropdown">
                <label class="filter-label">Type</label>
                <select 
                  class="form-select form-select-sm" 
                  v-model="typeFilter" 
                  @change="applyFilters"
                >
                  <option value="all">All types</option>
                  <option value="parent">Parent Categories</option>
                  <option value="subcategory">Subcategories</option>
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
                  placeholder="Search categories..."
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

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading categories...</span>
      </div>
      <p class="mt-2 text-muted">Loading categories...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="alert alert-danger" role="alert">
      <strong>Error:</strong> {{ error }}
      <button @click="fetchCategories" class="btn btn-sm btn-outline-danger ms-2">
        Retry
      </button>
    </div>

    <!-- Category Cards Section -->
    <div v-if="!loading && !error" class="row g-3 mb-4">
      <div 
        v-for="category in filteredCategories" 
        :key="category.id || category.name"
        class="col-6 col-md-3"
      >
        <CardTemplate
          size="compact"
          :border-color="getCategoryBorderColor(category, categories.indexOf(category))"
          border-position="start"
          :title="category.category_name"
          :subtitle="category.description || category.subtitle || `${category.name} products`"
          shadow="sm"
          clickable
          @click="viewCategory(category)"
        >
          <template #content>
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <div class="text-primary fw-bold h5 mb-1">
                  {{ category.subcategories ? category.subcategories.reduce((total, sub) => total + (sub.product_count || 0), 0) : 0 }}
                </div>
                <small class="text-tertiary-medium">Products</small>
              </div>
              <div :class="getCategoryIconClass(category, categories.indexOf(category))">
                <component 
                  :is="getCategoryIcon(category, categories.indexOf(category))" 
                  :size="20" 
                  :class="getCategoryIconColor(category, categories.indexOf(category))"
                />
              </div>
            </div>
            <div class="d-flex gap-1 mt-2">
              <button 
                class="btn btn-view btn-sm btn-with-icon-sm"
                @click.stop="viewCategory(category)"
                data-bs-toggle="tooltip"
                title="View Category Details"
              >
                <Eye :size="14" />
                View
              </button>
              <button 
                class="btn btn-delete btn-sm btn-with-icon-sm"
                @click.stop="deleteCategory(category)"
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

    <!-- Empty State -->
    <div v-if="!loading && !error && filteredCategories.length === 0" class="text-center py-5">
      <Package :size="64" class="text-muted mb-3" />
      <h5 class="text-muted">No categories found</h5>
      <p class="text-muted mb-3">
        {{ categories.length === 0 ? 'Get started by creating your first category.' : 'Try adjusting your search or filters.' }}
      </p>
      <button 
        v-if="categories.length === 0"
        class="btn btn-success"
        @click="handleAddCategory"
      >
        <Plus :size="16" class="me-1" />
        Add First Category
      </button>
    </div>

    <!-- Add Category Modal -->
    <AddCategoryModal ref="addCategoryModal" @category-added="onCategoryAdded" />
  </div>
</template>

<script>
import CardTemplate from '@/components/common/CardTemplate.vue'
import AddCategoryModal from '@/components/categories/AddCategoryModal.vue'
import categoryApiService from '@/services/apiCategory' // Adjust path as needed
import { 
  Plus, 
  Search,
  X,
  Package, 
  Trash2,
  FileText,
  Eye,
  Coffee,
  Star,
  Zap,
  Utensils,
  ShoppingBag,
  Grid3x3
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
    FileText,
    Eye,
    Coffee,
    Star,
    Zap,
    Utensils,
    ShoppingBag,
    Grid3x3
  },
  data() {
    return {
      selectedCategories: [],
      
      // UI State
      searchMode: false,
      loading: false,
      error: null,
      isCreatingCategory: false,
      exporting: false, // Add this line
      
      // Filters
      statusFilter: 'all',
      typeFilter: 'all',
      searchFilter: '',
      
      // API Data
      categories: []
    }
  },
  computed: {
    filteredCategories() {
      let filtered = [...this.categories]
      
      // Apply search filter
      if (this.searchFilter.trim()) {
        const searchTerm = this.searchFilter.toLowerCase().trim()
        filtered = filtered.filter(category => 
          (category.name || '').toLowerCase().includes(searchTerm) ||
          (category.description || '').toLowerCase().includes(searchTerm)
        )
      }
      
      // Apply status filter
      if (this.statusFilter !== 'all') {
        filtered = filtered.filter(category => {
          if (this.statusFilter === 'active') {
            return category.status === 'active' || category.is_active === true || (!category.hasOwnProperty('status') && !category.hasOwnProperty('is_active'))
          } else if (this.statusFilter === 'inactive') {
            return category.status === 'inactive' || category.is_active === false
          }
          return true
        })
      }
      
      // Apply type filter
      if (this.typeFilter !== 'all') {
        filtered = filtered.filter(category => {
          if (this.typeFilter === 'parent') {
            return !category.parent_id || category.type === 'parent'
          } else if (this.typeFilter === 'subcategory') {
            return category.parent_id || category.type === 'subcategory'
          }
          return true
        })
      }
      
      return filtered
    }
  },
  async mounted() {
    await this.fetchCategories()
  },
  methods: {
    async fetchCategories() {
      this.loading = true
      this.error = null
      
      try {
        const response = await categoryApiService.CategoryData()
        console.log('Categories fetched:', response)
        
        // Handle different response structures
        if (response.data && Array.isArray(response.data)) {
          this.categories = response.data
        } else if (Array.isArray(response)) {
          this.categories = response
        } else if (response.categories && Array.isArray(response.categories)) {
          this.categories = response.categories
        } else {
          console.warn('Unexpected response structure:', response)
          this.categories = []
        }
        
      } catch (error) {
        console.error('Error fetching categories:', error)
        this.error = error.message || 'Failed to fetch categories'
        this.categories = []
      } finally {
        this.loading = false
      }
    },

    // Icon mapping based on category name or index
    getCategoryIcon(category, index) {
      const categoryName = (category.category_name || '').toLowerCase()
      
      // Try to match by name first
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
      
      // Fallback to rotation based on index
      const icons = ['Package', 'Coffee', 'Star', 'Zap', 'Utensils', 'ShoppingBag', 'Grid3x3']
      return icons[index % icons.length]
    },

    getCategoryBorderColor(category, index) {
      const categoryName = (category.name || '').toLowerCase()
      
      // Try to match by name first
      if (categoryName.includes('noodle') || categoryName.includes('pasta')) {
        return 'secondary'
      } else if (categoryName.includes('drink') || categoryName.includes('beverage')) {
        return 'primary'
      } else if (categoryName.includes('topping') || categoryName.includes('extra')) {
        return 'info'
      } else if (categoryName.includes('snack') || categoryName.includes('side')) {
        return 'success'
      }
      
      // Fallback to rotation based on index
      const colors = ['secondary', 'primary', 'info', 'success', 'warning', 'danger']
      return colors[index % colors.length]
    },

    getCategoryIconClass(category, index) {
      const borderColor = this.getCategoryBorderColor(category, index)
      return `category-icon bg-${borderColor}-light rounded-circle p-2`
    },

    getCategoryIconColor(category, index) {
      const borderColor = this.getCategoryBorderColor(category, index)
      return `text-${borderColor}`
    },

     handleAddCategory() {
        console.log('Add Category button clicked')
        
        // Set loading state
        this.isCreatingCategory = true
        
        // Call the modal's openAddMode method
        if (this.$refs.addCategoryModal) {
          this.$refs.addCategoryModal.openAddMode()
        } else {
          console.error('AddCategoryModal ref not found')
          this.isCreatingCategory = false
        }
      },

      async onCategoryAdded(newCategory) {
        try {
          console.log('New category added:', newCategory)
          
          // Refresh the categories list
          await this.fetchCategories()
          
          // Show success message (optional)
          console.log(`Category "${newCategory.category_name}" added successfully!`)
          
        } catch (error) {
          console.error('Error refreshing categories after add:', error)
        } finally {
          // Reset loading state
          this.isCreatingCategory = false
        }
      },

      async onCategoryUpdated(updatedCategory) {
        try {
          console.log('Category updated:', updatedCategory)
          
          // Refresh the categories list
          await this.fetchCategories()
          
        } catch (error) {
          console.error('Error refreshing categories after update:', error)
        }
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
        // No need to call applyFilters as computed property handles it
      }
    },

    clearSearch() {
      this.searchFilter = ''
      this.searchMode = false
    },

   async exportData() {
      this.exporting = true
      
      try {
        // Use dedicated export endpoint
        const exportData = await categoryApiService.ExportCategoryData({
          format: 'csv',
          include_products: true
        })
        
        // The backend returns pre-formatted CSV data
        const blob = new Blob([exportData], { type: 'text/csv;charset=utf-8;' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `categories_export_${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
        
      } catch (error) {
        console.error('Error exporting categories:', error)
        alert('Failed to export categories. Please try again.')
      } finally {
        this.exporting = false
      }
    },

  // Helper method for formatting dates (add if not already present)
  formatDate(dateString) {
    if (!dateString) return 'N/A'
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch (error) {
      return 'Invalid Date'
    }
  },

    deleteSelected() {
      if (this.selectedCategories.length === 0) return
      
      const confirmed = confirm(`Are you sure you want to delete ${this.selectedCategories.length} category(ies)?`)
      if (!confirmed) return

      console.log('Delete selected categories:', this.selectedCategories)
      // TODO: Implement bulk delete functionality
    },

    applyFilters() {
      // Filters are now handled by computed property
      console.log('Filters applied:', {
        status: this.statusFilter,
        type: this.typeFilter,
        search: this.searchFilter
      })
    },

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
        params: { id: categoryId } // Use params instead of query
      })
    },

    async deleteCategory(category) {
      const categoryName = category.name || category.title || 'this category'
      const productCount = category.product_count || category.count || 0
      
      let confirmMessage = `Are you sure you want to delete the "${categoryName}" category?`
      
      if (productCount > 0) {
        confirmMessage += `\n\nThis category contains ${productCount} product(s). Deleting this category will also remove all products in it.`
      }
      
      const confirmed = confirm(confirmMessage)
      if (!confirmed) return

      try {
        console.log('Delete category:', category)
        // TODO: Implement category deletion API call
        // await categoryApiService.deleteCategory(category.id)
        
        // For now, just remove from local array
        const index = this.categories.findIndex(c => c.id === category._id)
        if (index > -1) {
          this.categories.splice(index, 1)
        }
        
        // Or refresh from server
        // await this.fetchCategories()
        
      } catch (error) {
        console.error('Error deleting category:', error)
        alert('Failed to delete category: ' + error.message)
      }
    }
  }
}
</script>

<style scoped>
.categories-page {
  background-color: var(--neutral-light);
  min-height: 100vh;
}

.text-primary-dark {
  color: var(--primary-dark) !important;
}

.text-tertiary-medium {
  color: var(--tertiary-medium) !important;
}

/* Action Bar Controls */
.action-bar-controls {
  border-bottom: 1px solid var(--neutral);
  background-color: white;
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
  height: calc(1.5em + 0.75rem + 2px);
}

.search-container .position-relative .btn {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Custom hover states for export buttons */
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

/* Custom category card styles */
.category-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
}

/* Background colors for category icons */
.bg-primary-light {
  background-color: var(--primary-light) !important;
}

.bg-secondary-light {
  background-color: var(--secondary-light) !important;
}

.bg-info-light {
  background-color: var(--info-light) !important;
}

.bg-success-light {
  background-color: var(--success-light) !important;
}

.bg-warning-light {
  background-color: var(--warning-light) !important;
}

.bg-danger-light {
  background-color: var(--danger-light) !important;
}

/* Ensure proper gap in category cards */
.row.g-3 {
  --bs-gutter-x: 1rem;
  --bs-gutter-y: 1rem;
}

/* Loading and empty states */
.spinner-border {
  width: 2rem;
  height: 2rem;
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
}
</style>