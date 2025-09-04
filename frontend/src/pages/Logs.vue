<template>
  <div class="logs-page">
    <!-- Page Title -->
    <div class="page-header">
      <h1 class="page-title">System Logs</h1>
      <div class="header-actions">
        <!-- Auto-refresh status and controls in one line -->
        <div class="auto-refresh-status">
          <i class="bi bi-arrow-repeat text-success" :class="{ 'spinning': loading }"></i>
          <span class="status-text">
            <span v-if="autoRefreshEnabled">Updates in {{ countdown }}s</span>
            <span v-else>Auto-refresh disabled</span>
          </span>
          
          <!-- Toggle button -->
          <button 
            class="btn btn-sm"
            :class="autoRefreshEnabled ? 'btn-outline-secondary' : 'btn-outline-success'"
            @click="toggleAutoRefresh"
          >
            {{ autoRefreshEnabled ? 'Disable' : 'Enable' }}
          </button>
        </div>
        
        <!-- Connection health indicator -->
        <div class="connection-indicator" :class="getConnectionStatus()">
          <i :class="getConnectionIcon()"></i>
          <span class="connection-text">{{ getConnectionText() }}</span>
        </div>
        
        <!-- Hidden/Emergency Refresh - Only show if error or connection lost -->
        <button 
          v-if="error || connectionLost" 
          class="btn btn-warning" 
          @click="emergencyReconnect"
          :disabled="loading"
        >
          <i class="bi bi-arrow-clockwise" :class="{ 'spinning': loading }"></i>
          {{ loading ? 'Reconnecting...' : 'Reconnect' }}
        </button>
      </div>
    </div>

    <!-- Filters Section -->
    <div class="filters-section">
      <div class="filter-group">
        <label for="categoryFilter">Filter by Category:</label>
        <select id="categoryFilter" v-model="categoryFilter" @change="handleFilterChange" :disabled="loading">
          <option value="all">All Categories</option>
          <option value="session">Sessions</option>
          <option value="login">Login</option>
          <option value="logout">Logout</option>
          <option value="category">Categories</option>
          <option value="product">Products</option>
          <option value="customer">Customers</option>
          <option value="user">Users</option>
          <option value="create">Create Actions</option>
          <option value="update">Update Actions</option>
          <option value="delete">Delete Actions</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="searchFilter">Search User ID:</label>
        <input 
          id="searchFilter" 
          v-model="searchFilter" 
          @input="handleFilterChange"
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
          @change="handlePageSizeChange"
          :disabled="loading"
        >
          <option value="10">10</option>
          <option value="25">25</option>
          <option value="50">50</option>
          <option value="100">100</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && session_logs.length === 0" class="loading-state">
      <div class="spinner-border text-accent"></div>
      <p class="text-secondary">Loading session logs...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-state">
      <div class="alert alert-danger text-center" role="alert">
        <i class="bi bi-exclamation-triangle"></i>
        <p class="mb-3">{{ error }}</p>
        <button class="btn btn-submit" @click="loadLogs" :disabled="loading">
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
    <div v-if="!loading && paginatedLogs.length > 0" class="table-info">
      <span>
        Showing positions {{ startRecord }} to {{ endRecord }} of {{ filteredLogs.length }} entries
        <span v-if="hasActiveFilters" class="filter-indicator">
          (filtered from {{ totalLogsCount }} total records)
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
            <th style="text-align: center;">Amount/Qty</th>
            <th style="text-align: center;">Status</th>
            <th>Timestamp</th>
            <th>Remarks</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="sessionLog in paginatedLogs" 
            :key="sessionLog.log_id || sessionLog._id"
            :class="{ 'new-entry': isNewEntry(sessionLog) }"
          >
            <td class="log-id-column">
              <span class="position-number" :class="sessionLog.logType">{{ sessionLog.formattedLogId }}</span>
            </td>
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
    <div v-if="!loading && paginatedLogs.length === 0 && !error" class="empty-state">
      <div class="card">
        <div class="card-body text-center py-5">
          <i class="bi bi-file-text empty-state-icon"></i>
          <p class="mt-3 mb-3 text-tertiary">
            {{ session_logs.length === 0 ? 'No session logs found' : 'No logs match the current filters' }}
          </p>
          <button v-if="session_logs.length === 0" class="btn btn-submit" @click="loadLogs">
            <i class="bi bi-arrow-clockwise"></i>
            Refresh Logs
          </button>
          <div v-else class="d-flex gap-2 justify-content-center">
            <button class="btn btn-cancel" @click="clearFilters">
              <i class="bi bi-funnel"></i>
              Clear Filters
            </button>
            <button class="btn btn-refresh" @click="loadLogs">
              <i class="bi bi-arrow-clockwise"></i>
              Refresh Data
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination Controls -->
    <div v-if="totalPages > 1" class="pagination-container">
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
        <small class="text-tertiary">
          Page {{ currentPage }} of {{ totalPages }} 
          ({{ filteredLogs.length }} filtered records out of {{ totalLogsCount }} total)
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
      loading: false,
      error: null,
      
      // Filters
      categoryFilter: 'all',
      searchFilter: '',
      
      // Pagination data
      currentPage: 1,
      pageSize: 25,
      
      // Auto-refresh functionality
      autoRefreshEnabled: true,
      autoRefreshInterval: 30000,
      baseRefreshInterval: 30000,
      autoRefreshTimer: null,
      countdown: 30,
      countdownTimer: null,
      
      // Connection health tracking
      connectionLost: false,
      consecutiveErrors: 0,
      lastSuccessfulLoad: null,
      
      // Smart refresh rate tracking
      recentActivity: [],
      activityCheckInterval: 60000,
      
      // Performance optimizations
      filterDebounceTimer: null,
      lastLoadTime: null,
      newEntryIds: new Set(),
      
      // Memoization cache
      memoizedFilters: {
        categoryFilter: 'all',
        searchFilter: '',
        result: []
      }
    }
  },
  
  computed: {
    // Memoized filtered logs for better performance
    filteredLogs() {
      if (
        this.memoizedFilters.categoryFilter === this.categoryFilter &&
        this.memoizedFilters.searchFilter === this.searchFilter &&
        this.memoizedFilters.result.length > 0
      ) {
        return this.memoizedFilters.result
      }
      
      let filtered = [...this.session_logs]
      
      if (this.categoryFilter !== 'all') {
        filtered = filtered.filter(log => {
          const eventType = (log.event_type || '').toLowerCase()
          return eventType.includes(this.categoryFilter.toLowerCase())
        })
      }

      if (this.searchFilter.trim()) {
        const search = this.searchFilter.toLowerCase()
        filtered = filtered.filter(log => 
          (log.user_id || '').toLowerCase().includes(search)
        )
      }
      
      filtered.sort((a, b) => {
        const dateA = new Date(a.timestamp || 0)
        const dateB = new Date(b.timestamp || 0)
        return dateB - dateA
      })
      
      this.memoizedFilters = {
        categoryFilter: this.categoryFilter,
        searchFilter: this.searchFilter,
        result: filtered
      }
      
      return filtered
    },
    
    totalPages() {
      return Math.ceil(this.filteredLogs.length / this.pageSize)
    },

    paginatedLogs() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      const logs = this.filteredLogs.slice(start, end)
      
      return logs.map((log, index) => {
        const position = start + index + 1;
        const logType = this.getLogType(log);
        
        return {
          ...log,
          positionNumber: position,
          logType: logType,
          formattedLogId: this.getFormattedLogId(log, position)
        }
      })
    },
    
    startRecord() {
      return this.filteredLogs.length === 0 ? 0 : (this.currentPage - 1) * this.pageSize + 1
    },
    
    endRecord() {
      const end = this.currentPage * this.pageSize
      return end > this.filteredLogs.length ? this.filteredLogs.length : end
    },
    
    totalLogsCount() {
      return this.session_logs.length
    },

    hasActiveFilters() {
      return this.categoryFilter !== 'all' || this.searchFilter.trim() !== ''
    },
    
    visiblePages() {
      const pages = []
      const delta = 2
      
      if (this.totalPages <= 7) {
        for (let i = 1; i <= this.totalPages; i++) {
          pages.push(i)
        }
        return pages
      }
      
      pages.push(1)
      
      const start = Math.max(2, this.currentPage - delta)
      const end = Math.min(this.totalPages - 1, this.currentPage + delta)
      
      if (start > 2) pages.push('...')
      
      for (let i = start; i <= end; i++) {
        if (i !== 1 && i !== this.totalPages) {
          pages.push(i)
        }
      }
      
      if (end < this.totalPages - 1) pages.push('...')
      
      if (this.totalPages > 1) pages.push(this.totalPages)
      
      return pages
    }
  },
  
  methods: {
    async loadLogs(isAutoRefresh = false, isEmergencyReconnect = false) {
      return await this.loadCombinedLogs(isAutoRefresh, isEmergencyReconnect)
    },

    async loadCombinedLogs(isAutoRefresh = false, isEmergencyReconnect = false) {
      if (this.loading && !isAutoRefresh && !isEmergencyReconnect) return
      
      this.loading = true
      if (!isEmergencyReconnect) {
        this.error = null
      }
      
      try {
        let logType = 'all'
        if (['session', 'login', 'logout'].includes(this.categoryFilter)) {
          logType = 'session'
        } else if (['category', 'product', 'customer', 'user', 'create', 'update', 'delete'].includes(this.categoryFilter)) {
          logType = 'audit'
        }

        const response = await APILogs.DisplayCombinedLogs({
          limit: 100,
          type: logType
        })
        
        const previousLogsLength = this.session_logs.length
        
        let newLogs = []
        if (response && response.success && response.data) {
          newLogs = response.data
          console.log(`Loaded ${newLogs.length} combined logs (${response.session_count} session, ${response.audit_count} audit)`)
        } else if (Array.isArray(response)) {
          newLogs = response
        } else if (response && response.data) {
          newLogs = response.data
        }
        
        this.connectionLost = false
        this.consecutiveErrors = 0
        this.lastSuccessfulLoad = Date.now()
        this.error = null
        
        this.trackActivityAndAdjustRefreshRate(newLogs, previousLogsLength)
        
        if (isAutoRefresh && this.session_logs.length > 0) {
          const existingIds = new Set(this.session_logs.map(log => log.log_id || log._id))
          newLogs.forEach(log => {
            const id = log.log_id || log._id
            if (!existingIds.has(id)) {
              this.newEntryIds.add(id)
              this.recentActivity.push({
                timestamp: Date.now(),
                logId: id
              })
            }
          })
          
          setTimeout(() => {
            this.newEntryIds.clear()
          }, 5000)
        }
        
        this.session_logs = newLogs
        this.lastLoadTime = Date.now()
        this.memoizedFilters.result = []
        
        if (!isAutoRefresh) {
          this.currentPage = 1
        }
        
        if (this.currentPage > this.totalPages && this.totalPages > 0) {
          this.currentPage = this.totalPages
        }
        
      } catch (error) {
        console.error("Error loading combined logs:", error)
        
        this.consecutiveErrors++
        this.error = error.message || 'Failed to load logs'
        
        if (this.consecutiveErrors >= 3) {
          this.connectionLost = true
        }
        
        if (this.consecutiveErrors >= 2) {
          this.autoRefreshInterval = Math.min(this.baseRefreshInterval * 2, 120000)
        }
        
        if (!isAutoRefresh) {
          this.session_logs = []
        }
      } finally {
        this.loading = false
      }
    },

    async emergencyReconnect() {
      console.log('Emergency reconnect initiated')
      this.consecutiveErrors = 0
      this.connectionLost = false
      await this.loadLogs(false, true)
      
      if (!this.autoRefreshEnabled) {
        this.autoRefreshEnabled = true
        this.startAutoRefresh()
      }
    },

    trackActivityAndAdjustRefreshRate(newLogs, previousLength) {
      const now = Date.now()
      
      this.recentActivity = this.recentActivity.filter(
        activity => now - activity.timestamp < 300000
      )
      
      const recentCount = this.recentActivity.filter(
        activity => now - activity.timestamp < 120000
      ).length
      
      if (recentCount >= 10) {
        this.autoRefreshInterval = 10000
        console.log('High activity detected: refresh rate increased to 10s')
      } else if (recentCount >= 5) {
        this.autoRefreshInterval = 20000
        console.log('Medium activity detected: refresh rate set to 20s')
      } else if (recentCount === 0 && this.recentActivity.length === 0) {
        this.autoRefreshInterval = 60000
        console.log('No activity detected: refresh rate decreased to 60s')
      } else {
        this.autoRefreshInterval = this.baseRefreshInterval
      }
      
      if (this.autoRefreshEnabled && this.autoRefreshTimer) {
        this.startAutoRefresh()
      }
    },

    getConnectionStatus() {
      if (this.connectionLost) return 'connection-lost'
      if (this.consecutiveErrors > 0) return 'connection-unstable'
      if (this.lastSuccessfulLoad && (Date.now() - this.lastSuccessfulLoad < 60000)) return 'connection-good'
      return 'connection-unknown'
    },

    getConnectionIcon() {
      switch (this.getConnectionStatus()) {
        case 'connection-good': return 'bi bi-wifi text-success'
        case 'connection-unstable': return 'bi bi-wifi-1 text-warning'
        case 'connection-lost': return 'bi bi-wifi-off text-danger'
        default: return 'bi bi-wifi text-muted'
      }
    },

    getConnectionText() {
      switch (this.getConnectionStatus()) {
        case 'connection-good': return 'Connected'
        case 'connection-unstable': return 'Unstable'
        case 'connection-lost': return 'Connection Lost'
        default: return 'Connecting...'
      }
    },

    toggleAutoRefresh() {
      if (this.autoRefreshEnabled) {
        this.autoRefreshEnabled = false
        this.stopAutoRefresh()
        console.log('Auto-refresh disabled by user')
      } else {
        this.autoRefreshEnabled = true
        this.startAutoRefresh()
        console.log('Auto-refresh enabled by user')
      }
    },
    
    startAutoRefresh() {
      this.stopAutoRefresh()
      
      this.countdown = this.autoRefreshInterval / 1000
      this.countdownTimer = setInterval(() => {
        this.countdown--
        if (this.countdown <= 0) {
          this.countdown = this.autoRefreshInterval / 1000
        }
      }, 1000)
      
      this.autoRefreshTimer = setInterval(() => {
        this.loadLogs(true)
      }, this.autoRefreshInterval)
      
      console.log(`Auto-refresh started (${this.autoRefreshInterval / 1000}s interval)`)
    },
    
    stopAutoRefresh() {
      if (this.autoRefreshTimer) {
        clearInterval(this.autoRefreshTimer)
        this.autoRefreshTimer = null
      }
      
      if (this.countdownTimer) {
        clearInterval(this.countdownTimer)
        this.countdownTimer = null
      }
      
      console.log('Auto-refresh disabled')
    },

    handleFilterChange() {
      if (this.filterDebounceTimer) {
        clearTimeout(this.filterDebounceTimer)
      }
      
      this.filterDebounceTimer = setTimeout(() => {
        this.applyFilters()
      }, 300)
    },
    
    applyFilters() {
      this.currentPage = 1
      this.memoizedFilters.result = []
      
      console.log('Filters applied:', {
        category: this.categoryFilter,
        search: this.searchFilter,
        results: this.filteredLogs.length
      })
    },

    clearFilters() {
      this.categoryFilter = 'all'
      this.searchFilter = ''
      this.currentPage = 1
      this.memoizedFilters.result = []
    },

    goToPage(page) {
      if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
        this.currentPage = page
      }
    },
    
    handlePageSizeChange() {
      this.currentPage = 1
      console.log(`Page size changed to: ${this.pageSize}`)
    },

    getLogType(log) {
      const eventType = (log.event_type || '').toLowerCase();
      
      if (eventType.includes('session') || 
          eventType.includes('login') || 
          eventType.includes('logout') || 
          eventType.includes('auth')) {
        return 'session';
      }
      
      if (eventType.includes('create') || 
          eventType.includes('update') || 
          eventType.includes('delete') || 
          eventType.includes('product') || 
          eventType.includes('customer') || 
          eventType.includes('category') || 
          eventType.includes('user')) {
        return 'audit';
      }
      
      return 'session';
    },

    getFormattedLogId(log, position) {
      const logType = this.getLogType(log);
      const prefix = logType === 'session' ? 'SES' : 'AUD';
      
      const typeCounter = this.getTypeCounter(position, logType);
      
      return `${prefix}-${typeCounter}`;
    },

    getTypeCounter(currentPosition, logType) {
      let counter = 0;
      
      for (let i = 0; i < currentPosition; i++) {
        if (i < this.filteredLogs.length) {
          const log = this.filteredLogs[i];
          if (this.getLogType(log) === logType) {
            counter++;
          }
        }
      }
      
      return counter;
    },

    getAmountQty(sessionLog) {
      const eventType = (sessionLog.event_type || '').toLowerCase()
      return (eventType === 'session' || eventType === 'session complete') 
        ? 'None' 
        : sessionLog.amount_qty || '-'
    },
    
    getStatusClass(status) {
      const statusMap = {
        'completed': 'status-success',
        'success': 'status-success',
        'active': 'status-active',
        'failed': 'status-failed',
        'error': 'status-failed'
      }
      
      return statusMap[(status || '').toLowerCase()] || 'status-default'
    },

    formatTimestamp(timestamp) {
      if (!timestamp) return 'N/A'
      
      try {
        if (!this._timestampCache) this._timestampCache = new Map()
        
        if (this._timestampCache.has(timestamp)) {
          return this._timestampCache.get(timestamp)
        }
        
        const formatted = new Date(timestamp).toLocaleDateString('en-US', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        })
        
        this._timestampCache.set(timestamp, formatted)
        return formatted
      } catch (error) {
        return timestamp
      }
    },
    
    isNewEntry(sessionLog) {
      const id = sessionLog.log_id || sessionLog._id
      return this.newEntryIds.has(id)
    }
  },
  
  async mounted() {
    console.log('=== System Logs component mounted ===')
    await this.loadLogs()
    
    this.autoRefreshEnabled = true
    this.startAutoRefresh()
  },
  
  beforeUnmount() {
    this.stopAutoRefresh()
    
    if (this.filterDebounceTimer) {
      clearTimeout(this.filterDebounceTimer)
    }
    
    if (this._timestampCache) {
      this._timestampCache.clear()
    }
  }
}
</script>

