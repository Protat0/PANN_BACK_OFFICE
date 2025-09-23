<template>
  <div class="page-container p-8">
    
    <!-- Loading State -->
    <div v-if="isLoading && !hasCustomers" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
      <p class="text-secondary">Loading customers...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="status-error rounded-lg p-6 mb-6">
      <h3 class="text-lg font-medium text-status-error mb-2">Error Loading Customers</h3>
      <p class="text-status-error mb-4">{{ error }}</p>
      <button 
        @click="handleRetry" 
        class="btn-submit px-4 py-2 rounded transition-all-theme"
        :disabled="isLoading"
      >
        {{ isLoading ? 'Retrying...' : 'Try Again' }}
      </button>
    </div>

    <!-- Action Bar -->
    <ActionBar
      v-if="!isLoading || hasCustomers"
      entity-name="customer"
      add-button-text="ADD CUSTOMER"
      search-placeholder="Search customers..."
      :add-options="addOptions"
      :selected-items="selectedCustomers"
      :selection-actions="selectionActions"
      :filters="filters"
      :search-value="searchValue"
      :exporting="exporting"
      @add-action="handleAddAction"
      @selection-action="handleSelectionAction"
      @filter-change="handleFilterChange"
      @search-input="handleSearchInput"
      @search-clear="handleSearchClear"
      @toggle-columns="handleToggleColumns"
      @export="handleExport"
    />

    <!-- Table with TableTemplate -->
    <TableTemplate 
      v-if="hasCustomers || isLoading"
      :items-per-page="itemsPerPage"
      :total-items="totalCustomers"
      :current-page="currentPage"
      :show-pagination="totalCustomers > itemsPerPage"
      @page-changed="handlePageChange"
    >
      <template #header>
        <tr>
          <th style="width: 150px;">Customer ID</th>
          <th>Full Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th style="width: 120px;">Loyalty Points</th>
          <th style="width: 100px;">Status</th>
          <th style="width: 140px;">Date Created</th>
          <th style="width: 120px;" class="text-center">Actions</th>
        </tr>
      </template>
      
      <template #body>
        <tr v-for="customer in paginatedCustomers" :key="customer._id || customer.customer_id">
          <td>
            <span class="badge bg-light text-primary" style="font-family: monospace;">
              {{ customer.customer_id || customer._id }}
            </span>
          </td>
          <td>
            <div class="fw-medium text-tertiary-dark">
              {{ customer.full_name || 'N/A' }}
            </div>
          </td>
          <td>
            <div class="text-tertiary-medium">
              {{ customer.email }}
            </div>
          </td>
          <td>
            <div class="text-tertiary-medium">
              {{ customer.phone || 'N/A' }}
            </div>
          </td>
          <td class="text-center">
            <span class="badge bg-success">
              {{ customer.loyalty_points || 0 }}
            </span>
          </td>
          <td class="text-center">
            <span 
              class="badge"
              :class="customer.status === 'active' ? 'bg-success' : 'bg-secondary'"
            >
              {{ customer.status || 'active' }}
            </span>
          </td>
          <td>
            <div class="text-tertiary-medium" style="font-size: 0.875rem;">
              {{ formatDate(customer.date_created) }}
            </div>
          </td>
          <td>
            <div class="d-flex justify-content-center gap-1">
              <button 
                class="btn btn-outline-primary action-btn action-btn-view" 
                @click="viewCustomer(customer)" 
                title="View Customer Details"
              >
                <Eye :size="14" />
              </button>
              <button 
                class="btn btn-outline-secondary action-btn action-btn-edit" 
                @click="editCustomer(customer)" 
                title="Edit Customer"
              >
                <Edit :size="14" />
              </button>
              <button 
                class="btn btn-outline-danger action-btn action-btn-delete" 
                @click="deleteCustomer(customer)" 
                title="Delete Customer"
              >
                <Trash2 :size="14" />
              </button>
            </div>
          </td>
        </tr>
      </template>
    </TableTemplate>

    <!-- Empty State -->
    <div v-if="!hasCustomers && !isLoading && !error" class="text-center py-12 surface-card rounded-lg shadow-md">
      <div class="text-6xl mb-4">👥</div>
      <h3 class="text-lg font-medium text-primary mb-2">No Customers Found</h3>
      <p class="text-secondary mb-6">Get started by adding your first customer.</p>
      <button 
        class="btn-submit px-6 py-3 rounded transition-all-theme"
        @click="openAddCustomerModal"
      >
        Add First Customer
      </button>
    </div>
  </div>

  <AddCustomerModal
    ref="customerModal"
    :mode="modalMode"
    :customer="selectedCustomer"
    @close="handleModalClose"
    @success="handleModalSuccess"
  />

</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCustomers } from '@/composables/api/useCustomers.js'
import TableTemplate from '@/components/common/TableTemplate.vue'
import ActionBar from '@/components/common/ActionBar.vue'
import AddCustomerModal from '@/components/customers/AddCustomerModal.vue'

// Use the customers composable
const {
  customers,
  isLoading,
  error,
  statistics,
  totalCustomers,
  hasCustomers,
  fetchCustomers,
  fetchStatistics,
  clearError
} = useCustomers()

