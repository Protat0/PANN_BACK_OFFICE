<template>
  <div class="promotions-page">
    <!-- Main Content -->
    <div class="container-fluid py-4">
      <!-- Action Bar and Filters -->
      <div class="action-bar-container mb-3">
        <div class="action-row">
          <!-- Left Side: Main Actions -->
          <div v-if="selectedPromotions.length === 0" class="d-flex gap-2">
            <button 
              class="btn btn-add btn-sm btn-with-icon"
              @click="handleSinglePromo"
            >
              <Plus :size="14" />
              ADD PROMO
            </button>

            <button 
              class="btn btn-outline-secondary btn-sm"
              @click="exportData"
              :disabled="loading"
            >
              EXPORT
            </button>

            <button 
              class="btn btn-outline-info btn-sm"
              @click="refreshPromotions"
              :disabled="loading"
            >
              <RotateCcw :size="14" />
              REFRESH
            </button>
          </div>

          <!-- Selection Actions -->
          <div v-if="selectedPromotions.length > 0" class="d-flex gap-2">
            <button 
              class="btn btn-delete btn-sm btn-with-icon"
              @click="deleteSelected"
              :disabled="loading"
            >
              <Trash2 :size="14" />
              DELETE ({{ selectedPromotions.length }})
            </button>
          </div>

          <!-- Right Side: Search and Filters -->
          <div class="filters-section d-flex align-items-center gap-2">
            <!-- Search Toggle -->
            <button 
              class="btn btn-secondary btn-sm search-toggle-btn"
              @click="toggleSearchMode"
              :class="{ 'active': searchMode }"
            >
              <Search :size="16" />
            </button>

            <!-- Filter Dropdowns -->
            <template v-if="!searchMode">
              <div class="filter-group">
                <label class="filter-label">Discount Type</label>
                <select 
                  class="form-select form-select-sm" 
                  v-model="discountTypeFilter" 
                  @change="applyFilters"
                >
                  <option value="all">All types</option>
                  <option value="percentage">Percentage</option>
                  <option value="fixed_amount">Fixed Amount</option>
                  <option value="buy_x_get_y">BOGO</option>
                </select>
              </div>

              <div class="filter-group">
                <label class="filter-label">Status</label>
                <select 
                  class="form-select form-select-sm" 
                  v-model="statusFilter" 
                  @change="applyFilters"
                >
                  <option value="all">All status</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="expired">Expired</option>
                  <option value="scheduled">Scheduled</option>
                </select>
              </div>
            </template>

            <!-- Search Bar -->
            <div v-if="searchMode" class="search-container">
              <div class="position-relative">
                <input 
                  ref="searchInput"
                  v-model="searchFilter" 
                  @input="debounceSearch"
                  @keyup.enter="performSearch"
                  type="text" 
                  class="form-control form-control-sm search-input"
                  placeholder="Search promotions..."
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

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="error" class="alert alert-danger" role="alert">
        <strong>Error:</strong> {{ error }}
        <button class="btn btn-sm btn-outline-danger ms-2" @click="refreshPromotions">
          Try Again
        </button>
      </div>

      <div class="row" v-if="!loading">
        <div class="col-12">
          <!-- Promotions Table -->
          <DataTable
            :total-items="pagination.total_items"
            :current-page="pagination.current_page"
            :items-per-page="pagination.items_per_page"
            @page-changed="handlePageChange"
          >
            <template #header>
              <tr>
                <th class="text-center" style="width: 50px;">
                  <div class="form-check">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      :checked="isAllSelected"
                      :indeterminate="isIndeterminate"
                      @change="toggleSelectAll"
                    >
                  </div>
                </th>
                <th>Promotion Name</th>
                <th>Discount Type</th>
                <th>Discount Value</th>
                <th>Start Date</th>
                <th>End Date</th>
                <th>Status</th>
                <th>Last Updated</th>
                <th class="text-center" style="width: 120px;">Actions</th>
              </tr>
            </template>

            <template #body>
              <tr 
                v-for="promotion in promotions" 
                :key="promotion.promotion_id"
                :class="{ 'table-primary': selectedPromotions.includes(promotion.promotion_id) }"
              >
                <td class="text-center">
                  <div class="form-check">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      :value="promotion.promotion_id"
                      v-model="selectedPromotions"
                    >
                  </div>
                </td>
                <td>
                  <div class="fw-medium text-tertiary-dark">{{ promotion.promotion_name }}</div>
                </td>
                <td>
                  <span class="badge" :class="getDiscountTypeBadgeClass(promotion.discount_type)">
                    {{ formatDiscountType(promotion.discount_type) }}
                  </span>
                </td>
                <td class="text-tertiary-dark">
                  {{ formatDiscountValue(promotion.discount_value, promotion.discount_type) }}
                </td>
                <td class="text-tertiary-medium">
                  {{ formatDate(promotion.start_date) }}
                </td>
                <td class="text-tertiary-medium">
                  {{ formatDate(promotion.end_date) }}
                </td>
                <td>
                  <span class="badge" :class="getStatusBadgeClass(promotion.status)">
                    {{ formatStatus(promotion.status) }}
                  </span>
                </td>
                <td class="text-tertiary-medium">
                  {{ formatDateTime(promotion.last_updated) }}
                </td>
                <td class="text-center">
                  <div class="d-flex justify-content-center gap-1">
                    <button 
                      class="btn btn-outline-primary action-btn action-btn-view"
                      @click="viewPromotion(promotion)"
                      title="View Details"
                    >
                      <Eye :size="12" />
                    </button>
                    <button 
                      class="btn btn-outline-secondary action-btn action-btn-edit"
                      @click="editPromotion(promotion)"
                      title="Edit"
                    >
                      <Edit :size="12" />
                    </button>
                    <button 
                      class="btn btn-outline-danger action-btn action-btn-delete"
                      @click="deletePromotion(promotion)"
                      title="Delete"
                    >
                      <Trash2 :size="12" />
                    </button>
                  </div>
                </td>
              </tr>

              <!-- Empty State -->
              <tr v-if="promotions.length === 0 && !loading">
                <td colspan="9" class="text-center py-5">
                  <div class="text-tertiary-medium">
                    <Package :size="48" class="mb-3 opacity-50" />
                    <div>No promotions found</div>
                    <small>Start by creating your first promotional campaign</small>
                  </div>
                </td>
              </tr>
            </template>
          </DataTable>
        </div>
      </div>
    </div>

    <!-- Add Promo Modal -->
    <AddPromoModal ref="addPromoModal" @promotion-saved="handlePromotionSaved" />
  </div>