<style scoped>
/* ==========================================================================
   LOGS PAGE - SEMANTIC THEME SYSTEM WITH DARK MODE SUPPORT
   ========================================================================== */

.logs-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  background-color: var(--surface-secondary);
  min-height: 100vh;
  color: var(--text-secondary);
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* ==========================================================================
   PAGE HEADER
   ========================================================================== */

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  transition: color 0.3s ease;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.auto-refresh-status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: var(--surface-primary);
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border-secondary);
  min-width: 280px;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.status-text {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
  flex: 1;
  transition: color 0.3s ease;
}

.connection-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.connection-good {
  background: var(--surface-primary);
  border: 1px solid var(--border-success);
  color: var(--status-success);
}

.connection-unstable {
  background: var(--surface-primary);
  border: 1px solid var(--status-warning);
  color: var(--status-warning);
}

.connection-lost {
  background: var(--surface-primary);
  border: 1px solid var(--border-error);
  color: var(--status-error);
}

.connection-unknown {
  background: var(--surface-primary);
  border: 1px solid var(--border-secondary);
  color: var(--text-tertiary);
}

/* ==========================================================================
   FILTERS SECTION
   ========================================================================== */

.filters-section {
  background: var(--surface-primary);
  padding: 1.5rem;
  border-radius: 0.75rem;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-secondary);
  margin-bottom: 1.5rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  align-items: end;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.filter-group label {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.875rem;
  display: block;
  margin-bottom: 0.5rem;
  transition: color 0.3s ease;
}

