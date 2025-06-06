<template>
  <div class="customers-page">
    <!-- Header Section -->
    <div class="page-header">
      <!-- Search Bar replacing the title -->
      <div class="search-section">
        <div class="search-container">
          <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
            <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
            <path d="21 21l-4.35-4.35" stroke="currentColor" stroke-width="2"/>
          </svg>
          <input 
            v-model="searchQuery"
            @input="handleSearch"
            type="text" 
            class="search-input"
            placeholder="Search customers by name, email, phone, or address..."
          />
          <button 
            v-if="searchQuery" 
            @click="clearSearch" 
            class="clear-search-btn"
            title="Clear search"
          >
            ✕
          </button>
        </div>
        <div v-if="searchQuery" class="search-results-info">
          Showing {{ filteredCustomers.length }} of {{ customers.length }} customers
        </div>
      </div>
      
      <div class="header-actions">
        <button 
          class="btn btn-secondary" 
          @click="deleteSelected" 
          :disabled="selectedCustomers.length === 0 || loading"
        >
          Delete Selected ({{ selectedCustomers.length }})
        </button>
        <button class="btn btn-success" @click="showAddCustomerModal">
          Add Customer
        </button>
        <button class="btn btn-primary" @click="exportData">
          Export
        </button>
        <button class="btn btn-info" @click="refreshData" :disabled="loading">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && customers.length === 0" class="loading-state">
      <p>Loading customers...</p>
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

    <!-- Table Container -->
    <div v-if="!loading || customers.length > 0" class="table-container">
      <table class="customers-table">
        <thead>
          <tr>
            <th class="checkbox-column">
              <input 
                type="checkbox" 
                @change="selectAll" 
                :checked="allSelected"
                :indeterminate="someSelected"
              />
            </th>
            <th style="padding-left: 57px;">ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Delivery Address</th>
            <th>Loyalty Points</th>
            <th>Date Created</th>
            <th class="actions-column">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="customer in filteredCustomers" 
            :key="customer._id || customer.customer_id"
            :class="{ 'selected': selectedCustomers.includes(customer._id || customer.customer_id) }"
          >
            <td class="checkbox-column">
              <input 
                type="checkbox" 
                :value="customer._id || customer.customer_id"
                v-model="selectedCustomers"
              />
            </td>
            <td class="id-column" :title="customer.customer_id || customer._id">
              {{ (customer.customer_id || customer._id).slice(-6) }}
            </td>
            <td class="name-column">
              <span v-html="highlightMatch(customer.full_name, searchQuery)"></span>
            </td>
            <td class="email-column">
              <span v-html="highlightMatch(customer.email, searchQuery)"></span>
            </td>
            <td class="phone-column">
              <span v-html="highlightMatch(customer.phone || 'N/A', searchQuery)"></span>
            </td>
            <td class="address-column">
              <span v-html="highlightMatch(formatAddress(customer.delivery_address), searchQuery)"></span>
            </td>
            <td class="points-column">{{ customer.loyalty_points || 0 }}</td>
            <td class="date-column">{{ formatDate(customer.date_created) }}</td>
            <td class="actions-column">
              <div class="action-buttons">
                <button class="action-btn" @click="editCustomer(customer)" title="Edit">
                  ✏️
                </button>
                <button class="action-btn" @click="viewCustomer(customer)" title="View">
                  👁️
                </button>
                <button class="action-btn delete" @click="deleteCustomer(customer)" title="Delete">
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && filteredCustomers.length === 0 && !error" class="empty-state">
      <p v-if="searchQuery">No customers found matching "{{ searchQuery }}"</p>
      <p v-else>No customers found</p>
      <button v-if="!searchQuery" class="btn btn-primary" @click="showAddCustomerModal">
        Add First Customer
      </button>
      <button v-else class="btn btn-secondary" @click="clearSearch">
        Clear Search
      </button>
    </div>

    <!-- Customer Modal (Add/Edit) -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h2>{{ isEditMode ? 'Edit Customer' : 'Add New Customer' }}</h2>
        
        <form @submit.prevent="saveCustomer" class="customer-form">
          <div class="form-group">
            <label for="full_name">Full Name:</label>
            <input 
              id="full_name"
              v-model="customerForm.full_name" 
              type="text" 
              required 
              :disabled="formLoading"
            />
          </div>

          <div class="form-group">
            <label for="email">Email:</label>
            <input 
              id="email"
              v-model="customerForm.email" 
              type="email" 
              required 
              :disabled="formLoading"
            />
          </div>

          <div class="form-group">
            <label for="phone">Phone:</label>
            <input 
              id="phone"
              v-model="customerForm.phone" 
              type="tel" 
              :disabled="formLoading"
            />
          </div>

          <div class="form-group">
            <label for="street">Street Address:</label>
            <input 
              id="street"
              v-model="customerForm.delivery_address.street" 
              type="text" 
              :disabled="formLoading"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="city">City:</label>
              <input 
                id="city"
                v-model="customerForm.delivery_address.city" 
                type="text" 
                :disabled="formLoading"
              />
            </div>

            <div class="form-group">
              <label for="postal_code">Postal Code:</label>
              <input 
                id="postal_code"
                v-model="customerForm.delivery_address.postal_code" 
                type="text" 
                :disabled="formLoading"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="loyalty_points">Loyalty Points:</label>
            <input 
              id="loyalty_points"
              v-model.number="customerForm.loyalty_points" 
              type="number" 
              min="0"
              :disabled="formLoading"
            />
          </div>

          <div v-if="formError" class="form-error">
            {{ formError }}
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" :disabled="formLoading">
              Cancel
            </button>
            <button type="submit" :disabled="formLoading" class="btn-primary">
              {{ formLoading ? 'Saving...' : (isEditMode ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- View Customer Modal -->
    <div v-if="showViewModal" class="modal-overlay" @click="closeViewModal">
      <div class="modal-content" @click.stop>
        <h2>Customer Details</h2>
        <div class="customer-details" v-if="selectedCustomer">
          <div class="detail-row">
            <strong>ID:</strong> {{ selectedCustomer.customer_id || selectedCustomer._id }}
          </div>
          <div class="detail-row">
            <strong>Name:</strong> {{ selectedCustomer.full_name }}
          </div>
          <div class="detail-row">
            <strong>Email:</strong> {{ selectedCustomer.email }}
          </div>
          <div class="detail-row">
            <strong>Phone:</strong> {{ selectedCustomer.phone || 'N/A' }}
          </div>
          <div class="detail-row">
            <strong>Address:</strong> {{ formatAddress(selectedCustomer.delivery_address) }}
          </div>
          <div class="detail-row">
            <strong>Loyalty Points:</strong> {{ selectedCustomer.loyalty_points || 0 }}
          </div>
          <div class="detail-row">
            <strong>Status:</strong> {{ selectedCustomer.status || 'active' }}
          </div>
          <div class="detail-row">
            <strong>Date Created:</strong> {{ formatDate(selectedCustomer.date_created) }}
          </div>
          <div class="detail-row">
            <strong>Last Updated:</strong> {{ formatDate(selectedCustomer.last_updated) }}
          </div>
        </div>
        <div class="form-actions">
          <button @click="closeViewModal">Close</button>
          <button @click="editCustomer(selectedCustomer)" class="btn-primary">Edit</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiService from '../services/api.js'

export default {
  name: 'CustomersPage',
  data() {
    return {
      customers: [],
      filteredCustomers: [],
      selectedCustomers: [],
      loading: false,
      error: null,
      successMessage: null,
      searchQuery: '',
      
      // Modal states
      showModal: false,
      showViewModal: false,
      isEditMode: false,
      formLoading: false,
      formError: null,
      selectedCustomer: null,
      
      // Customer form data
      customerForm: {
        full_name: '',
        email: '',
        phone: '',
        delivery_address: {
          street: '',
          city: '',
          postal_code: ''
        },
        loyalty_points: 0
      }
    }
  },
  computed: {
    allSelected() {
      return this.filteredCustomers.length > 0 && this.selectedCustomers.length === this.filteredCustomers.length
    },
    someSelected() {
      return this.selectedCustomers.length > 0 && this.selectedCustomers.length < this.filteredCustomers.length
    }
  },
  methods: {
    async fetchCustomers() {
      this.loading = true
      this.error = null
      
      try {
        console.log('Fetching customers from API...')
        const data = await apiService.getCustomers()
        this.customers = data
        this.filteredCustomers = data
        console.log('Customers loaded:', data)
      } catch (error) {
        console.error('Error fetching customers:', error)
        this.error = `Failed to load customers: ${error.message}`
      } finally {
        this.loading = false
      }
    },

    handleSearch() {
      if (!this.searchQuery.trim()) {
        this.filteredCustomers = this.customers
        return
      }

      const query = this.searchQuery.toLowerCase()
      this.filteredCustomers = this.customers.filter(customer => {
        const fullName = (customer.full_name || '').toLowerCase()
        const email = (customer.email || '').toLowerCase()
        const phone = (customer.phone || '').toLowerCase()
        const address = this.formatAddress(customer.delivery_address).toLowerCase()
        
        return fullName.includes(query) ||
               email.includes(query) ||
               phone.includes(query) ||
               address.includes(query)
      })

      // Clear selections when searching
      this.selectedCustomers = []
    },

    clearSearch() {
      this.searchQuery = ''
      this.filteredCustomers = this.customers
      this.selectedCustomers = []
    },

    highlightMatch(text, query) {
      if (!query || !text) return text
      
      const regex = new RegExp(`(${query})`, 'gi')
      return text.replace(regex, '<mark class="search-highlight">$1</mark>')
    },

    async refreshData() {
      this.successMessage = null
      await this.fetchCustomers()
      this.handleSearch() // Reapply search after refresh
    },

    selectAll(event) {
      if (event.target.checked) {
        this.selectedCustomers = this.filteredCustomers.map(customer => customer._id || customer.customer_id)
      } else {
        this.selectedCustomers = []
      }
    },

    async deleteSelected() {
      if (this.selectedCustomers.length === 0) return
      
      const confirmed = confirm(`Are you sure you want to delete ${this.selectedCustomers.length} customer(s)?`)
      if (!confirmed) return

      this.loading = true
      let successCount = 0
      let errorCount = 0

      for (const customerId of this.selectedCustomers) {
        try {
          await apiService.deleteCustomer(customerId)
          successCount++
        } catch (error) {
          console.error(`Error deleting customer ${customerId}:`, error)
          errorCount++
        }
      }

      if (successCount > 0) {
        this.successMessage = `Successfully deleted ${successCount} customer(s)`
        if (errorCount > 0) {
          this.successMessage += ` (${errorCount} failed)`
        }
        this.selectedCustomers = []
        await this.fetchCustomers()
      } else {
        this.error = 'Failed to delete customers'
      }

      this.loading = false
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        this.successMessage = null
      }, 3000)
    },

    async deleteCustomer(customer) {
      const confirmed = confirm(`Are you sure you want to delete customer "${customer.full_name}"?`)
      if (!confirmed) return

      try {
        await apiService.deleteCustomer(customer._id || customer.customer_id)
        this.successMessage = `Customer "${customer.full_name}" deleted successfully`
        await this.fetchCustomers()
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error deleting customer:', error)
        this.error = `Failed to delete customer: ${error.message}`
      }
    },

    showAddCustomerModal() {
      this.isEditMode = false
      this.customerForm = {
        full_name: '',
        email: '',
        phone: '',
        delivery_address: {
          street: '',
          city: '',
          postal_code: ''
        },
        loyalty_points: 0
      }
      this.formError = null
      this.showModal = true
    },

    editCustomer(customer) {
      this.isEditMode = true
      this.selectedCustomer = customer
      this.customerForm = {
        full_name: customer.full_name || '',
        email: customer.email || '',
        phone: customer.phone || '',
        delivery_address: {
          street: customer.delivery_address?.street || '',
          city: customer.delivery_address?.city || '',
          postal_code: customer.delivery_address?.postal_code || ''
        },
        loyalty_points: customer.loyalty_points || 0
      }
      this.formError = null
      this.showViewModal = false
      this.showModal = true
    },

    viewCustomer(customer) {
      this.selectedCustomer = customer
      this.showViewModal = true
    },

    closeModal() {
      this.showModal = false
      this.isEditMode = false
      this.selectedCustomer = null
      this.formError = null
    },

    closeViewModal() {
      this.showViewModal = false
      this.selectedCustomer = null
    },

    async saveCustomer() {
      this.formLoading = true
      this.formError = null

      try {
        if (this.isEditMode) {
          // Update existing customer
          const customerId = this.selectedCustomer._id || this.selectedCustomer.customer_id
          await apiService.updateCustomer(customerId, this.customerForm)
          this.successMessage = `Customer "${this.customerForm.full_name}" updated successfully`
        } else {
          // Create new customer
          await apiService.createCustomer(this.customerForm)
          this.successMessage = `Customer "${this.customerForm.full_name}" created successfully`
        }

        this.closeModal()
        await this.fetchCustomers()
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error saving customer:', error)
        this.formError = error.message
      } finally {
        this.formLoading = false
      }
    },

    exportData() {
      // Export filtered customers to CSV
      const headers = ['ID', 'Name', 'Email', 'Phone', 'Address', 'Loyalty Points', 'Date Created']
      const csvContent = [
        headers.join(','),
        ...this.filteredCustomers.map(customer => [
          customer.customer_id || customer._id,
          customer.full_name,
          customer.email,
          customer.phone || '',
          this.formatAddress(customer.delivery_address),
          customer.loyalty_points || 0,
          this.formatDate(customer.date_created)
        ].join(','))
      ].join('\n')

      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `customers_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      window.URL.revokeObjectURL(url)
    },

    formatAddress(address) {
      if (!address) return 'N/A'
      if (typeof address === 'string') return address
      
      const parts = []
      if (address.street) parts.push(address.street)
      if (address.city) parts.push(address.city)
      if (address.postal_code) parts.push(address.postal_code)
      
      return parts.length > 0 ? parts.join(', ') : 'N/A'
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    }
  },

  async mounted() {
  console.log('Customers component mounted')
  
  // Force scroll to top immediately
  window.scrollTo(0, 0)
  
  await this.fetchCustomers()
  
  // Ensure we're at top after data loads
  this.$nextTick(() => {
    window.scrollTo(0, 0)
  })
  }
}
</script>

<style scoped>
.customers-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  background-color: #f8fafc;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  gap: 2rem;
}

/* Search Section Styles */
.search-section {
  flex: 1;
  max-width: 500px;
}

.search-container {
  position: relative;
  display: flex;
  align-items: center;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.search-container:focus-within {
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.search-icon {
  color: #9ca3af;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 1rem;
  background: transparent;
  color: #1f2937;
}

.search-input::placeholder {
  color: #9ca3af;
}

.clear-search-btn {
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

.search-results-info {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
  padding-left: 1rem;
}

/* Search highlighting */
.search-highlight {
  background-color: #fef3c7;
  color: #92400e;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-shrink: 0;
}

.btn {
  padding: 0.5rem 1.25rem;
  border-radius: 0.5rem;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  white-space: nowrap;
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

.table-container {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.customers-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed; /* KEY: This forces columns to respect width settings */
}

.customers-table thead {
  background-color: #4f46e5;
  color: white;
}

.customers-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.875rem;
  letter-spacing: 0.025em;
}

.customers-table td {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.875rem;
}

.customers-table tbody tr:hover {
  background-color: #f8fafc;
}

.customers-table tbody tr.selected {
  background-color: #ede9fe;
}

/* Define exact column widths */
.customers-table th.checkbox-column,
.customers-table td.checkbox-column {
  width: 40px;
  text-align: center;
}

.customers-table th.id-column,
.customers-table td.id-column {
  width: 60px;
  font-weight: 500;
  color: #6366f1;
  font-family: monospace;
  text-align: center;
  font-size: 0.75rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.customers-table th.name-column,
.customers-table td.name-column {
  width: 18%;
  font-weight: 500;
  color: #1e293b;
}

.customers-table th.email-column,
.customers-table td.email-column {
  width: 20%;
  color: #64748b;
}

.customers-table th.phone-column,
.customers-table td.phone-column {
  width: 12%;
  color: #64748b;
}

.customers-table th.address-column,
.customers-table td.address-column {
  width: 20%;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.customers-table th.points-column,
.customers-table td.points-column {
  width: 80px;
  font-weight: 500;
  text-align: center;
  color: black;
}

.customers-table th.date-column,
.customers-table td.date-column {
  width: 100px;
  color: #64748b;
  font-size: 0.8125rem;
}

.customers-table th.actions-column,
.customers-table td.actions-column {
  width: 120px;
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
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h2 {
  margin-bottom: 1.5rem;
  color: #1f2937;
}

.customer-form {
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

.form-group input {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group input:disabled {
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

.customer-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  display: flex;
  gap: 1rem;
  color: black;
}

.detail-row strong {
  min-width: 120px;
  color: #374151;
}

/* Custom checkbox styling */
input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #8b5cf6;
  cursor: pointer;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .customers-page {
    padding: 1rem;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .customers-table {
    min-width: 900px;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .search-section {
    max-width: none;
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
  
  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.8125rem;
  }
  
  .customers-table th,
  .customers-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.8125rem;
  }
  
  .address-column {
    max-width: 150px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .modal-content {
    padding: 1.5rem;
  }

  .search-container {
    padding: 0.5rem 0.75rem;
  }

  .search-input {
    font-size: 0.875rem;
  }

  .search-results-info {
    text-align: center;
    padding-left: 0;
  }
}

@media (max-width: 480px) {
  .search-container {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .search-icon {
    align-self: flex-start;
    margin-right: 0;
  }

  .search-input::placeholder {
    font-size: 0.875rem;
  }
}
</style>