</template>

<script>
import DataTable from '@/components/common/TableTemplate.vue'
import AddPromoModal from '@/components/promotions/AddPromoModal.vue'
import promotionApiService from '@/services/apiPromotions.js'

export default {
  name: 'Promotions',
  components: {
    DataTable,
    AddPromoModal
  },
  data() {
    return {
      promotions: [],
      selectedPromotions: [],
      pagination: {
        current_page: 1,
        total_pages: 1,
        total_items: 0,
        items_per_page: 20
      },
      
      // UI State
      loading: false,
      error: null,
      searchMode: false,
      
      // Filters
      discountTypeFilter: 'all',
      statusFilter: 'all',
      searchFilter: '',
      searchTimeout: null
    }
  },
  computed: {
    isAllSelected() {
      return this.selectedPromotions.length === this.promotions.length && this.promotions.length > 0
    },
    isIndeterminate() {
      return this.selectedPromotions.length > 0 && this.selectedPromotions.length < this.promotions.length
    }
  },
  async mounted() {
    await this.loadPromotions()
  },
  methods: {
    async loadPromotions() {
      try {
        this.loading = true
        this.error = null
        
        const params = {
          page: this.pagination.current_page,
          limit: this.pagination.items_per_page
        }
        
        // Add filters
        if (this.discountTypeFilter !== 'all') {
          params.discount_type = this.discountTypeFilter
        }
        if (this.statusFilter !== 'all') {
          params.status = this.statusFilter
        }
        if (this.searchFilter.trim()) {
          params.search_query = this.searchFilter.trim()
        }
        
        const response = await promotionApiService.getAllPromotions(params)
        
        if (response.success) {
          this.promotions = response.promotions
          this.pagination = response.pagination
        } else {
          this.error = response.message || 'Failed to load promotions'
        }
        
      } catch (error) {
        console.error('Error loading promotions:', error)
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async refreshPromotions() {
      this.selectedPromotions = []
      await this.loadPromotions()
    },

    handleSinglePromo() {
      if (this.$refs.addPromoModal && this.$refs.addPromoModal.openAdd) {
        this.$refs.addPromoModal.openAdd()
      }
    },

    async exportData() {
      try {
        const filters = {}
        if (this.discountTypeFilter !== 'all') {
          filters.discount_type = this.discountTypeFilter
        }
        if (this.statusFilter !== 'all') {
          filters.status = this.statusFilter
        }
        
        const exportData = await promotionApiService.exportPromotions(filters, 'json')
        
        // Create and download file
        const blob = new Blob([exportData], { type: 'application/json' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `promotions_${new Date().toISOString().split('T')[0]}.json`
        link.click()
        window.URL.revokeObjectURL(url)
        
      } catch (error) {
        console.error('Export error:', error)
        alert('Export failed: ' + error.message)
      }
    },

    async deleteSelected() {
      if (this.selectedPromotions.length === 0) return
      
      const confirmed = confirm(`Are you sure you want to delete ${this.selectedPromotions.length} promotion(s)?`)
      if (!confirmed) return

      try {
        this.loading = true
        const result = await promotionApiService.deleteMultiplePromotions(this.selectedPromotions)
        
        if (result.success) {
          const successCount = result.results.filter(r => r.success).length
          alert(`Successfully deleted ${successCount} promotion(s)`)
          this.selectedPromotions = []
          await this.loadPromotions()
        }
      } catch (error) {
        console.error('Bulk delete error:', error)
        alert('Delete failed: ' + error.message)
      } finally {
        this.loading = false
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

    debounceSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.performSearch()
      }, 500)
    },

    async performSearch() {
      this.pagination.current_page = 1
      await this.loadPromotions()
    },

    async applyFilters() {
      this.pagination.current_page = 1
      this.selectedPromotions = []
      await this.loadPromotions()
    },

    async handlePageChange(page) {
      this.pagination.current_page = page
      await this.loadPromotions()
    },

    toggleSelectAll() {
      if (this.isAllSelected) {
        this.selectedPromotions = []
      } else {
        this.selectedPromotions = this.promotions.map(p => p.promotion_id)
      }
    },

    async handlePromotionSaved() {
      await this.refreshPromotions()
    },

    // Formatting methods
    formatDiscountType(type) {
      const types = {
        'percentage': 'Percentage',
        'fixed_amount': 'Fixed Amount',
        'buy_x_get_y': 'BOGO'
      }
      return types[type] || type
    },

    formatDiscountValue(value, type) {
      if (type === 'percentage') {
        return `${value}%`
      } else if (type === 'fixed_amount') {
        return `₱${value}`
      }
      return value
    },

    formatStatus(status) {
      const statuses = {
        'active': 'Active',
        'inactive': 'Inactive',
        'expired': 'Expired',
        'scheduled': 'Scheduled'
      }
      return statuses[status] || status
    },

    formatDate(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },

    formatDateTime(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    getDiscountTypeBadgeClass(type) {
      const classes = {
        'percentage': 'bg-primary text-white',
        'fixed_amount': 'bg-success text-white',
        'buy_x_get_y': 'bg-info text-white'
      }
      return classes[type] || 'bg-secondary text-white'
    },

    getStatusBadgeClass(status) {
      const classes = {
        'active': 'bg-success text-white',
        'inactive': 'bg-secondary text-white',
        'expired': 'bg-danger text-white',
        'scheduled': 'bg-warning text-dark'
      }
      return classes[status] || 'bg-secondary text-white'
    },

    viewPromotion(promotion) {
      if (this.$refs.addPromoModal && this.$refs.addPromoModal.openView) {
        this.$refs.addPromoModal.openView(promotion)
      }
    },

    editPromotion(promotion) {
      if (this.$refs.addPromoModal && this.$refs.addPromoModal.openEdit) {
        this.$refs.addPromoModal.openEdit(promotion)
      }
    },

    async deletePromotion(promotion) {
      const confirmed = confirm(`Are you sure you want to delete "${promotion.promotion_name}"?`)
      if (!confirmed) return

      try {
        this.loading = true
        const result = await promotionApiService.deletePromotion(promotion.promotion_id)
        
        if (result.success) {
          alert('Promotion deleted successfully')
          await this.loadPromotions()
        } else {
          alert('Delete failed: ' + result.message)
        }
      } catch (error) {
        console.error('Delete error:', error)
        alert('Delete failed: ' + error.message)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
/* Keep existing styles */
.promotions-page {
  min-height: 100vh;
  background-color: var(--neutral-light);
}

.action-bar-container {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
  padding: 1rem;
}

.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.filters-section {
  flex-shrink: 0;
}

.search-toggle-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  flex-shrink: 0;
}

.filter-group {
  min-width: 140px;
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

.btn.active {
  background-color: var(--primary);
  border-color: var(--primary);
  color: white;
}

@media (max-width: 768px) {
  .action-row {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .filters-section {
    justify-content: flex-start;
  }
  
  .filter-group {
    min-width: 120px;
  }
  
  .search-container {
    min-width: 100%;
  }
}
</style>