.filter-group select,
.filter-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-primary);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background-color: var(--input-bg);
  color: var(--input-text);
  transition: all 0.3s ease;
}

.filter-group select:focus,
.filter-group input:focus {
  outline: none;
  border-color: var(--border-accent);
  box-shadow: 0 0 0 3px rgba(160, 123, 227, 0.25);
}

.filter-group select::placeholder,
.filter-group input::placeholder {
  color: var(--input-placeholder);
}

/* ==========================================================================
   LOADING AND ERROR STATES
   ========================================================================== */

.loading-state, 
.error-state {
  text-align: center;
  padding: 3rem;
  background: var(--surface-primary);
  border-radius: 0.75rem;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-secondary);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.error-state {
  color: var(--status-error);
}

.refresh-indicator {
  background: var(--surface-primary);
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border-primary);
  margin-bottom: 1rem;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.table-info {
  background: var(--surface-primary);
  padding: 1rem 1.5rem;
  border-radius: 0.75rem 0.75rem 0 0;
  border-bottom: 1px solid var(--border-secondary);
  font-size: 0.875rem;
  color: var(--text-tertiary);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-secondary);
  border-bottom: none;
  transition: all 0.3s ease;
}

.filter-indicator {
  color: var(--text-accent);
  font-weight: 500;
}

