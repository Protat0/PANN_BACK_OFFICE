<template>
  <div class="container-fluid py-4 suppliers-page">
    <!-- Header Section -->
    <div class="d-flex justify-content-between align-items-center mb-4 page-header">
      <h1 class="h2 fw-semibold text-primary-dark mb-0">Supplier Management</h1>
      <div class="d-flex gap-2 flex-wrap">
        <!-- Add Suppliers Dropdown -->
        <div class="dropdown" ref="addDropdownRef">
          <button 
            class="btn btn-primary btn-sm btn-with-icon-sm dropdown-toggle" 
            type="button"
            @click="addDropdown.toggleDropdown"
            :class="{ 'active': addDropdown.showDropdown.value }"
          >
            <Plus :size="16" />
            Add Suppliers
          </button>
          
          <div 
            class="dropdown-menu custom-dropdown-menu" 
            :class="{ 'show': addDropdown.showDropdown.value }"
          >
            <button class="dropdown-item custom-dropdown-item" @click="handleSingleSupplier">
              <div class="d-flex align-items-center gap-3">
                <Plus :size="18" class="text-primary" />
                <div>
                  <div class="fw-semibold">Single Supplier</div>
                  <small class="text-muted">Add one supplier manually</small>
                </div>
              </div>
            </button>
            
            <button class="dropdown-item custom-dropdown-item" @click="handleBulkAdd">
              <div class="d-flex align-items-center gap-3">
                <Building :size="18" class="text-primary" />
                <div>
                  <div class="fw-semibold">Bulk Entry</div>
                  <small class="text-muted">Add multiple suppliers (5-20 items)</small>
                </div>
              </div>
            </button>
            
            <button class="dropdown-item custom-dropdown-item" @click="handleImport">
              <div class="d-flex align-items-center gap-3">
                <FileText :size="18" class="text-primary" />
                <div>
                  <div class="fw-semibold">Import File</div>
                  <small class="text-muted">Upload CSV/Excel (20+ items)</small>
                </div>
              </div>
            </button>
          </div>
        </div>
        
        <button 
          class="btn btn-outline-primary btn-sm btn-with-icon-sm"
          @click="exportComposable.openExportModal"
        >
          <Download :size="16" />
          Export
        </button>
        <button 
          class="btn btn-outline-secondary btn-sm btn-with-icon-sm"
          @click="suppliersComposable.refreshData" 
          :disabled="suppliersComposable.loading.value"
          :class="{ 'btn-loading': suppliersComposable.loading.value }"
        >
          <RefreshCw :size="16" :class="{ 'spin': suppliersComposable.loading.value }" />
          {{ suppliersComposable.loading.value ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Reports Section -->
    <div class="row mb-4" v-if="!suppliersComposable.loading.value">
      <div class="col-md-6 col-lg-3 mb-3">
        <div class="card border-start border-warning border-4 h-100 report-card" @click="showActiveOrdersReport">
          <div class="card-body">
            <h6 class="card-title text-tertiary-dark mb-2">Active Orders</h6>
            <h2 class="text-warning fw-bold mb-1">{{ suppliersComposable.reportData.activeOrdersCount }}</h2>
            <small class="text-tertiary-medium">Pending Purchase Orders</small>
          </div>
        </div>
      </div>
      <div class="col-md-6 col-lg-3 mb-3">
        <div class="card border-start border-success border-4 h-100 report-card" @click="showTopSuppliersReport">
          <div class="card-body">
            <h6 class="card-title text-tertiary-dark mb-2">Top Performers</h6>
            <h2 class="text-success fw-bold mb-1">{{ suppliersComposable.reportData.topSuppliersCount }}</h2>
            <small class="text-tertiary-medium">High Volume Suppliers</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-6 col-lg-3">
            <label for="typeFilter" class="form-label text-tertiary-dark fw-medium">Type</label>
            <select id="typeFilter" class="form-select" v-model="suppliersComposable.filters.type">
              <option value="all">All Types</option>
              <option value="food">Food & Beverages</option>
              <option value="packaging">Packaging</option>
              <option value="equipment">Equipment</option>
              <option value="services">Services</option>
            </select>
          </div>
          
          <div class="col-md-6 col-lg-3">
            <label for="statusFilter" class="form-label text-tertiary-dark fw-medium">Status</label>
            <select id="statusFilter" class="form-select" v-model="suppliersComposable.filters.status">
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="pending">Pending</option>
            </select>
          </div>

          <div class="col-md-6 col-lg-3">
            <label for="orderFilter" class="form-label text-tertiary-dark fw-medium">Order Volume</label>
            <select id="orderFilter" class="form-select" v-model="suppliersComposable.filters.order">
              <option value="all">All Volumes</option>
              <option value="high">High Volume (10+)</option>
              <option value="medium">Medium Volume (5-9)</option>
              <option value="low">Low Volume (1-4)</option>
              <option value="none">No Orders</option>
            </select>
          </div>

          <div class="col-md-6 col-lg-3">
            <label for="searchFilter" class="form-label text-tertiary-dark fw-medium">Search</label>
            <input 
              id="searchFilter" 
              v-model="suppliersComposable.filters.search" 
              type="text" 
              class="form-control"
              placeholder="Search by name, email, or phone..."
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="suppliersComposable.loading.value && suppliersComposable.suppliers.value.length === 0" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-tertiary-medium">Loading suppliers...</p>
    </div>

    <!-- Error State -->
    <div v-if="suppliersComposable.error.value" class="alert alert-danger text-center" role="alert">
      <p class="mb-3">{{ suppliersComposable.error.value }}</p>
      <button class="btn btn-primary" @click="suppliersComposable.refreshData">Try Again</button>
    </div>

    <!-- Success Message -->
    <div v-if="suppliersComposable.successMessage.value" class="alert alert-success text-center" role="alert">
      {{ suppliersComposable.successMessage.value }}
    </div>

    <!-- Table Controls -->
    <div v-if="!suppliersComposable.loading.value || suppliersComposable.suppliers.value.length > 0" class="card mb-3">
      <div class="card-body py-3">
        <div class="d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center gap-3">
            <button 
              class="btn btn-sm btn-danger"
              @click="suppliersComposable.deleteSelected" 
              :disabled="suppliersComposable.selectedSuppliers.value.length === 0 || suppliersComposable.loading.value"
            >
              <i class="bi bi-trash me-1"></i>
              Delete Selected ({{ suppliersComposable.selectedSuppliers.value.length }})
            </button>
          </div>
          <small class="text-tertiary-medium">
            Showing {{ suppliersComposable.filteredSuppliers.value.length }} of {{ suppliersComposable.suppliers.value.length }} suppliers
          </small>
        </div>
      </div>
    </div>

    <!-- Suppliers Grid -->
    <div v-if="!suppliersComposable.loading.value || suppliersComposable.suppliers.value.length > 0" class="row g-4">
      <div 
        v-for="supplier in suppliersComposable.filteredSuppliers.value" 
        :key="supplier.id"
        class="col-12 col-md-6 col-lg-4"
      >
        <SupplierCard
          :supplier="supplier"
          :is-selected="suppliersComposable.selectedSuppliers.value.includes(supplier.id)"
          @toggle-select="toggleSupplierSelection"
          @edit="formComposable.editSupplier"
          @view="viewSupplier"
          @create-order="createOrder"
          @delete="suppliersComposable.deleteSupplier"
        />
      </div>

      <!-- Empty State -->
      <div v-if="suppliersComposable.filteredSuppliers.value.length === 0" class="col-12">
        <div class="text-center py-5">
          <div class="card">
            <div class="card-body py-5">
              <i class="bi bi-building display-1 text-muted mb-3"></i>
              <p class="text-tertiary-medium mb-3">
                {{ suppliersComposable.suppliers.value.length === 0 ? 'No suppliers found' : 'No suppliers match the current filters' }}
              </p>
              <button 
                v-if="suppliersComposable.suppliers.value.length === 0" 
                class="btn btn-primary" 
                @click="handleSingleSupplier"
              >
                <i class="bi bi-plus me-1"></i>
                Add First Supplier
              </button>
              <button 
                v-else 
                class="btn btn-secondary" 
                @click="suppliersComposable.clearFilters"
              >
                <i class="bi bi-arrow-clockwise me-1"></i>
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Order Modal -->
    <CreateOrderModal
      :show="createOrderComposable.showCreateOrderModal.value"
      :supplier="createOrderComposable.selectedSupplier.value"
      @close="createOrderComposable.closeCreateOrderModal"
      @save="handleOrderSave"
    />

    <!-- Add Supplier Modal -->
    <SupplierFormModal
      :show="formComposable.showAddModal.value"
      :is-edit="formComposable.isEditMode.value"
      :form-data="formComposable.formData"
      :form-errors="formComposable.formErrors.value"
      :loading="formComposable.formLoading.value"
      :is-valid="formComposable.isFormValid.value"
      :add-another="formComposable.addAnotherAfterSave.value"
      @close="formComposable.closeAddModal"
      @save="handleSaveSupplier"
      @clear-error="formComposable.clearFormError"
      @update:add-another="formComposable.addAnotherAfterSave.value = $event"
    />

    <!-- Bulk Suppliers Modal -->
    <BulkSuppliersModal
      :show="bulkComposable.showBulkModal.value"
      :existing-suppliers="suppliersComposable.suppliers.value"
      @close="bulkComposable.closeBulkModal"
      @save="handleBulkSave"
    />

    <!-- Import File Modal -->
    <ImportFileModal
      :show="importComposable.showImportModal.value"
      :existing-suppliers="suppliersComposable.suppliers.value"
      @close="importComposable.closeImportModal"
      @save="handleImportSave"
    />

    <!-- Export Modal -->
    <ExportModal
      :show="exportComposable.showExportModal.value"
      :selected-format="exportComposable.selectedExportFormat.value"
      :options="exportComposable.exportOptions"
      @close="exportComposable.closeExportModal"
      @select-format="exportComposable.selectedExportFormat.value = $event"
      @update-option="exportComposable.exportOptions[$event] = $event"
      @export="handleExport"
    />
  </div>
</template>

<script>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Plus, 
  Download, 
  RefreshCw,
  Building, 
  FileText
} from 'lucide-vue-next'

// Composables
import { useSuppliers } from '@/composables/ui/suppliers/useSuppliers'
import { useSupplierForm } from '@/composables/ui/suppliers/useSupplierForm'
import { useExport } from '@/composables/ui/suppliers/useExport'
import { useDropdown } from '@/composables/ui/suppliers/useDropdown'
import { useBulkSuppliers } from '@/composables/ui/suppliers/useBulkSuppliers'
import { useImportSuppliers } from '@/composables/ui/suppliers/useImportSuppliers'
import { useCreateOrder } from '@/composables/ui/suppliers/useCreateOrder'

// Components
import SupplierCard from '@/components/suppliers/SupplierCard.vue'
import SupplierFormModal from '@/components/suppliers/SupplierFormModal.vue'
import ExportModal from '@/components/suppliers/ExportModal.vue'
import BulkSuppliersModal from '@/components/suppliers/BulkSuppliersModal.vue'
import ImportFileModal from '@/components/suppliers/ImportFileModal.vue'
import CreateOrderModal from '@/components/suppliers/CreateOrderModal.vue'

export default {
  name: 'Suppliers',
  components: {
    Plus,
    Download,
    RefreshCw,
    Building,
    FileText,
    SupplierCard,
    SupplierFormModal,
    BulkSuppliersModal,
    ExportModal,
    ImportFileModal,
    CreateOrderModal
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
    const router = useRouter()

    // Load suppliers on mount
    onMounted(async () => {
      console.log('Suppliers component mounted')
      await suppliersComposable.fetchSuppliers()
    })

    // Methods
    const handleSingleSupplier = (event) => {
      if (event) event.stopPropagation()
      formComposable.showAddSupplierModal()
      addDropdown.closeDropdown()
    }
    
    const handleBulkAdd = (event) => {
      event.stopPropagation()
      bulkComposable.openBulkModal() 
      addDropdown.closeDropdown()
    }

    const handleBulkSave = (newSuppliers) => {
      const result = bulkComposable.handleBulkSave(
        newSuppliers, 
        suppliersComposable.suppliers.value
      )
      
      if (result.success) {
        suppliersComposable.successMessage.value = result.message
        
        setTimeout(() => {
          suppliersComposable.successMessage.value = null
        }, 3000)
      }
    }
    
    const handleImport = (event) => {
      event.stopPropagation()
      importComposable.openImportModal()
      addDropdown.closeDropdown()
    }

    const toggleSupplierSelection = (supplierId) => {
      const selectedSuppliers = suppliersComposable.selectedSuppliers.value
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
      const result = await formComposable.saveSupplier(suppliersComposable.suppliers.value)
      
      if (result.success) {
        suppliersComposable.successMessage.value = result.message
        
        setTimeout(() => {
          suppliersComposable.successMessage.value = null
        }, 3000)
      }
    }

    const handleOrderSave = (orderData) => {
      const result = createOrderComposable.handleOrderSave(
        orderData, 
        suppliersComposable.suppliers.value
      )
      
      if (result.success) {
        suppliersComposable.successMessage.value = result.message
        
        setTimeout(() => {
          suppliersComposable.successMessage.value = null
        }, 3000)
      } else {
        suppliersComposable.error.value = result.error
      }
    }

    const handleImportSave = (importedSuppliers) => {
      const result = importComposable.handleImportSave(
        importedSuppliers, 
        suppliersComposable.suppliers.value
      )
      
      if (result.success) {
        suppliersComposable.successMessage.value = result.message
        
        setTimeout(() => {
          suppliersComposable.successMessage.value = null
        }, 3000)
      }
    }

    const handleExport = () => {
      const result = exportComposable.handleExport(suppliersComposable.suppliers.value)
      
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
      alert('Active Orders Report - Coming soon!')
    }

    const showTopSuppliersReport = () => {
      alert('Top Suppliers Report - Coming soon!')
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
      showTopSuppliersReport
    }
  }
}
</script>

<style scoped>
/* Import colors and buttons CSS */
@import '@/assets/styles/colors.css';
@import '@/assets/styles/buttons.css';

/* Custom dropdown styling */
.custom-dropdown-menu {
  min-width: 280px;
  border: 1px solid var(--neutral);
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  animation: dropdownSlide 0.2s ease;
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

/* Report cards hover effect */
.report-card {
  cursor: pointer;
  transition: all 0.2s ease;
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.15);
}

/* Custom color classes using colors.css variables */
.text-primary-dark {
  color: var(--primary-dark) !important;
}

.text-tertiary-dark {
  color: var(--tertiary-dark) !important;
}

.text-tertiary-medium {
  color: var(--tertiary-medium) !important;
}

/* Spin animation for refresh button */
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Form controls focus states */
.form-select:focus,
.form-control:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25);
}

/* Suppliers page background */
.suppliers-page {
  background-color: var(--neutral-light);
  min-height: 100vh;
}

/* Page header styling */
.page-header {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .custom-dropdown-menu {
    min-width: 250px;
    right: 0;
    left: auto;
  }
  
  .custom-dropdown-item {
    padding: 0.875rem 1rem;
  }
  
  .page-header {
    padding: 1rem;
  }
  
  .page-header h1 {
    font-size: 1.5rem;
  }
  
  .d-flex.gap-2.flex-wrap {
    gap: 0.5rem !important;
  }
}

@media (max-width: 576px) {
  .btn-sm {
    font-size: 0.8rem;
    padding: 0.375rem 0.5rem;
  }
  
  .custom-dropdown-menu {
    min-width: 220px;
  }
}
</style>