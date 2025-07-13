<template>
  <div class="logs-page">
    <!-- Page Title -->
    <div class="page-header">
      <h1 class="page-title">System Logs</h1>
      <div class="header-actions">
        <button class="btn btn-warning" @click="loadLogs" :disabled="loading">
          <i class="bi bi-arrow-clockwise" :class="{ 'spinning': loading }"></i>
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Filters Section -->
    <div class="filters-section">
      <div class="filter-group">
        <label for="categoryFilter">Filter by Category:</label>
        <select id="categoryFilter" v-model="categoryFilter" @change="applyFilters" :disabled="loading">
          <option value="all">All Categories</option>
          <option value="login">Login</option>
          <option value="logout">Logout</option>
          <option value="session">Session</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="searchFilter">Search User ID:</label>
        <input 
          id="searchFilter" 
          v-model="searchFilter" 
          @input="applyFilters"
          type="text" 
          placeholder="Search specific user ID..."
          :disabled="loading"
        />
      </div>

      <div class="filter-group">
        <label for="pageSize">Records per page:</label>
        <select 
          id="pageSize" 
          v-model="pageSize" 
          @change="changePageSize"
          :disabled="loading"
        >
          <option value="10">10</option>
          <option value="50">50</option>
          <option value="100">100</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && session_logs.length === 0" class="loading-state">
      <div class="spinner-border text-primary"></div>
      <p>Loading session logs...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-state">
      <div class="alert alert-danger text-center" role="alert">
        <i class="bi bi-exclamation-triangle"></i>
        <p class="mb-3">{{ error }}</p>
        <button class="btn btn-primary" @click="loadLogs" :disabled="loading">
          <i class="bi bi-arrow-clockwise"></i>
          {{ loading ? 'Retrying...' : 'Try Again' }}
        </button>
      </div>
    </div>

    <!-- Refresh Progress Indicator -->
    <div v-if="loading && session_logs.length > 0" class="refresh-indicator">
      <div class="alert alert-info d-flex align-items-center" role="alert">
        <div class="spinner-border spinner-border-sm me-2" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        Refreshing logs data...
      </div>
    </div>

    <!-- Table Info -->
    <div v-if="!loading && filteredLogs.length > 0" class="table-info">
      <span>
        Showing {{ startRecord }} to {{ endRecord }} of {{ filteredLogs.length }} entries
        <span v-if="searchFilter" class="filter-indicator">
          (filtered from {{ session_logs.length }} total records)
        </span>
      </span>
    </div>

    <!-- Data Table -->
    <div v-if="!loading || session_logs.length > 0" class="table-container">
      <table class="logs-table">
        <thead>
          <tr>
            <th>Log ID</th>
            <th>User ID</th>
            <th>Ref. ID</th>
            <th>Event Type</th>
            <th>Amount/Qty</th>
            <th>Status</th>
            <th>Timestamp</th>
            <th>Remarks</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="(sessionLog, index) in paginatedLogs" 
            :key="sessionLog.log_id || sessionLog._id || index"
          >
            <td class="log-id-column">{{ sessionLog.log_id }}</td>
            <td class="user-id-column">{{ sessionLog.user_id }}</td>
            <td class="ref-id-column">{{ sessionLog.ref_id }}</td>
            <td class="event-type-column">{{ sessionLog.event_type }}</td>
            <td class="amount-column">{{ getAmountQty(sessionLog) }}</td>
            <td class="status-column">
              <span :class="['status-badge', getStatusClass(sessionLog.status)]">
                {{ sessionLog.status }}
              </span>
            </td>
            <td class="timestamp-column">{{ formatTimestamp(sessionLog.timestamp) }}</td>
            <td class="remarks-column" :title="sessionLog.remarks">{{ sessionLog.remarks }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && filteredLogs.length === 0 && !error" class="empty-state">
      <div class="card">
        <div class="card-body text-center py-5">
          <i class="bi bi-file-text" style="font-size: 3rem; color: #6b7280;"></i>
          <p class="mt-3 mb-3">
            {{ session_logs.length === 0 ? 'No session logs found' : 'No logs match the current filters' }}
          </p>
          <button v-if="session_logs.length === 0" class="btn btn-primary" @click="loadLogs">
            <i class="bi bi-arrow-clockwise"></i>
            Refresh Logs
          </button>
          <div v-else class="d-flex gap-2 justify-content-center">
            <button class="btn btn-secondary" @click="clearFilters">
              <i class="bi bi-funnel"></i>
              Clear Filters
            </button>
            <button class="btn btn-info" @click="loadLogs">
              <i class="bi bi-arrow-clockwise"></i>
              Refresh Data
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination Controls -->
    <div v-if="filteredLogs.length > 0" class="pagination-container">
      <nav aria-label="Logs pagination">
        <ul class="pagination pagination-sm justify-content-center">
          <!-- Previous button -->
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <button 
              class="page-link" 
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage === 1"
            >
              <i class="bi bi-chevron-left"></i> Previous
            </button>
          </li>
          
          <!-- Page numbers -->
          <li 
            v-for="(page, index) in visiblePages" 
            :key="index"
            class="page-item" 
            :class="{ 
              active: page === currentPage,
              disabled: page === '...'
            }"
          >
            <button 
              v-if="page !== '...'"
              class="page-link" 
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
            <span v-else class="page-link">{{ page }}</span>
          </li>
          
          <!-- Next button -->
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <button 
              class="page-link" 
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
            >
              Next <i class="bi bi-chevron-right"></i>
            </button>
          </li>
        </ul>
      </nav>
      
      <!-- Pagination info -->
      <div class="pagination-info">
        <small class="text-muted">
          Page {{ currentPage }} of {{ totalPages }} 
          ({{ filteredLogs.length }} total records)
        </small>
      </div>
    </div>
  </div>