/* ==========================================================================
   TABLE CONTAINER
   ========================================================================== */

.table-container {
  background: var(--surface-primary);
  border-radius: 0.75rem;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-secondary);
  overflow: hidden;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.logs-table thead {
  background-color: var(--primary-medium);
  color: var(--text-inverse);
}

.logs-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.875rem;
  letter-spacing: 0.025em;
  color: var(--text-inverse);
  border-bottom: 1px solid var(--primary-dark);
}

.logs-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-secondary);
  font-size: 0.875rem;
  transition: all 0.3s ease;
  color: var(--text-secondary);
}

.logs-table tbody tr:hover {
  background-color: var(--state-hover);
}

.logs-table tbody tr.new-entry {
  background-color: var(--status-warning-bg);
  animation: highlight-fade 3s ease-out;
}

@keyframes highlight-fade {
  0% {
    background-color: var(--status-warning-bg);
    transform: scale(1.01);
  }
  100% {
    background-color: var(--surface-primary);
    transform: scale(1);
  }
}

/* ==========================================================================
   LOG-SPECIFIC STYLES
   ========================================================================== */

.position-number {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-weight: 600;
  font-size: 0.75rem;
  color: var(--text-inverse);
  border: 2px solid transparent;
}

.position-number.session {
  background-color: var(--primary-medium);
  border-color: var(--primary-dark);
}

