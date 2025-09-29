<template>
  <div class="container-fluid pt-2 pb-4 suppliers-page">
    <!-- Page Title -->
    <div class="mb-3">
      <h1 class="h3 fw-semibold text-primary-dark mb-0">Supplier Management</h1>
    </div>

    <!-- Reports Section -->
    <div class="row mb-3" v-if="!suppliersComposable.loading?.value">
      <div class="col-6 col-md-6 mb-2">
        <CardTemplate
          size="xs"
          border-color="warning"
          border-position="start"
          title="Active Orders"
          :value="reportsComposable.activeOrdersCount"
          value-color="warning"
          subtitle="Pending Purchase Orders"
          clickable
          @click="reportsComposable.openActiveOrdersModal"
        />
      </div>
      <div class="col-6 col-md-6 mb-2">
        <CardTemplate
          size="xs"
          border-color="success"
          border-position="start"
          title="Top Performers"
          :value="reportsComposable.topPerformersCount"
          value-color="success"
          subtitle="High Volume Suppliers"
          clickable
          @click="reportsComposable.openTopPerformersModal"
        />
      </div>
    </div>

    <!-- Debug Info (remove in production) -->
    <div v-if="false" class="alert alert-info mb-4">
      <h6>Debug Info:</h6>
      <p>Loading: {{ suppliersComposable.loading?.value ?? 'undefined' }}</p>
      <p>Suppliers Length: {{ suppliersComposable.suppliers?.value?.length ?? 'undefined' }}</p>
      <p>Report Data: {{ JSON.stringify(reportsComposable.reportData) }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="suppliersComposable.loading?.value && (!suppliersComposable.suppliers?.value || suppliersComposable.suppliers.value.length === 0)" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-tertiary-medium">Loading suppliers...</p>
    </div>

    <!-- Error State -->
    <div v-if="suppliersComposable.error?.value" class="alert alert-danger text-center" role="alert">
      <p class="mb-3">{{ suppliersComposable.error.value }}</p>
      <button class="btn btn-primary" @click="suppliersComposable.refreshData">Try Again</button>
    </div>

    <!-- Success Message -->
    <div v-if="suppliersComposable.successMessage?.value" class="alert alert-success text-center" role="alert">
      {{ suppliersComposable.successMessage.value }}
    </div>

    <!-- Action Bar and Filters - Separate Section -->
    <div v-if="!suppliersComposable.loading?.value || (suppliersComposable.suppliers?.value && suppliersComposable.suppliers.value.length > 0)" class="action-bar-container mb-3">
      <!-- Integrated Header with Actions and Filters -->
      <div class="action-bar-controls">
        <!-- Action Row: Action Buttons and Filters -->
        <div class="action-row">
          <!-- Left Side: Main Actions (Always visible when no selection) -->
          <div v-if="suppliersComposable.selectedSuppliers?.value?.length === 0" class="d-flex gap-2">
            <!-- Add Suppliers Dropdown -->
            <div class="dropdown" ref="addDropdownRef">
              <button 
                class="btn btn-success btn-sm btn-with-icon-sm dropdown-toggle"
                type="button"
                @click="toggleAddDropdown"
                :class="{ 'active': showAddDropdown }"
              >
                <Plus :size="14" />
                ADD ITEM
              </button>
              
              <div 
                class="dropdown-menu custom-dropdown-menu" 
                :class="{ 'show': showAddDropdown }"
              >
                <button class="dropdown-item custom-dropdown-item" @click="handleSingleSupplier">
                  <div class="d-flex align-items-center gap-3">
                    <Plus :size="16" class="text-primary" />
                    <div>
                      <div class="fw-semibold">Single Supplier</div>
                      <small class="text-muted">Add one supplier manually</small>
                    </div>
                  </div>
                </button>
                
                <button class="dropdown-item custom-dropdown-item" @click="handleBulkAdd">
                  <div class="d-flex align-items-center gap-3">
                    <Building :size="16" class="text-primary" />
                    <div>
                      <div class="fw-semibold">Bulk Entry</div>
                      <small class="text-muted">Add multiple suppliers (5-20 items)</small>
                    </div>
                  </div>
                </button>
                
                <button class="dropdown-item custom-dropdown-item" @click="handleImport">
                  <div class="d-flex align-items-center gap-3">
                    <FileText :size="16" class="text-primary" />
                    <div>
                      <div class="fw-semibold">Import File</div>
                      <small class="text-muted">Upload CSV/Excel (20+ items)</small>
                    </div>
                  </div>
                </button>
              </div>
            </div>

            <button 
              class="btn btn-outline-secondary btn-sm"
              @click="exportComposable.openExportModal"
            >
              EXPORT
            </button>
          </div>

          <!-- Selection Actions (Visible when items are selected) -->
          <div v-if="suppliersComposable.selectedSuppliers?.value?.length > 0" class="d-flex gap-2">
            <button 
              class="btn btn-delete btn-sm btn-with-icon-sm"
              @click="suppliersComposable.deleteSelected"
              :disabled="suppliersComposable.loading?.value"
            >
              <Trash2 :size="14" />
              DELETE
            </button>
          </div>

          <!-- Right Side: Filters and Search -->
          <div class="d-flex align-items-center gap-2">
            <!-- Search Toggle -->
            <button 
              class="btn btn-secondary btn-sm"
              @click="toggleSearchMode"
              :class="{ 'active': searchMode }"
              style="height: calc(1.5em + 0.75rem + 2px); display: flex; align-items: center; justify-content: center; padding: 0 0.75rem;"
            >
              <Search :size="16" />
            </button>

            <!-- Filter Dropdowns (Hidden when search is active) -->
            <template v-if="!searchMode">
              <div class="filter-dropdown">
                <label class="filter-label">Category</label>
                <select 
                  class="form-select form-select-sm" 
                  v-model="suppliersComposable.filters.type" 
                  @change="applyFilters"
                >
                  <option value="all">All items</option>
                  <option value="food">Food & Beverages</option>
                  <option value="packaging">Packaging</option>
                  <option value="equipment">Equipment</option>
                  <option value="services">Services</option>
                </select>
              </div>

              <div class="filter-dropdown">
                <label class="filter-label">Stock alert</label>
                <select 
                  class="form-select form-select-sm" 
                  v-model="suppliersComposable.filters.order" 
                  @change="applyFilters"
                >
                  <option value="all">All items</option>
                  <option value="high">High Volume (10+)</option>
                  <option value="medium">Medium Volume (5-9)</option>
                  <option value="low">Low Volume (1-4)</option>
                  <option value="none">No Orders</option>
                </select>
              </div>
            </template>

            <!-- Search Bar (Visible when search mode is active) -->
            <div v-if="searchMode" class="search-container">
              <div class="position-relative">
                <input 
                  ref="searchInputRef"
                  v-model="suppliersComposable.filters.search" 
                  @input="applyFilters"
                  type="text" 
                  class="form-control form-control-sm search-input"
                  placeholder="Search"
                />
                <button 
                  class="btn btn-sm btn-link position-absolute end-0 top-50 translate-middle-y"
                  @click="clearSearch"
                  style="border: none; padding: 0.25rem;"
                >
                  <X :size="16" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Suppliers Grid -->
    <div v-if="!suppliersComposable.loading?.value || (suppliersComposable.suppliers?.value && suppliersComposable.suppliers.value.length > 0)" class="row g-4">
      <div 
        v-for="supplier in suppliersComposable.filteredSuppliers?.value || []" 
        :key="supplier.id"
        class="col-12 col-md-6 col-lg-4"
      >
        <SupplierCard
          :supplier="supplier"
          :is-selected="suppliersComposable.selectedSuppliers?.value?.includes(supplier.id) || false"
          @toggle-select="toggleSupplierSelection"
          @edit="formComposable.editSupplier"
          @view="viewSupplier"
          @create-order="createOrder"
          @delete="suppliersComposable.deleteSupplier"
        />
      </div>

      <!-- Empty State -->
      <div v-if="!suppliersComposable.filteredSuppliers?.value?.length" class="col-12">
        <div class="text-center py-5">
          <div class="card">
            <div class="card-body py-5">
              <Building :size="48" class="text-tertiary-medium mb-3" />
              <p class="text-tertiary-medium mb-3">
                {{ !suppliersComposable.suppliers?.value?.length ? 'No suppliers found' : 'No suppliers match the current filters' }}
              </p>
              <button 
                v-if="!suppliersComposable.suppliers?.value?.length" 
                class="btn btn-primary btn-with-icon" 
                @click="handleSingleSupplier"
              >
                <Plus :size="16" />
                Add First Supplier
              </button>
              <button 
                v-else 
                class="btn btn-secondary btn-with-icon"
                @click="clearFilters"
              >
                <RefreshCw :size="16" />
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Orders Modal -->
    <ActiveOrdersModal
      :show="reportsComposable.showActiveOrdersModal.value"
      :orders="reportsComposable.activeOrders.value"
      :loading="reportsComposable.loading.value"
      @close="reportsComposable.closeActiveOrdersModal"
      @view-all="handleViewAllOrders"
    />

    <!-- Top Performers Modal -->
    <TopPerformersModal
      :show="reportsComposable.showTopPerformersModal.value"
      :suppliers="reportsComposable.topPerformers.value"
      :loading="reportsComposable.loading.value"
      @close="reportsComposable.closeTopPerformersModal"
    />

    <!-- Create Order Modal -->
    <CreateOrderModal
      :show="createOrderComposable.showCreateOrderModal?.value || false"
      :supplier="createOrderComposable.selectedSupplier?.value"
      @close="createOrderComposable.closeCreateOrderModal"
      @save="handleOrderSave"
    />

    <!-- Add Supplier Modal -->
    <SupplierFormModal
      :show="formComposable.showAddModal?.value || false"
      :is-edit="formComposable.isEditMode?.value || false"
      :form-data="formComposable.formData"
      :form-errors="formComposable.formErrors?.value || {}"
      :loading="formComposable.formLoading?.value || false"
      :is-valid="formComposable.isFormValid?.value || false"
      :add-another="formComposable.addAnotherAfterSave?.value || false"
      @close="formComposable.closeAddModal"
      @save="handleSaveSupplier"
      @clear-error="formComposable.clearFormError"
      @update:add-another="formComposable.addAnotherAfterSave.value = $event"
    />

    <!-- Bulk Suppliers Modal -->
    <BulkSuppliersModal
      :show="bulkComposable.showBulkModal?.value || false"
      :existing-suppliers="suppliersComposable.suppliers?.value || []"
      @close="bulkComposable.closeBulkModal"
      @save="handleBulkSave"
    />

    <!-- Import File Modal -->
    <ImportFileModal
      :show="importComposable.showImportModal?.value || false"
      :existing-suppliers="suppliersComposable.suppliers?.value || []"
      @close="importComposable.closeImportModal"
      @save="handleImportSave"
    />

    <!-- Export Modal -->
    <ExportModal
      :show="exportComposable.showExportModal?.value || false"
      :selected-format="exportComposable.selectedExportFormat?.value"
      :options="exportComposable.exportOptions"
      @close="exportComposable.closeExportModal"
      @select-format="exportComposable.selectedExportFormat.value = $event"
      @update-option="exportComposable.exportOptions[$event] = $event"
      @export="handleExport"
    />
  </div>
</template>

<script>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Plus, 
  Download, 
  RefreshCw,
  Building, 
  FileText,
  Trash2,
  Search,
  X
} from 'lucide-vue-next'

