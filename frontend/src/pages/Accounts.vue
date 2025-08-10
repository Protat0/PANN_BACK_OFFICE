<template>
  <div class="accounts-page">
    <!-- Header Section -->
    <div class="page-header">
      <h1 class="page-title">User Management</h1>
      <div class="header-actions">
        <!-- Auto-refresh status and controls (same as logs page) -->
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
        
        <!-- Connection health indicator (same as logs page) -->
        <div class="connection-indicator" :class="getConnectionStatus()">
          <i :class="getConnectionIcon()"></i>
          <span class="connection-text">{{ getConnectionText() }}</span>
        </div>
        
        <!-- Emergency Refresh - Only show if error or connection lost -->
        <button 
          v-if="error || connectionLost" 
          class="btn btn-warning" 
          @click="emergencyReconnect"
          :disabled="loading"
        >
          <i class="bi bi-arrow-clockwise" :class="{ 'spinning': loading }"></i>
          {{ loading ? 'Reconnecting...' : 'Reconnect' }}
        </button>

        <button 
          class="btn btn-danger" 
          @click="deleteSelected" 
          :disabled="selectedUsers.length === 0 || loading"
        >
          Delete Selected ({{ selectedUsers.length }})
        </button>
        <button class="btn btn-success" @click="showAddUserModal">
          Add User
        </button>
        <button class="btn btn-primary" @click="exportData" :disabled="loading || exporting">
           {{ exporting ? 'Exporting...' : 'Export' }}
        </button>
      </div>
    </div>

    <!-- Rest of the component remains the same -->
    <!-- Filters Section -->
    <div class="filters-section">
      <div class="filter-group">
        <label for="roleFilter">Filter by Role:</label>
        <select id="roleFilter" v-model="roleFilter" @change="applyFilters" :disabled="loading">
          <option value="all">All Roles</option>
          <option value="admin">Admin</option>
          <option value="employee">Employee</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label for="statusFilter">Filter by Status:</label>
        <select id="statusFilter" v-model="statusFilter" @change="applyFilters" :disabled="loading">
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="searchFilter">Search:</label>
        <input 
          id="searchFilter" 
          v-model="searchFilter" 
          @input="handleSearch"
          type="text" 
          placeholder="Search by name, email, or username..."
          :disabled="loading"
        />
        <button 
          v-if="searchFilter" 
          @click="clearSearch" 
          class="clear-search-btn"
          title="Clear search"
        >
          ✕
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && users.length === 0" class="loading-state">
      <div class="spinner-border text-primary"></div>
      <p>Loading user accounts...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-state">
      <div class="alert alert-danger text-center" role="alert">
        <i class="bi bi-exclamation-triangle"></i>
        <p class="mb-3">{{ error }}</p>
        <button class="btn btn-primary" @click="emergencyReconnect" :disabled="loading">
          <i class="bi bi-arrow-clockwise"></i>
          {{ loading ? 'Retrying...' : 'Try Again' }}
        </button>
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="success-message">
      <div class="alert alert-success text-center" role="alert">
        <i class="bi bi-check-circle"></i>
        {{ successMessage }}
      </div>
    </div>

    <!-- Refresh Progress Indicator -->
    <div v-if="loading && users.length > 0" class="refresh-indicator">
      <div class="alert alert-info d-flex align-items-center" role="alert">
        <div class="spinner-border spinner-border-sm me-2" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        Refreshing user data... {{ refreshProgress }}
      </div>
    </div>

    <!-- Cache Status (development info) -->
    <div v-if="showCacheStatus" class="cache-status">
      <div class="alert alert-info">
        <strong>Cache Status:</strong> 
        Hit Rate: {{ cacheStats.hitRate }}% | 
        Last Update: {{ formatCacheTime(cacheStats.lastUpdate) }} |
        <button class="btn btn-sm btn-outline-info ms-2" @click="cache.clear()">Clear Cache</button>
      </div>
    </div>

    <!-- Data Table -->
    <DataTable v-if="!loading || users.length > 0">
      <template #header>
        <tr>
          <th class="checkbox-column">
            <input 
              type="checkbox" 
              @change="selectAll" 
              :checked="allSelected"
              :indeterminate="someSelected"
              :disabled="loading"
            />
          </th>
          <th>ID</th>
          <th>Username</th>
          <th>Full Name</th>
          <th>Email</th>
          <th>Role</th>
          <th>Status</th>
          <th>Last Login</th>
          <th>Created on</th>
          <th class="actions-column">Actions</th>
        </tr>
      </template>

      <template #body>
        <tr 
          v-for="user in filteredUsers" 
          :key="user._id"
          :class="{ 
            'selected': selectedUsers.includes(user._id),
            'inactive': user.status === 'inactive',
            'refreshing': loading,
            'new-entry': newEntryIds.has(user._id)
          }"
        >
          <td class="checkbox-column">
            <input 
              type="checkbox" 
              :value="user._id"
              v-model="selectedUsers"
              :disabled="loading"
            />
          </td>
          <td class="id-column">{{ user._id.slice(-6) }}</td>
          <td class="username-column">
            <span v-html="highlightMatch(user.username, searchFilter)"></span>
          </td>
          <td class="name-column" :title="user.full_name">
            <span v-html="highlightMatch(user.full_name, searchFilter)"></span>
          </td>
          <td class="email-column" :title="user.email">
            <span v-html="highlightMatch(user.email, searchFilter)"></span>
          </td>
          <td class="role-column">
            <span :class="['role-badge', `role-${user.role}`]">
              {{ user.role }}
            </span>
          </td>
          <td class="status-column">
            <span :class="['status-badge', `status-${user.status}`]">
              {{ user.status }}
            </span>
          </td>
          <td class="login-column">{{ formatDate(user.last_login) }}</td>
          <td class="date-column">{{ formatDate(user.date_created) }}</td>
          <td class="actions-column">
            <div class="action-buttons">
              <button 
                class="btn btn-outline-secondary btn-icon-only btn-xs" 
                @click="editUser(user)"
                data-bs-toggle="tooltip"
                title="Edit"
                :disabled="loading"
              >
                <Edit :size="14" />
              </button>
              <button 
                class="btn btn-outline-primary btn-icon-only btn-xs" 
                @click="viewUser(user)"
                data-bs-toggle="tooltip"
                title="View"
                :disabled="loading"
              >
                <Eye :size="14" />
              </button>
              <button 
                class="btn btn-icon-only btn-xs"
                @click="toggleUserStatus(user)"
                data-bs-toggle="tooltip"
                :title="user.status === 'active' ? 'Deactivate' : 'Activate'"
                :class="user.status === 'active' ? 'btn-outline-warning' : 'btn-outline-success'"
                :disabled="loading"
              >
                <Lock v-if="user.status === 'active'" :size="14" />
                <Unlock v-else :size="14" />
              </button>
              <button 
                class="btn btn-outline-danger btn-icon-only btn-xs" 
                @click="deleteUser(user)"
                data-bs-toggle="tooltip"
                title="Delete"
                :disabled="loading"
              >
                <Trash2 :size="14" />
              </button>
            </div>
          </td>
        </tr>
      </template>
    </DataTable>

    <!-- Empty State -->
    <div v-if="!loading && filteredUsers.length === 0 && !error" class="empty-state">
      <div class="card">
        <div class="card-body text-center py-5">
          <i class="bi bi-people" style="font-size: 3rem; color: #6b7280;"></i>
          <p class="mt-3 mb-3">
            <span v-if="searchFilter">No users found matching "{{ searchFilter }}"</span>
            <span v-else-if="users.length === 0">No user accounts found</span>
            <span v-else>No users match the current filters</span>
          </p>
          <div class="d-flex gap-2 justify-content-center">
            <button v-if="!searchFilter && users.length === 0" class="btn btn-primary" @click="showAddUserModal">
              <i class="bi bi-person-plus"></i>
              Add First User
            </button>
            <button v-if="searchFilter" class="btn btn-secondary" @click="clearSearch">
              <i class="bi bi-funnel"></i>
              Clear Search
            </button>
            <button class="btn btn-secondary" @click="clearFilters">
              <i class="bi bi-funnel"></i>
              Clear Filters
            </button>
            <button class="btn btn-info" @click="refreshData">
              <i class="bi bi-arrow-clockwise"></i>
              Refresh Data
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- User Modal (Add/Edit) with Validation -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h2>{{ isEditMode ? 'Edit User Account' : 'Add New User Account' }}</h2>
        
        <form @submit.prevent="saveUser" class="user-form">
          <div class="form-row">
            <div class="form-group">
              <label for="username">Username:</label>
              <input 
                id="username"
                v-model="userForm.username" 
                type="text" 
                required 
                :disabled="formLoading"
                placeholder="Enter username"
                :class="{ 'error': validationErrors.username }"
                @input="validateField('username', $event.target.value)"
                @blur="validateField('username', $event.target.value)"
              />
              <div v-if="validationErrors.username" class="field-error">
                {{ validationErrors.username }}
              </div>
            </div>

            <div class="form-group">
              <label for="email">Email:</label>
              <input 
                id="email"
                v-model="userForm.email" 
                type="email" 
                required 
                :disabled="formLoading"
                placeholder="Enter email address"
                :class="{ 'error': validationErrors.email }"
                @input="validateField('email', $event.target.value)"
                @blur="validateField('email', $event.target.value)"
              />
              <div v-if="validationErrors.email" class="field-error">
                {{ validationErrors.email }}
              </div>
            </div>
          </div>

          <div class="form-group">
            <label for="full_name">Full Name:</label>
            <input 
              id="full_name"
              v-model="userForm.full_name" 
              type="text" 
              required 
              :disabled="formLoading"
              placeholder="Enter full name"
              :class="{ 'error': validationErrors.full_name }"
              @input="validateField('full_name', $event.target.value)"
              @blur="validateField('full_name', $event.target.value)"
            />
            <div v-if="validationErrors.full_name" class="field-error">
              {{ validationErrors.full_name }}
            </div>
          </div>

          <div v-if="!isEditMode" class="form-group">
            <label for="password">Password:</label>
            <input 
              id="password"
              v-model="userForm.password" 
              type="password" 
              required 
              :disabled="formLoading"
              placeholder="Enter password"
              minlength="6"
              :class="{ 'error': validationErrors.password }"
              @input="validateField('password', $event.target.value)"
              @blur="validateField('password', $event.target.value)"
            />
            <div v-if="validationErrors.password" class="field-error">
              {{ validationErrors.password }}
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="role">Role:</label>
              <select 
                id="role"
                v-model="userForm.role" 
                required 
                :disabled="formLoading"
                :class="{ 'error': validationErrors.role }"
                @change="validateField('role', $event.target.value)"
              >
                <option value="">Select Role</option>
                <option value="admin">Admin</option>
                <option value="employee">Employee</option>
              </select>
              <div v-if="validationErrors.role" class="field-error">
                {{ validationErrors.role }}
              </div>
            </div>

            <div class="form-group">
              <label for="status">Status:</label>
              <select 
                id="status"
                v-model="userForm.status" 
                required 
                :disabled="formLoading"
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>

          <!-- Overall form error -->
          <div v-if="formError" class="form-error">
            {{ formError }}
          </div>

          <!-- Validation loading indicator -->
          <div v-if="isValidating" class="validation-loading">
            <span>Validating...</span>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" :disabled="formLoading">
              Cancel
            </button>
            <button 
              type="submit" 
              :disabled="formLoading || hasValidationErrors || isValidating" 
              class="btn-primary"
            >
              {{ formLoading ? 'Saving...' : (isEditMode ? 'Update User' : 'Create User') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- View User Modal -->
    <div v-if="showViewModal" class="modal-overlay" @click="closeViewModal">
      <div class="modal-content" @click.stop>
        <h2>User Account Details</h2>
        <div class="user-details" v-if="selectedUser">
          <div class="detail-row">
            <strong>ID:</strong> {{ selectedUser._id }}
          </div>
          <div class="detail-row">
            <strong>Username:</strong> {{ selectedUser.username }}
          </div>
          <div class="detail-row">
            <strong>Full Name:</strong> {{ selectedUser.full_name }}
          </div>
          <div class="detail-row">
            <strong>Email:</strong> {{ selectedUser.email }}
          </div>
          <div class="detail-row">
            <strong>Role:</strong> 
            <span :class="['role-badge', `role-${selectedUser.role}`]">
              {{ selectedUser.role }}
            </span>
          </div>
          <div class="detail-row">
            <strong>Status:</strong> 
            <span :class="['status-badge', `status-${selectedUser.status}`]">
              {{ selectedUser.status }}
            </span>
          </div>
          <div class="detail-row">
            <strong>Source:</strong> {{ selectedUser.source || 'system' }}
          </div>
          <div class="detail-row">
            <strong>Last Login:</strong> {{ formatDate(selectedUser.last_login) }}
          </div>
          <div class="detail-row">
            <strong>Date Created:</strong> {{ formatDate(selectedUser.date_created) }}
          </div>
          <div class="detail-row">
            <strong>Last Updated:</strong> {{ formatDate(selectedUser.last_updated) }}
          </div>
        </div>
        <div class="form-actions">
          <button @click="closeViewModal">Close</button>
          <button @click="editUser(selectedUser)" class="btn-primary">Edit User</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiService from '../services/api.js'
import DataTable from '../components/common/TableTemplate.vue'
import { Edit, Eye, Lock, Unlock, Trash2 } from 'lucide-vue-next'

// ============ ADVANCED CACHING SYSTEM ============
class UserCache {
  constructor() {
    this.users = new Map()
    this.metadata = {
      lastUpdate: null,
      hitCount: 0,
      missCount: 0,
      enabled: true
    }
    this.ttl = 5 * 60 * 1000 // 5 minutes cache TTL
  }

  // Check if cache entry is still valid
  isValid(timestamp) {
    return timestamp && (Date.now() - timestamp < this.ttl)
  }

  // Get users from cache
  getUsers() {
    const cached = this.users.get('all')
    if (cached && this.isValid(cached.timestamp)) {
      this.metadata.hitCount++
      console.log('🎯 Cache HIT: Users loaded from cache')
      return cached.data
    }
    this.metadata.missCount++
    console.log('❌ Cache MISS: Users not in cache or expired')
    return null
  }

  // Store users in cache
  setUsers(data) {
    this.users.set('all', {
      data: data,
      timestamp: Date.now()
    })
    this.metadata.lastUpdate = Date.now()
    console.log('💾 Cache SET: Users cached successfully')
  }

  // Get cache statistics
  getStats() {
    const total = this.metadata.hitCount + this.metadata.missCount
    const hitRate = total > 0 ? Math.round((this.metadata.hitCount / total) * 100) : 0
    
    return {
      enabled: this.metadata.enabled,
      hitRate: hitRate,
      lastUpdate: this.metadata.lastUpdate,
      size: this.users.size,
      hitCount: this.metadata.hitCount,
      missCount: this.metadata.missCount
    }
  }

  // Clear all cache
  clear() {
    this.users.clear()
    this.metadata.hitCount = 0
    this.metadata.missCount = 0
    this.metadata.lastUpdate = null
    console.log('🗑️ Cache CLEARED: All cached data removed')
  }

  // Disable cache
  disable() {
    this.metadata.enabled = false
    this.clear()
  }

  // Enable cache
  enable() {
    this.metadata.enabled = true
  }
}

export default {
  name: 'AccountsPage',
  components: {
    DataTable,
    Edit,
    Eye,
    Lock,
    Unlock,
    Trash2
  },
  data() {
    return {
      users: [],
      filteredUsers: [],
      selectedUsers: [],
      loading: false,
      exporting: false,
      error: null,
      successMessage: null,
      
      // Enhanced refresh tracking
      lastRefresh: null,
      refreshProgress: '',
      refreshStartTime: null,
      
      // Auto-refresh functionality
      autoRefreshEnabled: true,
      autoRefreshInterval: 30000, // 30 seconds
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
      
      // Cache system
      cache: new UserCache(),
      showCacheStatus: false, // Set to true for development
      
      // Performance optimizations
      searchTimeout: null,
      lastLoadTime: null,
      newEntryIds: new Set(),
      
      // Filters
      roleFilter: 'all',
      statusFilter: 'all',
      searchFilter: '',
      
      // Modal states
      showModal: false,
      showViewModal: false,
      isEditMode: false,
      formLoading: false,
      formError: null,
      selectedUser: null,
      
      // Validation states
      validationErrors: {},
      isValidating: false,
      
      // User form data
      userForm: {
        username: '',
        email: '',
        full_name: '',
        password: '',
        role: '',
        status: 'active'
      }
    }
  },
  computed: {
    allSelected() {
      return this.filteredUsers.length > 0 && this.selectedUsers.length === this.filteredUsers.length
    },
    someSelected() {
      return this.selectedUsers.length > 0 && this.selectedUsers.length < this.filteredUsers.length
    },
    hasValidationErrors() {
      return Object.keys(this.validationErrors).length > 0
    },
    cacheStats() {
      return this.cache.getStats()
    }
  },
  methods: {
    // ============ VALIDATION METHODS ============
    checkEmailDuplicate(email, excludeId = null) {
      if (!email) return false
      
      return this.users.some(user => {
        const userId = user._id
        const isDifferentUser = excludeId ? userId !== excludeId : true
        return user.email && 
               user.email.toLowerCase() === email.toLowerCase() && 
               isDifferentUser
      })
    },

    checkUsernameDuplicate(username, excludeId = null) {
      if (!username) return false
      
      return this.users.some(user => {
        const userId = user._id
        const isDifferentUser = excludeId ? userId !== excludeId : true
        return user.username && 
               user.username.toLowerCase() === username.toLowerCase() && 
               isDifferentUser
      })
    },

    validateField(fieldName, value) {
      const errors = { ...this.validationErrors }
      const excludeId = this.isEditMode ? this.selectedUser._id : null

      switch (fieldName) {
        case 'email':
          if (!value) {
            errors.email = 'Email is required'
          } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            errors.email = 'Please enter a valid email address'
          } else if (this.checkEmailDuplicate(value, excludeId)) {
            errors.email = 'This email is already registered'
          } else {
            delete errors.email
          }
          break

        case 'username':
          if (!value) {
            errors.username = 'Username is required'
          } else if (value.length < 3) {
            errors.username = 'Username must be at least 3 characters long'
          } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            errors.username = 'Username can only contain letters, numbers, and underscores'
          } else if (this.checkUsernameDuplicate(value, excludeId)) {
            errors.username = 'This username is already taken'
          } else {
            delete errors.username
          }
          break

        case 'full_name':
          if (!value) {
            errors.full_name = 'Full name is required'
          } else if (value.length < 2) {
            errors.full_name = 'Full name must be at least 2 characters long'
          } else {
            delete errors.full_name
          }
          break

        case 'password':
          if (!this.isEditMode) {
            if (!value) {
              errors.password = 'Password is required'
            } else if (value.length < 6) {
              errors.password = 'Password must be at least 6 characters long'
            } else {
              delete errors.password
            }
          }
          break

        case 'role':
          if (!value) {
            errors.role = 'Role is required'
          } else {
            delete errors.role
          }
          break
      }

      this.validationErrors = errors
      return !errors[fieldName]
    },

    validateForm() {
      this.validationErrors = {}
      
      const fieldsToValidate = ['email', 'username', 'full_name', 'role']
      if (!this.isEditMode) {
        fieldsToValidate.push('password')
      }
      
      for (const field of fieldsToValidate) {
        this.validateField(field, this.userForm[field])
      }

      return Object.keys(this.validationErrors).length === 0
    },

    clearValidation() {
      this.validationErrors = {}
    },

    // ============ ENHANCED DATA FETCHING WITH CACHING ============
    async fetchUsers(isAutoRefresh = false, isEmergencyReconnect = false) {
      if (this.loading && !isAutoRefresh && !isEmergencyReconnect) return
      
      // Check cache first
      if (!isEmergencyReconnect && this.cache.metadata.enabled) {
        const cachedUsers = this.cache.getUsers()
        if (cachedUsers && !isAutoRefresh) {
          this.users = cachedUsers
          this.applyFilters()
          console.log('✅ Users loaded from cache instantly')
          return
        }
      }

      this.loading = true
      if (!isEmergencyReconnect) {
        this.error = null
      }
      this.refreshStartTime = Date.now()
      
      try {
        const previousLength = this.users.length
        
        // Simulate progress updates
        const progressInterval = setInterval(() => {
          if (!this.loading) {
            clearInterval(progressInterval)
            return
          }
          
          const elapsed = Date.now() - this.refreshStartTime
          if (elapsed < 1000) {
            this.refreshProgress = 'Connecting to server...'
          } else if (elapsed < 2000) {
            this.refreshProgress = 'Fetching user data...'
          } else {
            this.refreshProgress = 'Processing user roles...'
          }
        }, 500)
        
        console.log(`📡 Fetching users from API... (${isAutoRefresh ? 'auto-refresh' : isEmergencyReconnect ? 'emergency-reconnect' : 'manual'})`)
        const data = await apiService.getUsers()
        
        clearInterval(progressInterval)
        
        // Connection health tracking
        this.connectionLost = false
        this.consecutiveErrors = 0
        this.lastSuccessfulLoad = Date.now()
        this.error = null
        
        // Smart refresh rate adjustment
        this.trackActivityAndAdjustRefreshRate(data, previousLength)
        
        // Track new entries for highlighting
        if (isAutoRefresh && this.users.length > 0) {
          const existingIds = new Set(this.users.map(user => user._id))
          data.forEach(user => {
            if (!existingIds.has(user._id)) {
              this.newEntryIds.add(user._id)
              this.recentActivity.push({
                timestamp: Date.now(),
                userId: user._id
              })
            }
          })
          
          setTimeout(() => {
            this.newEntryIds.clear()
          }, 5000)
        }
        
        // Filter for admin and employee roles only
        const filteredUsers = data.filter(user => 
          user.role === 'admin' || user.role === 'employee'
        )
        
        // Store in cache
        if (this.cache.metadata.enabled) {
          this.cache.setUsers(filteredUsers)
        }
        
        this.users = filteredUsers
        this.applyFilters()
        this.lastRefresh = new Date()
        this.lastLoadTime = Date.now()
        
        console.log(`✅ Users loaded successfully: ${filteredUsers.length} users`)
        
      } catch (error) {
        console.error('❌ Error fetching users:', error)
        
        this.consecutiveErrors++
        this.error = this.getDetailedErrorMessage(error)
        
        if (this.consecutiveErrors >= 3) {
          this.connectionLost = true
          console.log('Connection marked as lost after 3 consecutive errors')
        }
        
        if (this.consecutiveErrors >= 2) {
          this.autoRefreshInterval = Math.min(this.baseRefreshInterval * 2, 120000) // Max 2 minutes
          console.log(`Slowing refresh rate to ${this.autoRefreshInterval / 1000}s due to errors`)
        }
        
        if (!isAutoRefresh) {
          this.users = []
          this.filteredUsers = []
        }
      } finally {
        this.loading = false
        this.refreshProgress = ''
      }
    },

    // Smart refresh rate adjustment based on activity
    trackActivityAndAdjustRefreshRate(newData, previousLength) {
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
        this.autoRefreshInterval = 10000 // High activity: 10 seconds
        console.log('High activity detected: refresh rate increased to 10s')
      } else if (recentCount >= 5) {
        this.autoRefreshInterval = 20000 // Medium activity: 20 seconds
        console.log('Medium activity detected: refresh rate set to 20s')
      } else if (recentCount === 0 && this.recentActivity.length === 0) {
        this.autoRefreshInterval = 60000 // No activity: 60 seconds
        console.log('No activity detected: refresh rate decreased to 60s')
      } else {
        this.autoRefreshInterval = this.baseRefreshInterval // Normal activity
      }
      
      // Restart auto-refresh with new interval if it's running
      if (this.autoRefreshEnabled && this.autoRefreshTimer) {
        this.startAutoRefresh()
      }
    },

    // Emergency reconnect method
    async emergencyReconnect() {
      console.log('Emergency reconnect initiated')
      this.consecutiveErrors = 0
      this.connectionLost = false
      await this.fetchUsers(false, true)
      
      if (!this.autoRefreshEnabled) {
        this.autoRefreshEnabled = true
        this.startAutoRefresh()
      }
    },

    // Connection status methods
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

    getDetailedErrorMessage(error) {
      if (error.name === 'NetworkError' || error.message.includes('fetch')) {
        return 'Network connection failed. Please check your internet connection and try again.'
      } else if (error.status === 401) {
        return 'Authentication failed. Please log in again.'
      } else if (error.status === 403) {
        return 'Access denied. You do not have permission to view user accounts.'
      } else if (error.status === 500) {
        return 'Server error occurred. Please try again later.'
      }
      return `Failed to load user accounts: ${error.message || 'Unknown error occurred'}`
    },

    // ============ AUTO-REFRESH SYSTEM ============
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
        this.fetchUsers(true)
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
      
      console.log('Auto-refresh stopped')
    },

    // ============ ENHANCED REFRESH SYSTEM ============
    async refreshData() {
      console.log('=== COMPREHENSIVE USER DATA REFRESH INITIATED ===')
      
      this.successMessage = null
      this.error = null
      
      const currentSelections = [...this.selectedUsers]
      const currentFilters = {
        role: this.roleFilter,
        status: this.statusFilter,
        search: this.searchFilter
      }
      
      console.log('Preserving current state:', {
        selections: currentSelections,
        filters: currentFilters
      })
      
      try {
        if (this.cache.metadata.enabled) {
          this.cache.clear()
          console.log('🗑️ Cache cleared for fresh data')
        }
        
        await this.fetchUsers(false)
        
        // Restore user selections
        this.selectedUsers = currentSelections.filter(userId => 
          this.users.some(user => user._id === userId)
        )
        
        // Restore filters
        this.roleFilter = currentFilters.role
        this.statusFilter = currentFilters.status
        this.searchFilter = currentFilters.search
        
        this.applyFilters()
        
        this.successMessage = `User data refreshed successfully. ${this.users.length} accounts loaded.`
        
        console.log('✅ Comprehensive refresh completed successfully')
        console.log('Final state:', {
          totalUsers: this.users.length,
          filteredUsers: this.filteredUsers.length,
          selectedUsers: this.selectedUsers.length
        })
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
        
      } catch (error) {
        console.error('❌ Comprehensive refresh failed:', error)
      }
    },

    // ============ CACHE MANAGEMENT METHODS ============
    formatCacheTime(timestamp) {
      if (!timestamp) return 'Never'
      
      const now = Date.now()
      const diff = now - timestamp
      const minutes = Math.floor(diff / 60000)
      const seconds = Math.floor((diff % 60000) / 1000)
      
      if (minutes > 0) {
        return `${minutes}m ${seconds}s ago`
      } else {
        return `${seconds}s ago`
      }
    },

    // ============ FILTER METHODS ============
    handleSearch() {
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout)
      }
      
      this.searchTimeout = setTimeout(() => {
        this.applyFilters()
      }, 300) // 300ms debounce
    },

    applyFilters() {
      console.log('Applying filters:', {
        role: this.roleFilter,
        status: this.statusFilter,
        search: this.searchFilter
      })
      
      let filtered = [...this.users]
      const originalCount = filtered.length

      // Role filter
      if (this.roleFilter !== 'all') {
        filtered = filtered.filter(user => user.role === this.roleFilter)
      }

      // Status filter
      if (this.statusFilter !== 'all') {
        filtered = filtered.filter(user => user.status === this.statusFilter)
      }

      // Search filter
      if (this.searchFilter.trim()) {
        const search = this.searchFilter.toLowerCase()
        filtered = filtered.filter(user => 
          user.full_name?.toLowerCase().includes(search) ||
          user.email?.toLowerCase().includes(search) ||
          user.username?.toLowerCase().includes(search)
        )
      }

      this.filteredUsers = filtered
      
      console.log(`Filters applied: ${originalCount} → ${filtered.length} users`)
    },

    clearFilters() {
      console.log('Clearing all filters')
      this.roleFilter = 'all'
      this.statusFilter = 'all'
      this.searchFilter = ''
      this.applyFilters()
      
      this.successMessage = 'Filters cleared successfully'
      setTimeout(() => {
        this.successMessage = null
      }, 2000)
    },

    clearSearch() {
      this.searchFilter = ''
      this.applyFilters()
      this.selectedUsers = []
    },

    highlightMatch(text, query) {
      if (!query || !text) return text
      
      const regex = new RegExp(`(${query})`, 'gi')
      return text.replace(regex, '<mark class="search-highlight">$1</mark>')
    },

    // ============ SELECTION METHODS ============
    selectAll(event) {
      if (event.target.checked) {
        this.selectedUsers = this.filteredUsers.map(user => user._id)
      } else {
        this.selectedUsers = []
      }
    },

    // ============ CRUD OPERATIONS ============
    async deleteSelected() {
      if (this.selectedUsers.length === 0) return
      
      const confirmed = confirm(`Are you sure you want to delete ${this.selectedUsers.length} user account(s)?`)
      if (!confirmed) return

      this.loading = true
      let successCount = 0
      let errorCount = 0

      for (const userId of this.selectedUsers) {
        try {
          await apiService.deleteUser(userId)
          successCount++
        } catch (error) {
          console.error(`Error deleting user ${userId}:`, error)
          errorCount++
        }
      }

      if (successCount > 0) {
        this.successMessage = `Successfully deleted ${successCount} user account(s)`
        if (errorCount > 0) {
          this.successMessage += ` (${errorCount} failed)`
        }
        this.selectedUsers = []
        
        this.cache.clear()
        await this.fetchUsers()
      } else {
        this.error = 'Failed to delete user accounts'
      }

      this.loading = false
      
      setTimeout(() => {
        this.successMessage = null
      }, 3000)
    },

    async deleteUser(user) {
      const confirmed = confirm(`Are you sure you want to delete user account "${user.username}"?`)
      if (!confirmed) return

      try {
        await apiService.deleteUser(user._id)
        this.successMessage = `User account "${user.username}" deleted successfully`
        
        this.cache.clear()
        await this.fetchUsers()
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error deleting user:', error)
        this.error = `Failed to delete user account: ${error.message}`
      }
    },

    async toggleUserStatus(user) {
      const newStatus = user.status === 'active' ? 'inactive' : 'active'
      const action = newStatus === 'active' ? 'activate' : 'deactivate'
      
      const confirmed = confirm(`Are you sure you want to ${action} user "${user.username}"?`)
      if (!confirmed) return

      try {
        await apiService.updateUser(user._id, { status: newStatus })
        this.successMessage = `User "${user.username}" ${action}d successfully`
        
        this.cache.clear()
        await this.fetchUsers()
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error updating user status:', error)
        this.error = `Failed to ${action} user: ${error.message}`
      }
    },

    // ============ MODAL METHODS ============
    showAddUserModal() {
      this.isEditMode = false
      this.userForm = {
        username: '',
        email: '',
        full_name: '',
        password: '',
        role: '',
        status: 'active'
      }
      this.formError = null
      this.clearValidation()
      this.showModal = true
    },

    editUser(user) {
      this.isEditMode = true
      this.selectedUser = user
      this.userForm = {
        username: user.username || '',
        email: user.email || '',
        full_name: user.full_name || '',
        password: '',
        role: user.role || '',
        status: user.status || 'active'
      }
      this.formError = null
      this.clearValidation()
      this.showViewModal = false
      this.showModal = true
    },

    viewUser(user) {
      this.selectedUser = user
      this.showViewModal = true
    },

    closeModal() {
      this.showModal = false
      this.isEditMode = false
      this.selectedUser = null
      this.formError = null
      this.clearValidation()
    },

    closeViewModal() {
      this.showViewModal = false
      this.selectedUser = null
    },

    async saveUser() {
      this.formLoading = true
      this.formError = null

      try {
        const isValid = this.validateForm()
        
        if (!isValid) {
          const errorMessages = Object.values(this.validationErrors)
          this.formError = errorMessages.join(', ')
          this.formLoading = false
          return
        }

        if (this.isEditMode) {
          const updateData = {
            username: this.userForm.username,
            email: this.userForm.email,
            full_name: this.userForm.full_name,
            role: this.userForm.role,
            status: this.userForm.status
          }
          
          await apiService.updateUser(this.selectedUser._id, updateData)
          this.successMessage = `User account "${this.userForm.username}" updated successfully`
        } else {
          await apiService.createUser(this.userForm)
          this.successMessage = `User account "${this.userForm.username}" created successfully`
        }

        this.closeModal()
        
        this.cache.clear()
        await this.fetchUsers()
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error saving user:', error)
        this.formError = error.message
      } finally {
        this.formLoading = false
      }
    },

    // ============ UTILITY METHODS ============
    exportData() {
      this.exporting = true
      
      try {
        const headers = ['ID', 'Username', 'Full Name', 'Email', 'Role', 'Status', 'Last Login', 'Date Created']
        const csvContent = [
          headers.join(','),
          ...this.filteredUsers.map(user => [
            user._id.slice(-6),
            user.username,
            user.full_name,
            user.email,
            user.role,
            user.status,
            this.formatDate(user.last_login),
            this.formatDate(user.date_created)
          ].join(','))
        ].join('\n')

        const blob = new Blob([csvContent], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `user_accounts_${new Date().toISOString().split('T')[0]}.csv`
        a.click()
        window.URL.revokeObjectURL(url)
      } finally {
        this.exporting = false
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'Never'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  },

  async mounted() {
    console.log('=== ACCOUNTS COMPONENT MOUNTED ===')
    await this.fetchUsers()
    
    // Start auto-refresh
    if (this.autoRefreshEnabled) {
      this.startAutoRefresh()
    }
    
    console.log('✅ Component initialization complete')
  },

  beforeUnmount() {
    this.stopAutoRefresh()
    
    if (this.searchTimeout) {
      clearTimeout(this.searchTimeout)
    }
    
    console.log('🧹 Component cleanup complete')
  }
}
</script>

<style scoped>
.accounts-page {
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

/* Auto-refresh status indicator (same as logs page) */
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

/* Connection indicator (same as logs page) */
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

/* New entry highlighting */
.new-entry {
  background-color: #f0fdf4 !important;
  border-left: 4px solid #10b981 !important;
  animation: highlight-fade 5s ease-out;
}

@keyframes highlight-fade {
  0% { 
    background-color: #dcfce7;
    border-left-color: #22c55e;
  }
  100% { 
    background-color: #f0fdf4;
    border-left-color: #10b981;
  }
}

/* Search highlighting */
.search-highlight {
  background-color: #fef3c7;
  color: #92400e;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-weight: 500;
}

.email-column {
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #64748b;
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

.btn-success {
  background-color: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #059669;
}

.btn-warning {
  background-color: #f59e0b;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background-color: #d97706;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #dc2626;
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
  font-size: 0.8125rem;
  border-radius: 0.25rem;
}

.btn-outline-secondary {
  color: #6c757d;
  border: 1px solid #6c757d;
  background-color: transparent;
}

.btn-outline-secondary:hover:not(:disabled) {
  color: #fff;
  background-color: #6c757d;
  border-color: #6c757d;
}

.btn-outline-success {
  color: #10b981;
  border: 1px solid #10b981;
  background-color: transparent;
}

.btn-outline-success:hover:not(:disabled) {
  color: #fff;
  background-color: #10b981;
  border-color: #10b981;
}

.btn-outline-info {
  color: #06b6d4;
  border: 1px solid #06b6d4;
  background-color: transparent;
}

.btn-outline-info:hover:not(:disabled) {
  color: #fff;
  background-color: #06b6d4;
  border-color: #06b6d4;
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
  position: relative;
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
  transition: all 0.2s ease;
}

.filter-group select:focus,
.filter-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.clear-search-btn {
  position: absolute;
  right: 8px;
  top: 32px;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
  font-size: 1.25rem;
  line-height: 1;
}

.clear-search-btn:hover {
  color: #6b7280;
  background-color: #f3f4f6;
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

.success-message {
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #16a34a;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
  text-align: center;
}

.refresh-indicator {
  margin-bottom: 1rem;
}

/* Cache status */
.cache-status {
  margin-bottom: 1rem;
}

/* Column width definitions */
.checkbox-column {
  width: 40px;
  text-align: center;
}

.id-column {
  width: 80px;
  font-weight: 500;
  color: #6366f1;
  font-family: monospace;
}

.username-column {
  max-width: 100px;
  font-weight: 500;
  color: #1e293b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.name-column {
  width: 100px;
  max-width: 120px;
  color: #1e293b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.email-column {
  width: 100px;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.role-column, .status-column {
  width: 100px;
}

.role-badge, .status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.role-badge.role-admin {
  background-color: #fef3c7;
  color: #92400e;
}

.role-badge.role-employee {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-badge.status-active {
  background-color: #dcfce7;
  color: #166534;
}

.status-badge.status-inactive {
  background-color: #fee2e2;
  color: #991b1b;
}

.login-column, .date-column {
  color: #64748b;
  width: 140px;
  font-size: 0.8125rem;
}

.actions-column {
  width: 160px;
  text-align: center;
  vertical-align: middle;
}

/* Action Button Styles */
.btn-xs {
  padding: 0.25rem 0.4rem;
  font-size: 0.75rem;
  line-height: 1;
  border-radius: 0.375rem;
}

.btn-icon-only {
  padding: 0.35rem;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 1px solid;
}

.btn-outline-secondary {
  color: #6b7280;
  border-color: #d1d5db;
  background-color: transparent;
}

.btn-outline-secondary:hover:not(:disabled) {
  color: #374151;
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

.btn-outline-primary {
  color: #3b82f6;
  border-color: #93c5fd;
  background-color: transparent;
}

.btn-outline-primary:hover:not(:disabled) {
  color: #ffffff;
  background-color: #3b82f6;
  border-color: #3b82f6;
}

.btn-outline-success {
  color: #10b981;
  border-color: #86efac;
  background-color: transparent;
}

.btn-outline-success:hover:not(:disabled) {
  color: #ffffff;
  background-color: #10b981;
  border-color: #10b981;
}

.btn-outline-warning {
  color: #f59e0b;
  border-color: #fcd34d;
  background-color: transparent;
}

.btn-outline-danger {
  color: #ef4444;
  border-color: #fca5a5;
  background-color: transparent;
}

.btn-outline-danger:hover:not(:disabled) {
  color: #ffffff;
  background-color: #ef4444;
  border-color: #ef4444;
}

.action-buttons {
  display: flex;
  justify-content: center;
  align-items: center;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #64748b;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

/* Modal Styles */
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
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h2 {
  margin-bottom: 1.5rem;
  color: #1f2937;
}

.user-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group label {
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group input:disabled,
.form-group select:disabled {
  background-color: #f9fafb;
  cursor: not-allowed;
}

/* Validation Styles */
.form-group input.error,
.form-group select.error {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.form-group input.error:focus,
.form-group select.error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
}

.field-error {
  color: #ef4444;
  font-size: 0.75rem;
  margin-top: 0.25rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.field-error::before {
  content: "⚠";
  font-size: 0.875rem;
}

.validation-loading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0.5rem 0;
}

.validation-loading::before {
  content: "";
  width: 16px;
  height: 16px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.form-error {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  margin: 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-error::before {
  content: "❌";
  font-size: 1rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.form-actions button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  border: 1px solid #d1d5db;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.form-actions button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #e5e7eb;
  color: #9ca3af;
}

.form-actions button.btn-primary {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.form-actions button.btn-primary:disabled {
  background-color: #e5e7eb;
  color: #9ca3af;
  border-color: #e5e7eb;
}

.form-actions button:hover:not(:disabled) {
  background-color: #f9fafb;
}

.form-actions button.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.detail-row strong {
  min-width: 120px;
  color: #374151;
}

/* Custom checkbox styling */
input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #4f46e5;
  cursor: pointer;
}

/* Enhanced Alert Styles */
.alert {
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
  border: 1px solid transparent;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.alert-success {
  color: #0f5132;
  background-color: #d1e7dd;
  border-color: #badbcc;
}

.alert-danger {
  color: #842029;
  background-color: #f8d7da;
  border-color: #f5c2c7;
}

.alert-info {
  color: #055160;
  background-color: #d1ecf1;
  border-color: #b8daff;
}

.alert-warning {
  color: #664d03;
  background-color: #fff3cd;
  border-color: #ffecb5;
}

.d-flex {
  display: flex !important;
}

.align-items-center {
  align-items: center !important;
}

.justify-content-between {
  justify-content: space-between !important;
}

.justify-content-center {
  justify-content: center !important;
}

.gap-2 {
  gap: 0.5rem !important;
}

.me-2 {
  margin-right: 0.5rem !important;
}

.ms-2 {
  margin-left: 0.5rem !important;
}

.mt-3 {
  margin-top: 1rem !important;
}

.mb-3 {
  margin-bottom: 1rem !important;
}

.py-5 {
  padding-top: 3rem !important;
  padding-bottom: 3rem !important;
}

.text-center {
  text-align: center !important;
}

.text-success {
  color: #198754 !important;
}

.text-warning {
  color: #ffc107 !important;
}

.text-danger {
  color: #dc3545 !important;
}

.text-muted {
  color: #6c757d !important;
}

.spinner-border {
  display: inline-block;
  width: 2rem;
  height: 2rem;
  vertical-align: text-bottom;
  border: 0.25em solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spinner-border 0.75s linear infinite;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.2em;
}

@keyframes spinner-border {
  to { transform: rotate(360deg); }
}

.visually-hidden {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  white-space: nowrap !important;
  border: 0 !important;
}

.card {
  position: relative;
  display: flex;
  flex-direction: column;
  min-width: 0;
  word-wrap: break-word;
  background-color: #fff;
  background-clip: border-box;
  border: 1px solid rgba(0, 0, 0, 0.125);
  border-radius: 0.375rem;
}

.card-body {
  flex: 1 1 auto;
  padding: 1rem;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .accounts-page {
    padding: 1rem;
  }

  .filters-section {
    grid-template-columns: 1fr;
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

  .form-row {
    grid-template-columns: 1fr;
  }

  .modal-content {
    padding: 1.5rem;
  }

  .filters-section {
    padding: 1rem;
  }

  .field-error {
    font-size: 0.7rem;
  }
  
  .validation-loading {
    font-size: 0.8125rem;
  }
  
  .form-error {
    font-size: 0.8125rem;
    padding: 0.5rem;
  }

  .auto-refresh-status {
    flex-direction: column;
    text-align: center;
    gap: 0.25rem;
    min-width: auto;
  }

  .connection-indicator {
    order: -1;
  }
}

@media (max-width: 640px) {
  .header-actions {
    grid-template-columns: repeat(2, 1fr);
    display: grid;
    gap: 0.5rem;
  }

  .btn {
    font-size: 0.75rem;
    padding: 0.5rem 0.75rem;
  }

  .auto-refresh-status {
    grid-column: span 2;
  }

  .connection-indicator {
    grid-column: span 2;
  }
}
</style>