.position-number.audit {
  background-color: var(--secondary);
  border-color: var(--secondary-dark);
}

/* Status badges */
.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  display: inline-block;
  min-width: 60px;
  text-align: center;
}

.status-success {
  background-color: var(--status-success-bg);
  color: var(--status-success);
  border: 1px solid var(--status-success);
}

.status-active {
  background-color: var(--status-info-bg);
  color: var(--status-info);
  border: 1px solid var(--status-info);
}

.status-failed {
  background-color: var(--status-error-bg);
  color: var(--status-error);
  border: 1px solid var(--status-error);
}

.status-default {
  background-color: var(--surface-tertiary);
  color: var(--text-tertiary);
  border: 1px solid var(--border-secondary);
}

/* ==========================================================================
   EMPTY STATE
   ========================================================================== */

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-tertiary);
  background: var(--surface-primary);
  border-radius: 0.75rem;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-secondary);
  transition: all 0.3s ease;
}

.empty-state-icon {
  font-size: 3rem;
  color: var(--text-tertiary);
  transition: color 0.3s ease;
}

.card {
  background: var(--surface-primary);
  border-radius: 0.5rem;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-secondary);
  transition: all 0.3s ease;
}

.card-body {
  padding: 1.5rem;
}

/* ==========================================================================
   PAGINATION
   ========================================================================== */

