<template>
  <div class="accounts-page">
    <!-- Header Section -->
    <div class="page-header">
      <h1 class="page-title">User Management</h1>
      <div class="header-actions">
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
          <i class="bi bi-download"></i> {{ exporting ? 'Exporting...' : 'Export' }}
        </button>
        <button class="btn btn-warning" @click="refreshData" :disabled="loading">
          <i class="bi bi-arrow-clockwise" :class="{ 'spinning': loading }"></i>
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>
    </div>

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
          @input="applyFilters"
          type="text" 
          placeholder="Search by name, email, or username..."
          :disabled="loading"
        />
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
        <button class="btn btn-primary" @click="refreshData" :disabled="loading">
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
            'refreshing': loading
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
          <td class="username-column">{{ user.username }}</td>
          <td class="name-column" :title="user.full_name">{{ user.full_name }}</td>
          <td class="email-column" :title="user.email">{{ user.email }}</td>
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
            {{ users.length === 0 ? 'No user accounts found' : 'No users match the current filters' }}
          </p>
          <button v-if="users.length === 0" class="btn btn-primary" @click="showAddUserModal">
            <i class="bi bi-person-plus"></i>
            Add First User
          </button>
          <div v-else class="d-flex gap-2 justify-content-center">
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

    <!-- User Modal (Add/Edit) -->
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
                :disabled="formLoading || isEditMode"
                placeholder="Enter username"
              />
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
              />
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
            />
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
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="role">Role:</label>
              <select 
                id="role"
                v-model="userForm.role" 
                required 
                :disabled="formLoading"
              >
                <option value="">Select Role</option>
                <option value="admin">Admin</option>
                <option value="employee">Employee</option>
              </select>
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

          <div v-if="formError" class="form-error">
            {{ formError }}
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" :disabled="formLoading">
              Cancel
            </button>
            <button type="submit" :disabled="formLoading" class="btn-primary">
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
    }
  },
  methods: {
    // ================================================================
    // DATA FETCHING
    // ================================================================
    async fetchUsers() {
      this.loading = true
      this.error = null
      this.refreshStartTime = Date.now()
      
      try {
        console.log('=== Fetching Users from API ===')
        this.refreshProgress = 'Connecting to server...'
        
        // Simulate progress updates
        const progressInterval = setInterval(() => {
          if (!this.loading) {
            clearInterval(progressInterval)
            return
          }
          
          const elapsed = Date.now() - this.refreshStartTime
          if (elapsed < 1000) {
            this.refreshProgress = 'Fetching user data...'
          } else if (elapsed < 2000) {
            this.refreshProgress = 'Processing user roles...'
          } else {
            this.refreshProgress = 'Finalizing data...'
          }
        }, 500)
        
        const data = await apiService.getUsers()
        
        // Clear progress interval
        clearInterval(progressInterval)
        
        console.log('Raw API Response:', data)
        
        // Filter for admin and employee roles only
        this.users = data.filter(user => 
          user.role === 'admin' || user.role === 'employee'
        )
        
        console.log('Filtered Users:', this.users)
        console.log('Total Users Loaded:', this.users.length)
        
        // Apply current filters to maintain user's view
        this.applyFilters()
        
        // Update last refresh timestamp
        this.lastRefresh = new Date()
        
        // Clear any existing errors
        this.error = null
        
        console.log('✅ Users successfully loaded and filtered')
        
      } catch (error) {
        console.error('❌ Error fetching users:', error)
        this.error = `Failed to load user accounts: ${error.message || 'Unknown error occurred'}`
        
        // Provide more specific error messages
        if (error.name === 'NetworkError' || error.message.includes('fetch')) {
          this.error = 'Network connection failed. Please check your internet connection and try again.'
        } else if (error.status === 401) {
          this.error = 'Authentication failed. Please log in again.'
        } else if (error.status === 403) {
          this.error = 'Access denied. You do not have permission to view user accounts.'
        } else if (error.status === 500) {
          this.error = 'Server error occurred. Please try again later.'
        }
        
      } finally {
        this.loading = false
        this.refreshProgress = ''
      }
    },

    async refreshData() {
      console.log('=== COMPREHENSIVE DATA REFRESH INITIATED ===')
      
      // Clear any existing messages
      this.successMessage = null
      this.error = null
      
      // Preserve current user selections and filters
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
        // Fetch fresh user data
        await this.fetchUsers()
        
        // Restore user selections (only valid ones)
        this.selectedUsers = currentSelections.filter(userId => 
          this.users.some(user => user._id === userId)
        )
        
        // Restore filters
        this.roleFilter = currentFilters.role
        this.statusFilter = currentFilters.status
        this.searchFilter = currentFilters.search
        
        // Reapply filters
        this.applyFilters()
        
        // Show success message
        this.successMessage = `User data refreshed successfully. ${this.users.length} accounts loaded.`
        
        console.log('✅ Comprehensive refresh completed successfully')
        console.log('Final state:', {
          totalUsers: this.users.length,
          filteredUsers: this.filteredUsers.length,
          selectedUsers: this.selectedUsers.length
        })
        
        // Auto-clear success message
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
        
      } catch (error) {
        console.error('❌ Comprehensive refresh failed:', error)
        // Error is already handled in fetchUsers()
      }
    },

    // ================================================================
    // FILTER METHODS
    // ================================================================
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
      
      // Show feedback
      this.successMessage = 'Filters cleared successfully'
      setTimeout(() => {
        this.successMessage = null
      }, 2000)
    },

    // ================================================================
    // SELECTION METHODS
    // ================================================================
    selectAll(event) {
      if (event.target.checked) {
        this.selectedUsers = this.filteredUsers.map(user => user._id)
      } else {
        this.selectedUsers = []
      }
    },

    // ================================================================
    // CRUD OPERATIONS
    // ================================================================
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
        await this.refreshData()
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
        await this.refreshData()
        
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
        await this.refreshData()
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error updating user status:', error)
        this.error = `Failed to ${action} user: ${error.message}`
      }
    },

    // ================================================================
    // MODAL METHODS
    // ================================================================
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
      this.showModal = true
    },

    editUser(user) {
      this.isEditMode = true
      this.selectedUser = user
      this.userForm = {
        username: user.username || '',
        email: user.email || '',
        full_name: user.full_name || '',
        password: '', // Don't pre-fill password
        role: user.role || '',
        status: user.status || 'active'
      }
      this.formError = null
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
    },

    closeViewModal() {
      this.showViewModal = false
      this.selectedUser = null
    },

    async saveUser() {
      this.formLoading = true
      this.formError = null

      try {
        if (this.isEditMode) {
          // Update existing user (exclude password and username from updates)
          const updateData = {
            email: this.userForm.email,
            full_name: this.userForm.full_name,
            role: this.userForm.role,
            status: this.userForm.status
          }
          
          await apiService.updateUser(this.selectedUser._id, updateData)
          this.successMessage = `User account "${this.userForm.username}" updated successfully`
        } else {
          // Create new user
          await apiService.createUser(this.userForm)
          this.successMessage = `User account "${this.userForm.username}" created successfully`
        }

        this.closeModal()
        await this.refreshData()
        
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

    // ================================================================
    // UTILITY METHODS
    // ================================================================
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
    console.log('=== Accounts component mounted ===')
    await this.fetchUsers()
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
}

.email-column {
  width: 160px;
  max-width: 160px;
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

.btn-outline-warning:hover:not(:disabled) {
  color: #ffffff;
  background-color: #f59e0b;
  border-color: #f59e0b;
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

.form-error {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
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

.form-actions button.btn-primary {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
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
}
</style>