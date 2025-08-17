<template>
  <div class="container-fluid pt-2 pb-4 categories-page">
    <!-- Page Title and Uncategorized Link -->
    <div class="d-flex justify-content-between align-items-start mb-3">
      <div>
        <h1 class="h3 fw-semibold text-primary-dark mb-0">Category Management</h1>
      </div>
      <div>
        <router-link 
          to="/uncategorized" 
          class="btn btn-warning btn-sm btn-with-icon-sm"
        >
          <Package :size="14" class="me-1" />
          Uncategorized ({{ uncategorizedCount }})
        </router-link>
      </div>
    </div>

    <!-- Action Bar and Filters -->
    <div class="action-bar-container mb-3">
      <div class="action-bar-controls">
        <div class="action-row">
          <!-- Left Side: Main Actions -->
          <div v-if="selectedCategories.length === 0" class="d-flex gap-2">
            <button 
              class="btn btn-success btn-sm btn-with-icon-sm"
              @click="handleAddCategory"
              :disabled="isCreatingCategory"
            >
              <div v-if="isCreatingCategory" class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <Plus v-else :size="14" />
              {{ isCreatingCategory ? 'CREATING...' : 'ADD CATEGORY' }}
            </button>

            <button 
              class="btn btn-outline-secondary btn-sm"
              @click="exportData" 
              :disabled="exporting || categories.length === 0"
            >
              EXPORT
              <div v-if="exporting" class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">Exporting...</span>
              </div>
            </button>

            <button 
              class="btn btn-outline-info btn-sm"
              @click="refreshData"
              :disabled="refreshing"
            >
              <div v-if="refreshing" class="spinner-border spinner-border-sm me-1" role="status">
                <span class="visually-hidden">Refreshing...</span>
              </div>
              <RefreshCw v-else :size="14" class="me-1" />
              REFRESH
            </button>
          </div>

          <!-- Bulk Actions (when categories are selected) -->
          <div v-if="selectedCategories.length > 0" class="d-flex gap-2">
            <span class="badge bg-primary fs-6 px-3 py-2">
              {{ selectedCategories.length }} selected
            </span>
            
            <button 
              class="btn btn-outline-danger btn-sm"
              @click="bulkSoftDelete"
              :disabled="bulkOperating"
            >
              <Trash2 :size="14" class="me-1" />
              DELETE SELECTED
            </button>

            <button 
              class="btn btn-outline-secondary btn-sm"
              @click="clearSelection"
            >
              <X :size="14" class="me-1" />
              CLEAR
            </button>
          </div>

          <!-- Right Side: Filters and Search -->
          <div class="d-flex align-items-center gap-2">
            <button 
              class="btn btn-secondary btn-sm"
              @click="toggleSearchMode"
              :class="{ 'active': searchMode }"
              style="height: calc(1.5em + 0.75rem + 2px); display: flex; align-items: center; justify-content: center; padding: 0 0.75rem;"
            >
              <Search :size="16" />
            </button>

            <!-- Filter Dropdowns -->
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
                  <option value="deleted">Deleted</option>
                </select>
              </div>

              <div class="filter-dropdown">
                <label class="filter-label">Sort</label>
                <select 
                  class="form-select form-select-sm" 
                  v-model="sortBy" 
                  @change="applySorting"
                >
                  <option value="name_asc">Name A-Z</option>
                  <option value="name_desc">Name Z-A</option>
                  <option value="products_desc">Most Products</option>
                  <option value="products_asc">Least Products</option>
                  <option value="created_desc">Newest First</option>
                  <option value="created_asc">Oldest First</option>
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
      <button @click="refreshData" class="btn btn-sm btn-outline-danger ms-2">
        <RefreshCw :size="14" class="me-1" />
        Retry
      </button>
    </div>

    <!-- Category Cards Section -->
    <div v-if="!loading && !error" class="row g-3 mb-4">
      <div 
        v-for="category in sortedAndFilteredCategories" 
        :key="category.id || category._id || category.name"
        class="col-6 col-md-3"
      >
        <CardTemplate
          size="compact"
          :border-color="getCategoryBorderColor(category, categories.indexOf(category))"
          border-position="start"
          :title="category.category_name"
          :subtitle="getCategorySubtitle(category)"
          shadow="sm"
          clickable
          @click="viewCategory(category)"
          :class="{ 
            'deleted-category': category.isDeleted,
            'selected-category': selectedCategories.includes(category._id || category.id)
          }"
        >
          <template #content>
            <!-- Selection checkbox for bulk operations -->
            <div v-if="!category.isDeleted" class="selection-checkbox">
              <input 
                type="checkbox" 
                class="form-check-input"
                :checked="selectedCategories.includes(category._id || category.id)"
                @click.stop="toggleCategorySelection(category)"
              />
            </div>

            <!-- Deleted indicator -->
            <div v-if="category.isDeleted" class="deleted-badge mb-2">
              <small class="badge bg-warning text-dark">
                <Trash2 :size="12" class="me-1" />
                DELETED {{ formatDeletionDate(category.deleted_at) }}
              </small>
            </div>

            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <div class="text-primary fw-bold h5 mb-1">
                  {{ getCategoryProductCount(category) }}
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

            <!-- Action buttons -->
            <div class="d-flex gap-1 mt-2">
              <button 
                v-if="!category.isDeleted"
                class="btn btn-view btn-sm btn-with-icon-sm"
                @click.stop="viewCategory(category)"
                data-bs-toggle="tooltip"
                title="View Category Details"
              >
                <Eye :size="14" />
                <span class="btn-text">View</span>
              </button>

              <template v-if="!category.isDeleted">
                <button 
                  class="btn btn-delete btn-sm btn-with-icon-sm"
                  @click.stop="softDeleteCategory(category)"
                  data-bs-toggle="tooltip"
                  title="Soft Delete Category"
                >
                  <Trash2 :size="14" />
                  Delete
                </button>
              </template>
              
              <template v-else>
                <button 
                  class="btn btn-success btn-sm btn-with-icon-sm"
                  @click.stop="restoreCategory(category)"
                  data-bs-toggle="tooltip"
                  title="Restore Category"
                >
                  <RotateCcw :size="14" />
                  Restore
                </button>
                
                <button 
                  v-if="isAdmin"
                  class="btn btn-danger btn-sm btn-with-icon-sm"
                  @click.stop="hardDeleteCategory(category)"
                  data-bs-toggle="tooltip"
                  title="Permanently Delete Category"
                >
                  <X :size="14" />
                  Hard Delete
                </button>
              </template>
            </div>
          </template>
        </CardTemplate>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && !error && sortedAndFilteredCategories.length === 0" class="text-center py-5">
      <Package :size="64" class="text-muted mb-3" />
      <h5 class="text-muted">No categories found</h5>
      <p class="text-muted mb-3">
        {{ getEmptyStateMessage() }}
      </p>
      <button 
        v-if="categories.length === 0 && !showDeleted"
        class="btn btn-success"
        @click="handleAddCategory"
      >
        <Plus :size="16" class="me-1" />
        Add First Category
      </button>
    </div>

    <!-- Add Category Modal -->
    <AddCategoryModal ref="addCategoryModal" @category-added="onCategoryAdded" />

    <!-- Success Messages -->
    <div 
      v-if="successMessage" 
      class="alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3" 
      style="z-index: 1060; min-width: 300px;"
    >
      <CheckCircle :size="20" class="me-2" />
      {{ successMessage }}
      <button type="button" class="btn-close" @click="successMessage = ''"></button>
    </div>

    <!-- Error Messages -->
    <div 
      v-if="errorMessage" 
      class="alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3" 
      style="z-index: 1060; min-width: 300px;"
    >
      <AlertCircle :size="20" class="me-2" />
      {{ errorMessage }}
      <button type="button" class="btn-close" @click="errorMessage = ''"></button>
    </div>

    <!-- Warning Messages -->
    <div 
      v-if="warningMessage" 
      class="alert alert-warning alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3" 
      style="z-index: 1060; min-width: 300px;"
    >
      <AlertTriangle :size="20" class="me-2" />
      {{ warningMessage }}
      <button type="button" class="btn-close" @click="warningMessage = ''"></button>
    </div>
  </div>
