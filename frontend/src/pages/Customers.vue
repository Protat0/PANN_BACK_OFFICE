<template>
  <div class="page-container p-4">
    
    <!-- Loading State -->
    <div v-if="isLoading && !hasCustomers" class="text-center py-12">
      <div class="spinner-border text-accent mb-4" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-secondary">Loading customers...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="status-error rounded-lg p-4 mb-4">
      <h3 class="text-lg fw-medium text-status-error mb-2">Error Loading Customers</h3>
      <p class="text-status-error mb-3">{{ error }}</p>
      <button 
        @click="handleRetry" 
        class="btn btn-submit transition-theme"
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
      :show-columns-button="false"
      @add-action="handleAddAction"
      @selection-action="handleSelectionAction"
      @filter-change="handleFilterChange"
      @search-input="handleSearchInput"
      @search-clear="handleSearchClear"
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
      class="shadow-md"
    >
      <template #header>
        <tr>
          <th style="width: 150px;">Customer ID</th>
          <th style="width: 140px;">Username</th>  <!-- Add this line -->
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
        <tr v-for="customer in paginatedCustomers" :key="customer._id || customer.customer_id" class="hover-surface transition-theme">
          <td>
            <span class="badge surface-tertiary text-accent border-theme-subtle fw-medium" style="font-family: var(--font-mono, 'Courier New', monospace);">
              {{ customer.customer_id || customer._id }}
            </span>
          </td>
          <!-- Add this username column -->
          <td>
            <div class="fw-medium text-tertiary-dark">
              {{ customer.username || 'N/A' }}
            </div>
          </td>
          <td>
            <div class="fw-medium text-primary">
              {{ customer.full_name || 'N/A' }}
            </div>
          </td>
          <td>
            <div class="text-secondary">
              {{ customer.email }}
            </div>
          </td>
          <td>
            <div class="text-secondary">
              {{ customer.phone || 'N/A' }}
            </div>
          </td>
          <td class="text-center">
            <span class="badge bg-success text-inverse fw-medium">
              {{ customer.loyalty_points || 0 }}
            </span>
          </td>
          <td class="text-center">
            <span 
              class="badge fw-medium"
              :class="customer.status === 'active' ? 'bg-success text-inverse' : 'surface-tertiary text-tertiary border-theme'"
            >
              {{ customer.status || 'active' }}
            </span>
          </td>
          <td>
            <div class="text-tertiary small">
              {{ formatDate(customer.date_created) }}
            </div>
          </td>
          <td>
            <div class="d-flex justify-content-center gap-1">
              <button 
                class="btn btn-outline-primary action-btn action-btn-view btn-icon-only btn-sm shadow-sm" 
                @click="viewCustomer(customer)" 
                title="View Customer Details"
              >
                <Eye :size="14" />
              </button>
              <button 
                class="btn btn-outline-secondary action-btn action-btn-edit btn-icon-only btn-sm shadow-sm" 
                @click="editCustomer(customer)" 
                title="Edit Customer"
              >
                <Edit :size="14" />
              </button>
              <button 
                class="btn btn-outline-danger action-btn action-btn-delete btn-icon-only btn-sm shadow-sm" 
                @click="deleteCustomer(customer)" 
                title="Delete Customer"
                :disabled="deletingCustomerId === (customer._id || customer.customer_id)"
              >
                <Trash2 v-if="deletingCustomerId !== (customer._id || customer.customer_id)" :size="14" />
                <div v-else class="spinner-border spinner-border-sm"></div>
              </button>
            </div>
          </td>
        </tr>
      </template>
    </TableTemplate>

    <!-- Empty State -->
    <div v-if="!hasCustomers && !isLoading && !error" class="text-center py-12 surface-card rounded shadow-md">
      <div class="display-1 mb-4">👥</div>
      <h3 class="h4 fw-medium text-primary mb-2">No Customers Found</h3>
      <p class="text-secondary mb-4">Get started by adding your first customer.</p>
      <button 
        class="btn btn-submit px-4 py-2 shadow-sm transition-theme"
        @click="openAddCustomerModal"
      >
        Add First Customer
      </button>
    </div>

    <!-- Add Delete Confirmation Modal -->
    <div class="modal fade" ref="deleteModalElement" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header border-theme">
            <h5 class="modal-title text-error">Confirm Delete</h5>
            <button type="button" class="btn-close" @click="closeDeleteModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="customerToDelete" class="text-center">
              <div class="text-5xl mb-3">⚠️</div>
              <h6 class="text-primary mb-3">Delete Customer</h6>
              <p class="text-secondary mb-3">
                Are you sure you want to delete customer 
                <strong>{{ customerToDelete.full_name }}</strong>?
              </p>
              <div class="alert alert-warning" role="alert">
                <small>
                  This will hide the customer from the active list, but they can be restored later if needed.
                </small>
              </div>
            </div>
          </div>
          <div class="modal-footer border-theme">
            <button type="button" class="btn btn-secondary" @click="closeDeleteModal">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-danger" 
              @click="confirmDelete"
              :disabled="isLoading"
            >
              <span v-if="isLoading">Deleting...</span>
              <span v-else>Delete Customer</span>
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>

  <!-- Customer Modal -->
  <AddCustomerModal
    ref="customerModal"
    :mode="modalMode"
    :customer="selectedCustomer"
    @close="handleModalClose"
    @success="handleModalSuccess"
    @mode-changed="handleModeChanged"
  />

  <!-- Delete Confirmation Modal -->
  <DeleteConfirmationModal
    ref="deleteModal"
    :is-loading="deletingCustomerId !== null"
    @confirm="confirmDelete"
    @cancel="cancelDelete"
  />

