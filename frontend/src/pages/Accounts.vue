<template>
  <div class="accounts-page">
    <!-- Header Section -->
    <div class="page-header">
      <h1 class="page-title">User Accounts</h1>
      <div class="header-actions">
        <button 
          class="btn btn-secondary" 
          @click="deleteSelected" 
          :disabled="selectedUsers.length === 0 || loading"
        >
          Delete Selected ({{ selectedUsers.length }})
        </button>
        <button class="btn btn-success" @click="showAddUserModal">
          Add User
        </button>
        <button class="btn btn-primary" @click="exportData">
          Export
        </button>
        <button class="btn btn-info" @click="refreshData" :disabled="loading">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-group">
        <label for="roleFilter">Filter by Role:</label>
        <select id="roleFilter" v-model="roleFilter" @change="applyFilters">
          <option value="all">All Roles</option>
          <option value="admin">Admin</option>
          <option value="employee">Employee</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label for="statusFilter">Filter by Status:</label>
        <select id="statusFilter" v-model="statusFilter" @change="applyFilters">
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
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && users.length === 0" class="loading-state">
      <p>Loading user accounts...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-state">
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="refreshData">Try Again</button>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
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
            />
          </th>
          <th style="padding-left: 30px;">ID</th>
          <th>Username</th>
          <th>Full Name</th>
          <th>Email</th>
          <th>Role</th>
          <th>Status</th>
          <th>Last Login</th>
          <th>Date Created</th>
          <th class="actions-column" style="padding-left: 50px;">Actions</th>
        </tr>
      </template>

      <template #body>
        <tr 
          v-for="user in filteredUsers" 
          :key="user._id"
          :class="{ 
            'selected': selectedUsers.includes(user._id),
            'inactive': user.status === 'inactive'
          }"
        >
          <td class="checkbox-column">
            <input 
              type="checkbox" 
              :value="user._id"
              v-model="selectedUsers"
            />
          </td>
          <td class="id-column">{{ user._id.slice(-6) }}</td>
          <td class="username-column">{{ user.username }}</td>
          <td class="name-column">{{ user.full_name }}</td>
          <td class="email-column">{{ user.email }}</td>
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
              <button class="action-btn" @click="editUser(user)" title="Edit">
                ✏️
              </button>
              <button class="action-btn" @click="viewUser(user)" title="View">
                👁️
              </button>
              <button 
                class="action-btn"
                @click="toggleUserStatus(user)" 
                :title="user.status === 'active' ? 'Deactivate' : 'Activate'"
              >
                {{ user.status === 'active' ? '🔒' : '🔓' }}
              </button>
              <button class="action-btn delete" @click="deleteUser(user)" title="Delete">
                🗑️
              </button>
            </div>
          </td>
        </tr>
      </template>
    </DataTable>

    <!-- Empty State -->
    <div v-if="!loading && filteredUsers.length === 0 && !error" class="empty-state">
      <p>{{ users.length === 0 ? 'No user accounts found' : 'No users match the current filters' }}</p>
      <button v-if="users.length === 0" class="btn btn-primary" @click="showAddUserModal">
        Add First User
      </button>
      <button v-else class="btn btn-secondary" @click="clearFilters">
        Clear Filters
      </button>
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
import DataTable from '../components/TableTemplate.vue'

export default {
  name: 'AccountsPage',
  components: {
    DataTable
  },
  data() {
    return {
      users: [],
      filteredUsers: [],
      selectedUsers: [],
      loading: false,
      error: null,
      successMessage: null,
      
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
    async fetchUsers() {
      this.loading = true
      this.error = null
      
      try {
        console.log('Fetching users from API...')
        const data = await apiService.getUsers()
        
        // Filter for admin and employee roles only
        this.users = data.filter(user => 
          user.role === 'admin' || user.role === 'employee'
        )
        
        this.applyFilters()
        console.log('Users loaded:', this.users)
      } catch (error) {
        console.error('Error fetching users:', error)
        this.error = `Failed to load user accounts: ${error.message}`
      } finally {
        this.loading = false
      }
    },

    applyFilters() {
      let filtered = [...this.users]

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
    },

    clearFilters() {
      this.roleFilter = 'all'
      this.statusFilter = 'all'
      this.searchFilter = ''
      this.applyFilters()
    },

    async refreshData() {
      this.successMessage = null
      await this.fetchUsers()
    },

    selectAll(event) {
      if (event.target.checked) {
        this.selectedUsers = this.filteredUsers.map(user => user._id)
      } else {
        this.selectedUsers = []
      }
    },

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
        await this.fetchUsers()
      } else {
        this.error = 'Failed to delete user accounts'
      }

      this.loading = false
      
      // Clear success message after 3 seconds
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
        await this.fetchUsers()
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error updating user status:', error)
        this.error = `Failed to ${action} user: ${error.message}`
      }
    },

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

    exportData() {
      // Export users to CSV
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
    console.log('Accounts component mounted')
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

.filters-section {
  background: white;
  padding: 1.5rem;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
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

.btn {
  padding: 0.5rem 1.25rem;
  border-radius: 0.5rem;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
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

.btn-info {
  background-color: #06b6d4;
  color: white;
}

.btn-info:hover:not(:disabled) {
  background-color: #0891b2;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  font-weight: 500;
  color: #1e293b;
}

.name-column {
  color: #1e293b;
}

.email-column {
  color: #64748b;
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
  width: 140px;
  text-align: center;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
  justify-content: center;
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
  background-color: #e2e8f0;
}

.action-btn.delete:hover {
  background-color: #fee2e2;
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
</style>