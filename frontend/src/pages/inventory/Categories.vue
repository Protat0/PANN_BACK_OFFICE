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
            >
              <Plus :size="14" />
              ADD CATEGORY
            </button>

            <button 
              class="btn btn-outline-secondary btn-sm"
              @click="exportData"
            >
              EXPORT
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

    <!-- Category Cards Section -->
    <div class="row g-3 mb-4">
      <!-- Noodles Category -->
      <div class="col-6 col-md-3">
        <CardTemplate
          size="compact"
          border-color="secondary"
          border-position="start"
          title="Noodles"
          subtitle="Main category for all noodle products"
          shadow="sm"
          clickable
          @click="viewCategory('noodles')"
        >
          <template #content>
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <div class="text-primary fw-bold h5 mb-1">{{ categoryCounts.noodles || 0 }}</div>
                <small class="text-tertiary-medium">Products</small>
              </div>
              <div class="category-icon bg-secondary-light rounded-circle p-2">
                <Package :size="20" class="text-secondary" />
              </div>
            </div>
            <div class="d-flex gap-1 mt-2">
              <button 
                class="btn btn-view btn-sm btn-with-icon-sm"
                @click.stop="viewCategory('noodles')"
                data-bs-toggle="tooltip"
                title="View Category Details"
              >
                <Eye :size="14" />
                View
              </button>
              <button 
                class="btn btn-delete btn-sm btn-with-icon-sm"
                @click.stop="deleteCategory('noodles')"
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

      <!-- Drinks Category -->
      <div class="col-6 col-md-3">
        <CardTemplate
          size="compact"
          border-color="primary"
          border-position="start"
          title="Drinks"
          subtitle="Beverages and drink products"
          shadow="sm"
          clickable
          @click="viewCategory('drinks')"
        >
          <template #content>
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <div class="text-primary fw-bold h5 mb-1">{{ categoryCounts.drinks || 0 }}</div>
                <small class="text-tertiary-medium">Products</small>
              </div>
              <div class="category-icon bg-primary-light rounded-circle p-2">
                <Coffee :size="20" class="text-primary" />
              </div>
            </div>
            <div class="d-flex gap-1 mt-2">
              <button 
                class="btn btn-view btn-sm btn-with-icon-sm"
                @click.stop="viewCategory('drinks')"
                data-bs-toggle="tooltip"
                title="View Category Details"
              >
                <Eye :size="14" />
                View
              </button>
              <button 
                class="btn btn-delete btn-sm btn-with-icon-sm"
                @click.stop="deleteCategory('drinks')"
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

      <!-- Toppings Category -->
      <div class="col-6 col-md-3">
        <CardTemplate
          size="compact"
          border-color="info"
          border-position="start"
          title="Toppings"
          subtitle="Additional toppings and extras"
          shadow="sm"
          clickable
          @click="viewCategory('toppings')"
        >
          <template #content>
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <div class="text-primary fw-bold h5 mb-1">{{ categoryCounts.toppings || 0 }}</div>
                <small class="text-tertiary-medium">Products</small>
              </div>
              <div class="category-icon bg-info-light rounded-circle p-2">
                <Star :size="20" class="text-info" />
              </div>
            </div>
            <div class="d-flex gap-1 mt-2">
              <button 
                class="btn btn-view btn-sm btn-with-icon-sm"
                @click.stop="viewCategory('toppings')"
                data-bs-toggle="tooltip"
                title="View Category Details"
              >
                <Eye :size="14" />
                View
              </button>
              <button 
                class="btn btn-delete btn-sm btn-with-icon-sm"
                @click.stop="deleteCategory('toppings')"
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

      <!-- Snacks Category -->
      <div class="col-6 col-md-3">
        <CardTemplate
          size="compact"
          border-color="success"
          border-position="start"
          title="Snacks"
          subtitle="Chips, crackers and side items"
          shadow="sm"
          clickable
          @click="viewCategory('snacks')"
        >
          <template #content>
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <div class="text-primary fw-bold h5 mb-1">{{ categoryCounts.snacks || 0 }}</div>
                <small class="text-tertiary-medium">Products</small>
              </div>
              <div class="category-icon bg-success-light rounded-circle p-2">
                <Zap :size="20" class="text-success" />
              </div>
            </div>
            <div class="d-flex gap-1 mt-2">
              <button 
                class="btn btn-view btn-sm btn-with-icon-sm"
                @click.stop="viewCategory('snacks')"
                data-bs-toggle="tooltip"
                title="View Category Details"
              >
                <Eye :size="14" />
                View
              </button>
              <button 
                class="btn btn-delete btn-sm btn-with-icon-sm"
                @click.stop="deleteCategory('snacks')"
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

    <!-- Add Category Modal -->
    <AddCategoryModal ref="addCategoryModal" />
  </div>
</template>

<script>
import CardTemplate from '@/components/common/CardTemplate.vue'
import AddCategoryModal from '@/components/categories/AddCategoryModal.vue'
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
  Zap
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
    Zap
  },
  data() {
    return {
      selectedCategories: [],
      
      // UI State
      searchMode: false,
      
      // Filters
      statusFilter: 'all',
      typeFilter: 'all',
      searchFilter: '',
      
      // Category data
      categoryCounts: {
        noodles: 15,
        drinks: 8,
        toppings: 12,
        snacks: 6
      }
    }
  },
  methods: {
    handleAddCategory() {
      console.log('Add Category button clicked')
      
      // Call the modal's openAddMode method
      if (this.$refs.addCategoryModal) {
        this.$refs.addCategoryModal.openAddMode()
      } else {
        console.error('AddCategoryModal ref not found')
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
        this.applyFilters()
      }
    },

    clearSearch() {
      this.searchFilter = ''
      this.searchMode = false
      this.applyFilters()
    },

    exportData() {
      console.log('Export categories data')
      // TODO: Implement category export functionality
    },

    deleteSelected() {
      if (this.selectedCategories.length === 0) return
      
      const confirmed = confirm(`Are you sure you want to delete ${this.selectedCategories.length} category(ies)?`)
      if (!confirmed) return

      console.log('Delete selected categories:', this.selectedCategories)
      // TODO: Implement bulk delete functionality
    },

    applyFilters() {
      console.log('Applying filters:', {
        status: this.statusFilter,
        type: this.typeFilter,
        search: this.searchFilter
      })
      // TODO: Implement filter logic when categories data is available
    },

    viewCategory(categoryId) {
      console.log('View category:', categoryId)
      // Navigate to category details page using the correct route
      this.$router.push('/categorydetails')
    },

    deleteCategory(categoryId) {
      const categoryNames = {
        noodles: 'Noodles',
        drinks: 'Drinks',
        toppings: 'Toppings',
        snacks: 'Snacks'
      }
      
      const categoryName = categoryNames[categoryId] || categoryId
      const productCount = this.categoryCounts[categoryId] || 0
      
      let confirmMessage = `Are you sure you want to delete the "${categoryName}" category?`
      
      if (productCount > 0) {
        confirmMessage += `\n\nThis category contains ${productCount} product(s). Deleting this category will also remove all products in it.`
      }
      
      const confirmed = confirm(confirmMessage)
      if (!confirmed) return

      console.log('Delete category:', categoryId)
      // TODO: Implement category deletion
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

/* Ensure proper gap in category cards */
.row.g-3 {
  --bs-gutter-x: 1rem;
  --bs-gutter-y: 1rem;
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