</template>

<script>
import APILogs from '@/services/apiLogs'

export default {
  name: 'SystemLogs',
  data() {
    return {
      session_logs: [],
      filteredLogs: [],
      loading: false,
      error: null,
      
      // Filters
      categoryFilter: 'all',
      searchFilter: '',
      
      // Pagination data
      currentPage: 1,
      pageSize: 10
    }
  },
  
  computed: {
    // Calculate total pages based on filtered logs
    totalPages() {
      return Math.ceil(this.filteredLogs.length / this.pageSize)
    },
    
    // Get logs for current page
    paginatedLogs() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.filteredLogs.slice(start, end)
    },
    
    // Calculate record numbers for display
    startRecord() {
      return this.filteredLogs.length === 0 ? 0 : (this.currentPage - 1) * this.pageSize + 1
    },
    
    endRecord() {
      const end = this.currentPage * this.pageSize
      return end > this.filteredLogs.length ? this.filteredLogs.length : end
    },
    
    // Visible page numbers for pagination
    visiblePages() {
      const pages = []
      const delta = 2 // Show 2 pages on each side of current page
      
      // For small number of total pages, show all
      if (this.totalPages <= 7) {
        for (let i = 1; i <= this.totalPages; i++) {
          pages.push(i)
        }
        return pages
      }
      
      // Always include first page
      pages.push(1)
      
      // Calculate start and end of middle range
      const start = Math.max(2, this.currentPage - delta)
      const end = Math.min(this.totalPages - 1, this.currentPage + delta)
      
      // Add gap if needed between 1 and start
      if (start > 2) {
        pages.push('...')
      }
      
      // Add middle range (excluding first and last page)
      for (let i = start; i <= end; i++) {
        if (i !== 1 && i !== this.totalPages) {
          pages.push(i)
        }
      }
      
      // Add gap if needed between end and last page
      if (end < this.totalPages - 1) {
        pages.push('...')
      }
      
      // Always include last page (if not page 1)
      if (this.totalPages > 1) {
        pages.push(this.totalPages)
      }
      
      return pages
    }
  },
  
  methods: {
    // ================================================================
    // DATA FETCHING
    // ================================================================
    async loadLogs() {
      this.loading = true
      this.error = null
      
      try {
        console.log("Loading session logs...")
        
        const response = await APILogs.DisplayLogs()
        console.log("API Response:", response)
        
        // Handle different response formats
        if (response && response.success && response.data) {
          this.session_logs = response.data
        } else if (Array.isArray(response)) {
          this.session_logs = response
        } else if (response && response.data) {
          this.session_logs = response.data
        } else {
          this.session_logs = []
        }
        
        // Apply current filters
        this.applyFilters()
        
        // Reset to first page when data loads
        this.currentPage = 1
        
        console.log(`Loaded ${this.session_logs.length} session logs`)
        
      } catch (error) {
        console.error("Error loading session logs:", error)
        this.error = error.message || 'Failed to load session logs'
        this.session_logs = []
        this.filteredLogs = []
      } finally {
        this.loading = false
      }
    },

    // ================================================================
    // FILTER METHODS
    // ================================================================
    applyFilters() {
      console.log('Applying filters:', {
        category: this.categoryFilter,
        search: this.searchFilter
      })
      
      let filtered = [...this.session_logs]
      const originalCount = filtered.length

      // Category filter
      if (this.categoryFilter !== 'all') {
        filtered = filtered.filter(log => {
          const eventType = (log.event_type || '').toLowerCase()
          return eventType.includes(this.categoryFilter.toLowerCase())
        })
      }

      // Search filter (user ID)
      if (this.searchFilter.trim()) {
        const search = this.searchFilter.toLowerCase()
        filtered = filtered.filter(log => 
          (log.user_id || '').toLowerCase().includes(search)
        )
      }

      this.filteredLogs = filtered
      
      // Reset to first page when filters change
      this.currentPage = 1
      
      console.log(`Filters applied: ${originalCount} → ${filtered.length} logs`)
    },

    clearFilters() {
      console.log('Clearing all filters')
      this.categoryFilter = 'all'
      this.searchFilter = ''
      this.applyFilters()
    },

    // ================================================================
    // PAGINATION METHODS
    // ================================================================
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
      }
    },
    
    changePageSize() {
      this.currentPage = 1 // Reset to first page
      console.log(`Page size changed to: ${this.pageSize}`)
    },

    // ================================================================
    // UTILITY METHODS
    // ================================================================
    getAmountQty(sessionLog) {
      const eventType = (sessionLog.event_type || '').toLowerCase()
      
      // If event is "session", return "None"
      if (eventType === 'session' || eventType === 'session complete') {
        return 'None'
      }
      
      // For other events, return the amount_qty or default
      return sessionLog.amount_qty || '-'
    },
    
    getStatusClass(status) {
      const statusLower = (status || '').toLowerCase()
      switch (statusLower) {
        case 'completed':
        case 'success':
          return 'status-success'
        case 'active':
          return 'status-active'
        case 'failed':
        case 'error':
          return 'status-failed'
        default:
          return 'status-default'
      }
    },

    formatTimestamp(timestamp) {
      if (!timestamp) return 'N/A'
      try {
        const date = new Date(timestamp)
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (error) {
        return timestamp
      }
    }
  },
  
  // Watch for page size changes
  watch: {
    pageSize() {
      this.currentPage = 1
    }
  },
  
  // Load data when component mounts
  async mounted() {
    console.log('=== System Logs component mounted ===')
    await this.loadLogs()
  }
}
</script>

