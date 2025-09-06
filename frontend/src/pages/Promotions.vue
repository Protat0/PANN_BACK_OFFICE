<template>
  <div class="promotions-page">
    <!-- Main Content -->
    <div class="container-fluid py-4">
      <!-- Action Bar and Filters -->
      <div class="action-bar-container mb-3">
        <div class="action-row">
          <!-- Left Side: Main Actions (Always visible when no selection) -->
          <div v-if="selectedPromotions.length === 0" class="d-flex gap-2">
            <!-- Add Promo Button -->
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
            >
              EXPORT
            </button>
          </div>

          <!-- Selection Actions (Visible when items are selected) -->
          <div v-if="selectedPromotions.length > 0" class="d-flex gap-2">
            <button 
              class="btn btn-delete btn-sm btn-with-icon"
              @click="deleteSelected"
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

            <!-- Filter Dropdowns (Hidden when search is active) -->
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
                  <option value="fixed">Fixed Amount</option>
                  <option value="buy_one_get_one">BOGO</option>
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

            <!-- Search Bar (Visible when search mode is active) -->
            <div v-if="searchMode" class="search-container">
              <div class="position-relative">
                <input 
                  ref="searchInput"
                  v-model="searchFilter" 
                  @input="applyFilters"
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

      <div class="row">
        <div class="col-12">
          <!-- Promotions Table -->
          <DataTable
            :total-items="totalPromotions"
            :current-page="currentPage"
            :items-per-page="itemsPerPage"
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
                v-for="promotion in paginatedPromotions" 
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
              <tr v-if="promotions.length === 0">
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
    <AddPromoModal ref="addPromoModal" />
  </div>
</template>

<script>
import DataTable from '@/components/common/TableTemplate.vue'
import AddPromoModal from '@/components/promotions/AddPromoModal.vue'

