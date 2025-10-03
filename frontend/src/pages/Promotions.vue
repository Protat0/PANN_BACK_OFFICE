<template>
  <div class="promotions-page">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">Promotion Management</h1>
      <p class="page-subtitle">Manage promotional campaigns and discounts</p>
    </div>

    <!-- Action Bar -->
    <ActionBar
      entity-name="promotion"
      add-button-text="ADD PROMO"
      search-placeholder="Search promotions by name..."
      :add-options="addOptions"
      :selected-items="selectedPromotions"
      :selection-actions="selectionActions"
      :filters="filters"
      :search-value="searchFilter"
      :show-columns-button="false"
      :show-export-button="true"
      :exporting="exporting"
      @add-action="handleAddAction"
      @selection-action="handleSelectionAction"
      @filter-change="handleFilterChange"
      @search-input="handleSearchInput"
      @search-clear="handleSearchClear"
      @export="exportData"
    />

    <!-- Loading State -->
    <div v-if="loading && promotions.length === 0" class="loading-state">
      <div class="spinner-border"></div>
      <p>Loading promotions...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-state">
      <div class="alert alert-danger">
        <p>{{ error }}</p>
        <button class="btn btn-primary" @click="refreshPromotions">
          Try Again
        </button>
      </div>
    </div>

    <!-- Data Table -->
    <TableTemplate
      v-if="!loading || promotions.length > 0"
      :items-per-page="pagination.items_per_page"
      :total-items="pagination.total_items"
      :current-page="pagination.current_page"
      :show-pagination="true"
      @page-changed="handlePageChange"
    >
      <template #header>
        <tr>
          <th class="checkbox-column">
            <input 
              type="checkbox" 
              class="form-check-input"
              @change="toggleSelectAll" 
              :checked="isAllSelected"
              :indeterminate.prop="isIndeterminate"
            />
          </th>
          <th>Promotion Name</th>
          <th>Discount Type</th>
          <th>Discount Value</th>
          <th>Start Date</th>
          <th>End Date</th>
          <th>Status</th>
          <th>Last Updated</th>
          <th>Actions</th>
        </tr>
      </template>

      <template #body>
        <tr 
          v-for="promotion in promotions" 
          :key="promotion.promotion_id"
          :class="{ 'table-primary': selectedPromotions.includes(promotion.promotion_id) }"
        >
          <td class="checkbox-column">
            <input 
              type="checkbox" 
              class="form-check-input"
              :value="promotion.promotion_id"
              v-model="selectedPromotions"
            />
          </td>
          <td>{{ promotion.promotion_name }}</td>
          <td>
            <span 
              class="badge"
              :class="getDiscountTypeBadgeClass(promotion.discount_type)"
            >
              {{ formatDiscountType(promotion.discount_type) }}
            </span>
          </td>
          <td class="text-tertiary-medium">
            {{ formatDiscountValue(promotion.discount_value, promotion.discount_type) }}
          </td>
          <td class="text-tertiary-medium">
            {{ formatDate(promotion.start_date) }}
          </td>
          <td class="text-tertiary-medium">
            {{ formatDate(promotion.end_date) }}
          </td>
          <td>
            <span 
              class="badge"
              :class="getStatusBadgeClass(promotion.status)"
            >
              {{ formatStatus(promotion.status) }}
            </span>
          </td>
          <td class="text-tertiary-medium">
            {{ formatDateTime(promotion.last_updated) }}
          </td>
          <td>
            <div class="d-flex gap-1">
              <button
                class="btn btn-outline btn-sm action-btn action-btn-view"
                @click="viewPromotion(promotion)"
                title="View Details"
              >
                <Eye :size="14" />
              </button>
              <button
                class="btn btn-outline btn-sm action-btn action-btn-edit"
                @click="editPromotion(promotion)"
                title="Edit Promotion"
              >
                <Edit :size="14" />
              </button>
              <button
                class="btn btn-outline btn-sm action-btn action-btn-delete"
                @click="deletePromotion(promotion)"
                title="Delete Promotion"
              >
                <Trash2 :size="14" />
              </button>
            </div>
          </td>
        </tr>
      </template>
    </TableTemplate>

    <!-- Empty State -->
    <div v-if="!loading && promotions.length === 0 && !error" class="empty-state">
      <div class="card">
        <div class="card-body">
          <p class="empty-message">No promotions found</p>
          <p class="empty-submessage">Get started by creating your first promotional campaign</p>
          <button class="btn btn-add" @click="handleSinglePromo">
            Add First Promotion
          </button>
        </div>
      </div>
    </div>

    <!-- Add Promo Modal -->
    <AddPromoModal ref="addPromoModal" @promotion-saved="handlePromotionSaved" />
  </div>