// Composables
import { useSuppliers } from '@/composables/ui/suppliers/useSuppliers'
import { useSupplierForm } from '@/composables/ui/suppliers/useSupplierForm'
import { useExport } from '@/composables/ui/suppliers/useExport'
import { useDropdown } from '@/composables/ui/suppliers/useDropdown'
import { useBulkSuppliers } from '@/composables/ui/suppliers/useBulkSuppliers'
import { useImportSuppliers } from '@/composables/ui/suppliers/useImportSuppliers'
import { useCreateOrder } from '@/composables/ui/suppliers/useCreateOrder'
import { useSupplierReports } from '@/composables/ui/suppliers/useSupplierReports'

// Components
import CardTemplate from '@/components/common/CardTemplate.vue'
import SupplierCard from '@/components/suppliers/SupplierCard.vue'
import SupplierFormModal from '@/components/suppliers/SupplierFormModal.vue'
import ExportModal from '@/components/suppliers/ExportModal.vue'
import BulkSuppliersModal from '@/components/suppliers/BulkSuppliersModal.vue'
import ImportFileModal from '@/components/suppliers/ImportFileModal.vue'
import CreateOrderModal from '@/components/suppliers/CreateOrderModal.vue'
import ActiveOrdersModal from '@/components/suppliers/ActiveOrdersModal.vue'
import TopPerformersModal from '@/components/suppliers/TopPerformersModal.vue'