export default {
  name: 'Promotions',
  components: {
    DataTable,
    AddPromoModal
  },
  data() {
    return {
      promotions: [
        {
          promotion_id: '1',
          promotion_name: 'New Year Special',
          discount_type: 'percentage',
          discount_value: 20,
          start_date: '2025-01-01',
          end_date: '2025-01-31',
          status: 'active',
          last_updated: '2025-01-15T10:30:00Z',
          applicable_products: ['prod1', 'prod2']
        },
        {
          promotion_id: '2',
          promotion_name: 'Student Discount',
          discount_type: 'fixed',
          discount_value: 50,
          start_date: '2025-01-01',
          end_date: '2025-12-31',
          status: 'active',
          last_updated: '2025-01-10T14:20:00Z',
          applicable_products: ['prod3']
        },
        {
          promotion_id: '3',
          promotion_name: 'Weekend Sale',
          discount_type: 'percentage',
          discount_value: 15,
          start_date: '2025-01-20',
          end_date: '2025-01-22',
          status: 'expired',
          last_updated: '2025-01-23T09:15:00Z',
          applicable_products: ['prod1', 'prod4']
        }
      ],
      filteredPromotions: [],
      selectedPromotions: [],
      currentPage: 1,
      itemsPerPage: 10,
      
      // UI State
      searchMode: false,
      
      // Filters
      discountTypeFilter: 'all',
      statusFilter: 'all',
      searchFilter: ''
    }
  },
  computed: {
    totalPromotions() {
      return this.filteredPromotions.length
    },
    paginatedPromotions() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredPromotions.slice(start, end)
    },
    isAllSelected() {
      return this.selectedPromotions.length === this.paginatedPromotions.length && this.paginatedPromotions.length > 0
    },
    isIndeterminate() {
      return this.selectedPromotions.length > 0 && this.selectedPromotions.length < this.paginatedPromotions.length
    }
  },
  mounted() {
    this.filteredPromotions = [...this.promotions]
  },
  methods: {
    handleSinglePromo() {
      if (this.$refs.addPromoModal && this.$refs.addPromoModal.openAdd) {
        this.$refs.addPromoModal.openAdd()
      }
    },
    exportData() {
      console.log('Export promotions data')
      // Implement export functionality
    },
    deleteSelected() {
      if (this.selectedPromotions.length === 0) return
      
      const confirmed = confirm(`Are you sure you want to delete ${this.selectedPromotions.length} promotion(s)?`)
      if (!confirmed) return

      console.log('Delete selected promotions:', this.selectedPromotions)
      // Implement bulk delete
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
    applyFilters() {
      let filtered = [...this.promotions]

      // Filter by discount type
      if (this.discountTypeFilter !== 'all') {
        filtered = filtered.filter(promo => promo.discount_type === this.discountTypeFilter)
      }

      // Filter by status
      if (this.statusFilter !== 'all') {
        filtered = filtered.filter(promo => promo.status === this.statusFilter)
      }

      // Filter by search
      if (this.searchFilter.trim()) {
        const search = this.searchFilter.toLowerCase()
        filtered = filtered.filter(promo => 
          promo.promotion_name?.toLowerCase().includes(search) ||
          promo.promotion_id?.toLowerCase().includes(search)
        )
      }

      this.currentPage = 1
      this.selectedPromotions = []
      this.filteredPromotions = filtered
    },
    clearFilters() {
      this.discountTypeFilter = 'all'
      this.statusFilter = 'all'
      this.searchFilter = ''
      this.searchMode = false
      this.applyFilters()
    },

    // Table methods
    handlePageChange(page) {
      this.currentPage = page
    },
    toggleSelectAll() {
      if (this.isAllSelected) {
        this.selectedPromotions = []
      } else {
        this.selectedPromotions = this.paginatedPromotions.map(p => p.promotion_id)
      }
    },
    formatDiscountType(type) {
      const types = {
        'percentage': 'Percentage',
        'fixed': 'Fixed Amount',
        'buy_one_get_one': 'BOGO'
      }
      return types[type] || type
    },
    formatDiscountValue(value, type) {
      if (type === 'percentage') {
        return `${value}%`
      } else if (type === 'fixed') {
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
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },
    formatDateTime(dateString) {
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
        'fixed': 'bg-success text-white',
        'buy_one_get_one': 'bg-info text-white'
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
    deletePromotion(promotion) {
      console.log('Delete promotion:', promotion)
      // Implement delete logic
    }
  }
}
</script>

<style scoped>
/* Import colors and buttons CSS */
@import '@/assets/styles/colors.css';
@import '@/assets/styles/buttons.css';

/* Page Container - Theme Aware */
.promotions-page {
  min-height: 100vh;
  background-color: var(--surface-secondary); /* Changed from --neutral-light */
  color: var(--text-secondary);
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Action Bar Styles - Theme Aware */
.action-bar-container {
  background-color: var(--surface-primary); /* Changed from white */
  border: 1px solid var(--border-secondary);
  border-radius: 0.75rem;
  box-shadow: var(--shadow-sm); /* Use semantic shadow */
  overflow: hidden;
  padding: 1rem;
  transition: all 0.3s ease;
}

/* Single Row Layout */
.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

/* Filters Section */
.filters-section {
  flex-shrink: 0;
}

/* Search Toggle Button - Theme Aware */
.search-toggle-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  flex-shrink: 0;
  background-color: var(--surface-primary);
  color: var(--text-secondary);
  border: 1px solid var(--border-primary);
  transition: all 0.2s ease;
}

.search-toggle-btn:hover {
  background-color: var(--state-hover);
  color: var(--text-primary);
}

.search-toggle-btn.active {
  background-color: var(--text-accent);
  border-color: var(--border-accent);
  color: var(--text-inverse);
}

/* Filter Groups - Theme Aware */
.filter-group {
  min-width: 140px;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-tertiary); /* Changed from --tertiary-medium */
  margin-bottom: 0.25rem;
  display: block;
}

/* Form Controls - Theme Aware */
.form-select,
.form-control {
  background-color: var(--input-bg);
  border: 1px solid var(--input-border);
  color: var(--input-text);
  transition: all 0.2s ease;
}

.form-select:focus,
.form-control:focus {
  border-color: var(--border-accent);
  box-shadow: 0 0 0 0.2rem rgba(160, 123, 227, 0.25);
  background-color: var(--input-bg);
  color: var(--input-text);
}

.form-control::placeholder {
  color: var(--input-placeholder);
}

/* Search Container - Theme Aware */
.search-container {
  min-width: 300px;
}

.search-input {
  padding-right: 2.5rem;
  height: calc(1.5em + 0.75rem + 2px);
  background-color: var(--input-bg);
  border: 1px solid var(--input-border);
  color: var(--input-text);
}

.search-input:focus {
  border-color: var(--border-accent);
  box-shadow: 0 0 0 0.2rem rgba(160, 123, 227, 0.25);
}

.search-container .position-relative .btn {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  transition: color 0.2s ease;
}

.search-container .position-relative .btn:hover {
  color: var(--text-secondary);
}

/* Button States - Theme Aware */
.btn {
  background-color: var(--surface-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
  transition: all 0.2s ease;
}

.btn:hover {
  background-color: var(--state-hover);
  color: var(--text-primary);
}

.btn.active {
  background-color: var(--text-accent);
  border-color: var(--border-accent);
  color: var(--text-inverse);
}

/* Specific button types */
.btn-add {
  background-color: var(--status-success);
  color: var(--text-inverse);
  border-color: var(--border-success);
}

.btn-add:hover {
  background-color: var(--success-dark);
  border-color: var(--success-dark);
}

.btn-delete {
  background-color: var(--status-error);
  color: var(--text-inverse);
  border-color: var(--border-error);
}

.btn-delete:hover {
  background-color: var(--error-dark);
  border-color: var(--error-dark);
}

.btn-outline-secondary {
  color: var(--text-tertiary);
  border-color: var(--border-primary);
  background-color: transparent;
}

.btn-outline-secondary:hover {
  color: var(--text-primary);
  background-color: var(--state-hover);
  border-color: var(--border-accent);
}

.btn-outline-primary {
  color: var(--text-accent);
  border-color: var(--border-accent);
  background-color: transparent;
}

.btn-outline-primary:hover {
  color: var(--text-inverse);
  background-color: var(--text-accent);
  border-color: var(--text-accent);
}

.btn-outline-danger {
  color: var(--status-error);
  border-color: var(--border-error);
  background-color: transparent;
}

.btn-outline-danger:hover {
  color: var(--text-inverse);
  background-color: var(--status-error);
  border-color: var(--status-error);
}

/* Table and Badge Styling - Theme Aware */
.table-primary {
  background-color: var(--state-selected) !important;
}

.badge {
  border: 1px solid;
  transition: all 0.3s ease;
}

.badge.bg-primary {
  background-color: var(--text-accent) !important;
  color: var(--text-inverse) !important;
  border-color: var(--text-accent) !important;
}

.badge.bg-success {
  background-color: var(--status-success) !important;
  color: var(--text-inverse) !important;
  border-color: var(--status-success) !important;
}

.badge.bg-info {
  background-color: var(--status-info) !important;
  color: var(--text-inverse) !important;
  border-color: var(--status-info) !important;
}

.badge.bg-danger {
  background-color: var(--status-error) !important;
  color: var(--text-inverse) !important;
  border-color: var(--status-error) !important;
}

.badge.bg-warning {
  background-color: var(--status-warning) !important;
  color: var(--text-primary) !important;
  border-color: var(--status-warning) !important;
}

.badge.bg-secondary {
  background-color: var(--surface-tertiary) !important;
  color: var(--text-primary) !important;
  border-color: var(--border-primary) !important;
}

/* Text Colors - Theme Aware */
.text-tertiary-dark {
  color: var(--text-primary) !important; /* Use primary for main content */
}

.text-tertiary-medium {
  color: var(--text-tertiary) !important;
}

.fw-medium {
  color: var(--text-primary);
}

/* Form Check Controls - Theme Aware */
.form-check-input {
  background-color: var(--input-bg);
  border: 1px solid var(--input-border);
  transition: all 0.2s ease;
}

.form-check-input:focus {
  border-color: var(--border-accent);
  box-shadow: 0 0 0 0.2rem rgba(160, 123, 227, 0.25);
}

.form-check-input:checked {
  background-color: var(--text-accent);
  border-color: var(--text-accent);
}

/* Action Buttons - Theme Aware */
.action-btn {
  width: 24px;
  height: 24px;
  border-radius: 0.375rem;
  border-width: 1.5px;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.action-btn-view {
  color: var(--text-accent);
  border-color: var(--border-accent);
}

.action-btn-view:hover {
  background-color: var(--text-accent);
  color: var(--text-inverse);
}

.action-btn-edit {
  color: var(--text-tertiary);
  border-color: var(--border-primary);
}

.action-btn-edit:hover {
  background-color: var(--state-hover);
  color: var(--text-primary);
}

.action-btn-delete {
  color: var(--status-error);
  border-color: var(--border-error);
}

.action-btn-delete:hover {
  background-color: var(--status-error);
  color: var(--text-inverse);
}

/* Empty State - Theme Aware */
.py-5 {
  color: var(--text-tertiary);
}

.opacity-50 {
  opacity: 0.5;
  color: var(--text-tertiary);
}

/* Responsive Design */
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

/* Add smooth transitions for theme switching */
* {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

/* Disable transitions for reduced motion users */
@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
  }
}
</style>