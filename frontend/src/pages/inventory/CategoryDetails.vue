<template>
  <div class="container-fluid pt-2 pb-4 surface-secondary">
    <!-- Breadcrumb Navigation -->
    <nav aria-label="breadcrumb" class="mb-3">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link to="/inventory" class="text-tertiary-medium">Inventory</router-link>
        </li>
        <li class="breadcrumb-item">
          <router-link to="/categories" class="text-tertiary-medium">Categories</router-link>
        </li>
        <li class="breadcrumb-item active text-primary" aria-current="page">Category Details</li>
      </ol>
    </nav>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-accent" role="status">
        <span class="visually-hidden">Loading category details...</span>
      </div>
      <p class="mt-2 text-tertiary-medium">Loading category details...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="status-error mb-3">
      <strong>Error:</strong> {{ error }}
      <button @click="handleRetryLoad" class="btn btn-sm btn-export ms-2">
        Retry
      </button>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="status-success mb-3">
      {{ successMessage }}
    </div>

    <!-- Main Content -->
    <div v-if="!loading && !error && currentCategory">
      <!-- Page Header -->
      <div class="d-flex justify-content-between align-items-start mb-4">
        <div>
          <h1 class="h2 fw-bold text-primary mb-1">{{ currentCategory.category_name || 'Category Details' }}</h1>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-edit btn-sm btn-with-icon-sm" @click="handleEditCategory">
            <Edit :size="14" />
            Edit
          </button>
          <button 
            class="btn btn-export btn-sm btn-with-icon-sm" 
            :disabled="isExporting"
            @click="exportFilteredProducts()"
          >
            <Download :size="14" />
            {{ isExporting ? 'Exporting...' : getExportButtonText() }}
          </button>
        </div>
      </div>

      <!-- Category Information Cards -->
      <div class="row mb-4">
        <div class="col-md-8">
          <div class="card-theme h-100">
            <div class="card-body">
              <div class="row">
                <div class="col-6">
                  <div class="mb-3">
                    <label class="form-label text-primary fw-semibold">Category Name:</label>
                    <p class="mb-0 text-secondary">{{ currentCategory.category_name || 'N/A' }}</p>
                  </div>
                  <div class="mb-3">
                    <label class="form-label text-primary fw-semibold">Sub-Categories:</label>
                    <p class="mb-0 text-secondary">{{ currentCategory.sub_categories?.length || 0 }}</p>
                  </div>
                  <div class="mb-3">
                    <label class="form-label text-primary fw-semibold">Description:</label>
                    <p class="mb-0 text-secondary">{{ currentCategory.description || 'No description available' }}</p>
                  </div>
                </div>
                <div class="col-6">
                  <div class="mb-3">
                    <label class="form-label text-primary fw-semibold">Total Products:</label>
                    <p class="mb-0 text-secondary">{{ getProductCount(currentCategory) }}</p>
                  </div>
                  <div class="mb-3">
                    <label class="form-label text-primary fw-semibold">Status:</label>
                    <span :class="getStatusClass(currentCategory.status)">
                      {{ currentCategory.status?.charAt(0).toUpperCase() + currentCategory.status?.slice(1) || 'N/A' }}
                    </span>
                  </div>
                  <div class="mb-3">
                    <label class="form-label text-primary fw-semibold">Last Updated:</label>
                    <p class="mb-0 text-secondary">{{ formatDate(currentCategory.last_updated) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card-theme h-100">
            <div class="card-body d-flex align-items-center justify-content-center">
              <div class="text-center">
                <div v-if="currentCategory.image_url" class="category-image mb-3">
                  <img :src="currentCategory.image_url" alt="Category image" class="img-fluid rounded" style="max-height: 120px;" />
                </div>
                <div v-else class="category-image-placeholder surface-tertiary rounded p-4 mb-3">
                  <Package :size="64" class="text-tertiary" />
                </div>
                <small class="text-tertiary">Category Image</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Bar -->
      <div class="action-bar-container mb-3">
        <div class="surface-card border-theme action-bar-controls">
          <div class="action-row">
            <div class="d-flex align-items-end gap-2">
              <div class="filter-dropdown">
                <label class="filter-label text-tertiary">Filter</label>
                <select class="form-select form-select-sm input-theme" v-model="categoryFilter" @change="applyFilter">
                  <option value="all">All Products ({{ currentProducts.length }})</option>
                  <option 
                    v-for="subCat in currentCategory.sub_categories" 
                    :key="subCat.id || subCat.name" 
                    :value="subCat.name"
                  >
                    {{ subCat.name }} ({{ getSubcategoryProductCount(subCat.name) }})
                  </option>
                </select>
              </div>
              
              <button 
                v-if="selectedProducts.length === 0"
                class="btn btn-add btn-sm btn-with-icon-sm" 
                @click="handleAddSubCategory"
              >
                <Plus :size="14" />
                Add Sub Category
              </button>
              
              <button 
                v-if="selectedProducts.length > 0"
                class="btn btn-delete btn-sm btn-with-icon-sm" 
                @click="removeSelectedFromCategory"
              >
                <Trash2 :size="14" />
                Remove ({{ selectedProducts.length }})
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Products Table -->
      <DataTable
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
                :checked="isAllSelected"
                @change="toggleSelectAll"
                :indeterminate.prop="isIndeterminate"
              />
            </th>
            <th style="width: 120px;">Product ID</th>
            <th>Product Name</th>
            <th style="width: 140px;">Sub-Category</th>
            <th style="width: 120px;">Remaining Stock</th>
            <th style="width: 120px;">Selling Price</th>
            <th style="width: 120px;">Supplier</th>
            <th style="width: 100px;">Actions</th>
          </tr>
        </template>

        <template #body>
          <tr v-for="product in paginatedProducts" :key="product._id">
            <td>
              <input 
                type="checkbox" 
                class="form-check-input" 
                :value="product._id"
                v-model="selectedProducts"
              />
            </td>
            <td>
              <code class="text-tertiary surface-tertiary px-2 py-1 rounded">
                {{ product._id }}
              </code>
            </td>
            <td>
              <div class="fw-medium text-primary">{{ product.product_name }}</div>
            </td>
            <td>
               <select 
                  class="form-select form-select-sm input-complete"
                  :value="product.subcategory || 'None'"  
                  @change="handleUpdateProductSubcategory(product._id, $event.target.value)"
                >
                  <option 
                    v-for="subCat in currentCategory.sub_categories" 
                    :key="subCat.name" 
                    :value="subCat.name"
                  >
                    {{ subCat.name }}
                  </option>
                </select>
            </td>
            <td class="text-center">
              <span :class="getStockClass(product.stock)">
                {{ product.stock || 0 }}
              </span>
            </td>
            <td class="text-end fw-medium text-secondary">
              ₱{{ formatPrice(product.selling_price) }}
            </td>
            <td class="text-secondary">{{ product.supplier || 'N/A' }}</td>
            <td>
              <div class="d-flex gap-1 justify-content-center">
                <button 
                  class="btn btn-outline-danger btn-icon-only btn-xs action-btn action-btn-delete"
                  @click="removeProductFromCategory(product)"
                  data-bs-toggle="tooltip"
                  title="Remove from Category"
                >
                  <Trash2 :size="12" />
                </button>
              </div>
            </td>
          </tr>
        </template>
      </DataTable>

      <!-- Empty State -->
      <div v-if="filteredProducts.length === 0" class="text-center py-5">
        <div class="card-theme">
          <div class="card-body py-5">
            <Package :size="48" class="text-tertiary mb-3" />
            <p class="text-tertiary mb-3">
              {{ categoryFilter === 'all' ? 'No products found in this category' : 
                 `No products found in "${categoryFilter}" subcategory` }}
            </p>
            <button class="btn btn-add btn-with-icon" v-if="categoryFilter === 'all'">
              <Plus :size="16" />
              Add First Product
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <AddCategoryModal ref="editCategoryModal" @category-updated="onCategoryUpdated" />
    <AddSubcategoryModal ref="addSubcategoryModal" @subcategory-added="onSubcategoryAdded" />
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import DataTable from '@/components/common/TableTemplate.vue'
import AddSubcategoryModal from '@/components/categories/AddSubCategoryModal.vue'
import AddCategoryModal from '@/components/categories/AddCategoryModal.vue'
import categoryApiService from '@/services/apiCategory'

export default {
  name: 'CategoryDetails',
  components: {
    DataTable,
    AddCategoryModal,
    AddSubcategoryModal
  },
  
  setup() {
    const route = useRoute()
    
    // State
    const loading = ref(false)
    const error = ref(null)
    const successMessage = ref(null)
    const currentCategory = ref(null)
    const currentProducts = ref([])
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const categoryFilter = ref('all')
    const selectedProducts = ref([])
    const isExporting = ref(false)
    const categoryId = ref(null)
    const editCategoryModal = ref(null)
    const addSubcategoryModal = ref(null)


    // Computed
    const filteredProducts = computed(() => {
      if (categoryFilter.value === 'all') {
        return currentProducts.value
      }
      return currentProducts.value.filter(product => {
        const productSubcategory = product.subcategory || product.subcategory_id || product.subcategory_name
        return productSubcategory === categoryFilter.value
      })
    })
    
    const paginatedProducts = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      return filteredProducts.value.slice(start, end)
    })

    const isAllSelected = computed(() => {
      const currentPageProductIds = paginatedProducts.value.map(p => p._id)
      return currentPageProductIds.length > 0 && 
            currentPageProductIds.every(id => selectedProducts.value.includes(id))
    })

    const isIndeterminate = computed(() => {
      const currentPageProductIds = paginatedProducts.value.map(p => p._id)
      const selectedOnPage = currentPageProductIds.filter(id => selectedProducts.value.includes(id))
      return selectedOnPage.length > 0 && selectedOnPage.length < currentPageProductIds.length
    })

    // Methods
    const loadCategoryData = async (id) => {
      if (!id) {
        error.value = 'No category ID provided'
        return
      }
      
      loading.value = true
      error.value = null
      
      try {
        const categoryResponse = await categoryApiService.FindCategoryData({ id })
        
        if (categoryResponse) {
          currentCategory.value = categoryResponse.category || categoryResponse
          const products = await categoryApiService.FindProdcategory({ id })
          currentProducts.value = Array.isArray(products) ? products : []
        } else {
          throw new Error('Category not found')
        }
        
      } catch (err) {
        error.value = err.message || 'Failed to load category data'
        currentCategory.value = null
        currentProducts.value = []
      } finally {
        loading.value = false
      }
    }

    const handleRetryLoad = async () => {
      const id = route.params.id
      if (id) {
        await loadCategoryData(id)
      } else {
        error.value = 'No category ID available for retry'
      }
    }

    const applyFilter = () => {
      currentPage.value = 1
      selectedProducts.value = []
    }

    const handlePageChange = (page) => {
      currentPage.value = page
    }

    const toggleSelectAll = () => {
      const currentPageProductIds = paginatedProducts.value.map(p => p._id)
      
      if (isAllSelected.value) {
        selectedProducts.value = selectedProducts.value.filter(id => !currentPageProductIds.includes(id))
      } else {
        const newSelections = currentPageProductIds.filter(id => !selectedProducts.value.includes(id))
        selectedProducts.value = [...selectedProducts.value, ...newSelections]
      }
    }

    const handleUpdateProductSubcategory = async (productId, newSubcategory) => {
      try {
        await categoryApiService.SubCatChangeTab({
          product_id: productId,
          category_id: categoryId.value,
          new_subcategory: newSubcategory || "None"
        })
        
        const product = currentProducts.value.find(p => p._id === productId)
        if (product) {
          product.subcategory = newSubcategory || "None"
          product.subcategory_name = newSubcategory || "None"
          product.subcategory_id = newSubcategory || "None"
        }
        
        showSuccess('Product subcategory updated successfully')
        
      } catch (err) {
        showError(`Failed to update subcategory: ${err.message}`)
      }
    }

    const removeProductFromCategory = async (product) => {
      try {
        const confirmed = confirm(
          `Are you sure you want to remove "${product.name || product.product_name}" from the "${currentCategory.value.category_name}" category?\n\n` +
          `The product will be moved back to the "Uncategorized" category.`
        )
        
        if (!confirmed) return
        
        await categoryApiService.MoveProductToUncategorized({
          product_id: product._id,
          current_category_id: categoryId.value
        })
        
        const productIndex = currentProducts.value.findIndex(p => p._id === product._id)
        if (productIndex > -1) {
          currentProducts.value.splice(productIndex, 1)
        }
        
        selectedProducts.value = selectedProducts.value.filter(id => id !== product._id)
        showSuccess(`"${product.product_name}" has been moved to the Uncategorized category.`)
        
      } catch (err) {
        showError(`Failed to move product: ${err.message}`)
      }
    }

    const removeSelectedFromCategory = async () => {
      if (selectedProducts.value.length === 0) return
      
      const confirmed = confirm(`Are you sure you want to remove ${selectedProducts.value.length} product(s) from this category?`)
      if (!confirmed) return
      
      try {
        await categoryApiService.BulkMoveProductsToUncategorized({
          product_ids: selectedProducts.value,
          current_category_id: categoryId.value
        })
        
        currentProducts.value = currentProducts.value.filter(product => 
          !selectedProducts.value.includes(product._id)
        )
        
        const removedCount = selectedProducts.value.length
        selectedProducts.value = []
        
        showSuccess(`${removedCount} product(s) moved to Uncategorized category successfully!`)
        
      } catch (err) {
        showError(`Bulk move failed: ${err.message}`)
      }
    }

    // Modal handlers
    const handleEditCategory = () => {
      if (editCategoryModal.value) {
        editCategoryModal.value.openEditMode(currentCategory.value)
      } else {
        console.error('Edit category modal ref not found')
      }
    }

    // In CategoryDetails.vue
    const handleAddSubCategory = () => {
      console.log('Add subcategory button clicked')
      console.log('Modal ref:', addSubcategoryModal.value)
      console.log('Current category:', currentCategory.value)
      
      if (addSubcategoryModal.value) {
        console.log('Opening modal...')
        addSubcategoryModal.value.openModal(
          currentCategory.value._id,
          currentCategory.value.category_name || 'Unknown Category'
        )
      } else {
        console.error('Add subcategory modal ref not found')
      }
    }

    const onCategoryUpdated = () => {
      const id = route.params.id
      if (id) loadCategoryData(id)
    }

    const onSubcategoryAdded = async () => {
      try {
        await loadCategoryData(categoryId.value)
        showSuccess('Subcategory added successfully')
      } catch (err) {
        showError('Subcategory added but failed to refresh data. Please refresh the page.')
      }
    }

    // Utility methods
    const showSuccess = (message) => {
      successMessage.value = message
      setTimeout(() => { successMessage.value = null }, 3000)
    }

    const showError = (message) => {
      error.value = message
      setTimeout(() => { error.value = null }, 5000)
    }

    const formatPrice = (price) => parseFloat(price || 0).toFixed(2)

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const getStatusClass = (status) => {
      return status === 'active' ? 'badge bg-success text-white' : 'badge bg-danger text-white'
    }
    
    const getStockClass = (stock) => {
      if (stock === 0) return 'text-error fw-bold'
      if (stock <= 15) return 'text-warning fw-semibold'
      return 'text-success fw-medium'
    }

    const getSubcategoryProductCount = (subcategoryName) => {
      return currentProducts.value.filter(product => {
        const productSubcategory = product.subcategory || product.subcategory_id || product.subcategory_name
        return productSubcategory === subcategoryName
      }).length
    }

    const getProductCount = (category) => {
      if (category.sub_categories) {
        return category.sub_categories.reduce((total, sub) => total + (sub.products?.length || 0), 0)
      }
      return category.product_count || 0
    }

    const exportFilteredProducts = () => {
      // Placeholder - implement export logic
      console.log('Export functionality to be implemented')
    }

    const getExportButtonText = () => `Export (${filteredProducts.value.length})`

    // Watch for route changes
    watch(() => route.params.id, (newId) => {
      if (newId) {
        categoryId.value = newId
        loadCategoryData(newId)
      }
    }, { immediate: true })

    return {
      // State
      loading, error, successMessage, currentCategory, currentProducts, currentPage, itemsPerPage,
      categoryFilter, selectedProducts, isExporting, categoryId,
      
      // Computed
      filteredProducts, paginatedProducts, isAllSelected, isIndeterminate,
      
      editCategoryModal,
      addSubcategoryModal,

      // Methods
      loadCategoryData, handleRetryLoad, applyFilter, handlePageChange, toggleSelectAll,
      handleUpdateProductSubcategory, removeProductFromCategory, removeSelectedFromCategory,
      handleEditCategory, handleAddSubCategory, onCategoryUpdated, onSubcategoryAdded,
      
      // Utility methods
      formatPrice, formatDate, getStatusClass, getStockClass, getSubcategoryProductCount,
      getProductCount, exportFilteredProducts, getExportButtonText
    }
  }
}
</script>

<style scoped>
.action-bar-controls {
  border-radius: 0.75rem;
}

.action-row {
  display: flex;
  justify-content: flex-start;
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

.category-image-placeholder {
  width: 100%;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed var(--border-secondary);
}

.breadcrumb {
  background: none;
  padding: 0;
  margin: 0;
}

.breadcrumb-item + .breadcrumb-item::before {
  content: ">";
  color: var(--text-tertiary);
}

.breadcrumb-item a {
  text-decoration: none;
}

.breadcrumb-item a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .action-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .d-flex.gap-2 {
    flex-direction: column;
    gap: 0.5rem !important;
  }
  
  .filter-dropdown {
    min-width: 100%;
  }
}
</style>