.pagination-container {
  background: var(--surface-primary);
  padding: 1.5rem;
  border-radius: 0 0 0.75rem 0.75rem;
  border-top: 1px solid var(--border-secondary);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-secondary);
  border-top: none;
  transition: all 0.3s ease;
}

.pagination-info {
  text-align: center;
  margin-top: 1rem;
}

.page-link {
  border: 1px solid var(--border-primary);
  color: var(--text-accent);
  background: var(--surface-primary);
  transition: all 0.3s ease;
}

.page-link:hover {
  background-color: var(--state-hover);
  border-color: var(--border-accent);
  color: var(--text-accent);
}

.page-item.active .page-link {
  background-color: var(--text-accent);
  border-color: var(--border-accent);
  color: var(--text-inverse);
}

.page-item.disabled .page-link {
  color: var(--text-disabled);
  background-color: var(--surface-tertiary);
  border-color: var(--border-secondary);
  cursor: not-allowed;
}

/* ==========================================================================
   ALERT STYLES
   ========================================================================== */

.alert-danger {
  background-color: var(--status-error-bg);
  border-color: var(--border-error);
  color: var(--status-error);
}

.alert-info {
  background-color: var(--status-info-bg);
  border-color: var(--status-info);
  color: var(--status-info);
}

/* ==========================================================================
   UTILITY CLASSES
   ========================================================================== */

