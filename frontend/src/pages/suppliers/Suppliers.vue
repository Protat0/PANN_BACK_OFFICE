<template>
  <div class="container-fluid py-4 suppliers-page">
    <!-- Header Section -->
    <div class="d-flex justify-content-between align-items-center mb-4 page-header">
      <h1 class="h2 fw-semibold text-primary-dark mb-0">Supplier Management</h1>
      <div class="d-flex gap-2 flex-wrap">
        <!-- Add Suppliers Dropdown -->
        <div class="dropdown" ref="addDropdown">
          <button 
            class="btn btn-success-light btn-with-icon dropdown-toggle" 
            type="button"
            @click="toggleAddDropdown"
            :class="{ 'active': showAddDropdown }"
          >
            <Plus :size="16" />
            Add Suppliers
          </button>
          
          <div 
            class="dropdown-menu custom-dropdown-menu" 
            :class="{ 'show': showAddDropdown }"
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
          class="btn btn-primary-light btn-with-icon"
          @click="exportData"
        >
          <Download :size="16" />
          Export
        </button>
        <button 
          class="btn btn-info-light btn-with-icon"
          @click="refreshData" 
          :disabled="loading"
          :class="{ 'btn-loading': loading }"
        >
          <RefreshCw :size="16" :class="{ 'spin': loading }" />
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Reports Section -->
    <div class="row mb-4" v-if="!loading">
      <div class="col-md-6 col-lg-3 mb-3">
        <div class="card border-start border-warning border-4 h-100 report-card" @click="showActiveOrdersReport">
          <div class="card-body">
            <h6 class="card-title text-tertiary-dark mb-2">Active Orders</h6>
            <h2 class="text-warning fw-bold mb-1">{{ activeOrdersCount }}</h2>
            <small class="text-tertiary-medium">Pending Purchase Orders</small>
          </div>
        </div>
      </div>
      <div class="col-md-6 col-lg-3 mb-3">
        <div class="card border-start border-success border-4 h-100 report-card" @click="showTopSuppliersReport">
          <div class="card-body">
            <h6 class="card-title text-tertiary-dark mb-2">Top Performers</h6>
            <h2 class="text-success fw-bold mb-1">{{ topSuppliersCount }}</h2>
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
            <select id="typeFilter" class="form-select" v-model="typeFilter" @change="applyFilters">
              <option value="all">All Types</option>
              <option value="food">Food & Beverages</option>
              <option value="packaging">Packaging</option>
              <option value="equipment">Equipment</option>
              <option value="services">Services</option>
            </select>
          </div>
          
          <div class="col-md-6 col-lg-3">
            <label for="statusFilter" class="form-label text-tertiary-dark fw-medium">Status</label>
            <select id="statusFilter" class="form-select" v-model="statusFilter" @change="applyFilters">
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="pending">Pending</option>
            </select>
          </div>

          <div class="col-md-6 col-lg-3">
            <label for="orderFilter" class="form-label text-tertiary-dark fw-medium">Order Volume</label>
            <select id="orderFilter" class="form-select" v-model="orderFilter" @change="applyFilters">
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
              v-model="searchFilter" 
              @input="applyFilters"
              type="text" 
              class="form-control"
              placeholder="Search by name, email, or phone..."
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && suppliers.length === 0" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-tertiary-medium">Loading suppliers...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="alert alert-danger text-center" role="alert">
      <p class="mb-3">{{ error }}</p>
      <button class="btn btn-primary" @click="refreshData">Try Again</button>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="alert alert-success text-center" role="alert">
      {{ successMessage }}
    </div>

    <!-- Table Controls -->
    <div v-if="!loading || suppliers.length > 0" class="card mb-3">
      <div class="card-body py-3">
        <div class="d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center gap-3">
            <button 
              class="btn btn-sm btn-danger"
              @click="deleteSelected" 
              :disabled="selectedSuppliers.length === 0 || loading"
            >
              <i class="bi bi-trash me-1"></i>
              Delete Selected ({{ selectedSuppliers.length }})
            </button>
          </div>
          <small class="text-tertiary-medium">
            Showing {{ filteredSuppliers.length }} of {{ suppliers.length }} suppliers
          </small>
        </div>
      </div>
    </div>

    <!-- Suppliers Grid -->
    <div v-if="!loading || suppliers.length > 0" class="row g-4">
      <div 
        v-for="supplier in filteredSuppliers" 
        :key="supplier.id"
        class="col-12 col-md-6 col-lg-4"
      >
        <div class="card h-100 supplier-card" :class="{ 'card-selected': selectedSuppliers.includes(supplier.id) }">
          <div class="card-body d-flex flex-column">
            <!-- Supplier Header with Checkbox -->
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="d-flex align-items-center">
                <input 
                  type="checkbox" 
                  class="form-check-input me-3"
                  :value="supplier.id"
                  v-model="selectedSuppliers"
                />
                <div class="supplier-icon me-3">
                  <i class="bi bi-building"></i>
                </div>
                <h5 class="card-title mb-0 supplier-name">{{ supplier.name }}</h5>
              </div>
              <div class="dropdown">
                <button 
                  class="btn btn-link p-0 text-muted"
                  type="button"
                  :id="`dropdownMenuButton${supplier.id}`"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  <i class="bi bi-three-dots-vertical"></i>
                </button>
                <ul class="dropdown-menu" :aria-labelledby="`dropdownMenuButton${supplier.id}`">
                  <li>
                    <a class="dropdown-item" href="#" @click.prevent="editSupplier(supplier)">
                      <i class="bi bi-pencil me-2"></i>Edit
                    </a>
                  </li>
                  <li>
                    <a class="dropdown-item" href="#" @click.prevent="viewSupplier(supplier)">
                      <i class="bi bi-eye me-2"></i>View Details
                    </a>
                  </li>
                  <li>
                    <a class="dropdown-item" href="#" @click.prevent="createOrder(supplier)">
                      <i class="bi bi-plus me-2"></i>New Order
                    </a>
                  </li>
                  <li><hr class="dropdown-divider"></li>
                  <li>
                    <a class="dropdown-item text-danger" href="#" @click.prevent="deleteSupplier(supplier)">
                      <i class="bi bi-trash me-2"></i>Delete
                    </a>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Supplier Info -->
            <div class="mb-3">
              <div class="supplier-contact mb-2">
                <i class="bi bi-envelope text-muted me-2"></i>
                <span class="text-muted">{{ supplier.email || 'No email' }}</span>
              </div>
              <div class="supplier-contact mb-2">
                <i class="bi bi-telephone text-muted me-2"></i>
                <span class="text-muted">{{ supplier.phone || 'No phone' }}</span>
              </div>
              <div class="supplier-contact">
                <i class="bi bi-geo-alt text-muted me-2"></i>
                <span class="text-muted">{{ getShortAddress(supplier.address) }}</span>
              </div>
            </div>

            <!-- Purchase Orders Info -->
            <div class="mb-3 mt-auto">
              <p class="text-muted mb-1 purchase-orders-label">Purchase Orders</p>
              <div class="d-flex justify-content-between align-items-center">
                <span class="purchase-orders-count">{{ supplier.purchaseOrders }}</span>
                <span :class="['badge', 'rounded-pill', getStatusBadgeClass(supplier.status)]">
                  {{ formatStatus(supplier.status) }}
                </span>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="d-flex gap-2 mt-2">
              <button 
                class="btn btn-outline-primary btn-sm flex-fill"
                @click="viewSupplier(supplier)"
              >
                <i class="bi bi-eye me-1"></i>
                View
              </button>
              <button 
                class="btn btn-outline-success btn-sm flex-fill"
                @click="createOrder(supplier)"
              >
                <i class="bi bi-plus me-1"></i>
                Order
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredSuppliers.length === 0" class="col-12">
        <div class="text-center py-5">
          <div class="card">
            <div class="card-body py-5">
              <i class="bi bi-building display-1 text-muted mb-3"></i>
              <p class="text-tertiary-medium mb-3">
                {{ suppliers.length === 0 ? 'No suppliers found' : 'No suppliers match the current filters' }}
              </p>
              <button 
                v-if="suppliers.length === 0" 
                class="btn btn-primary" 
                @click="handleSingleSupplier"
              >
                <i class="bi bi-plus me-1"></i>
                Add First Supplier
              </button>
              <button 
                v-else 
                class="btn btn-secondary" 
                @click="clearFilters"
              >
                <i class="bi bi-arrow-clockwise me-1"></i>
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Supplier Modal -->
    <div v-if="showAddModal" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content modern-supplier-modal">
          <!-- Modal Header -->
          <div class="modal-header border-0 pb-0">
            <div class="d-flex align-items-center">
              <div class="modal-icon me-3">
                <Building :size="24" />
              </div>
              <div>
                <h4 class="modal-title mb-1">{{ isEditMode ? 'Edit Supplier' : 'Add New Supplier' }}</h4>
                <p class="text-muted mb-0 small">{{ isEditMode ? 'Update supplier information' : 'Enter supplier details to add them to your network' }}</p>
              </div>
            </div>
            <button 
              type="button" 
              class="btn-close" 
              @click="closeAddModal"
              aria-label="Close"
            ></button>
          </div>

          <!-- Modal Body -->
          <div class="modal-body pt-4">
            <form @submit.prevent="saveSupplier">
              <div class="row g-4">
                <!-- Left Column -->
                <div class="col-md-6">
                  <!-- Company/Supplier Name -->
                  <div class="form-group">
                    <label for="supplierName" class="form-label required">
                      <Building :size="16" class="me-2" />
                      Company Name
                    </label>
                    <input 
                      type="text" 
                      class="form-control modern-input" 
                      :class="{ 'is-invalid': formErrors.name }"
                      id="supplierName"
                      v-model="formData.name"
                      @input="clearFormError('name')"
                      placeholder="Enter company or supplier name"
                      required
                    >
                    <div v-if="formErrors.name" class="invalid-feedback">
                      {{ formErrors.name }}
                    </div>
                  </div>

                  <!-- Contact Person -->
                  <div class="form-group">
                    <label for="contactPerson" class="form-label">
                      <i class="bi bi-person me-2"></i>
                      Contact Person
                    </label>
                    <input 
                      type="text" 
                      class="form-control modern-input"
                      id="contactPerson"
                      v-model="formData.contactPerson"
                      placeholder="Primary contact name"
                    >
                  </div>

                  <!-- Email -->
                  <div class="form-group">
                    <label for="email" class="form-label">
                      <Mail :size="16" class="me-2" />
                      Email Address
                    </label>
                    <input 
                      type="email" 
                      class="form-control modern-input" 
                      :class="{ 'is-invalid': formErrors.email }"
                      id="email"
                      v-model="formData.email"
                      @input="clearFormError('email')"
                      placeholder="company@example.com"
                    >
                    <div v-if="formErrors.email" class="invalid-feedback">
                      {{ formErrors.email }}
                    </div>
                  </div>
                </div>

                <!-- Right Column -->
                <div class="col-md-6">
                  <!-- Phone Number -->
                  <div class="form-group">
                    <label for="phone" class="form-label">
                      <Phone :size="16" class="me-2" />
                      Phone Number
                    </label>
                    <input 
                      type="tel" 
                      class="form-control modern-input" 
                      :class="{ 'is-invalid': formErrors.phone }"
                      id="phone"
                      v-model="formData.phone"
                      @input="clearFormError('phone')"
                      placeholder="+63 912 345 6789"
                    >
                    <div v-if="formErrors.phone" class="invalid-feedback">
                      {{ formErrors.phone }}
                    </div>
                  </div>

                  <!-- Supplier Type -->
                  <div class="form-group">
                    <label for="supplierType" class="form-label">
                      <i class="bi bi-tag me-2"></i>
                      Supplier Type
                    </label>
                    <select 
                      class="form-select modern-input" 
                      id="supplierType"
                      v-model="formData.type"
                    >
                      <option value="">Select supplier type</option>
                      <option value="food">Food & Beverages</option>
                      <option value="packaging">Packaging Materials</option>
                      <option value="equipment">Equipment & Tools</option>
                      <option value="services">Services</option>
                      <option value="raw_materials">Raw Materials</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <!-- Status -->
                  <div class="form-group">
                    <label for="status" class="form-label">
                      <i class="bi bi-check-circle me-2"></i>
                      Status
                    </label>
                    <select 
                      class="form-select modern-input" 
                      id="status"
                      v-model="formData.status"
                    >
                      <option value="active">Active</option>
                      <option value="pending">Pending Approval</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>
                </div>

                <!-- Full Width Address -->
                <div class="col-12">
                  <div class="form-group">
                    <label for="address" class="form-label">
                      <MapPin :size="16" class="me-2" />
                      Business Address
                    </label>
                    <textarea 
                      class="form-control modern-input" 
                      :class="{ 'is-invalid': formErrors.address }"
                      id="address"
                      v-model="formData.address"
                      @input="clearFormError('address')"
                      rows="3"
                      placeholder="Enter complete business address including city and postal code"
                    ></textarea>
                    <div v-if="formErrors.address" class="invalid-feedback">
                      {{ formErrors.address }}
                    </div>
                  </div>
                </div>

                <!-- Notes Section -->
                <div class="col-12">
                  <div class="form-group mb-0">
                    <label for="notes" class="form-label">
                      <i class="bi bi-file-text me-2"></i>
                      Additional Notes
                    </label>
                    <textarea 
                      class="form-control modern-input" 
                      id="notes"
                      v-model="formData.notes"
                      rows="3"
                      placeholder="Any additional information about this supplier (payment terms, delivery schedules, etc.)"
                    ></textarea>
                    <small class="text-muted">Optional: Add any relevant notes about this supplier relationship</small>
                  </div>
                </div>
              </div>
            </form>
          </div>

          <!-- Modal Footer -->
          <div class="modal-footer border-0 pt-4">
            <div class="d-flex justify-content-between align-items-center w-100">
              <div class="form-check">
                <input class="form-check-input" type="checkbox" id="addAnother" v-model="addAnotherAfterSave">
                <label class="form-check-label text-muted" for="addAnother">
                  Add another supplier after saving
                </label>
              </div>
              <div class="d-flex gap-3">
                <button 
                  type="button" 
                  class="btn btn-outline-secondary px-4"
                  @click="closeAddModal"
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  class="btn btn-primary px-4"
                  @click="saveSupplier"
                  :disabled="!isFormValid || formLoading"
                  :class="{ 'btn-loading': formLoading }"
                >
                  <div v-if="formLoading" class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                  {{ isEditMode ? 'Update Supplier' : 'Add Supplier' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Modal -->
    <div v-if="showExportModal" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Export Suppliers</h5>
            <button 
              type="button" 
              class="btn-close" 
              @click="closeExportModal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <p class="mb-4 text-muted">
              Choose the format you want to export your suppliers data:
            </p>
            
            <div class="export-options">
              <div class="row g-3">
                <div class="col-6">
                  <div 
                    class="export-option"
                    :class="{ active: selectedExportFormat === 'excel' }"
                    @click="selectedExportFormat = 'excel'"
                  >
                    <div class="export-icon excel">
                      <i class="bi bi-file-earmark-excel"></i>
                    </div>
                    <div class="export-details">
                      <h6>Excel</h6>
                      <small class="text-muted">.xlsx format</small>
                    </div>
                  </div>
                </div>
                
                <div class="col-6">
                  <div 
                    class="export-option"
                    :class="{ active: selectedExportFormat === 'csv' }"
                    @click="selectedExportFormat = 'csv'"
                  >
                    <div class="export-icon csv">
                      <i class="bi bi-file-earmark-text"></i>
                    </div>
                    <div class="export-details">
                      <h6>CSV</h6>
                      <small class="text-muted">.csv format</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Export Options -->
            <div class="mt-4">
              <h6 class="mb-3">Export Options</h6>
              <div class="form-check">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  id="includeInactive"
                  v-model="exportOptions.includeInactive"
                >
                <label class="form-check-label" for="includeInactive">
                  Include inactive suppliers
                </label>
              </div>
              <div class="form-check">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  id="includeDetails"
                  v-model="exportOptions.includeDetails"
                >
                <label class="form-check-label" for="includeDetails">
                  Include detailed information
                </label>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="closeExportModal"
            >
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary"
              @click="handleExport"
              :disabled="!selectedExportFormat"
            >
              <i class="bi bi-download me-2"></i>
              Export
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { 
  Plus, 
  Download, 
  RefreshCw, 
  Edit, 
  Building, 
  FileText,
  Mail,
  Phone,
  MapPin
} from 'lucide-vue-next'

export default {
  name: 'Suppliers',
  components: {
    Plus,
    Download,
    RefreshCw,
    Edit,
    Building,
    FileText,
    Mail,
    Phone,
    MapPin
  },
  data() {
    return {
      suppliers: [],
      filteredSuppliers: [],
      selectedSuppliers: [],
      loading: false,
      error: null,
      successMessage: null,
      
      // Dropdown state
      showAddDropdown: false,
      
      // Report data
      activeOrdersCount: 0,
      topSuppliersCount: 0,
      
      // Filters
      typeFilter: 'all',
      statusFilter: 'all',
      orderFilter: 'all',
      searchFilter: '',
      
      // Modal states
      showAddModal: false,
      showExportModal: false,
      isEditMode: false,
      formLoading: false,
      selectedSupplier: null,
      
      // Form data
      formData: {
        name: '',
        contactPerson: '',
        email: '',
        phone: '',
        address: '',
        type: '',
        status: 'active',
        notes: ''
      },
      formErrors: {},
      addAnotherAfterSave: false,
      
      // Export data
      selectedExportFormat: '',
      exportOptions: {
        includeInactive: false,
        includeDetails: true
      }
    }
  },
  computed: {
    isFormValid() {
      return this.formData.name.trim() !== '' && Object.keys(this.formErrors).length === 0
    }
  },
  async mounted() {
    console.log('Suppliers component mounted')
    await this.fetchSuppliers()
    
    // Close dropdown when clicking outside
    document.addEventListener('click', this.handleClickOutside)
  },
  
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
  },
  
  methods: {
    // Click outside handler for dropdown
    handleClickOutside(event) {
      if (this.$refs.addDropdown && !this.$refs.addDropdown.contains(event.target)) {
        this.showAddDropdown = false
      }
    },

    // Dropdown Methods
    toggleAddDropdown(event) {
      event.stopPropagation()
      this.showAddDropdown = !this.showAddDropdown
    },
    
    closeAddDropdown() {
      this.showAddDropdown = false
    },
    
    handleSingleSupplier(event) {
      if (event) event.stopPropagation()
      this.showAddSupplierModal()
      this.closeAddDropdown()
    },
    
    handleBulkAdd(event) {
      event.stopPropagation()
      alert('Bulk add functionality - Coming soon!')
      this.closeAddDropdown()
    },
    
    handleImport(event) {
      event.stopPropagation()
      alert('Import functionality - Coming soon!')
      this.closeAddDropdown()
    },

    async fetchSuppliers() {
      this.loading = true
      this.error = null
      
      try {
        // Mock data - replace with actual API call
        const mockSuppliers = [
          {
            id: 1,
            name: 'John Doe Supplies',
            email: 'john@johndoesupplies.com',
            phone: '+63 912 345 6789',
            address: '123 Supply Street, Business District, Manila, Philippines',
            purchaseOrders: 4,
            status: 'active',
            type: 'food',
            createdAt: '2024-01-15'
          },
          {
            id: 2,
            name: 'Bravo Warehouse',
            email: 'contact@bravowarehouse.com',
            phone: '+63 917 888 9999',
            address: '456 Warehouse Ave, Industrial Park, Quezon City, Philippines',
            purchaseOrders: 5,
            status: 'active',
            type: 'packaging',
            createdAt: '2024-02-01'
          },
          {
            id: 3,
            name: 'San Juan Groups',
            email: 'info@sanjuangroups.ph',
            phone: '+63 922 111 2222',
            address: '789 Corporate Blvd, Makati City, Philippines',
            purchaseOrders: 12,
            status: 'active',
            type: 'equipment',
            createdAt: '2024-01-10'
          },
          {
            id: 4,
            name: 'Bagatayam Inc.',
            email: 'sales@bagatayam.com',
            phone: '+63 933 444 5555',
            address: '321 Trading St, Pasig City, Philippines',
            purchaseOrders: 8,
            status: 'active',
            type: 'services',
            createdAt: '2024-03-05'
          },
          {
            id: 5,
            name: 'Inactive Supplier Co.',
            email: 'test@inactive.com',
            phone: '+63 900 000 0000',
            address: '999 Test Street, Test City, Philippines',
            purchaseOrders: 0,
            status: 'inactive',
            type: 'food',
            createdAt: '2024-01-01'
          }
        ]
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500))
        
        this.suppliers = mockSuppliers
        this.applyFilters()
        this.fetchReportCounts()
        
      } catch (error) {
        console.error('Error fetching suppliers:', error)
        this.error = `Failed to load suppliers: ${error.message}`
      } finally {
        this.loading = false
      }
    },

    fetchReportCounts() {
      this.activeOrdersCount = this.suppliers.filter(s => s.purchaseOrders > 0 && s.status === 'active').length
      this.topSuppliersCount = this.suppliers.filter(s => s.purchaseOrders >= 10).length
    },

    showActiveOrdersReport() {
      alert('Active Orders Report - Coming soon!')
    },

    showTopSuppliersReport() {
      alert('Top Suppliers Report - Coming soon!')
    },

    applyFilters() {
      let filtered = [...this.suppliers]

      if (this.typeFilter !== 'all') {
        filtered = filtered.filter(supplier => supplier.type === this.typeFilter)
      }

      if (this.statusFilter !== 'all') {
        filtered = filtered.filter(supplier => supplier.status === this.statusFilter)
      }

      if (this.orderFilter !== 'all') {
        if (this.orderFilter === 'high') {
          filtered = filtered.filter(supplier => supplier.purchaseOrders >= 10)
        } else if (this.orderFilter === 'medium') {
          filtered = filtered.filter(supplier => supplier.purchaseOrders >= 5 && supplier.purchaseOrders < 10)
        } else if (this.orderFilter === 'low') {
          filtered = filtered.filter(supplier => supplier.purchaseOrders >= 1 && supplier.purchaseOrders < 5)
        } else if (this.orderFilter === 'none') {
          filtered = filtered.filter(supplier => supplier.purchaseOrders === 0)
        }
      }

      if (this.searchFilter.trim()) {
        const search = this.searchFilter.toLowerCase()
        filtered = filtered.filter(supplier => 
          supplier.name?.toLowerCase().includes(search) ||
          supplier.email?.toLowerCase().includes(search) ||
          supplier.phone?.includes(search)
        )
      }

      this.filteredSuppliers = filtered
    },

    clearFilters() {
      this.typeFilter = 'all'
      this.statusFilter = 'all'
      this.orderFilter = 'all'
      this.searchFilter = ''
      this.applyFilters()
    },

    async refreshData() {
      this.successMessage = null
      await this.fetchSuppliers()
    },

    async deleteSelected() {
      if (this.selectedSuppliers.length === 0) return
      
      const confirmed = confirm(`Are you sure you want to delete ${this.selectedSuppliers.length} supplier(s)?`)
      if (!confirmed) return

      try {
        // Mock delete - replace with actual API call
        this.suppliers = this.suppliers.filter(s => !this.selectedSuppliers.includes(s.id))
        this.selectedSuppliers = []
        this.applyFilters()
        this.successMessage = `Successfully deleted supplier(s)`
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error deleting suppliers:', error)
        this.error = `Failed to delete suppliers: ${error.message}`
      }
    },

    async deleteSupplier(supplier) {
      const confirmed = confirm(`Are you sure you want to delete "${supplier.name}"?`)
      if (!confirmed) return

      try {
        // Mock delete - replace with actual API call
        this.suppliers = this.suppliers.filter(s => s.id !== supplier.id)
        this.applyFilters()
        this.successMessage = `Supplier "${supplier.name}" deleted successfully`
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error deleting supplier:', error)
        this.error = `Failed to delete supplier: ${error.message}`
      }
    },

    showAddSupplierModal() {
      this.isEditMode = false
      this.selectedSupplier = null
      this.formData = {
        name: '',
        contactPerson: '',
        email: '',
        phone: '',
        address: '',
        type: '',
        status: 'active',
        notes: ''
      }
      this.formErrors = {}
      this.addAnotherAfterSave = false
      this.showAddModal = true
    },

    editSupplier(supplier) {
      this.isEditMode = true
      this.selectedSupplier = supplier
      this.formData = {
        name: supplier.name || '',
        contactPerson: supplier.contactPerson || '',
        email: supplier.email || '',
        phone: supplier.phone || '',
        address: supplier.address || '',
        type: supplier.type || '',
        status: supplier.status || 'active',
        notes: supplier.notes || ''
      }
      this.formErrors = {}
      this.addAnotherAfterSave = false
      this.showAddModal = true
    },

    viewSupplier(supplier) {
      // Navigate to supplier details page
      this.$router.push({ 
        name: 'SupplierDetails', 
        params: { supplierId: supplier.id } 
      })
    },

    createOrder(supplier) {
      alert(`Create order for ${supplier.name} - Coming soon!`)
    },

    closeAddModal() {
      this.showAddModal = false
      this.isEditMode = false
      this.selectedSupplier = null
      this.formData = {
        name: '',
        contactPerson: '',
        email: '',
        phone: '',
        address: '',
        type: '',
        status: 'active',
        notes: ''
      }
      this.formErrors = {}
      this.addAnotherAfterSave = false
    },

    validateForm() {
      const errors = {}

      // Name validation
      if (!this.formData.name.trim()) {
        errors.name = 'Supplier name is required'
      } else if (this.formData.name.trim().length < 2) {
        errors.name = 'Supplier name must be at least 2 characters'
      }

      // Email validation (optional but must be valid if provided)
      if (this.formData.email && !this.isValidEmail(this.formData.email)) {
        errors.email = 'Please enter a valid email address'
      }

      // Phone validation (optional but must be valid if provided)
      if (this.formData.phone && !this.isValidPhone(this.formData.phone)) {
        errors.phone = 'Please enter a valid phone number'
      }

      this.formErrors = errors
      return Object.keys(errors).length === 0
    },

    isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    },

    isValidPhone(phone) {
      const phoneRegex = /^[\d\s\+\-\(\)]+$/
      return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10
    },

    clearFormError(field) {
      if (this.formErrors[field]) {
        delete this.formErrors[field]
      }
    },

    async saveSupplier() {
      if (!this.validateForm()) return

      this.formLoading = true

      try {
        if (this.isEditMode) {
          // Mock update - replace with actual API call
          const index = this.suppliers.findIndex(s => s.id === this.selectedSupplier.id)
          if (index !== -1) {
            this.suppliers[index] = {
              ...this.suppliers[index],
              ...this.formData
            }
          }
          this.successMessage = `Supplier "${this.formData.name}" updated successfully`
        } else {
          // Mock create - replace with actual API call
          const newSupplier = {
            id: Date.now(),
            ...this.formData,
            purchaseOrders: 0,
            createdAt: new Date().toISOString().split('T')[0]
          }
          this.suppliers.push(newSupplier)
          this.successMessage = `Supplier "${this.formData.name}" created successfully`
        }

        this.closeAddModal()
        this.applyFilters()
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error saving supplier:', error)
        this.formErrors.general = error.message
      } finally {
        this.formLoading = false
      }
    },

    exportData() {
      this.showExportModal = true
    },

    closeExportModal() {
      this.showExportModal = false
      this.selectedExportFormat = ''
    },

    handleExport() {
      if (!this.selectedExportFormat) return

      try {
        const exportData = this.exportOptions.includeInactive 
          ? this.suppliers 
          : this.suppliers.filter(s => s.status === 'active')

        const headers = ['Name', 'Email', 'Phone', 'Address', 'Status', 'Purchase Orders', 'Type']
        const csvContent = [
          headers.join(','),
          ...exportData.map(supplier => [
            `"${supplier.name}"`,
            supplier.email || '',
            supplier.phone || '',
            `"${supplier.address || ''}"`,
            supplier.status,
            supplier.purchaseOrders,
            supplier.type || ''
          ].join(','))
        ].join('\n')

        const blob = new Blob([csvContent], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `suppliers_${new Date().toISOString().split('T')[0]}.${this.selectedExportFormat}`
        a.click()
        window.URL.revokeObjectURL(url)

        this.closeExportModal()
        this.successMessage = `Suppliers exported successfully as ${this.selectedExportFormat.toUpperCase()}`
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      } catch (error) {
        console.error('Error exporting suppliers:', error)
        this.error = `Failed to export suppliers: ${error.message}`
      }
    },

    getStatusBadgeClass(status) {
      const classes = {
        active: 'text-bg-success',
        inactive: 'text-bg-danger',
        pending: 'text-bg-warning'
      }
      return classes[status] || 'text-bg-secondary'
    },

    formatStatus(status) {
      return status.charAt(0).toUpperCase() + status.slice(1)
    },

    getShortAddress(address) {
      if (!address) return 'No address'
      return address.length > 50 ? address.substring(0, 50) + '...' : address
    }
  }
}
</script>