<style scoped>
.logs-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  background-color: #f8fafc;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* Enhanced button styles */
.btn {
  padding: 0.5rem 1.25rem;
  border-radius: 0.5rem;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: #e2e8f0;
  color: #475569;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #cbd5e1;
}

.btn-warning {
  background-color: #f59e0b;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background-color: #d97706;
}

.btn-info {
  background-color: #06b6d4;
  color: white;
}

.btn-info:hover:not(:disabled) {
  background-color: #0891b2;
}

/* Spinning icon animation */
.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Enhanced filters section */
.filters-section {
  background: white;
  padding: 1.5rem;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.filter-group select,
.filter-group input {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.filter-group select:focus,
.filter-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.loading-state, .error-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.error-state {
  color: #dc2626;
}

.refresh-indicator {
  margin-bottom: 1rem;
}

.table-info {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 0.75rem 0.75rem 0 0;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.875rem;
  color: #64748b;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.filter-indicator {
  color: #3b82f6;
  font-weight: 500;
}

.table-container {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.logs-table thead {
  background-color: #567cdc;
  color: white;
}

.logs-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.875rem;
  letter-spacing: 0.025em;
}

.logs-table td {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.875rem;
}

.logs-table tbody tr:hover {
  background-color: #f8fafc;
}

/* Column width definitions */
.log-id-column {
  width: 100px;
  font-weight: 500;
  color: #6366f1;
  font-family: monospace;
}

.user-id-column {
  width: 120px;
  font-weight: 500;
  color: #1e293b;
}

.ref-id-column {
  width: 120px;
  color: #64748b;
  font-family: monospace;
}

.event-type-column {
  width: 120px;
  color: #1e293b;
}

.amount-column {
  width: 100px;
  text-align: center;
  color: #1e293b;
}

.status-column {
  width: 100px;
  text-align: center;
}

.timestamp-column {
  width: 150px;
  color: #64748b;
  font-size: 0.8125rem;
}

.remarks-column {
  width: 200px;
  max-width: 200px;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Status badge styles */
.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.status-badge.status-success {
  background-color: #dcfce7;
  color: #166534;
}

.status-badge.status-active {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-badge.status-failed {
  background-color: #fee2e2;
  color: #991b1b;
}

.status-badge.status-default {
  background-color: #f1f5f9;
  color: #475569;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #64748b;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

/* Pagination styles */
.pagination-container {
  background: white;
  padding: 1.5rem;
  border-radius: 0 0 0.75rem 0.75rem;
  border-top: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.pagination {
  margin-bottom: 1rem;
}

.pagination-info {
  text-align: center;
}

.page-link {
  border: 1px solid #e2e8f0;
  color: #567cdc;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

.page-link:hover {
  background-color: #f8fafc;
  border-color: #567cdc;
  color: #567cdc;
}

.page-item.active .page-link {
  background-color: #567cdc;
  border-color: #567cdc;
  color: white;
}

.page-item.disabled .page-link {
  color: #9ca3af;
  background-color: #fff;
  border-color: #e2e8f0;
}

/* Alert styles */
.alert {
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid transparent;
}

.alert-danger {
  background-color: #fef2f2;
  border-color: #fecaca;
  color: #dc2626;
}

.alert-info {
  background-color: #eff6ff;
  border-color: #bfdbfe;
  color: #1d4ed8;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .logs-page {
    padding: 1rem;
  }

  .filters-section {
    grid-template-columns: 1fr;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .logs-table {
    min-width: 900px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .page-title {
    font-size: 1.5rem;
    text-align: center;
  }
  
  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.8125rem;
  }

  .filters-section {
    padding: 1rem;
  }

  .logs-table th,
  .logs-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.8125rem;
  }

  .pagination {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 640px) {
  .header-actions {
    grid-template-columns: 1fr;
    display: grid;
    gap: 0.5rem;
  }

  .btn {
    font-size: 0.75rem;
    padding: 0.5rem 0.75rem;
  }
}
</style>