.text-accent {
  color: var(--text-accent) !important;
}

.text-primary {
  color: var(--text-primary) !important;
}

.text-secondary {
  color: var(--text-secondary) !important;
}

.text-tertiary {
  color: var(--text-tertiary) !important;
}

.text-success {
  color: var(--status-success) !important;
}

.text-warning {
  color: var(--status-warning) !important;
}

.text-muted {
  color: var(--text-tertiary) !important;
}

/* ==========================================================================
   ANIMATIONS
   ========================================================================== */

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* ==========================================================================
   RESPONSIVE DESIGN
   ========================================================================== */

@media (max-width: 1024px) {
  .filters-section {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .auto-refresh-status {
    min-width: auto;
    flex: 1;
  }
}

@media (max-width: 768px) {
  .logs-page {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .auto-refresh-status,
  .connection-indicator {
    width: 100%;
  }
  
  .logs-table th,
  .logs-table td {
    padding: 0.5rem;
    font-size: 0.8125rem;
  }
  
  .position-number {
    padding: 0.125rem 0.375rem;
    font-size: 0.6875rem;
  }
}

@media (max-width: 576px) {
  .logs-page {
    padding: 0.5rem;
  }
  
  .page-title {
    font-size: 1.25rem;
  }
  
  .filters-section {
    padding: 1rem;
  }
  
  .logs-table {
    font-size: 0.75rem;
  }
  
  .logs-table th,
  .logs-table td {
    padding: 0.25rem;
  }
}
</style>