<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content large-modal" @click.stop>
      <div class="modal-header">
        <div class="header-info">
          <h2>{{ title }}</h2>
          <div class="report-meta">
            <span class="report-type">{{ getReportTypeLabel() }}</span>
            <span class="report-count">{{ data.length }} items</span>
            <span class="report-date">Generated: {{ formatDateTime(new Date()) }}</span>
          </div>
        </div>
        <div class="header-actions">
          <button @click="exportReport" class="btn btn-success" :disabled="data.length === 0">
            Export CSV
          </button>
          <button @click="refreshReport" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Loading...' : 'Refresh' }}
          </button>
          <button class="close-btn" @click="$emit('close')">
            ✕
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading report data...</p>
      </div>

      <!-- Report Content -->
      <div v-else-if="data.length > 0" class="report-content">
        <!-- Report Summary -->
        <div class="report-summary">
          <div class="summary-cards">
            <div class="summary-card" v-if="type === 'low-stock'">
              <div class="card-label">Critical Stock</div>
              <div class="card-value critical">{{ getCriticalStockCount() }}</div>
              <div class="card-subtitle">Items at 0 stock</div>
            </div>
            <div class="summary-card" v-if="type === 'low-stock'">
              <div class="card-label">Low Stock</div>
              <div class="card-value warning">{{ getLowStockCount() }}</div>
              <div class="card-subtitle">Below threshold</div>
            </div>
            <div class="summary-card" v-if="type === 'expiring'">
              <div class="card-label">Expired</div>
              <div class="card-value critical">{{ getExpiredCount() }}</div>
              <div class="card-subtitle">Already expired</div>
            </div>
            <div class="summary-card" v-if="type === 'expiring'">
              <div class="card-label">Expiring Soon</div>
              <div class="card-value warning">{{ getExpiringSoonCount() }}</div>
              <div class="card-subtitle">Within 7 days</div>
            </div>
            <div class="summary-card">
              <div class="card-label">Total Value</div>
              <div class="card-value">₱{{ getTotalValue() }}</div>
              <div class="card-subtitle">At cost price</div>
            </div>
          </div>
        </div>

        <!-- Filters -->
        <div class="report-filters">
          <div class="filter-group">
            <label for="categoryFilter">Filter by Category:</label>
            <select id="categoryFilter" v-model="filters.category" @change="applyFilters">
              <option value="">All Categories</option>
              <option value="noodles">Noodles</option>
              <option value="drinks">Drinks</option>
              <option value="toppings">Toppings</option>
            </select>
          </div>
          <div class="filter-group">
            <label for="severityFilter">Filter by Severity:</label>
            <select id="severityFilter" v-model="filters.severity" @change="applyFilters">
              <option value="">All Severities</option>
              <option value="critical">Critical</option>
              <option value="warning">Warning</option>
              <option value="normal">Normal</option>
            </select>
          </div>
          <div class="filter-group">
            <label for="searchFilter">Search:</label>
            <input 
              id="searchFilter"
              v-model="filters.search"
              @input="applyFilters"
              type="text" 
              placeholder="Search products..."
            />
          </div>
        </div>

        <!-- Report Table -->
        <div class="report-table-container">
          <table class="report-table">
            <thead>
              <tr>
                <th class="sortable" @click="sortBy('product_name')">
                  Product Name
                  <span class="sort-indicator" v-if="sortField === 'product_name'">
                    {{ sortOrder === 'asc' ? '↑' : '↓' }}
                  </span>
                </th>
                <th class="sortable" @click="sortBy('SKU')">
                  SKU
                  <span class="sort-indicator" v-if="sortField === 'SKU'">
                    {{ sortOrder === 'asc' ? '↑' : '↓' }}
                  </span>
                </th>
                <th>Category</th>
                <th class="sortable" @click="sortBy('stock')">
                  Current Stock
                  <span class="sort-indicator" v-if="sortField === 'stock'">
                    {{ sortOrder === 'asc' ? '↑' : '↓' }}
                  </span>
                </th>
                <th v-if="type === 'low-stock'">Threshold</th>
                <th v-if="type === 'low-stock'">Shortage</th>
                <th v-if="type === 'expiring'" class="sortable" @click="sortBy('expiry_date')">
                  Expiry Date
                  <span class="sort-indicator" v-if="sortField === 'expiry_date'">
                    {{ sortOrder === 'asc' ? '↑' : '↓' }}
                  </span>
                </th>
                <th v-if="type === 'expiring'">Days Until Expiry</th>
                <th>Value Impact</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in paginatedData" :key="item._id" :class="getRowClass(item)">
                <td class="product-cell">
                  <div class="product-info">
                    <span class="product-name">{{ item.product_name }}</span>
                    <span class="product-unit">{{ item.unit || 'N/A' }}</span>
                  </div>
                </td>
                <td class="sku-cell">{{ item.SKU }}</td>
                <td class="category-cell">
                  <span :class="['category-badge', `category-${getCategorySlug(item.category_id)}`]">
                    {{ getCategoryName(item.category_id) }}
                  </span>
                </td>
                <td class="stock-cell">
                  <span :class="getStockClass(item)">{{ item.stock }}</span>
                </td>
                <td v-if="type === 'low-stock'" class="threshold-cell">{{ item.low_stock_threshold }}</td>
                <td v-if="type === 'low-stock'" class="shortage-cell">
                  <span class="shortage-value">{{ getShortage(item) }}</span>
                </td>
                <td v-if="type === 'expiring'" class="expiry-cell">
                  <span :class="getExpiryClass(item.expiry_date)">
                    {{ formatDate(item.expiry_date) }}
                  </span>
                </td>
                <td v-if="type === 'expiring'" class="days-cell">
                  <span :class="getDaysClass(item.expiry_date)">
                    {{ getDaysUntilExpiry(item.expiry_date) }}
                  </span>
                </td>
                <td class="value-cell">₱{{ getItemValue(item) }}</td>
                <td class="actions-cell">
                  <div class="action-buttons">
                    <button @click="$emit('view-product', item)" class="action-btn view" title="View Details">
                      👁️
                    </button>
                    <button @click="$emit('edit-product', item)" class="action-btn edit" title="Edit Product">
                      ✏️
                    </button>
                    <button @click="$emit('restock-product', item)" class="action-btn restock" title="Update Stock">
                      📦
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination">
          <button 
            @click="currentPage = 1" 
            :disabled="currentPage === 1"
            class="btn btn-sm"
          >
            First
          </button>
          <button 
            @click="currentPage--" 
            :disabled="currentPage === 1"
            class="btn btn-sm"
          >
            Previous
          </button>
          <span class="page-info">
            Page {{ currentPage }} of {{ totalPages }} ({{ processedData.length }} items)
          </span>
          <button 
            @click="currentPage++" 
            :disabled="currentPage === totalPages"
            class="btn btn-sm"
          >
            Next
          </button>
          <button 
            @click="currentPage = totalPages" 
            :disabled="currentPage === totalPages"
            class="btn btn-sm"
          >
            Last
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">📊</div>
        <h3>No {{ type === 'low-stock' ? 'Low Stock' : 'Expiring' }} Items Found</h3>
        <p>
          {{ type === 'low-stock' 
            ? 'All products are currently above their low stock thresholds.' 
            : 'No products are expiring in the specified timeframe.' 
          }}
        </p>
        <button @click="refreshReport" class="btn btn-primary">
          <span class="icon">🔄</span>
          Refresh Report
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ReportsModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    type: {
      type: String, // 'low-stock' or 'expiring'
      required: true
    },
    title: {
      type: String,
      required: true
    },
    data: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'export', 'refresh', 'view-product', 'edit-product', 'restock-product'],
  data() {
    return {
      filters: {
        category: '',
        severity: '',
        search: ''
      },
      sortField: '',
      sortOrder: 'asc',
      currentPage: 1,
      itemsPerPage: 20
    }
  },
  computed: {
    processedData() {
      let filtered = [...this.data]

      // Category filter
      if (this.filters.category) {
        filtered = filtered.filter(item => item.category_id === this.filters.category)
      }

      // Severity filter
      if (this.filters.severity) {
        filtered = filtered.filter(item => this.getItemSeverity(item) === this.filters.severity)
      }

      // Search filter
      if (this.filters.search) {
        const search = this.filters.search.toLowerCase()
        filtered = filtered.filter(item => 
          item.product_name?.toLowerCase().includes(search) ||
          item.SKU?.toLowerCase().includes(search)
        )
      }

      // Apply sorting
      if (this.sortField) {
        filtered.sort((a, b) => {
          let aVal = a[this.sortField]
          let bVal = b[this.sortField]
          
          if (this.sortField === 'expiry_date') {
            aVal = new Date(aVal)
            bVal = new Date(bVal)
          }
          
          if (aVal < bVal) return this.sortOrder === 'asc' ? -1 : 1
          if (aVal > bVal) return this.sortOrder === 'asc' ? 1 : -1
          return 0
        })
      }

      return filtered
    },
    totalPages() {
      return Math.ceil(this.processedData.length / this.itemsPerPage)
    },
    paginatedData() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.processedData.slice(start, end)
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        this.resetFilters()
      }
    },
    data: {
      handler() {
        this.currentPage = 1
      },
      deep: true
    }
  },
  methods: {
    handleOverlayClick() {
      this.$emit('close')
    },
    resetFilters() {
      this.filters = {
        category: '',
        severity: '',
        search: ''
      }
      this.sortField = ''
      this.sortOrder = 'asc'
      this.currentPage = 1
    },
    applyFilters() {
      this.currentPage = 1
    },
    sortBy(field) {
      if (this.sortField === field) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortField = field
        this.sortOrder = 'asc'
      }
    },
    exportReport() {
      const reportData = {
        type: this.type,
        title: this.title,
        data: this.processedData,
        filters: this.filters,
        generatedAt: new Date()
      }
      this.$emit('export', reportData)
    },
    refreshReport() {
      this.$emit('refresh')
    },
    getReportTypeLabel() {
      return this.type === 'low-stock' ? 'Inventory Alert' : 'Expiry Alert'
    },
    getCriticalStockCount() {
      return this.data.filter(item => item.stock === 0).length
    },
    getLowStockCount() {
      return this.data.filter(item => item.stock > 0 && item.stock <= (item.low_stock_threshold || 0)).length
    },
    getExpiredCount() {
      return this.data.filter(item => {
        if (!item.expiry_date) return false
        const expiry = new Date(item.expiry_date)
        return expiry < new Date()
      }).length
    },
    getExpiringSoonCount() {
      return this.data.filter(item => {
        if (!item.expiry_date) return false
        const expiry = new Date(item.expiry_date)
        const today = new Date()
        const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
        return daysUntilExpiry >= 0 && daysUntilExpiry <= 7
      }).length
    },
    getTotalValue() {
      const total = this.data.reduce((sum, item) => {
        return sum + (item.stock * (item.cost_price || 0))
      }, 0)
      return total.toFixed(2)
    },
    getItemSeverity(item) {
      if (this.type === 'low-stock') {
        if (item.stock === 0) return 'critical'
        if (item.stock <= (item.low_stock_threshold || 0)) return 'warning'
        return 'normal'
      } else {
        if (!item.expiry_date) return 'normal'
        const expiry = new Date(item.expiry_date)
        const today = new Date()
        const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
        
        if (daysUntilExpiry < 0) return 'critical'
        if (daysUntilExpiry <= 7) return 'warning'
        return 'normal'
      }
    },
    getRowClass(item) {
      const severity = this.getItemSeverity(item)
      return `severity-${severity}`
    },
    getShortage(item) {
      return Math.max(0, (item.low_stock_threshold || 0) - item.stock)
    },
    getItemValue(item) {
      const value = item.stock * (item.cost_price || 0)
      return value.toFixed(2)
    },
    getCategoryName(categoryId) {
      const categories = {
        'noodles': 'Noodles',
        'drinks': 'Drinks',
        'toppings': 'Toppings'
      }
      return categories[categoryId] || categoryId || 'Unknown'
    },
    getCategorySlug(categoryId) {
      return categoryId?.toLowerCase().replace(/\s+/g, '-') || 'unknown'
    },
    getStockClass(item) {
      if (item.stock === 0) return 'stock-critical'
      if (item.stock <= (item.low_stock_threshold || 0)) return 'stock-warning'
      return 'stock-normal'
    },
    getExpiryClass(expiryDate) {
      if (!expiryDate) return ''
      const today = new Date()
      const expiry = new Date(expiryDate)
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      
      if (daysUntilExpiry < 0) return 'expired'
      if (daysUntilExpiry <= 7) return 'expiring-soon'
      if (daysUntilExpiry <= 30) return 'expiring-month'
      return ''
    },
    getDaysClass(expiryDate) {
      if (!expiryDate) return ''
      const today = new Date()
      const expiry = new Date(expiryDate)
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      
      if (daysUntilExpiry < 0) return 'days-expired'
      if (daysUntilExpiry <= 7) return 'days-critical'
      if (daysUntilExpiry <= 30) return 'days-warning'
      return 'days-normal'
    },
    getDaysUntilExpiry(expiryDate) {
      if (!expiryDate) return 'N/A'
      
      const today = new Date()
      const expiry = new Date(expiryDate)
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      
      if (daysUntilExpiry < 0) return `${Math.abs(daysUntilExpiry)} days ago`
      if (daysUntilExpiry === 0) return 'Today'
      if (daysUntilExpiry === 1) return 'Tomorrow'
      return `${daysUntilExpiry} days`
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        })
      } catch (error) {
        console.error('Error formatting date:', error)
        return 'Invalid Date'
      }
    },
    formatDateTime(date) {
      try {
        return date.toLocaleString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (error) {
        console.error('Error formatting datetime:', error)
        return 'Invalid Date'
      }
    }
  },
  mounted() {
    this.handleEscape = (e) => {
      if (e.key === 'Escape' && this.show && !this.loading) {
        this.$emit('close')
      }
    }
    
    document.addEventListener('keydown', this.handleEscape)
  },

  beforeUnmount() {
    if (this.handleEscape) {
      document.removeEventListener('keydown', this.handleEscape)
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
  border-bottom: 1px solid #e5e7eb;
  background: #f8fafc;
  border-radius: 12px 12px 0 0;
}

.header-info h2 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.report-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
  flex-wrap: wrap;
}