</template>

<script>
import ActionBar from '@/components/common/ActionBar.vue'
import TableTemplate from '@/components/common/TableTemplate.vue'
import AddPromoModal from '@/components/promotions/AddPromoModal.vue'
import promotionApiService from '@/services/apiPromotions.js'

export default {
  name: 'Promotions',
  components: {
    ActionBar,
    TableTemplate,
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
      exporting: false,
      
      // Filters
      discountTypeFilter: 'all',
      statusFilter: 'all',
      searchFilter: ''
    }
  },
  computed: {
    isAllSelected() {
      return this.promotions.length > 0 && this.selectedPromotions.length === this.promotions.length
    },
    isIndeterminate() {
      return this.selectedPromotions.length > 0 && this.selectedPromotions.length < this.promotions.length
    },
    addOptions() {
      return [
        {
          key: 'single',
          icon: 'Plus',
          title: 'Add Single Promotion',
          description: 'Create a new promotional campaign'
        }
      ]
    },
    selectionActions() {
      return [
        {
          key: 'delete',
          icon: 'Trash2',
          label: 'Delete',
          buttonClass: 'btn-delete-dynamic has-items'
        }
      ]
    },
    filters() {
      return [
        {
          key: 'discountType',
          label: 'Discount Type',
          value: this.discountTypeFilter,
          options: [
            { value: 'all', label: 'All Types' },
            { value: 'percentage', label: 'Percentage' },
            { value: 'fixed_amount', label: 'Fixed Amount' },
            { value: 'buy_x_get_y', label: 'BOGO' }
          ]
        },
        {
          key: 'status',
          label: 'Status',
          value: this.statusFilter,
          options: [
            { value: 'all', label: 'All Status' },
            { value: 'active', label: 'Active' },
            { value: 'inactive', label: 'Inactive' },
            { value: 'expired', label: 'Expired' },
            { value: 'scheduled', label: 'Scheduled' }
          ]
        }
      ]
    }
  },
  async mounted() {
    await this.loadPromotions()
  },
  methods: {
    handleAddAction(actionKey) {
      if (actionKey === 'single') {
        this.handleSinglePromo()
      }
    },

    handleSelectionAction(actionKey) {
      if (actionKey === 'delete') {
        this.deleteSelected()
      }
    },

    handleFilterChange(filterKey, value) {
      if (filterKey === 'discountType') {
        this.discountTypeFilter = value
      } else if (filterKey === 'status') {
        this.statusFilter = value
      }
      this.applyFilters()
    },

    handleSearchInput(value) {
      this.searchFilter = value
      this.applyFilters()
    },

    handleSearchClear() {
      this.searchFilter = ''
      this.applyFilters()
    },

    toggleSelectAll(event) {
      if (event.target.checked) {
        this.selectedPromotions = this.promotions.map(p => p.promotion_id)
      } else {
        this.selectedPromotions = []
      }
    },

    async loadPromotions() {
      try {
        this.loading = true
        this.error = null
        
        const params = {
          page: this.pagination.current_page,
          limit: this.pagination.items_per_page
        }
        
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

    async applyFilters() {
      this.pagination.current_page = 1
      this.selectedPromotions = []
      await this.loadPromotions()
    },

    async handlePageChange(page) {
      this.pagination.current_page = page
      await this.loadPromotions()
    },

    handleSinglePromo() {
      if (this.$refs.addPromoModal && this.$refs.addPromoModal.openAdd) {
        this.$refs.addPromoModal.openAdd()
      }
    },

    async exportData() {
      this.exporting = true
      
      try {
        const filters = {}
        if (this.discountTypeFilter !== 'all') {
          filters.discount_type = this.discountTypeFilter
        }
        if (this.statusFilter !== 'all') {
          filters.status = this.statusFilter
        }
        
        const exportData = await promotionApiService.exportPromotions(filters, 'json')
        
        const blob = new Blob([exportData], { type: 'application/json' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `promotions_${new Date().toISOString().split('T')[0]}.json`
        link.click()
        window.URL.revokeObjectURL(url)
        
      } catch (error) {
        console.error('Export error:', error)
        this.error = 'Export failed: ' + error.message
      } finally {
        this.exporting = false
      }
    },

    async deleteSelected() {
      if (this.selectedPromotions.length === 0) return
      
      const confirmed = confirm(`Delete ${this.selectedPromotions.length} promotion(s)?`)
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
        this.error = 'Delete failed: ' + error.message
      } finally {
        this.loading = false
      }
    },

    async deletePromotion(promotion) {
      const confirmed = confirm(`Delete promotion "${promotion.promotion_name}"?`)
      if (!confirmed) return

      try {
        this.loading = true
        const result = await promotionApiService.deletePromotion(promotion.promotion_id)
        
        if (result.success) {
          alert('Promotion deleted successfully')
          await this.loadPromotions()
        } else {
          this.error = 'Delete failed: ' + result.message
        }
      } catch (error) {
        console.error('Delete error:', error)
        this.error = 'Delete failed: ' + error.message
      } finally {
        this.loading = false
      }
    },

    async handlePromotionSaved() {
      await this.refreshPromotions()
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
      return new Date(dateString).toLocaleString()
    },

    getDiscountTypeBadgeClass(type) {
      const classes = {
        'percentage': 'bg-primary',
        'fixed_amount': 'bg-success',
        'buy_x_get_y': 'bg-info'
      }
      return classes[type] || 'bg-secondary'
    },

    getStatusBadgeClass(status) {
      const classes = {
        'active': 'bg-success',
        'inactive': 'bg-secondary',
        'expired': 'bg-danger',
        'scheduled': 'bg-warning'
      }
      return classes[status] || 'bg-secondary'
    }
  }
}
</script>

<style scoped>
.promotions-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.page-subtitle {
  color: var(--text-tertiary);
  margin: 0;
  font-size: 0.875rem;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 3rem;
  background: var(--surface-primary);
  border-radius: 0.75rem;
  box-shadow: var(--shadow-md);
  margin-top: 1rem;
}

.spinner-border {
  width: 2rem;
  height: 2rem;
  border: 0.25em solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spinner-border 0.75s linear infinite;
}

@keyframes spinner-border {
  to { transform: rotate(360deg); }
}

.alert {
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.alert-danger {
  background-color: var(--status-error-bg);
  color: var(--status-error);
  border: 1px solid var(--status-error);
}

.empty-state .card {
  background: var(--surface-primary);
  border: 1px solid var(--border-secondary);
  border-radius: 0.75rem;
}

.empty-state .card-body {
  padding: 3rem;
}

.empty-message {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.empty-submessage {
  color: var(--text-tertiary);
  margin-bottom: 1.5rem;
}

.checkbox-column {
  width: 40px;
  text-align: center;
}

.d-flex {
  display: flex;
}

.gap-1 {
  gap: 0.25rem;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.bg-primary {
  background: var(--primary-light);
  color: var(--primary-dark);
}

.badge.bg-warning {
  background: var(--status-warning-bg);
  color: var(--status-warning);
}

.badge.bg-info {
  background: var(--status-info-bg);
  color: var(--status-info);
}

.badge.bg-success {
  background: var(--status-success-bg);
  color: var(--status-success);
}

.badge.bg-secondary {
  background: var(--surface-tertiary);
  color: var(--text-tertiary);
}

.badge.bg-danger {
  background: var(--status-error-bg);
  color: var(--status-error);
}
</style>