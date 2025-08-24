<template>
  <div v-if="isVisible" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <div class="header-info">
          <h2 class="mb-2" style="color: var(--tertiary-dark)">{{ title }}</h2>
          <div class="report-meta d-flex flex-wrap gap-3 align-items-center">
            <span class="badge bg-primary">{{ getReportTypeLabel() }}</span>
            <span class="text-muted">{{ data.length }} items</span>
            <span class="text-muted">Generated: {{ formatDateTime(new Date()) }}</span>
          </div>
        </div>
        <div class="header-actions d-flex gap-2">
          <button 
            @click="exportToCSV" 
            class="btn btn-success btn-sm" 
            :disabled="data.length === 0"
          >
            <i class="bi bi-download me-1"></i>
            Export CSV
          </button>
          <button 
            @click="refreshReportData" 
            class="btn btn-primary btn-sm" 
            :disabled="loading"
          >
            <i class="bi bi-arrow-clockwise me-1"></i>
            {{ loading ? 'Loading...' : 'Refresh' }}
          </button>
          <button class="btn-close" @click="hideModal" aria-label="Close"></button>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="error" class="alert alert-danger m-3" role="alert">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
        <button @click="clearError" class="btn-close float-end" aria-label="Close"></button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-muted">Loading report data...</p>
      </div>

      <!-- Report Content -->
      <div v-else-if="data.length > 0" class="report-content">
        <!-- Report Summary -->
        <div class="report-summary mb-4">
          <div class="row g-3">
            <div v-if="reportType === 'low-stock'" class="col-md-6 col-lg-3">
              <div class="card border-danger">
                <div class="card-body text-center">
                  <div class="fs-6 text-muted text-uppercase mb-1">Critical Stock</div>
                  <div class="fs-2 fw-bold text-danger">{{ getCriticalStockCount() }}</div>
                  <div class="small text-muted">Items at 0 stock</div>
                </div>
              </div>
            </div>
            <div v-if="reportType === 'low-stock'" class="col-md-6 col-lg-3">
              <div class="card border-warning">
                <div class="card-body text-center">
                  <div class="fs-6 text-muted text-uppercase mb-1">Low Stock</div>
                  <div class="fs-2 fw-bold text-warning">{{ getLowStockCount() }}</div>
                  <div class="small text-muted">Below threshold</div>
                </div>
              </div>
            </div>
            <div v-if="reportType === 'expiring'" class="col-md-6 col-lg-3">
              <div class="card border-danger">
                <div class="card-body text-center">
                  <div class="fs-6 text-muted text-uppercase mb-1">Expired</div>
                  <div class="fs-2 fw-bold text-danger">{{ getExpiredCount() }}</div>
                  <div class="small text-muted">Already expired</div>
                </div>
              </div>
            </div>
            <div v-if="reportType === 'expiring'" class="col-md-6 col-lg-3">
              <div class="card border-warning">
                <div class="card-body text-center">
                  <div class="fs-6 text-muted text-uppercase mb-1">Expiring Soon</div>
                  <div class="fs-2 fw-bold text-warning">{{ getExpiringSoonCount() }}</div>
                  <div class="small text-muted">Within 7 days</div>
                </div>
              </div>
            </div>
            <div class="col-md-6 col-lg-3">
              <div class="card" style="border-color: var(--primary)">
                <div class="card-body text-center">
                  <div class="fs-6 text-muted text-uppercase mb-1">Total Value</div>
                  <div class="fs-2 fw-bold" style="color: var(--primary)">₱{{ getTotalValue() }}</div>
                  <div class="small text-muted">At cost price</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Filters -->
        <div class="report-filters bg-light p-3 rounded mb-4">
          <div class="row g-3">
            <div class="col-md-4">
              <label for="categoryFilter" class="form-label">Filter by Category:</label>
              <select 
                id="categoryFilter" 
                v-model="filters.category" 
                @change="applyFilters"
                class="form-select"
              >
                <option value="">All Categories</option>
                <option value="noodles">Noodles</option>
                <option value="drinks">Drinks</option>
                <option value="toppings">Toppings</option>
              </select>
            </div>
            <div class="col-md-4">
              <label for="severityFilter" class="form-label">Filter by Severity:</label>
              <select 
                id="severityFilter" 
                v-model="filters.severity" 
                @change="applyFilters"
                class="form-select"
              >
                <option value="">All Severities</option>
                <option value="critical">Critical</option>
                <option value="warning">Warning</option>
                <option value="normal">Normal</option>
              </select>
            </div>
            <div class="col-md-4">
              <label for="searchFilter" class="form-label">Search:</label>
              <input 
                id="searchFilter"
                v-model="filters.search"
                @input="applyFilters"
                type="text" 
                placeholder="Search products..."
                class="form-control"
              />
            </div>
          </div>
        </div>

        <!-- Report Table -->
        <div class="table-responsive mb-4">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th class="sortable" @click="sortBy('product_name')" style="cursor: pointer;">
                  Product Name
                  <i v-if="sortField === 'product_name'" 
                     :class="['bi', sortOrder === 'asc' ? 'bi-sort-up' : 'bi-sort-down']"
                     class="ms-1"></i>
                </th>
                <th class="sortable" @click="sortBy('SKU')" style="cursor: pointer;">
                  SKU
                  <i v-if="sortField === 'SKU'" 
                     :class="['bi', sortOrder === 'asc' ? 'bi-sort-up' : 'bi-sort-down']"
                     class="ms-1"></i>
                </th>
                <th>Category</th>
                <th class="sortable" @click="sortBy('stock')" style="cursor: pointer;">
                  Current Stock
                  <i v-if="sortField === 'stock'" 
                     :class="['bi', sortOrder === 'asc' ? 'bi-sort-up' : 'bi-sort-down']"
                     class="ms-1"></i>
                </th>
                <th v-if="reportType === 'low-stock'">Threshold</th>
                <th v-if="reportType === 'low-stock'">Shortage</th>
                <th v-if="reportType === 'expiring'" class="sortable" @click="sortBy('expiry_date')" style="cursor: pointer;">
                  Expiry Date
                  <i v-if="sortField === 'expiry_date'" 
                     :class="['bi', sortOrder === 'asc' ? 'bi-sort-up' : 'bi-sort-down']"
                     class="ms-1"></i>
                </th>
                <th v-if="reportType === 'expiring'">Days Until Expiry</th>
                <th>Value Impact</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in paginatedData" :key="item._id" :class="getTableRowClass(item)">
                <td>
                  <div class="d-flex flex-column">
                    <span class="fw-medium" style="color: var(--tertiary-dark)">{{ item.product_name }}</span>
                    <small class="text-muted">{{ item.unit || 'N/A' }}</small>
                  </div>
                </td>
                <td><code class="text-primary">{{ item.SKU }}</code></td>
                <td>
                  <span :class="getCategoryBadgeClass(item.category_id)">
                    {{ getCategoryName(item.category_id) }}
                  </span>
                </td>
                <td>
                  <span :class="getBootstrapStockClass(item)">{{ item.stock }}</span>
                </td>
                <td v-if="reportType === 'low-stock'">{{ item.low_stock_threshold }}</td>
                <td v-if="reportType === 'low-stock'">
                  <span class="text-danger fw-bold">{{ getShortage(item) }}</span>
                </td>
                <td v-if="reportType === 'expiring'">
                  <span :class="getBootstrapExpiryClass(item.expiry_date)">
                    {{ formatDate(item.expiry_date) }}
                  </span>
                </td>
                <td v-if="reportType === 'expiring'">
                  <span :class="getBootstrapDaysClass(item.expiry_date)">
                    {{ getDaysUntilExpiry(item.expiry_date) }}
                  </span>
                </td>
                <td class="fw-medium">₱{{ getItemValue(item) }}</td>
                <td>
                  <div class="btn-group btn-group-sm" role="group">
                    <button 
                      @click="$emit('view-product', item)" 
                      class="btn btn-outline-primary"
                      title="View Details"
                    >
                      <i class="bi bi-eye"></i>
                    </button>
                    <button 
                      @click="$emit('edit-product', item)" 
                      class="btn btn-outline-secondary"
                      title="Edit Product"
                    >
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button 
                      @click="$emit('restock-product', item)" 
                      class="btn btn-outline-success"
                      title="Update Stock"
                    >
                      <i class="bi bi-box"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <nav v-if="totalPages > 1" aria-label="Report pagination">
          <ul class="pagination justify-content-center">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <button class="page-link" @click="currentPage = 1" :disabled="currentPage === 1">
                First
              </button>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <button class="page-link" @click="currentPage--" :disabled="currentPage === 1">
                Previous
              </button>
            </li>
            <li class="page-item active">
              <span class="page-link">
                Page {{ currentPage }} of {{ totalPages }} ({{ processedData.length }} items)
              </span>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <button class="page-link" @click="currentPage++" :disabled="currentPage === totalPages">
                Next
              </button>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <button class="page-link" @click="currentPage = totalPages" :disabled="currentPage === totalPages">
                Last
              </button>
            </li>
          </ul>
        </nav>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state text-center py-5">
        <div class="display-1 mb-3">📊</div>
        <h3 class="mb-3" style="color: var(--tertiary-dark)">No {{ reportType === 'low-stock' ? 'Low Stock' : 'Expiring' }} Items Found</h3>
        <p class="text-muted mb-4">
          {{ reportType === 'low-stock' 
            ? 'All products are currently above their low stock thresholds.' 
            : 'No products are expiring in the specified timeframe.' 
          }}
        </p>
        <button @click="refreshReportData" class="btn btn-primary">
          <i class="bi bi-arrow-clockwise me-2"></i>
          Refresh Report
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { useReportsModal } from '@/composables/ui/products/useReportsModal'