// Local reactive state for pagination
const currentPage = ref(1)
const itemsPerPage = ref(10)

// Modal state
const customerModal = ref(null)
const modalMode = ref('create')
const selectedCustomer = ref(null)

// Action bar configuration
const selectedCustomers = ref([])
const searchValue = ref('')
const exporting = ref(false)

const addOptions = ref([
  {
    key: 'single',
    icon: 'Plus',
    title: 'Add Customer',
    description: 'Add one customer manually'
  },
  {
    key: 'import',
    icon: 'Upload',
    title: 'Import Customers',
    description: 'Upload CSV/Excel file'
  }
])

const selectionActions = ref([
  {
    key: 'delete',
    icon: 'Trash2',
    label: 'DELETE',
    buttonClass: 'btn-delete'
  }
])

const filters = ref([
  {
    key: 'status',
    label: 'Status',
    value: 'all',
    options: [
      { value: 'all', label: 'All customers' },
      { value: 'active', label: 'Active' },
      { value: 'inactive', label: 'Inactive' }
    ]
  },
  {
    key: 'points',
    label: 'Loyalty Points',
    value: 'all',
    options: [
      { value: 'all', label: 'All points' },
      { value: 'high', label: 'High (100+)' },
      { value: 'medium', label: 'Medium (50-99)' },
      { value: 'low', label: 'Low (0-49)' }
    ]
  }
])

// Computed for paginated customers
const paginatedCustomers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return customers.value.slice(start, end)
})

// Methods
const handleRetry = async () => {
  clearError()
  await fetchCustomers()
}

const handlePageChange = (page) => {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch {
    return 'Invalid Date'
  }
}

// Action bar event handlers
const handleAddAction = (actionKey) => {
  switch (actionKey) {
    case 'single':
      openAddCustomerModal()
      break
    case 'import':
      console.log('Import customers')
      break
  }
}

const handleSelectionAction = (actionKey, selectedItems) => {
  switch (actionKey) {
    case 'delete':
      console.log('Delete selected customers:', selectedItems)
      break
  }
}

const handleFilterChange = (filterKey, value) => {
  console.log('Filter changed:', filterKey, value)
  const filter = filters.value.find(f => f.key === filterKey)
  if (filter) {
    filter.value = value
  }
}

const handleSearchInput = (value) => {
  searchValue.value = value
  console.log('Search:', value)
}

const handleSearchClear = () => {
  searchValue.value = ''
  console.log('Search cleared')
}

const handleToggleColumns = () => {
  console.log('Toggle columns')
}

const handleExport = () => {
  console.log('Export customers')
}

// Modal methods
const openAddCustomerModal = () => {
  modalMode.value = 'create'
  selectedCustomer.value = null
  customerModal.value?.openModal()
}

const openEditCustomerModal = (customer) => {
  modalMode.value = 'edit'
  selectedCustomer.value = customer
  customerModal.value?.openModal()
}

const handleModalClose = () => {
  modalMode.value = 'create'
  selectedCustomer.value = null
}

const handleModalSuccess = (customerData) => {
  console.log('Customer saved successfully:', customerData)
  // The table will automatically update via the useCustomers composable
}

// Table action handlers
const viewCustomer = (customer) => {
  console.log('View customer:', customer)
  // TODO: Implement view modal or navigate to detail page
}

const editCustomer = (customer) => {
  openEditCustomerModal(customer)
}

const deleteCustomer = (customer) => {
  console.log('Delete customer:', customer)
  // TODO: Implement delete confirmation and API call
}

// Initialize on mount
onMounted(async () => {
  try {
    await Promise.all([
      fetchCustomers(),
      fetchStatistics()
    ])
  } catch (err) {
    console.error('Failed to initialize customers page:', err)
  }
})
</script>

<style scoped>
/* Utility classes for responsive grid */
.grid {
  display: grid;
}

.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.gap-4 {
  gap: 1rem;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive grid */
@media (min-width: 768px) {
  .md\:grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

/* Button and utility classes */
.btn-submit:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-submit:disabled {
  transform: none;
  opacity: 0.6;
  cursor: not-allowed;
}

.badge {
  display: inline-block;
  padding: 0.35em 0.65em;
  font-size: 0.75em;
  font-weight: 600;
  line-height: 1;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: 0.25rem;
}

.bg-light {
  background-color: #f8f9fa !important;
  color: #6c757d !important;
}

.bg-success {
  background-color: #198754 !important;
  color: white !important;
}

.bg-secondary {
  background-color: #6c757d !important;
  color: white !important;
}

.text-primary {
  color: var(--primary) !important;
}

.fw-medium {
  font-weight: 500 !important;
}

.text-center {
  text-align: center !important;
}

.d-flex {
  display: flex !important;
}

.justify-content-center {
  justify-content: center !important;
}

.gap-1 {
  gap: 0.25rem !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .p-8 {
    padding: 1rem;
  }
  
  .text-3xl {
    font-size: 1.875rem;
  }
}
</style>