.report-type {
  background: #e0e7ff;
  color: #5b21b6;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0.25rem;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background-color: #e5e7eb;
  color: #374151;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #6b7280;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.report-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
}

.report-summary {
  margin-bottom: 2rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.summary-card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.75rem;
  border: 2px solid #e5e7eb;
  text-align: center;
}

.card-label {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.card-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.card-value.critical {
  color: #dc2626;
}

.card-value.warning {
  color: #d97706;
}

.card-subtitle {
  font-size: 0.75rem;
  color: #6b7280;
}

.report-filters {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 0.75rem;
  margin-bottom: 1.5rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.filter-group select,
.filter-group input {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
}

.report-table-container {
  overflow-x: auto;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
  margin-bottom: 1.5rem;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.report-table th {
  background: #f9fafb;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
}

.report-table th.sortable {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.report-table th.sortable:hover {
  background: #f3f4f6;
}

.sort-indicator {
  margin-left: 0.5rem;
  color: #3b82f6;
}

.report-table td {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: middle;
}

.report-table tbody tr:hover {
  background: #f9fafb;
}

.report-table tbody tr.severity-critical {
  background: #fef2f2;
}

.report-table tbody tr.severity-warning {
  background: #fffbeb;
}

.product-cell {
  min-width: 200px;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.product-name {
  font-weight: 500;
  color: #1f2937;
}

.product-unit {
  font-size: 0.75rem;
  color: #6b7280;
}

.sku-cell {
  font-family: monospace;
  font-size: 0.875rem;
  color: #6366f1;
}

.category-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.category-badge.category-noodles {
  background: #fef3c7;
  color: #92400e;
}

.category-badge.category-drinks {
  background: #dbeafe;
  color: #1e40af;
}

.category-badge.category-toppings {
  background: #e0e7ff;
  color: #5b21b6;
}

.stock-cell {
  font-weight: 600;
}

.stock-critical {
  color: #dc2626;
}

.stock-warning {
  color: #d97706;
}

.stock-normal {
  color: #059669;
}

.shortage-value {
  color: #dc2626;
  font-weight: 600;
}

.expiry-cell,
.days-cell {
  font-size: 0.875rem;
}

.expired,
.days-expired {
  color: #dc2626;
  font-weight: 600;
}

.expiring-soon,
.days-critical {
  color: #ea580c;
  font-weight: 600;
}

.expiring-month,
.days-warning {
  color: #d97706;
  font-weight: 500;
}

.days-normal {
  color: #059669;
}

.value-cell {
  font-weight: 500;
  text-align: right;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
  font-size: 1rem;
}

.action-btn:hover {
  background-color: #f3f4f6;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
}

.page-info {
  font-size: 0.875rem;
  color: #6b7280;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1.25rem;
}

.empty-state p {
  color: #6b7280;
  margin-bottom: 1.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn .icon {
  font-size: 1rem;
}

/* Responsive Design */
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
    justify-content: space-between;
  }

  .report-content {
    padding: 1rem 1.5rem;
  }

  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .report-filters {
    grid-template-columns: 1fr;
  }

  .report-table {
    font-size: 0.875rem;
  }

  .report-table th,
  .report-table td {
    padding: 0.75rem 0.5rem;
  }

  .pagination {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .action-buttons {
    flex-direction: column;
    gap: 0.125rem;
  }
}

@media (max-width: 480px) {
  .modal-header {
    padding: 0.75rem 1rem;
  }

  .report-content {
    padding: 0.75rem 1rem;
  }

  .summary-cards {
    grid-template-columns: 1fr;
  }

  .report-meta {
    flex-direction: column;
    gap: 0.5rem;
  }

  .header-actions {
    flex-direction: column;
  }
}

/* Custom scrollbar */
.report-content::-webkit-scrollbar {
  width: 8px;
}

.report-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.report-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.report-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>