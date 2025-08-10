<template>
  <div class="customers-page">
    <div class="page-header">
      <h1 class="page-title">Customer Management</h1>
    </div>

    <!-- KPI Cards Row -->
    <div class="row g-4 mb-2">
      <div class="col-md-4">
        <CardTemplate
          title="Active Users"
          :value="activeUsersCount"
          subtitle="Total Active Users"
          size="md"
          value-color="success"
          border-color="success"
          border-position="start"
          shadow="sm"
        />
      </div>
      <div class="col-md-4">
        <CardTemplate
          title="Monthly New Users"
          :value="monthlyUsersCount"
          subtitle="This month's new users"
          size="md"
          value-color="primary"
          border-color="primary"
          border-position="start"
          shadow="sm"
        />
      </div>
      <div class="col-md-4">
        <CardTemplate
          title="Daily Customer Logins"
          :value="dailyUsersCount"
          subtitle="Last 24 hours"
          size="md"
          value-color="info"
          border-color="info"
          border-position="start"
          shadow="sm"
        />
      </div>
    </div>

    <!-- Header Section with Search and Actions -->
    <div class="search-section-wrapper">
      <div class="search-and-actions-row">
        <!-- Search Bar -->
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
        
        <!-- Action Buttons -->
        <div class="action-buttons-group">
          <!-- Auto-refresh status and controls -->
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
            :disabled="selectedCustomers.length === 0 || loading"
          >
            Delete Selected ({{ selectedCustomers.length }})
          </button>
          <button class="btn btn-success" @click="showAddCustomerModal">
            <Plus :size="16" />
            Add Customer
          </button>
          <button class="btn btn-primary" @click="exportData" :disabled="loading || exporting">
            <i class="bi bi-download"></i> {{ exporting ? 'Exporting...' : 'Export' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Refresh Progress Indicator -->
    <div v-if="loading && customers.length > 0" class="refresh-indicator">
      <div class="alert alert-info d-flex align-items-center" role="alert">
        <div class="spinner-border spinner-border-sm me-2" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        Refreshing customer data... {{ refreshProgress }}
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && customers.length === 0" class="loading-state">
      <div class="spinner-border text-primary"></div>
      <p>Loading customers...</p>
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

    <!-- Table -->
    <DataTable 
      v-if="!loading || customers.length > 0"
      :items-per-page="itemsPerPage"
      :total-items="filteredCustomers.length"
      :current-page="currentPage"
      @page-changed="handlePageChange"
    >
      <template #header>
        <tr>
          <th class="text-center" style="width: 50px;">
            <input 
              type="checkbox" 
              class="form-check-input"
              @change="selectAll" 
              :checked="allSelected"
              :indeterminate="someSelected"
            />
          </th>
          <th style="width: 80px;">ID</th>
          <th>Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Delivery Address</th>
          <th class="text-center" style="width: 100px;">Points</th>
          <th style="width: 120px;">Date Created</th>
          <th class="text-center" style="width: 130px;">Actions</th>
        </tr>
      </template>
      
      <template #body>
        <tr 
          v-for="customer in paginatedCustomers" 
          :key="customer._id || customer.customer_id"
          :class="{ 'table-primary': selectedCustomers.includes(customer._id || customer.customer_id) }"
        >
          <td class="text-center">
            <input 
              type="checkbox" 
              class="form-check-input"
              :value="customer._id || customer.customer_id"
              v-model="selectedCustomers"
            />
          </td>
          <td>
            <span class="badge bg-light text-primary" style="font-family: monospace;">
              {{ (customer.customer_id || customer._id).slice(-6) }}
            </span>
          </td>
          <td class="fw-medium" style="color: var(--tertiary-dark);">
            <span v-html="highlightMatch(customer.full_name, searchQuery)"></span>
          </td>
          <td style="color: var(--tertiary-medium);">
            <span v-html="highlightMatch(customer.email, searchQuery)"></span>
          </td>
          <td style="color: var(--tertiary-medium);">
            <span v-html="highlightMatch(customer.phone || 'N/A', searchQuery)"></span>
          </td>
          <td style="color: var(--tertiary-medium);">
            <span v-html="highlightMatch(formatAddress(customer.delivery_address), searchQuery)" 
                  :title="formatAddress(customer.delivery_address)"></span>
          </td>
          <td class="text-center">
            <span class="badge bg-success">{{ customer.loyalty_points || 0 }}</span>
          </td>
          <td style="color: var(--tertiary-medium); font-size: 0.875rem;">
            {{ formatDate(customer.date_created) }}
          </td>
          <td>
            <div class="d-flex justify-content-center gap-1">
              <button class="btn btn-outline-primary action-btn action-btn-edit" 
                      @click="editCustomer(customer)" 
                      title="Edit">
                <Edit :size="14" />
              </button>
              <button class="btn btn-outline-primary action-btn action-btn-view" 
                      @click="viewCustomer(customer)" 
                      title="View">
                <Eye :size="14" />
              </button>
              <button class="btn btn-outline-danger action-btn action-btn-delete" 
                      @click="deleteCustomer(customer)" 
                      title="Delete">
                <Trash2 :size="14" />
              </button>
            </div>
          </td>
        </tr>
      </template>
    </DataTable>

    <!-- Empty State -->
    <div v-if="!loading && filteredCustomers.length === 0 && !error" 
         class="text-center py-5 bg-white rounded shadow-sm">
      <UserX :size="48" style="color: var(--tertiary-medium);" class="mb-3" />
      <p style="color: var(--tertiary-medium);">
        {{ customers.length === 0 ? 'No customers found' : 'No customers match the current filters' }}
      </p>
      <button 
        v-if="customers.length === 0" 
        class="btn btn-primary btn-with-icon mt-3" 
        @click="showAddCustomerModal"
      >
        <Plus :size="16" />
        <span>Add First Customer</span>
      </button>
      <button 
        v-else 
        class="btn btn-secondary btn-with-icon mt-3"
        @click="clearFilters"
      >
        <RefreshCw :size="16" />
        <span>Clear Filters</span>
      </button>
    </div>

    <!-- Customer Modal -->
    <AddCustomerModal
      :show="showCustomerModal"
      :mode="modalMode"
      :customer="modalCustomer"
      @close="closeCustomerModal"
      @edit-mode="handleEditMode"
    />
  </div>
</template>

<script>
import { onMounted } from 'vue'
import CardTemplate from '@/components/common/CardTemplate.vue'
import DataTable from '../components/common/TableTemplate.vue'
import AddCustomerModal from '@/components/customers/AddCustomerModal.vue'
import { useCustomers } from '../composables/ui/customers/useCustomers.js'
import { Plus, RefreshCw, Search, X, Edit, Eye, Trash2, UserX } from 'lucide-vue-next'

export default {
  name: 'CustomersPage',
  components: {
    CardTemplate,
    DataTable,
    AddCustomerModal,
    Plus,
    RefreshCw,
    Search,
    X,
    Edit,
    Eye,
    Trash2,
    UserX
  },
  setup() {
    const {
      // State
      customers,
      filteredCustomers,
      selectedCustomers,
      loading,
      error,
      successMessage,
      searchQuery,
      searchMode,
      statusFilter,
      pointsFilter,
      currentPage,
      itemsPerPage,
      showCustomerModal,
      modalMode,
      modalCustomer,
      activeUsersCount,
      monthlyUsersCount,
      dailyUsersCount,
      
      // Auto-refresh functionality
      autoRefreshEnabled,
      countdown,
      connectionLost,
      exporting,
      refreshProgress,
      
      // Computed
      allSelected,
      someSelected,
      paginatedCustomers,
      
      // Methods
      initialize,
      toggleAutoRefresh,
      handleSearch,
      clearSearch,
      applyFilters,
      clearFilters,
      refreshData,
      selectAll,
      deleteSelected: deleteSelectedCustomers,
      deleteCustomer,
      showAddCustomerModal,
      editCustomer,
      viewCustomer,
      handleEditMode,
      closeCustomerModal,
      exportData,
      formatAddress,
      formatDate,
      highlightMatch,
      handlePageChange,
      emergencyReconnect,
      getConnectionStatus,
      getConnectionIcon,
      getConnectionText
    } = useCustomers()

    onMounted(() => {
      window.scrollTo(0, 0)
      initialize()
    })

    return {
      // State
      customers,
      filteredCustomers,
      selectedCustomers,
      loading,
      error,
      successMessage,
      searchQuery,
      searchMode,
      statusFilter,
      pointsFilter,
      currentPage,
      itemsPerPage,
      showCustomerModal,
      modalMode,
      modalCustomer,
      activeUsersCount,
      monthlyUsersCount,
      dailyUsersCount,
      
      // Auto-refresh functionality
      autoRefreshEnabled,
      countdown,
      connectionLost,
      exporting,
      refreshProgress,
      
      // Computed
      allSelected,
      someSelected,
      paginatedCustomers,
      
      // Methods
      toggleAutoRefresh,
      handleSearch,
      clearSearch,
      applyFilters,
      clearFilters,
      refreshData,
      selectAll,
      deleteSelected: deleteSelectedCustomers,
      deleteCustomer,
      showAddCustomerModal,
      editCustomer,
      viewCustomer,
      handleEditMode,
      closeCustomerModal,
      exportData,
      formatAddress,
      formatDate,
      highlightMatch,
      handlePageChange,
      emergencyReconnect,
      getConnectionStatus,
      getConnectionIcon,
      getConnectionText
    }
  }
}
</script>

<style scoped>
.customers-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  gap: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

/* Search and Actions Row */
.search-and-actions-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

/* Search Section Styles */
.search-section {
  flex: 1;
  max-width: 500px;
}

.action-buttons-group {
  display: flex;
  gap: 0.75rem;
  flex-shrink: 0;
  align-items: flex-start;
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

/* Auto-refresh status indicator */
.auto-refresh-status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #f0fdf4;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #bbf7d0;
  min-width: 220px;
}

.status-text {
  font-size: 0.875rem;
  color: #16a34a;
  font-weight: 500;
  flex: 1;
}

/* Connection indicator */
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

/* Action Button Styles */
.action-btn {
  padding: 0.25rem 0.4rem;
  font-size: 0.75rem;
  line-height: 1;
  border-radius: 0.25rem;
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

/* Utility classes */
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

.gap-1 {
  gap: 0.25rem !important;
}

.gap-2 {
  gap: 0.5rem !important;
}

.me-2 {
  margin-right: 0.5rem !important;
}

.mb-3 {
  margin-bottom: 1rem !important;
}

.mt-3 {
  margin-top: 1rem !important;
}

.py-5 {
  padding-top: 3rem !important;
  padding-bottom: 3rem !important;
}

.text-center {
  text-align: center !important;
}

.fw-medium {
  font-weight: 500 !important;
}

.badge {
  display: inline-block;
  padding: 0.35em 0.65em;
  font-size: 0.75em;
  font-weight: 700;
  line-height: 1;
  color: #fff;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: 0.25rem;
}

.bg-light {
  background-color: #f8f9fa !important;
}

.bg-success {
  background-color: #198754 !important;
}

.text-primary {
  color: #0d6efd !important;
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

/* Responsive Design */
@media (max-width: 1024px) {
  .customers-page {
    padding: 1rem;
  }
  
  .search-and-actions-row {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .search-section {
    max-width: none;
  }

  .action-buttons-group {
    justify-content: center;
    flex-wrap: wrap;
  }

  .auto-refresh-status {
    min-width: auto;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.8125rem;
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

@media (max-width: 576px) {
  .customers-page {
    padding: 0.75rem;
  }
}
</style>