export default {
  name: 'Suppliers',
  components: {
    Plus,
    Download,
    RefreshCw,
    Building,
    FileText,
    Trash2,
    Search,
    X,
    CardTemplate,
    SupplierCard,
    SupplierFormModal,
    BulkSuppliersModal,
    ExportModal,
    ImportFileModal,
    CreateOrderModal,
    ActiveOrdersModal,
    TopPerformersModal
  },
  setup() {
    // Initialize composables
    const suppliersComposable = useSuppliers()
    const formComposable = useSupplierForm()
    const exportComposable = useExport()
    const addDropdown = useDropdown()
    const bulkComposable = useBulkSuppliers()
    const importComposable = useImportSuppliers()
    const createOrderComposable = useCreateOrder()
    const reportsComposable = useSupplierReports()
    const router = useRouter()

    // Local reactive state for UI
    const showAddDropdown = ref(false)
    const searchMode = ref(false)
    const addDropdownRef = ref(null)
    const searchInputRef = ref(null)

    // Debug log to check if composables are working
    console.log('Suppliers composable:', suppliersComposable)
    console.log('Loading state:', suppliersComposable.loading?.value)

    // Load suppliers on mount
    onMounted(async () => {
      console.log('Suppliers component mounted')
      try {
        await suppliersComposable.fetchSuppliers()
        await reportsComposable.refreshReports()
        
        // Add click outside listener
        document.addEventListener('click', handleClickOutside)
      } catch (error) {
        console.error('Error fetching suppliers:', error)
      }
    })

    // Cleanup
    const cleanup = () => {
      document.removeEventListener('click', handleClickOutside)
    }

    // Methods
    const handleClickOutside = (event) => {
      if (addDropdownRef.value && !addDropdownRef.value.contains(event.target)) {
        showAddDropdown.value = false
      }
    }

    const toggleAddDropdown = (event) => {
      event.stopPropagation()
      showAddDropdown.value = !showAddDropdown.value
    }

    const closeAddDropdown = () => {
      showAddDropdown.value = false
    }

    const toggleSearchMode = () => {
      searchMode.value = !searchMode.value
      
      if (searchMode.value) {
        setTimeout(() => {
          if (searchInputRef.value) {
            searchInputRef.value.focus()
          }
        }, 50)
      } else {
        if (suppliersComposable.filters) {
          suppliersComposable.filters.search = ''
        }
        applyFilters()
      }
    }

    const clearSearch = () => {
      if (suppliersComposable.filters) {
        suppliersComposable.filters.search = ''
      }
      searchMode.value = false
      applyFilters()
    }

    const applyFilters = () => {
      // This would typically trigger filtering in the composable
      if (suppliersComposable.applyFilters) {
        suppliersComposable.applyFilters()
      }
    }

    const clearFilters = () => {
      if (suppliersComposable.clearFilters) {
        suppliersComposable.clearFilters()
      }
      searchMode.value = false
    }

    const handleSingleSupplier = (event) => {
      if (event) event.stopPropagation()
      formComposable.showAddSupplierModal()
      closeAddDropdown()
    }
    
    const handleBulkAdd = (event) => {
      event.stopPropagation()
      bulkComposable.openBulkModal() 
      closeAddDropdown()
    }

    const handleBulkSave = (newSuppliers) => {
      const result = bulkComposable.handleBulkSave(
        newSuppliers, 
        suppliersComposable.suppliers?.value || []
      )
      
      if (result.success) {
        suppliersComposable.successMessage.value = result.message
        
        setTimeout(() => {
          suppliersComposable.successMessage.value = null
        }, 3000)
      }
    }
    
    const handleImport = (event) => {
      if (event) event.stopPropagation()
      importComposable.openImportModal()
      closeAddDropdown()
    }

    const toggleSupplierSelection = (supplierId) => {
      const selectedSuppliers = suppliersComposable.selectedSuppliers?.value || []
      const index = selectedSuppliers.indexOf(supplierId)
      
      if (index > -1) {
        selectedSuppliers.splice(index, 1)
      } else {
        selectedSuppliers.push(supplierId)
      }
    }

    const viewSupplier = (supplier) => {
      router.push({ 
        name: 'SupplierDetails', 
        params: { supplierId: supplier.id.toString() } 
      })
    }

    const createOrder = (supplier) => {
      createOrderComposable.openCreateOrderModal(supplier)
    }

    const handleSaveSupplier = async () => {
      const result = await formComposable.saveSupplier(suppliersComposable.suppliers?.value || [])
      
      if (result.success) {
        suppliersComposable.successMessage.value = result.message
        
        setTimeout(() => {
          suppliersComposable.successMessage.value = null
        }, 3000)
      }
    }

    const handleOrderSave = async (orderData) => {
      const result = await createOrderComposable.handleOrderSave(orderData)
      
      if (result.success) {
        suppliersComposable.successMessage.value = result.message
        
        // Refresh supplier data to update purchase order count
        await suppliersComposable.fetchSuppliers()
        
        // Refresh reports
        if (reportsComposable.refreshReports) {
          await reportsComposable.refreshReports()
        }
        
        setTimeout(() => {
          suppliersComposable.successMessage.value = null
        }, 3000)
      } else {
        suppliersComposable.error.value = result.error
        
        setTimeout(() => {
          suppliersComposable.error.value = null
        }, 5000)
      }
    }

    const handleImportSave = (importedSuppliers) => {
      const result = importComposable.handleImportSave(
        importedSuppliers, 
        suppliersComposable.suppliers?.value || []
      )
      
      if (result.success) {
        suppliersComposable.successMessage.value = result.message
        
        setTimeout(() => {
          suppliersComposable.successMessage.value = null
        }, 3000)
      }
    }

    const handleExport = () => {
      const result = exportComposable.handleExport(suppliersComposable.suppliers?.value || [])
      
      if (result.success) {
        suppliersComposable.successMessage.value = result.message
        
        setTimeout(() => {
          suppliersComposable.successMessage.value = null
        }, 3000)
      } else {
        suppliersComposable.error.value = result.error
      }
    }

    const showActiveOrdersReport = () => {
      console.log('Active Orders Report clicked')
      reportsComposable.openActiveOrdersModal()
    }

    const showTopSuppliersReport = () => {
      console.log('Top Suppliers Report clicked')
      reportsComposable.openTopPerformersModal()
    }

    const handleViewAllOrders = () => {
      const route = reportsComposable.handleViewAllOrders()
      router.push(route)
    }

    return {
      // Composables
      suppliersComposable,
      formComposable,
      exportComposable,
      addDropdown,
      bulkComposable,
      importComposable,
      createOrderComposable,
      reportsComposable,
      
      // Local state
      showAddDropdown,
      searchMode,
      addDropdownRef,
      searchInputRef,
      
      // Methods
      handleSingleSupplier,
      handleBulkAdd,
      handleImport,
      toggleSupplierSelection,
      viewSupplier,
      createOrder,
      handleOrderSave,
      handleSaveSupplier,
      handleBulkSave,
      handleImportSave,
      handleExport,
      showActiveOrdersReport,
      showTopSuppliersReport,
      handleViewAllOrders,
      toggleAddDropdown,
      closeAddDropdown,
      toggleSearchMode,
      clearSearch,
      applyFilters,
      clearFilters,
      cleanup
    }
  }
}
</script>

