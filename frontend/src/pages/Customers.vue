<template>
  <div class="customers-page">
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

    <!-- Action Bar -->
    <div v-if="!loading || customers.length > 0" class="mb-3">
      <div class="d-flex justify-content-between align-items-center">
        <!-- Left: Actions -->
        <div v-if="selectedCustomers.length === 0" class="d-flex gap-2">
          <button class="btn btn-success btn-sm btn-with-icon-sm" @click="showAddCustomerModal">
            <Plus :size="14" />
            ADD CUSTOMER
          </button>
          <button class="btn btn-outline-secondary btn-sm" @click="exportData">
            EXPORT
          </button>
          <button class="btn btn-outline-secondary btn-sm" @click="refreshData" :disabled="loading">
            <RefreshCw :size="14" :class="{ 'spin-animation': loading }" />
            REFRESH
          </button>
        </div>

        <!-- Selection Actions -->
        <div v-if="selectedCustomers.length > 0" class="d-flex gap-2">
          <button class="btn btn-delete btn-sm btn-with-icon-sm" @click="deleteSelected">
            <Trash2 :size="14" />
            DELETE
          </button>
        </div>

        <!-- Right: Search & Filters -->
        <div class="d-flex align-items-center gap-2">
          <!-- Search Toggle -->
          <button 
            class="btn btn-secondary btn-sm"
            @click="toggleSearchMode"
            :class="{ 'active': searchMode }"
          >
            <Search :size="16" />
          </button>

          <!-- Filters -->
          <template v-if="!searchMode">
            <div class="filter-dropdown">
              <label class="filter-label">Status</label>
              <select class="form-select form-select-sm" v-model="statusFilter" @change="applyFilters">
                <option value="all">All customers</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>

            <div class="filter-dropdown">
              <label class="filter-label">Points Range</label>
              <select class="form-select form-select-sm" v-model="pointsFilter" @change="applyFilters">
                <option value="all">All ranges</option>
                <option value="0-100">0-100 points</option>
                <option value="101-500">101-500 points</option>
                <option value="501+">501+ points</option>
              </select>
            </div>
          </template>

          <!-- Search Bar -->
          <div v-if="searchMode" class="search-container">
            <div class="position-relative">
              <input 
                ref="searchInput"
                v-model="searchQuery" 
                @input="handleSearch"
                type="text" 
                class="form-control form-control-sm"
                placeholder="Search customers..."
              />
              <button 
                class="btn btn-sm btn-link position-absolute end-0 top-50 translate-middle-y"
                @click="clearSearch"
              >
                <X :size="16" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && customers.length === 0" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3" style="color: var(--tertiary-medium);">Loading customers...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="alert alert-danger d-flex align-items-center justify-content-between" role="alert">
      <span>{{ error }}</span>
      <button class="btn btn-sm btn-danger" @click="refreshData">Try Again</button>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
      {{ successMessage }}
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

export default {
  name: 'CustomersPage',
  components: {
    CardTemplate,
    DataTable,
    AddCustomerModal
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
      
      // Computed
      allSelected,
      someSelected,
      paginatedCustomers,
      
      // Methods
      initialize,
      toggleSearchMode,
      handleSearch,
      clearSearch,
      applyFilters,
      clearFilters,
      refreshData,
      selectAll,
      deleteSelectedCustomers,
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
      handlePageChange
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
      
      // Computed
      allSelected,
      someSelected,
      paginatedCustomers,
      
      // Methods
      toggleSearchMode,
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
      handlePageChange
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

.spin-animation {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 1024px) {
  .customers-page {
    padding: 1rem;
  }
}

@media (max-width: 576px) {
  .customers-page {
    padding: 0.75rem;
  }
}
</style>