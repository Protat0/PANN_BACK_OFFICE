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
          
          <!-- Session Events -->
          <option value="session">Sessions</option>
          <option value="login">Login</option>
          <option value="logout">Logout</option>
          
          <!-- Audit Events -->
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
        <small class="text-muted">
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
      autoRefreshEnabled: true, // Enable by default for "automatic" branding
      autoRefreshInterval: 30000, // 30 seconds (base interval)
      baseRefreshInterval: 30000, // Store original interval
      autoRefreshTimer: null,
      countdown: 30,
      countdownTimer: null,
      
      // Connection health tracking (Option 2)
      connectionLost: false,
      consecutiveErrors: 0,
      lastSuccessfulLoad: null,
      
      // Smart refresh rate tracking (Option 3)
      recentActivity: [], // Track recent entries for smart adjustment
      activityCheckInterval: 60000, // Check activity every minute
      
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
      // Check if filters have changed
      if (
        this.memoizedFilters.categoryFilter === this.categoryFilter &&
        this.memoizedFilters.searchFilter === this.searchFilter &&
        this.memoizedFilters.result.length > 0
      ) {
        return this.memoizedFilters.result
      }
      
      // Apply filters
      let filtered = [...this.session_logs]
      
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
      
      // Sort by timestamp (latest first) to ensure consistent ordering
      filtered.sort((a, b) => {
        const dateA = new Date(a.timestamp || 0)
        const dateB = new Date(b.timestamp || 0)
        return dateB - dateA // Latest first
      })
      
      // Cache the result
      this.memoizedFilters = {
        categoryFilter: this.categoryFilter,
        searchFilter: this.searchFilter,
        result: filtered
      }
      
      return filtered
    },
    
    // Calculate total pages based on filtered logs
    totalPages() {
      return Math.ceil(this.filteredLogs.length / this.pageSize)
    },

    // Get logs for current page with formatted log IDs
    paginatedLogs() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      const logs = this.filteredLogs.slice(start, end)
      
      // Add formatted log ID and log type to each log
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
    
    // Calculate record numbers for display
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

    // Check if any filters are active
    hasActiveFilters() {
      return this.categoryFilter !== 'all' || this.searchFilter.trim() !== ''
    },
    
    // Optimized visible pages calculation
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
    // ================================================================
    // DATA FETCHING - OPTIMIZED WITH CONNECTION HEALTH & SMART REFRESH
    // ================================================================
    async loadLogs(isAutoRefresh = false, isEmergencyReconnect = false) {
      return await this.loadCombinedLogs(isAutoRefresh, isEmergencyReconnect)
    },

    // ADD this new method after loadLogs
    async loadCombinedLogs(isAutoRefresh = false, isEmergencyReconnect = false) {
      if (this.loading && !isAutoRefresh && !isEmergencyReconnect) return
      
      this.loading = true
      if (!isEmergencyReconnect) {
        this.error = null
      }
      
      try {
        // Use the new combined logs API
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
        
        // Handle response
        let newLogs = []
        if (response && response.success && response.data) {
          newLogs = response.data
          console.log(`Loaded ${newLogs.length} combined logs (${response.session_count} session, ${response.audit_count} audit)`)
        } else if (Array.isArray(response)) {
          newLogs = response
        } else if (response && response.data) {
          newLogs = response.data
        }
        
        // Connection health tracking (same as existing)
        this.connectionLost = false
        this.consecutiveErrors = 0
        this.lastSuccessfulLoad = Date.now()
        this.error = null
        
        // Smart refresh rate adjustment (same as existing)
        this.trackActivityAndAdjustRefreshRate(newLogs, previousLogsLength)
        
        // Track new entries for highlighting (same as existing)
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

    // OPTION 2: Emergency reconnect method
    async emergencyReconnect() {
      console.log('Emergency reconnect initiated')
      this.consecutiveErrors = 0
      this.connectionLost = false
      await this.loadLogs(false, true)
      
      // Restart auto-refresh if it was stopped
      if (!this.autoRefreshEnabled) {
        this.autoRefreshEnabled = true
        this.startAutoRefresh()
      }
    },

    // OPTION 3: Smart refresh rate adjustment based on activity
    trackActivityAndAdjustRefreshRate(newLogs, previousLength) {
      const now = Date.now()
      
      // Clean old activity data (older than 5 minutes)
      this.recentActivity = this.recentActivity.filter(
        activity => now - activity.timestamp < 300000
      )
      
      // Count recent activity (last 2 minutes)
      const recentCount = this.recentActivity.filter(
        activity => now - activity.timestamp < 120000
      ).length
      
      // Adjust refresh rate based on activity
      if (recentCount >= 10) {
        // High activity: refresh every 10 seconds
        this.autoRefreshInterval = 10000
        console.log('High activity detected: refresh rate increased to 10s')
      } else if (recentCount >= 5) {
        // Medium activity: refresh every 20 seconds
        this.autoRefreshInterval = 20000
        console.log('Medium activity detected: refresh rate set to 20s')
      } else if (recentCount === 0 && this.recentActivity.length === 0) {
        // No activity: refresh every 60 seconds
        this.autoRefreshInterval = 60000
        console.log('No activity detected: refresh rate decreased to 60s')
      } else {
        // Normal activity: use base interval
        this.autoRefreshInterval = this.baseRefreshInterval
      }
      
      // Restart auto-refresh with new interval if it's running
      if (this.autoRefreshEnabled && this.autoRefreshTimer) {
        this.startAutoRefresh()
      }
    },

    // OPTION 2: Connection status methods
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

    // ================================================================
    // AUTO-REFRESH FUNCTIONALITY
    // ================================================================
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
      this.stopAutoRefresh() // Clear any existing timers
      
      // Start countdown
      this.countdown = this.autoRefreshInterval / 1000
      this.countdownTimer = setInterval(() => {
        this.countdown--
        if (this.countdown <= 0) {
          this.countdown = this.autoRefreshInterval / 1000
        }
      }, 1000)
      
      // Start auto-refresh timer
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

    // ================================================================
    // FILTER METHODS - OPTIMIZED WITH DEBOUNCING
    // ================================================================
    handleFilterChange() {
      // Clear existing timer
      if (this.filterDebounceTimer) {
        clearTimeout(this.filterDebounceTimer)
      }
      
      // Debounce filter application for 300ms
      this.filterDebounceTimer = setTimeout(() => {
        this.applyFilters()
      }, 300)
    },
    
    applyFilters() {
      // Reset to first page when filters change
      this.currentPage = 1
      
      // Clear memoization cache to force recalculation
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

    // ================================================================
    // PAGINATION METHODS - OPTIMIZED
    // ================================================================
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
        this.currentPage = page
      }
    },
    
    handlePageSizeChange() {
      this.currentPage = 1
      console.log(`Page size changed to: ${this.pageSize}`)
    },

    // ================================================================
    // LOG TYPE AND FORMATTING METHODS
    // ================================================================
    
    // Determine log type based on event_type
    getLogType(log) {
      const eventType = (log.event_type || '').toLowerCase();
      
      // Session-related events
      if (eventType.includes('session') || 
          eventType.includes('login') || 
          eventType.includes('logout') || 
          eventType.includes('auth')) {
        return 'session';
      }
      
      // Audit-related events (CRUD operations)
      if (eventType.includes('create') || 
          eventType.includes('update') || 
          eventType.includes('delete') || 
          eventType.includes('product') || 
          eventType.includes('customer') || 
          eventType.includes('category') || 
          eventType.includes('user')) {
        return 'audit';
      }
      
      // Default to session if unsure
      return 'session';
    },

    // Generate formatted log ID (SES-1, AUD-1, etc.)
    getFormattedLogId(log, position) {
      const logType = this.getLogType(log);
      const prefix = logType === 'session' ? 'SES' : 'AUD';
      
      // Get the counter for this specific log type
      const typeCounter = this.getTypeCounter(position, logType);
      
      return `${prefix}-${typeCounter}`;
    },

    // Calculate counter for each log type separately
    getTypeCounter(currentPosition, logType) {
      let counter = 0;
      
      // Count logs of the same type up to current position
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

    // ================================================================
    // UTILITY METHODS - OPTIMIZED WITH MEMOIZATION
    // ================================================================
    getAmountQty(sessionLog) {
      const eventType = (sessionLog.event_type || '').toLowerCase()
      return (eventType === 'session' || eventType === 'session complete') 
        ? 'None' 
        : sessionLog.amount_qty || '-'
    },
    
    getStatusClass(status) {
      // Use Map for O(1) lookup instead of switch
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
        // Cache formatted dates to avoid repeated formatting
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
  
  // ================================================================
  // LIFECYCLE HOOKS
  // ================================================================
  async mounted() {
    console.log('=== System Logs component mounted ===')
    await this.loadLogs()
    
    // Initialize auto-refresh (enabled by default for "automatic" branding)
    this.autoRefreshEnabled = true
    this.startAutoRefresh()
  },
  
  beforeUnmount() {
    // Clean up timers
    this.stopAutoRefresh()
    
    if (this.filterDebounceTimer) {
      clearTimeout(this.filterDebounceTimer)
    }
    
    // Clear caches
    if (this._timestampCache) {
      this._timestampCache.clear()
    }
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
  align-items: center;
}

.auto-refresh-status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #f0fdf4;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #bbf7d0;
  min-width: 280px;
}

.status-text {
  font-size: 0.875rem;
  color: #16a34a;
  font-weight: 500;
  flex: 1;
}

.connection-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.connection-good {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #16a34a;
}

.connection-unstable {
  background: #fefce8;
  border: 1px solid #fde047;
  color: #ca8a04;
}

.connection-lost {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.connection-unknown {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #64748b;
}

.auto-refresh-indicator {
  margin-bottom: 1rem;
}

/* New entry highlight animation */
.new-entry {
  background-color: #fef3c7 !important;
  animation: newEntryFade 5s ease-out forwards;
}

@keyframes newEntryFade {
  0% {
    background-color: #fef3c7;
  }
  100% {
    background-color: transparent;
  }
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

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.btn-outline-success {
  background-color: transparent;
  color: #16a34a;
  border: 1px solid #16a34a;
}

.btn-outline-success:hover {
  background-color: #16a34a;
  color: white;
  border-color: #16a34a;
}

.btn-outline-secondary {
  background-color: transparent;
  color: #6b7280;
  border: 1px solid #6b7280;
}

.btn-outline-secondary:hover {
  background-color: #6b7280;
  color: white;
  border-color: #6b7280;
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
  transition: border-color 0.2s ease;
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
  transition: background-color 0.2s ease;
}

.logs-table tbody tr:hover {
  background-color: #f8fafc;
}

/* Updated Log ID column to show formatted IDs */
.log-id-column {
  width: 100px;
  text-align: center;
  font-weight: 600;
  color: #475569;
  padding: 0.5rem;
}

.position-number {
  display: inline-block;
  min-width: 60px;
  padding: 0.5rem 0.75rem;
  color: white;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 700;
  font-family: monospace;
  letter-spacing: 0.5px;
}

/* Session log styling (blue theme) */
.position-number.session {
  background-color: #567cdc;
  border: 2px solid #4f46e5;
}

/* Audit log styling (purple theme) */
.position-number.audit {
  background-color: #7c3aed;
  border: 2px solid #6d28d9;
}

/* Latest entry highlighting - keep original colors but add glow effect */
.logs-table tbody tr:first-child .position-number.session {
  animation: latestSessionPulse 2s ease-in-out;
  box-shadow: 0 0 0 3px rgba(86, 124, 220, 0.4);
}

.logs-table tbody tr:first-child .position-number.audit {
  animation: latestAuditPulse 2s ease-in-out;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.4);
}

@keyframes latestSessionPulse {
  0%, 100% { 
    background-color: #567cdc;
    border-color: #4f46e5;
    transform: scale(1);
  }
  50% { 
    background-color: #4f46e5;
    border-color: #3730a3;
    transform: scale(1.05);
  }
}

@keyframes latestAuditPulse {
  0%, 100% { 
    background-color: #7c3aed;
    border-color: #6d28d9;
    transform: scale(1);
  }
  50% { 
    background-color: #6d28d9;
    border-color: #5b21b6;
    transform: scale(1.05);
  }
}

/* New entry highlighting - orange for both types */
.new-entry .position-number.session,
.new-entry .position-number.audit {
  background-color: #f59e0b;
  border-color: #d97706;
  animation: newPositionFade 5s ease-out forwards;
}

@keyframes newPositionFade {
  0% {
    background-color: #f59e0b;
    border-color: #d97706;
    transform: scale(1.1);
  }
  25% {
    background-color: #f59e0b;
    border-color: #d97706;
  }
  100% {
    transform: scale(1);
  }
}

/* Other column styles */
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

.card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.card-body {
  padding: 1.5rem;
}

.py-5 {
  padding-top: 3rem;
  padding-bottom: 3rem;
}

.d-flex {
  display: flex;
}

.gap-2 {
  gap: 0.5rem;
}

.justify-content-center {
  justify-content: center;
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
  display: flex;
  list-style: none;
  padding: 0;
  margin: 0;
}

.pagination-sm .page-link {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.pagination-info {
  text-align: center;
}

.page-item {
  margin: 0;
}

.page-link {
  border: 1px solid #e2e8f0;
  color: #567cdc;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  text-decoration: none;
  background: white;
  border-radius: 0;
  margin: 0;
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
  cursor: not-allowed;
}

.page-item:first-child .page-link {
  border-radius: 0.375rem 0 0 0.375rem;
}

.page-item:last-child .page-link {
  border-radius: 0 0.375rem 0.375rem 0;
}

.justify-content-center {
  justify-content: center;
}

/* Alert styles */
.alert {
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid transparent;
  margin-bottom: 1rem;
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

.text-center {
  text-align: center;
}

.mb-3 {
  margin-bottom: 1rem;
}

.me-2 {
  margin-right: 0.5rem;
}

.mt-3 {
  margin-top: 1rem;
}

.spinner-border {
  width: 2rem;
  height: 2rem;
  border: 0.25em solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.2em;
}

.text-primary {
  color: #3b82f6;
}

.text-success {
  color: #10b981;
}

.text-muted {
  color: #6b7280;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
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

  .auto-refresh-status {
    min-width: auto;
    width: 100%;
    justify-content: center;
  }

  /* Responsive adjustments for position numbers */
  .log-id-column {
    width: 90px;
  }
  
  .position-number {
    font-size: 0.75rem;
    padding: 0.375rem 0.5rem;
    min-width: 50px;
  }
  
  .user-id-column,
  .ref-id-column,
  .event-type-column {
    width: 100px;
  }
  
  .amount-column,
  .status-column {
    width: 80px;
  }
  
  .timestamp-column {
    width: 130px;
  }
  
  .remarks-column {
    width: 150px;
    max-width: 150px;
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

  .auto-refresh-status {
    min-width: auto;
    padding: 0.5rem;
  }

  .connection-indicator {
    padding: 0.375rem 0.5rem;
  }
}
</style>