<style scoped>
/* Import colors and buttons CSS */
@import '@/assets/styles/colors.css';
@import '@/assets/styles/buttons.css';

.suppliers-page {
  background-color: var(--neutral-light);
  min-height: 100vh;
}

.text-primary-dark {
  color: var(--primary-dark) !important;
}

.text-tertiary-dark {
  color: var(--tertiary-dark) !important;
}

.text-tertiary-medium {
  color: var(--tertiary-medium) !important;
}

/* Action Bar Container */
.action-bar-container {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  overflow: visible;
  position: relative;
  z-index: 1000;
}

.action-bar-controls {
  border-bottom: 1px solid var(--neutral);
  background-color: white;
  position: relative;
  z-index: 1001;
}

.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

/* Filter Dropdown */
.filter-dropdown {
  min-width: 120px;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--tertiary-medium);
  margin-bottom: 0.25rem;
  display: block;
}

/* Search Container */
.search-container {
  min-width: 300px;
}

.search-input {
  padding-right: 2.5rem;
  height: calc(1.5em + 0.75rem + 2px);
}

.search-container .position-relative .btn {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Custom dropdown styling */
.dropdown {
  position: relative;
  z-index: 1100;
}

.custom-dropdown-menu {
  min-width: 280px;
  border: 1px solid var(--neutral);
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  animation: dropdownSlide 0.2s ease;
  z-index: 1200 !important;
  position: absolute !important;
  top: 100% !important;
  left: 0 !important;
  transform: none !important;
}

.custom-dropdown-menu.show {
  display: block !important;
  z-index: 1200 !important;
}

@keyframes dropdownSlide {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.custom-dropdown-item {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--neutral-light);
  transition: all 0.2s ease;
}

.custom-dropdown-item:last-child {
  border-bottom: none;
}

.custom-dropdown-item:hover {
  background-color: var(--primary-light);
}

/* Button States */
.btn.active {
  background-color: var(--primary);
  border-color: var(--primary);
  color: white;
}

/* Custom hover states for import/export buttons */
.btn.btn-outline-secondary:hover {
  background-color: var(--info-light);
  border-color: var(--info);
  color: var(--info-dark);
}

/* Form controls focus states */
.form-select:focus,
.form-control:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .action-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-container {
    min-width: 100%;
  }
}

@media (max-width: 576px) {
  .btn-sm {
    font-size: 0.8rem;
    padding: 0.375rem 0.5rem;
  }
}
</style>