</template>

<script>
import CardTemplate from '@/components/common/CardTemplate.vue'
import AddCategoryModal from '@/components/categories/AddCategoryModal.vue'
import categoryApiService from '@/services/apiCategory'
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
  RefreshCw,
  AlertCircle,
  CheckCircle,
  AlertTriangle
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
    RefreshCw,
    AlertCircle,
    CheckCircle,
    AlertTriangle
  },
  data() {
    return {
      // Selection and UI state
      selectedCategories: [],
      searchMode: false,
      loading: false,
      error: null,
      successMessage: '',
      errorMessage: '',
      warningMessage: '',
      
      // Operation states
      isCreatingCategory: false,
      exporting: false,
      refreshing: false,
      bulkOperating: false,
      
      // Filter and sort
      statusFilter: 'all',
      searchFilter: '',
      sortBy: 'name_asc',
      showDeleted: false,
      
      // Data
      categories: [],
      categoryStats: null,
      
      // User permissions
      isAdmin: true,
      
      // Uncategorized tracking
      uncategorizedCount: 0,
      UNCATEGORIZED_CATEGORY_ID: '686a4de143821e2b21f725c6'
    }
  },
  computed: {
    filteredCategories() {
      let filtered = [...this.categories]
      
      // Filter out the Uncategorized category from the main view
      filtered = filtered.filter(category => 
        category._id !== this.UNCATEGORIZED_CATEGORY_ID
      )
      
      // Apply search filter
      if (this.searchFilter.trim()) {
        const searchTerm = this.searchFilter.toLowerCase().trim()
        filtered = filtered.filter(category => 
          (category.category_name || '').toLowerCase().includes(searchTerm) ||
          (category.description || '').toLowerCase().includes(searchTerm)
        )
      }
      
      // Apply status filter
      if (this.statusFilter !== 'all') {
        filtered = filtered.filter(category => {
          if (this.statusFilter === 'active') {
            return category.status === 'active' && !category.isDeleted
          } else if (this.statusFilter === 'inactive') {
            return category.status === 'inactive' && !category.isDeleted
          } else if (this.statusFilter === 'deleted') {
            return category.isDeleted === true
          }
          return true
        })
      } else {
        if (this.statusFilter !== 'deleted') {
          filtered = filtered.filter(category => !category.isDeleted)
        }
      }
      
      return filtered
    },

    sortedAndFilteredCategories() {
      const filtered = [...this.filteredCategories]
      
      // Apply sorting
      return filtered.sort((a, b) => {
        switch (this.sortBy) {
          case 'name_asc':
            return (a.category_name || '').localeCompare(b.category_name || '')
          case 'name_desc':
            return (b.category_name || '').localeCompare(a.category_name || '')
          case 'products_desc':
            return this.getCategoryProductCount(b) - this.getCategoryProductCount(a)
          case 'products_asc':
            return this.getCategoryProductCount(a) - this.getCategoryProductCount(b)
          case 'created_desc':
            return new Date(b.created_at || 0) - new Date(a.created_at || 0)
          case 'created_asc':
            return new Date(a.created_at || 0) - new Date(b.created_at || 0)
          default:
            return 0
        }
      })
    }
  },
  async mounted() {
    await this.initializePage()
  },
  methods: {
    // ========== INITIALIZATION METHODS ==========
    async initializePage() {
      this.loading = true
      this.error = null
      
      try {
        // Use Promise.allSettled to handle partial failures gracefully
        const results = await Promise.allSettled([
          this.fetchCategories(),
          this.fetchCategoryStats(),
          this.fetchUncategorizedCount()
        ])
        
        // Check each operation result
        const operations = ['categories', 'stats', 'uncategorized count']
        let hasErrors = false
        let criticalError = false
        
        results.forEach((result, index) => {
          if (result.status === 'rejected') {
            console.warn(`Failed to load ${operations[index]}:`, result.reason)
            hasErrors = true
            
            // Categories are critical, others are optional
            if (index === 0) {
              criticalError = true
            }
          }
        })
        
        // Only show error if categories failed to load
        if (criticalError) {
          throw new Error('Failed to load categories. Please check your backend server and URL configuration.')
        }
        
        // Show warning if optional operations failed
        if (hasErrors && !criticalError) {
          this.showWarning('Some data could not be loaded. Core functionality is available.')
        }
        
      } catch (error) {
        console.error('Error initializing page:', error)
        this.error = error.message || 'Failed to load page data'
      } finally {
        this.loading = false
      }
    },

    async refreshData() {
      this.refreshing = true
      try {
        await this.initializePage()
        this.showSuccess('Data refreshed successfully!')
      } catch (error) {
        console.error('Error refreshing data:', error)
        this.showError('Failed to refresh data: ' + error.message)
      } finally {
        this.refreshing = false
      }
    },

    // ========== CORE CATEGORY METHODS ==========
    async fetchCategories() {
      try {
        const params = { include_deleted: true }
        const response = await categoryApiService.CategoryData(params)
        console.log('Categories fetched:', response)
        
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
        
        // Provide helpful error messages based on error type
        if (error.message && error.message.includes('404')) {
          console.warn('Categories endpoint not found - check backend URL configuration')
          this.categories = []
          throw new Error('Categories service not available. Please check your backend URL configuration.')
        } else if (error.message && error.message.includes('Category not found')) {
          console.warn('No categories exist in database')
          this.categories = []
          // Don't throw error for empty database - this is normal for new installations
          return
        }
        
        throw error
      }
    },

    async fetchCategoryStats() {
      try {
        console.log('Fetching category statistics...')
        const response = await categoryApiService.GetCategoryStats()
        this.categoryStats = response.data || response
        console.log('Category stats:', this.categoryStats)
      } catch (error) {
        console.warn('Category stats not available:', error.message)
        // Calculate basic stats from available data instead of failing
        this.categoryStats = {
          total_categories: this.categories ? this.categories.length : 0,
          active_categories: this.categories ? this.categories.filter(c => !c.isDeleted && (c.status === 'active' || !c.status)).length : 0,
          total_subcategories: this.categories ? this.categories.reduce((sum, cat) => sum + this.getCategorySubcategoryCount(cat), 0) : 0,
          deleted_categories: this.categories ? this.categories.filter(c => c.isDeleted).length : 0
        }
      }
    },

    async fetchUncategorizedCount() {
      try {
        console.log('Fetching uncategorized products count...')
        
        const products = await categoryApiService.FindProdcategory({ 
          id: this.UNCATEGORIZED_CATEGORY_ID 
        })
        
        this.uncategorizedCount = Array.isArray(products) ? products.length : 0
        console.log(`Found ${this.uncategorizedCount} uncategorized products`)
        
      } catch (error) {
        console.warn('Error fetching uncategorized count:', error.message)
        this.uncategorizedCount = 0
      }
    },

    // ========== CATEGORY CRUD METHODS ==========
    async handleAddCategory() {
      console.log('Add Category button clicked')
      this.isCreatingCategory = true
      
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
        await this.initializePage()
        this.showSuccess(`Category "${newCategory.category_name}" added successfully!`)
      } catch (error) {
        console.error('Error refreshing categories after add:', error)
        this.showError('Category added but failed to refresh list')
      } finally {
        this.isCreatingCategory = false
      }
    },

    viewCategory(category) {
      console.log('View category:', category)
      
      const categoryId = category._id || category.id || category.category_id
      
      if (!categoryId) {
        console.error('No valid ID found in category object')
        this.showError('Cannot view category: Invalid category ID')
        return
      }
      
      console.log('Navigating with ID:', categoryId)
      this.$router.push({
        name: 'Category Details',
        params: { id: categoryId }
      })
    },

    // ========== DELETE METHODS ==========
    async softDeleteCategory(category) {
      try {
        const deleteInfo = await categoryApiService.GetCategoryDeleteInfo(category._id)
        
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

        console.log('Soft deleting category:', category)
        
        await categoryApiService.SoftDeleteCategory(category._id)
        await this.initializePage()
        
        console.log('✅ Category soft deleted successfully')
        this.showSuccess(`Category "${categoryName}" has been deleted.`)
        
      } catch (error) {
        console.error('Error soft deleting category:', error)
        this.showError('Failed to delete category: ' + error.message)
      }
    },

    async restoreCategory(category) {
      try {
        const confirmed = confirm(`Are you sure you want to restore "${category.category_name}"?`)
        if (!confirmed) return

        console.log('Restoring category:', category)
        
        await categoryApiService.RestoreCategory(category._id)
        await this.initializePage()
        
        console.log('✅ Category restored successfully')
        this.showSuccess(`Category "${category.category_name}" has been restored.`)
        
      } catch (error) {
        console.error('Error restoring category:', error)
        this.showError('Failed to restore category: ' + error.message)
      }
    },

    async hardDeleteCategory(category) {
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
          this.showError('Confirmation text did not match. Operation cancelled.')
          return
        }

        console.log('Hard deleting category:', category)
        
        await categoryApiService.HardDeleteCategory(category._id)
        await this.initializePage()
        
        console.log('✅ Category permanently deleted')
        this.showSuccess(`Category "${categoryName}" has been permanently deleted.`)
        
      } catch (error) {
        console.error('Error hard deleting category:', error)
        this.showError('Failed to permanently delete category: ' + error.message)
      }
    },

    // ========== BULK OPERATIONS ==========
    toggleCategorySelection(category) {
      const categoryId = category._id || category.id
      const index = this.selectedCategories.indexOf(categoryId)
      
      if (index > -1) {
        this.selectedCategories.splice(index, 1)
      } else {
        this.selectedCategories.push(categoryId)
      }
    },

    clearSelection() {
      this.selectedCategories = []
    },

    async bulkSoftDelete() {
      if (this.selectedCategories.length === 0) return

      try {
        const confirmed = confirm(
          `Are you sure you want to delete ${this.selectedCategories.length} categories?\n\n` +
          `This will move all products in these categories to Uncategorized.`
        )
        if (!confirmed) return

        this.bulkOperating = true
        
        await categoryApiService.BulkOperations({
          operation: 'soft_delete',
          category_ids: this.selectedCategories
        })

        await this.initializePage()
        this.clearSelection()
        
        this.showSuccess(`Successfully deleted ${this.selectedCategories.length} categories.`)
        
      } catch (error) {
        console.error('Error in bulk delete:', error)
        this.showError('Failed to delete categories: ' + error.message)
      } finally {
        this.bulkOperating = false
      }
    },

    // ========== EXPORT METHODS ==========
    async exportData() {
      this.exporting = true
      
      try {
        console.log('🚀 Starting category export...')
        
        const exportParams = {
          format: 'csv',
          include_sales_data: true,
          include_deleted: this.statusFilter === 'deleted'
        }
        
        const blobData = await categoryApiService.ExportCategoryData(exportParams)
        
        if (!(blobData instanceof Blob)) {
          throw new Error('Invalid response: expected file data')
        }
        
        if (blobData.size === 0) {
          throw new Error('Export file is empty. No data to export.')
        }
        
        const url = window.URL.createObjectURL(blobData)
        const link = document.createElement('a')
        link.href = url
        
        const timestamp = new Date().toISOString().split('T')[0]
        const deletedSuffix = this.statusFilter === 'deleted' ? '_with_deleted' : ''
        link.download = `categories_export${deletedSuffix}_${timestamp}.csv`
        
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        console.log('✅ Export completed successfully')
        this.showSuccess('Categories exported successfully!')
        
      } catch (error) {
        console.error('❌ Export error:', error)
        const errorMessage = error.message || 'Export failed. Please try again.'
        this.showError(`Export failed: ${errorMessage}`)
      } finally {
        this.exporting = false
      }
    },

    // ========== UI UTILITY METHODS ==========
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
      }
    },

    clearSearch() {
      this.searchFilter = ''
      this.searchMode = false
    },

    applyFilters() {
      console.log('Filters applied:', {
        status: this.statusFilter,
        search: this.searchFilter,
        showingDeleted: this.statusFilter === 'deleted'
      })
      
      this.showDeleted = this.statusFilter === 'deleted'
      this.clearSelection()
    },

    applySorting() {
      console.log('Sorting applied:', this.sortBy)
      this.clearSelection()
    },

    // ========== CATEGORY DATA HELPERS ==========
    getCategoryProductCount(category) {
      if (!category) return 0
      
      // Try different ways to get product count
      if (category.product_count !== undefined) {
        return category.product_count
      }
      
      if (category.subcategories && Array.isArray(category.subcategories)) {
        return category.subcategories.reduce((total, sub) => {
          return total + (sub.product_count || 0)
        }, 0)
      }
      
      if (category.sub_categories && Array.isArray(category.sub_categories)) {
        return category.sub_categories.reduce((total, sub) => {
          const products = sub.products || []
          return total + (Array.isArray(products) ? products.length : 0)
        }, 0)
      }
      
      return 0
    },

    getCategorySubcategoryCount(category) {
      if (!category) return 0
      
      if (category.subcategories && Array.isArray(category.subcategories)) {
        return category.subcategories.length
      }
      
      if (category.sub_categories && Array.isArray(category.sub_categories)) {
        return category.sub_categories.length
      }
      
      return 0
    },

    getCategorySubtitle(category) {
      if (category.isDeleted) {
        return `Deleted ${this.formatDeletionDate(category.deleted_at)}`
      }
      
      const productCount = this.getCategoryProductCount(category)
      const subcategoryCount = this.getCategorySubcategoryCount(category)
      
      if (productCount === 0 && subcategoryCount === 0) {
        return category.description || 'Empty category'
      }
      
      if (subcategoryCount === 0) {
        return `${productCount} product${productCount !== 1 ? 's' : ''}`
      }
      
      return `${subcategoryCount} subcategory, ${productCount} product${productCount !== 1 ? 's' : ''}`
    },

    formatDeletionDate(dateString) {
      return categoryApiService.formatDeletionDate(dateString)
    },

    getEmptyStateMessage() {
      if (this.statusFilter === 'deleted') {
        return 'No deleted categories found.'
      } else if (this.searchFilter.trim()) {
        return `No categories found matching "${this.searchFilter}".`
      } else if (this.categories.length === 0) {
        return 'Get started by creating your first category.'
      } else {
        return 'Try adjusting your search or filters.'
      }
    },

    // ========== MESSAGE METHODS ==========
    showSuccess(message) {
      console.log('✅ Success:', message)
      this.successMessage = message
      this.errorMessage = ''
      this.warningMessage = ''
      
      setTimeout(() => {
        this.successMessage = ''
      }, 5000)
    },

    showError(message) {
      console.error('❌ Error:', message)
      this.errorMessage = message
      this.successMessage = ''
      this.warningMessage = ''
      
      setTimeout(() => {
        this.errorMessage = ''
      }, 7000)
    },

    showWarning(message) {
      console.warn('⚠️ Warning:', message)
      this.warningMessage = message
      this.successMessage = ''
      this.errorMessage = ''
      
      setTimeout(() => {
        this.warningMessage = ''
      }, 6000)
    },

    // ========== ICON AND STYLING METHODS ==========
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

.btn.btn-outline-secondary:hover {
  background-color: var(--info-light);
  border-color: var(--info);
  color: var(--info-dark);
}

.form-select:focus,
.form-control:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25);
}

.category-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
}

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

.row.g-3 {
  --bs-gutter-x: 1rem;
  --bs-gutter-y: 1rem;
}

.spinner-border {
  width: 2rem;
  height: 2rem;
}

.deleted-category {
  opacity: 0.85;
  border: 2px dashed #ffc107 !important;
}

.deleted-category:hover {
  opacity: 1;
}

.selected-category {
  border: 2px solid var(--primary) !important;
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25);
}

.selection-checkbox {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  z-index: 10;
}

.selection-checkbox .form-check-input {
  width: 1.2rem;
  height: 1.2rem;
}

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