export default {
  name: 'ReportsModal',
  emits: ['view-product', 'edit-product', 'restock-product'],
  setup(props, { emit }) {
    const {
      // State
      isVisible,
      loading,
      data,
      reportType,
      title,
      error,
      filters,
      sortField,
      sortOrder,
      currentPage,
      
      // Computed
      processedData,
      totalPages,
      paginatedData,
      
      // Actions
      hideModal,
      clearError,
      applyFilters,
      sortBy,
      refreshReportData,
      exportToCSV,
      
      // Summary Methods
      getCriticalStockCount,
      getLowStockCount,
      getExpiredCount,
      getExpiringSoonCount,
      getTotalValue,
      
      // Utility Methods
      getReportTypeLabel,
      getItemSeverity,
      getShortage,
      getItemValue,
      getCategoryName,
      formatDate,
      formatDateTime,
      getDaysUntilExpiry
    } = useReportsModal()

    const handleOverlayClick = () => {
      hideModal()
    }

    // Bootstrap-specific utility methods
    const getTableRowClass = (item) => {
      const severity = getItemSeverity(item)
      switch (severity) {
        case 'critical':
          return 'table-danger'
        case 'warning':
          return 'table-warning'
        default:
          return ''
      }
    }

    const getCategoryBadgeClass = (categoryId) => {
      const baseClass = 'badge'
      switch (categoryId?.toLowerCase()) {
        case 'noodles':
          return `${baseClass} bg-warning text-dark`
        case 'drinks':
          return `${baseClass} bg-info text-dark`
        case 'toppings':
          return `${baseClass} bg-secondary`
        default:
          return `${baseClass} bg-light text-dark`
      }
    }

    const getBootstrapStockClass = (item) => {
      if (item.stock === 0) return 'text-danger fw-bold'
      if (item.stock <= (item.low_stock_threshold || 0)) return 'text-warning fw-bold'
      return 'text-success fw-bold'
    }

    const getBootstrapExpiryClass = (expiryDate) => {
      if (!expiryDate) return ''
      const today = new Date()
      const expiry = new Date(expiryDate)
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      
      if (daysUntilExpiry < 0) return 'text-danger fw-bold'
      if (daysUntilExpiry <= 7) return 'text-warning fw-bold'
      if (daysUntilExpiry <= 30) return 'text-info'
      return ''
    }

    const getBootstrapDaysClass = (expiryDate) => {
      if (!expiryDate) return ''
      const today = new Date()
      const expiry = new Date(expiryDate)
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      
      if (daysUntilExpiry < 0) return 'text-danger fw-bold'
      if (daysUntilExpiry <= 7) return 'text-warning fw-bold'
      if (daysUntilExpiry <= 30) return 'text-info'
      return 'text-success'
    }

    return {
      // State
      isVisible,
      loading,
      data,
      reportType,
      title,
      error,
      filters,
      sortField,
      sortOrder,
      currentPage,
      
      // Computed
      processedData,
      totalPages,
      paginatedData,
      
      // Actions
      hideModal,
      clearError,
      applyFilters,
      sortBy,
      refreshReportData,
      exportToCSV,
      handleOverlayClick,
      
      // Summary Methods
      getCriticalStockCount,
      getLowStockCount,
      getExpiredCount,
      getExpiringSoonCount,
      getTotalValue,
      
      // Utility Methods
      getReportTypeLabel,
      getShortage,
      getItemValue,
      getCategoryName,
      formatDate,
      formatDateTime,
      getDaysUntilExpiry,
      
      // Bootstrap utility methods
      getTableRowClass,
      getCategoryBadgeClass,
      getBootstrapStockClass,
      getBootstrapExpiryClass,
      getBootstrapDaysClass
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 1200px;
  width: 95%;
  max-height: 90vh;
  overflow: hidden;
  animation: slideIn 0.3s ease;
  display: flex;
  flex-direction: column;
}

@keyframes slideIn {
  from { 
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to { 
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--neutral);
  background: var(--neutral-light);
  border-radius: 12px 12px 0 0;
}

.report-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
}

.sortable:hover {
  background-color: var(--neutral-light) !important;
}

/* Custom scrollbar */
.report-content::-webkit-scrollbar {
  width: 8px;
}

.report-content::-webkit-scrollbar-track {
  background: var(--neutral-light);
  border-radius: 4px;
}

.report-content::-webkit-scrollbar-thumb {
  background: var(--neutral-medium);
  border-radius: 4px;
}

.report-content::-webkit-scrollbar-thumb:hover {
  background: var(--neutral-dark);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .modal-content {
    margin: 0.5rem;
    max-height: calc(100vh - 1rem);
  }

  .modal-header {
    padding: 1rem 1.5rem;
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .header-actions {
    justify-content: space-between !important;
  }

  .report-content {
    padding: 1rem 1.5rem;
  }

  .btn-group {
    flex-direction: column !important;
  }

  .btn-group .btn {
    border-radius: 0.375rem !important;
    margin-bottom: 0.25rem;
  }
}

@media (max-width: 576px) {
  .modal-header {
    padding: 0.75rem 1rem;
  }

  .report-content {
    padding: 0.75rem 1rem;
  }

  .header-actions {
    flex-direction: column !important;
  }
}
</style>