</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Modal } from 'bootstrap'
import { useCustomers } from '@/composables/api/useCustomers.js'
import TableTemplate from '@/components/common/TableTemplate.vue'
import ActionBar from '@/components/common/ActionBar.vue'
import AddCustomerModal from '@/components/customers/AddCustomerModal.vue'
import DeleteConfirmationModal from '@/components/common/DeleteConfirmationModal.vue'

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
  deleteCustomer: deleteCustomerAPI,
  clearError
} = useCustomers()

// Local reactive state for pagination
const currentPage = ref(1)
const itemsPerPage = ref(10)

// Modal state
const customerModal = ref(null)
const deleteModal = ref(null)
const modalMode = ref('create')
const selectedCustomer = ref(null)
const deletingCustomerId = ref(null)


// Action bar configuration
const selectedCustomers = ref([])
const searchValue = ref('')
const exporting = ref(false)

// Delete modal state
const deleteModalElement = ref(null)
const customerToDelete = ref(null)
let deleteModalInstance = null

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

const handleSearchInput = async (value) => {
  searchValue.value = value
  if (value.trim()) {
    await searchCustomers(value.trim())
  } else {
    await fetchCustomers()
  }
  currentPage.value = 1 // Reset to first page
}

const handleSearchClear = async () => {
  searchValue.value = ''
  await fetchCustomers()
  currentPage.value = 1
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

const openViewCustomerModal = (customer) => {
  modalMode.value = 'view'
  selectedCustomer.value = customer
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

const handleModalSuccess = async (customerData) => {
  console.log('Customer saved successfully:', customerData)
  
  // Refresh the customers list to show the new/updated customer
  try {
    await fetchCustomers()
    console.log('Customer list refreshed successfully')
    
    // Optional: Reset to first page if adding new customer to show it at the top
    if (modalMode.value === 'create') {
      currentPage.value = 1
    }
    
  } catch (error) {
    console.error('Failed to refresh customer list:', error)
    // You could add a toast notification here if you have one
  }
}

// Table action handlers
const viewCustomer = (customer) => {
  openViewCustomerModal(customer)
}

const editCustomer = (customer) => {
  openEditCustomerModal(customer)
}

// Delete modal methods
const openDeleteModal = (customer) => {
  customerToDelete.value = customer
  if (deleteModalInstance) {
    deleteModalInstance.show()
  }
}

const closeDeleteModal = () => {
  customerToDelete.value = null
  if (deleteModalInstance) {
    deleteModalInstance.hide()
  }
}

const confirmDelete = async () => {
  if (!customerToDelete.value) return

  try {
    await deleteCustomerAPI(customerToDelete.value._id || customerToDelete.value.customer_id)
    
    // Show success message
    console.log('Customer deleted successfully')
    
    closeDeleteModal()
  } catch (error) {
    console.error('Failed to delete customer:', error)
  }
}

// Update the delete handler in your table
const deleteCustomer = (customer) => {
  openDeleteModal(customer)
}

onMounted(async () => {
  try {
    // Initialize data
    await Promise.all([
      fetchCustomers(),
      fetchStatistics()
    ])
    
    // Initialize delete modal
    if (deleteModalElement.value) {
      deleteModalInstance = new Modal(deleteModalElement.value)
      
      deleteModalElement.value.addEventListener('hidden.bs.modal', () => {
        customerToDelete.value = null
      })
      
      console.log('Delete modal initialized successfully') // Add this for debugging
    } else {
      console.error('Delete modal element not found')
    }
  } catch (err) {
    console.error('Failed to initialize customers page:', err)
  }
})
</script>

<style scoped>
/* Utility classes that complement the semantic system */
.spinner-border {
  width: 3rem;
  height: 3rem;
  border-width: 0.3em;
}

.spinner-border-sm {
  width: 0.875rem;
  height: 0.875rem;
  border-width: 0.125em;
}

.display-1 {
  font-size: 3.5rem;
  line-height: 1.2;
}

.small {
  font-size: 0.875rem;
}

/* Badge enhancements */
.badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
}

/* Action button spacing */
.action-btn {
  transition: all 0.2s ease;
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Responsive typography */
@media (max-width: 768px) {
  .p-4 {
    padding: 1rem;
  }
  
  .display-1 {
    font-size: 2.5rem;
  }
  
  .h4 {
    font-size: 1.25rem;
  }
}

/* Ensure proper text color inheritance for buttons */
.btn-icon-only {
  width: 2rem;
  height: 2rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* Loading animation */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.spinner-border {
  animation: spin 0.75s linear infinite;
}
</style>