<style scoped>
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

/* Button styling - Black with no borders, color on hover */
.btn-success-light {
  background-color: transparent;
  border: none;
  color: #000;
  transition: all 0.2s ease;
}

.btn-success-light:hover {
  background-color: var(--success);
  color: white;
}

.btn-primary-light {
  background-color: transparent;
  border: none;
  color: #000;
  transition: all 0.2s ease;
}

.btn-primary-light:hover {
  background-color: var(--primary);
  color: white;
}

.btn-info-light {
  background-color: transparent;
  border: none;
  color: #000;
  transition: all 0.2s ease;
}

.btn-info-light:hover {
  background-color: var(--info);
  color: white;
}

.btn-with-icon {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.btn-loading {
  position: relative;
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

/* Supplier card styling */
.supplier-card {
  border: 1px solid var(--neutral-medium);
  border-radius: 12px;
  transition: all 0.3s ease;
  background-color: white;
}

.supplier-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.supplier-card.card-selected {
  border-color: var(--primary);
  background-color: var(--primary-light);
}

.supplier-icon {
  width: 40px;
  height: 40px;
  background-color: var(--primary-light);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
}

.supplier-name {
  color: var(--primary);
  font-weight: 600;
  font-size: 1.1rem;
}

.supplier-contact {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
}

.purchase-orders-label {
  font-size: 0.9rem;
  color: var(--tertiary-dark);
  margin-bottom: 0.25rem;
}

.purchase-orders-count {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary);
}

/* Modern Modal styling */
.modern-supplier-modal {
  border-radius: 16px;
  border: none;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.modal-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--primary-light), var(--primary));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-dark);
}

.modal-title {
  color: var(--primary-dark);
  font-weight: 600;
  margin: 0;
}

.form-label {
  color: var(--tertiary-dark);
  font-weight: 500;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
}

.form-label.required::after {
  content: '*';
  color: var(--error);
  margin-left: 4px;
}

.modern-input {
  border: 2px solid var(--neutral-medium);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  background-color: #fafafa;
}

.modern-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.15);
  background-color: white;
}

.modern-input:hover:not(:focus) {
  border-color: var(--primary-light);
  background-color: white;
}

.modern-input.is-invalid {
  border-color: var(--error);
  background-color: #fef7f7;
}

.form-group {
  margin-bottom: 1.5rem;
}

.modal-header {
  padding: 2rem 2rem 1rem 2rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.modal-body {
  padding: 1.5rem 2rem;
}

.modal-footer {
  padding: 1rem 2rem 2rem 2rem;
  background-color: #f8f9fa;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  border: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(115, 146, 226, 0.3);
}

.btn-outline-secondary {
  border: 2px solid var(--neutral-medium);
  color: var(--tertiary-dark);
  border-radius: 8px;
  font-weight: 500;
}

.btn-outline-secondary:hover {
  background-color: var(--neutral-medium);
  border-color: var(--neutral-dark);
  color: white;
}

/* Export modal styling */
.export-option {
  padding: 1rem;
  border: 2px solid var(--neutral-medium);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  background-color: white;
}

.export-option:hover {
  border-color: var(--primary-light);
  box-shadow: 0 2px 8px rgba(115, 146, 226, 0.1);
}

.export-option.active {
  border-color: var(--primary);
  background-color: var(--primary-light);
}

.export-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 0.5rem;
  font-size: 1.5rem;
}

.export-icon.excel {
  background-color: #e8f5e8;
  color: #28a745;
}

.export-icon.csv {
  background-color: #fff3cd;
  color: #ffc107;
}

.export-details h6 {
  margin-bottom: 0.25rem;
  color: var(--tertiary-dark);
  font-weight: 600;
}

.export-details small {
  color: var(--tertiary-medium);
}

.form-check-label {
  color: var(--tertiary-dark);
  margin-left: 0.5rem;
}

.form-check-input:checked {
  background-color: var(--primary);
  border-color: var(--primary);
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
  
  .supplier-card {
    margin-bottom: 1rem;
  }
}
</style>