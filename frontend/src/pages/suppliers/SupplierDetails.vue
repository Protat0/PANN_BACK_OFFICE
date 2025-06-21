<template>
  <div class="supplier-details-page">
    <!-- Header Section -->
    <div class="d-flex justify-content-between align-items-center mb-4 page-header">
      <div class="d-flex align-items-center">
        <button 
          class="btn btn-outline-secondary me-3"
          @click="goBack"
        >
          <ArrowLeft :size="16" class="me-1" />
          Back to Suppliers
        </button>
        <div>
          <h1 class="h2 fw-semibold text-primary-dark mb-0">Supplier Details</h1>
          <p class="text-muted mb-0">View and manage supplier information</p>
        </div>
      </div>
      <div class="header-actions d-flex gap-2">
        <button class="btn btn-primary" @click="editSupplier">
          <Edit :size="16" class="me-1" />
          Edit
        </button>
        <button class="btn btn-success" @click="createOrder">
          <Plus :size="16" class="me-1" />
          New Order
        </button>
        <div class="dropdown">
          <button class="btn btn-outline-info dropdown-toggle" type="button" data-bs-toggle="dropdown">
            <Download :size="16" class="me-1" />
            Export
          </button>
          <ul class="dropdown-menu">
            <li><a class="dropdown-item" href="#" @click="exportSupplierData('csv')">Export as CSV</a></li>
            <li><a class="dropdown-item" href="#" @click="exportSupplierData('excel')">Export as Excel</a></li>
            <li><a class="dropdown-item" href="#" @click="exportSupplierReport">Export Full Report</a></li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-tertiary-medium">Loading supplier details...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="alert alert-danger text-center" role="alert">
      <p class="mb-3">{{ error }}</p>
      <button class="btn btn-primary" @click="fetchSupplierDetails">Try Again</button>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
      {{ successMessage }}
      <button type="button" class="btn-close" @click="successMessage = null"></button>
    </div>

    <!-- Supplier Details Content -->
    <div v-if="!loading && !error && supplier" class="row">
      <!-- Left Column - Supplier Info Card -->
      <div class="col-lg-4">
        <!-- Main Info Card -->
        <div class="card supplier-info-card mb-4">
          <div class="card-header bg-primary text-white">
            <div class="d-flex align-items-center">
              <div class="supplier-logo me-3">
                <Building :size="32" />
              </div>
              <div class="flex-grow-1">
                <h4 class="card-title mb-1">{{ supplier.name }}</h4>
                <span :class="['badge', 'status-badge', getStatusBadgeClass(supplier.status)]">
                  {{ formatStatus(supplier.status) }}
                </span>
              </div>
              <div class="dropdown">
                <button class="btn btn-link text-white p-0" type="button" data-bs-toggle="dropdown">
                  <MoreVertical :size="20" />
                </button>
                <ul class="dropdown-menu">
                  <li><a class="dropdown-item" href="#" @click="toggleFavorite">
                    <Star :size="16" class="me-2" :class="{ 'text-warning': supplier.isFavorite }" />
                    {{ supplier.isFavorite ? 'Remove from Favorites' : 'Add to Favorites' }}
                  </a></li>
                  <li><a class="dropdown-item" href="#" @click="duplicateSupplier">
                    <Copy :size="16" class="me-2" />
                    Duplicate Supplier
                  </a></li>
                  <li><hr class="dropdown-divider"></li>
                  <li><a class="dropdown-item text-danger" href="#" @click="deleteSupplier">
                    <Trash2 :size="16" class="me-2" />
                    Delete Supplier
                  </a></li>
                </ul>
              </div>
            </div>
          </div>
          <div class="card-body">
            <div class="info-item">
              <label>
                <User :size="16" class="me-2" />
                Contact Person:
              </label>
              <span>{{ supplier.contactPerson || 'Not specified' }}</span>
            </div>
            <div class="info-item">
              <label>
                <Phone :size="16" class="me-2" />
                Phone Number:
              </label>
              <span>
                {{ supplier.phone || 'Not provided' }}
                <button v-if="supplier.phone" class="btn btn-link p-0 ms-2" @click="callSupplier" title="Call">
                  <PhoneCall :size="14" />
                </button>
              </span>
            </div>
            <div class="info-item">
              <label>
                <Mail :size="16" class="me-2" />
                Email Address:
              </label>
              <span>
                {{ supplier.email || 'Not provided' }}
                <button v-if="supplier.email" class="btn btn-link p-0 ms-2" @click="emailSupplier" title="Send Email">
                  <Send :size="14" />
                </button>
              </span>
            </div>
            <div class="info-item">
              <label>
                <MapPin :size="16" class="me-2" />
                Address:
              </label>
              <span class="address-text">
                {{ supplier.address || 'Not specified' }}
                <button v-if="supplier.address" class="btn btn-link p-0 ms-2" @click="openMaps" title="View on Map">
                  <Navigation :size="14" />
                </button>
              </span>
            </div>
            <div class="info-item">
              <label>
                <Tag :size="16" class="me-2" />
                Supplier Type:
              </label>
              <span>{{ getSupplierTypeLabel(supplier.type) }}</span>
            </div>
            <div class="info-item">
              <label>
                <Calendar :size="16" class="me-2" />
                Member Since:
              </label>
              <span>{{ formatDate(supplier.createdAt) }}</span>
            </div>
            <div class="info-item mb-0">
              <label>
                <Clock :size="16" class="me-2" />
                Last Updated:
              </label>
              <span>{{ formatDate(supplier.updatedAt) }}</span>
            </div>
          </div>
        </div>

        <!-- Quick Stats Card -->
        <div class="card stats-card mb-4">
          <div class="card-header">
            <h5 class="card-title mb-0">
              <BarChart3 :size="18" class="me-2" />
              Quick Stats
            </h5>
          </div>
          <div class="card-body">
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-number text-primary">{{ supplier.purchaseOrders || 0 }}</div>
                <div class="stat-label">Total Orders</div>
              </div>
              <div class="stat-item">
                <div class="stat-number text-warning">{{ getActiveOrders() }}</div>
                <div class="stat-label">Active Orders</div>
              </div>
              <div class="stat-item">
                <div class="stat-number text-success">₱{{ formatCurrency(getTotalSpent()) }}</div>
                <div class="stat-label">Total Spent</div>
              </div>
              <div class="stat-item">
                <div class="stat-number text-info">{{ getDaysActive() }}</div>
                <div class="stat-label">Days Active</div>
              </div>
            </div>
            
            <!-- Performance Rating -->
            <div class="mt-3 pt-3 border-top">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <small class="text-muted">Performance Rating</small>
                <small class="text-muted">{{ supplier.rating || 4.5 }}/5.0</small>
              </div>
              <div class="progress" style="height: 6px;">
                <div 
                  class="progress-bar bg-success" 
                  :style="{ width: ((supplier.rating || 4.5) / 5 * 100) + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions Card -->
        <div class="card quick-actions-card">
          <div class="card-header">
            <h5 class="card-title mb-0">
              <Zap :size="18" class="me-2" />
              Quick Actions
            </h5>
          </div>
          <div class="card-body">
            <div class="d-grid gap-2">
              <button class="btn btn-outline-primary btn-sm" @click="createOrder">
                <Plus :size="16" class="me-2" />
                Create Purchase Order
              </button>
              <button class="btn btn-outline-info btn-sm" @click="viewPaymentHistory">
                <CreditCard :size="16" class="me-2" />
                Payment History
              </button>
              <button class="btn btn-outline-success btn-sm" @click="viewDocuments">
                <FileText :size="16" class="me-2" />
                View Documents
              </button>
              <button class="btn btn-outline-warning btn-sm" @click="scheduleVisit">
                <Calendar :size="16" class="me-2" />
                Schedule Visit
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Orders and Activity -->
      <div class="col-lg-8">
        <!-- Orders Section -->
        <div class="card orders-card mb-4">
          <div class="card-header">
            <div class="d-flex justify-content-between align-items-center">
              <h5 class="card-title mb-0">
                <ShoppingCart :size="18" class="me-2" />
                Purchase Orders
                <span class="badge bg-secondary ms-2">{{ filteredOrders.length }}</span>
              </h5>
              <div class="d-flex gap-2 align-items-center">
                <select class="form-select form-select-sm" v-model="orderStatusFilter" @change="filterOrders" style="width: auto;">
                  <option value="all">All Orders</option>
                  <option value="pending">Pending</option>
                  <option value="received">Received</option>
                  <option value="cancelled">Cancelled</option>
                </select>
                <div class="dropdown">
                  <button class="btn btn-outline-secondary btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    <Filter :size="14" />
                  </button>
                  <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="#" @click="sortOrders('date')">Sort by Date</a></li>
                    <li><a class="dropdown-item" href="#" @click="sortOrders('amount')">Sort by Amount</a></li>
                    <li><a class="dropdown-item" href="#" @click="sortOrders('status')">Sort by Status</a></li>
                  </ul>
                </div>
                <button class="btn btn-primary btn-sm" @click="createOrder">
                  <Plus :size="16" class="me-1" />
                  New Order
                </button>
              </div>
            </div>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover orders-table mb-0">
                <thead class="table-light">
                  <tr>
                    <th>
                      <input type="checkbox" class="form-check-input" v-model="selectAllOrders" @change="toggleSelectAllOrders">
                    </th>
                    <th>Order ID</th>
                    <th>Order Date</th>
                    <th>Items</th>
                    <th>Total Cost</th>
                    <th>Expected Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="order in filteredOrders" :key="order.id" :class="{ 'table-warning': isOverdue(order) }">
                    <td>
                      <input type="checkbox" class="form-check-input" :value="order.id" v-model="selectedOrders">
                    </td>
                    <td class="order-id">
                      <div class="d-flex align-items-center">
                        {{ order.id }}
                        <AlertTriangle v-if="isOverdue(order)" :size="14" class="text-warning ms-1" title="Overdue" />
                      </div>
                    </td>
                    <td>{{ formatDate(order.date) }}</td>
                    <td>
                      <div>
                        {{ order.quantity }} items
                        <br>
                        <small class="text-muted">{{ order.description || 'Various items' }}</small>
                      </div>
                    </td>
                    <td class="amount fw-bold">₱{{ formatCurrency(order.total) }}</td>
                    <td>
                      <div>
                        {{ formatDate(order.expectedDate) }}
                        <br>
                        <small :class="['text-muted', { 'text-danger': isOverdue(order) }]">
                          {{ getTimeRemaining(order.expectedDate) }}
                        </small>
                      </div>
                    </td>
                    <td>
                      <span :class="['badge', 'order-status', getOrderStatusClass(order.status)]">
                        {{ order.status }}
                      </span>
                    </td>
                    <td>
                      <div class="action-buttons">
                        <button 
                          class="btn btn-outline-primary btn-sm" 
                          @click="viewOrder(order)" 
                          title="View Order"
                        >
                          <Eye :size="14" />
                        </button>
                        <button 
                          class="btn btn-outline-info btn-sm" 
                          @click="editOrder(order)" 
                          title="Edit Order"
                          :disabled="order.status === 'Received' || order.status === 'Cancelled'"
                        >
                          <Edit :size="14" />
                        </button>
                        <div class="dropdown">
                          <button class="btn btn-outline-secondary btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                            <MoreVertical :size="14" />
                          </button>
                          <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#" @click="duplicateOrder(order)">Duplicate</a></li>
                            <li><a class="dropdown-item" href="#" @click="trackOrder(order)">Track Order</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="#" @click="deleteOrder(order)">Delete</a></li>
                          </ul>
                        </div>
                      </div>
                    </td>
                  </tr>
                  <!-- Empty State -->
                  <tr v-if="filteredOrders.length === 0">
                    <td colspan="8" class="text-center text-muted py-5">
                      <Package :size="48" class="text-muted mb-3" />
                      <div>
                        <h6 class="text-muted">No purchase orders found</h6>
                        <p class="mb-3">
                          {{ orderStatusFilter === 'all' 
                            ? 'This supplier has no purchase orders yet.' 
                            : `No ${orderStatusFilter} orders found.` }}
                        </p>
                        <button class="btn btn-primary btn-sm" @click="createOrder">
                          <Plus :size="16" class="me-1" />
                          Create First Order
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- Bulk Actions Bar -->
            <div v-if="selectedOrders.length > 0" class="alert alert-info mx-3 mb-3 d-flex justify-content-between align-items-center">
              <span>{{ selectedOrders.length }} order(s) selected</span>
              <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-primary" @click="bulkExportOrders">Export Selected</button>
                <button class="btn btn-outline-warning" @click="bulkUpdateStatus">Update Status</button>
                <button class="btn btn-outline-danger" @click="bulkDeleteOrders">Delete Selected</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Activity Timeline -->
        <div class="card activity-card">
          <div class="card-header">
            <h5 class="card-title mb-0">
              <Activity :size="18" class="me-2" />
              Recent Activity
            </h5>
          </div>
          <div class="card-body">
            <div class="timeline">
              <div v-for="activity in recentActivity" :key="activity.id" class="timeline-item">
                <div class="timeline-marker" :class="getActivityMarkerClass(activity.type)">
                  <component :is="getActivityIcon(activity.type)" :size="14" />
                </div>
                <div class="timeline-content">
                  <div class="timeline-header">
                    <strong>{{ activity.title }}</strong>
                    <small class="text-muted ms-2">{{ formatTimeAgo(activity.date) }}</small>
                  </div>
                  <p class="mb-1 text-muted">{{ activity.description }}</p>
                  <small class="text-muted">by {{ activity.user }}</small>
                </div>
              </div>
              
              <!-- Empty Timeline State -->
              <div v-if="recentActivity.length === 0" class="text-center py-4">
                <Clock :size="32" class="text-muted mb-2" />
                <p class="text-muted">No recent activity</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Notes Section -->
        <div v-if="supplier.notes || editableNotes" class="card notes-card mt-4">
          <div class="card-header">
            <div class="d-flex justify-content-between align-items-center">
              <h5 class="card-title mb-0">
                <FileText :size="18" class="me-2" />
                Additional Notes
              </h5>
              <button class="btn btn-outline-secondary btn-sm" @click="toggleNotesEdit">
                <Edit :size="14" class="me-1" />
                {{ editingNotes ? 'Save' : 'Edit' }}
              </button>
            </div>
          </div>
          <div class="card-body">
            <div v-if="!editingNotes" class="notes-content">
              {{ supplier.notes || 'No notes available' }}
            </div>
            <div v-else>
              <textarea 
                class="form-control" 
                v-model="editableNotes" 
                rows="4"
                placeholder="Add notes about this supplier..."
              ></textarea>
              <div class="mt-2">
                <button class="btn btn-primary btn-sm me-2" @click="saveNotes">Save</button>
                <button class="btn btn-secondary btn-sm" @click="cancelNotesEdit">Cancel</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Supplier Modal -->
    <div v-if="showEditModal" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content modern-modal">
          <div class="modal-header">
            <div class="d-flex align-items-center">
              <div class="modal-icon me-3">
                <Edit :size="24" />
              </div>
              <div>
                <h4 class="modal-title mb-1">Edit Supplier</h4>
                <p class="text-muted mb-0 small">Update supplier information</p>
              </div>
            </div>
            <button type="button" class="btn-close" @click="closeEditModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveSupplier">
              <div class="row g-3">
                <div class="col-md-6">
                  <label for="supplierName" class="form-label required">Company Name</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="supplierName"
                    v-model="editForm.name"
                    required
                  >
                </div>
                <div class="col-md-6">
                  <label for="contactPerson" class="form-label">Contact Person</label>
                  <input 
                    type="text" 
                    class="form-control"
                    id="contactPerson"
                    v-model="editForm.contactPerson"
                  >
                </div>
                <div class="col-md-6">
                  <label for="email" class="form-label">Email Address</label>
                  <input 
                    type="email" 
                    class="form-control"
                    id="email"
                    v-model="editForm.email"
                  >
                </div>
                <div class="col-md-6">
                  <label for="phone" class="form-label">Phone Number</label>
                  <input 
                    type="tel" 
                    class="form-control"
                    id="phone"
                    v-model="editForm.phone"
                  >
                </div>
                <div class="col-md-6">
                  <label for="type" class="form-label">Supplier Type</label>
                  <select class="form-select" id="type" v-model="editForm.type">
                    <option value="">Select type</option>
                    <option value="food">Food & Beverages</option>
                    <option value="packaging">Packaging Materials</option>
                    <option value="equipment">Equipment & Tools</option>
                    <option value="services">Services</option>
                    <option value="raw_materials">Raw Materials</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label for="status" class="form-label">Status</label>
                  <select class="form-select" id="status" v-model="editForm.status">
                    <option value="active">Active</option>
                    <option value="pending">Pending</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
                <div class="col-12">
                  <label for="address" class="form-label">Address</label>
                  <textarea 
                    class="form-control" 
                    id="address"
                    v-model="editForm.address"
                    rows="3"
                  ></textarea>
                </div>
                <div class="col-12">
                  <label for="notes" class="form-label">Notes</label>
                  <textarea 
                    class="form-control" 
                    id="notes"
                    v-model="editForm.notes"
                    rows="3"
                  ></textarea>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeEditModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="saveSupplier" :disabled="saving">
              <div v-if="saving" class="spinner-border spinner-border-sm me-2"></div>
              Update Supplier
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title text-danger">
              <AlertTriangle :size="20" class="me-2" />
              Delete Supplier
            </h5>
            <button type="button" class="btn-close" @click="showDeleteModal = false"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete <strong>{{ supplier.name }}</strong>?</p>
            <div class="alert alert-warning">
              <strong>Warning:</strong> This action cannot be undone. All associated purchase orders and history will be preserved but this supplier will be removed from your system.
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDeleteModal = false">Cancel</button>
            <button type="button" class="btn btn-danger" @click="confirmDeleteSupplier" :disabled="deleting">
              <div v-if="deleting" class="spinner-border spinner-border-sm me-2"></div>
              Delete Supplier
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { 
  ArrowLeft,
  Edit,
  Plus,
  Download,
  Building,
  User,
  Phone,
  Mail,
  MapPin,
  Tag,
  Calendar,
  Clock,
  BarChart3,
  ShoppingCart,
  Eye,
  Trash2,
  Package,
  FileText,
  MoreVertical,
  Star,
  Copy,
  PhoneCall,
  Send,
  Navigation,
  Zap,
  CreditCard,
  Filter,
  AlertTriangle,
  Activity
} from 'lucide-vue-next'

export default {
  name: 'SupplierDetails',
  components: {
    ArrowLeft,
    Edit,
    Plus,
    Download,
    Building,
    User,
    Phone,
    Mail,
    MapPin,
    Tag,
    Calendar,
    Clock,
    BarChart3,
    ShoppingCart,
    Eye,
    Trash2,
    Package,
    FileText,
    MoreVertical,
    Star,
    Copy,
    PhoneCall,
    Send,
    Navigation,
    Zap,
    CreditCard,
    Filter,
    AlertTriangle,
    Activity
  },
  props: {
    supplierId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      supplier: null,
      orders: [],
      filteredOrders: [],
      recentActivity: [],
      loading: false,
      error: null,
      successMessage: null,
      saving: false,
      deleting: false,
      orderStatusFilter: 'all',
      selectedOrders: [],
      selectAllOrders: false,
      
      // Edit modal state
      showEditModal: false,
      showDeleteModal: false,
      editForm: {
        name: '',
        contactPerson: '',
        email: '',
        phone: '',
        address: '',
        type: '',
        status: 'active',
        notes: ''
      },
      
      // Notes editing
      editingNotes: false,
      editableNotes: ''
    }
  },
  async mounted() {
    await this.fetchSupplierDetails()
  },
  watch: {
    supplierId: {
      handler() {
        this.fetchSupplierDetails()
      },
      immediate: false
    }
  },
  methods: {
    async fetchSupplierDetails() {
      this.loading = true
      this.error = null
      
      try {
        // Mock data - replace with actual API call
        const mockSupplier = {
          id: this.supplierId,
          name: 'John Doe Supplies',
          contactPerson: 'John Doe',
          email: 'john@johndoesupplies.com',
          phone: '+63 912 345 6789',
          address: '123 Supply Street, Business District, Manila, Philippines',
          purchaseOrders: 4,
          status: 'active',
          type: 'food',
          rating: 4.5,
          isFavorite: false,
          notes: 'Reliable supplier with consistent quality. Preferred delivery schedule: Tuesdays and Fridays. Payment terms: Net 30 days.',
          createdAt: '2024-01-15',
          updatedAt: '2024-12-10'
        }
        
        const mockOrders = [
          {
            id: 'PO-001',
            date: '2024-12-10',
            quantity: 12,
            total: 3600.00,
            expectedDate: '2024-12-25',
            status: 'Received',
            description: 'Rice and cooking oil'
          },
          {
            id: 'PO-002',
            date: '2024-11-15',
            quantity: 25,
            total: 7500.00,
            expectedDate: '2024-12-01',
            status: 'Pending',
            description: 'Fresh vegetables and fruits'
          },
          {
            id: 'PO-003',
            date: '2024-10-05',
            quantity: 13,
            total: 3900.00,
            expectedDate: '2024-10-20',
            status: 'Cancelled',
            description: 'Meat products'
          },
          {
            id: 'PO-004',
            date: '2024-09-11',
            quantity: 30,
            total: 9000.00,
            expectedDate: '2024-09-27',
            status: 'Received',
            description: 'Dairy products and beverages'
          }
        ]

        const mockActivity = [
          {
            id: 1,
            type: 'order_created',
            title: 'New Purchase Order Created',
            description: 'PO-002 created for ₱7,500.00',
            user: 'Admin User',
            date: '2024-11-15T10:30:00Z'
          },
          {
            id: 2,
            type: 'order_received',
            title: 'Order Received',
            description: 'PO-001 marked as received',
            user: 'Warehouse Manager',
            date: '2024-12-10T14:20:00Z'
          },
          {
            id: 3,
            type: 'supplier_updated',
            title: 'Supplier Information Updated',
            description: 'Contact details updated',
            user: 'Admin User',
            date: '2024-12-10T09:15:00Z'
          },
          {
            id: 4,
            type: 'payment_processed',
            title: 'Payment Processed',
            description: 'Payment of ₱3,600.00 processed for PO-001',
            user: 'Finance Team',
            date: '2024-12-11T11:45:00Z'
          }
        ]
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500))
        
        this.supplier = mockSupplier
        this.orders = mockOrders
        this.recentActivity = mockActivity
        this.editableNotes = mockSupplier.notes
        this.filterOrders()
        
      } catch (error) {
        console.error('Error fetching supplier details:', error)
        this.error = `Failed to load supplier details: ${error.message}`
      } finally {
        this.loading = false
      }
    },

    filterOrders() {
      if (this.orderStatusFilter === 'all') {
        this.filteredOrders = [...this.orders]
      } else {
        this.filteredOrders = this.orders.filter(order => 
          order.status.toLowerCase() === this.orderStatusFilter.toLowerCase()
        )
      }
    },

    sortOrders(criteria) {
      this.filteredOrders.sort((a, b) => {
        switch (criteria) {
          case 'date':
            return new Date(b.date) - new Date(a.date)
          case 'amount':
            return b.total - a.total
          case 'status':
            return a.status.localeCompare(b.status)
          default:
            return 0
        }
      })
    },

    toggleSelectAllOrders() {
      if (this.selectAllOrders) {
        this.selectedOrders = this.filteredOrders.map(order => order.id)
      } else {
        this.selectedOrders = []
      }
    },

    isOverdue(order) {
      const expectedDate = new Date(order.expectedDate)
      const today = new Date()
      return expectedDate < today && (order.status === 'Pending' || order.status === 'Active')
    },

    getTimeRemaining(dateString) {
      const expectedDate = new Date(dateString)
      const today = new Date()
      const diffTime = expectedDate - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays < 0) {
        return `${Math.abs(diffDays)} days overdue`
      } else if (diffDays === 0) {
        return 'Due today'
      } else if (diffDays === 1) {
        return 'Due tomorrow'
      } else {
        return `${diffDays} days remaining`
      }
    },

    formatTimeAgo(dateString) {
      const date = new Date(dateString)
      const now = new Date()
      const diffTime = Math.abs(now - date)
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
      const diffHours = Math.floor(diffTime / (1000 * 60 * 60))
      const diffMinutes = Math.floor(diffTime / (1000 * 60))

      if (diffDays > 0) {
        return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
      } else if (diffHours > 0) {
        return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
      } else if (diffMinutes > 0) {
        return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`
      } else {
        return 'Just now'
      }
    },

    getActivityIcon(type) {
      const icons = {
        order_created: Plus,
        order_received: Package,
        supplier_updated: Edit,
        payment_processed: CreditCard
      }
      return icons[type] || Activity
    },

    getActivityMarkerClass(type) {
      const classes = {
        order_created: 'bg-primary',
        order_received: 'bg-success',
        supplier_updated: 'bg-info',
        payment_processed: 'bg-warning'
      }
      return classes[type] || 'bg-secondary'
    },

    goBack() {
      this.$router.push({ name: 'Suppliers' })
    },

    editSupplier() {
      this.editForm = {
        name: this.supplier.name || '',
        contactPerson: this.supplier.contactPerson || '',
        email: this.supplier.email || '',
        phone: this.supplier.phone || '',
        address: this.supplier.address || '',
        type: this.supplier.type || '',
        status: this.supplier.status || 'active',
        notes: this.supplier.notes || ''
      }
      this.showEditModal = true
    },

    closeEditModal() {
      this.showEditModal = false
      this.editForm = {
        name: '',
        contactPerson: '',
        email: '',
        phone: '',
        address: '',
        type: '',
        status: 'active',
        notes: ''
      }
    },

    async saveSupplier() {
      this.saving = true
      
      try {
        // Mock save - replace with actual API call
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Update local supplier data
        this.supplier = {
          ...this.supplier,
          ...this.editForm,
          updatedAt: new Date().toISOString()
        }
        
        this.closeEditModal()
        this.successMessage = 'Supplier updated successfully!'
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
        
      } catch (error) {
        console.error('Error updating supplier:', error)
        this.error = `Failed to update supplier: ${error.message}`
      } finally {
        this.saving = false
      }
    },

    deleteSupplier() {
      this.showDeleteModal = true
    },

    async confirmDeleteSupplier() {
      this.deleting = true
      
      try {
        // Mock delete - replace with actual API call
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        this.showDeleteModal = false
        this.successMessage = 'Supplier deleted successfully'
        
        setTimeout(() => {
          this.goBack()
        }, 1500)
        
      } catch (error) {
        console.error('Error deleting supplier:', error)
        this.error = `Failed to delete supplier: ${error.message}`
      } finally {
        this.deleting = false
      }
    },

    toggleFavorite() {
      this.supplier.isFavorite = !this.supplier.isFavorite
      this.successMessage = `Supplier ${this.supplier.isFavorite ? 'added to' : 'removed from'} favorites`
      setTimeout(() => {
        this.successMessage = null
      }, 2000)
    },

    duplicateSupplier() {
      alert(`Duplicate supplier functionality - Coming soon!`)
    },

    callSupplier() {
      if (this.supplier.phone) {
        window.open(`tel:${this.supplier.phone}`)
      }
    },

    emailSupplier() {
      if (this.supplier.email) {
        window.open(`mailto:${this.supplier.email}`)
      }
    },

    openMaps() {
      if (this.supplier.address) {
        const encodedAddress = encodeURIComponent(this.supplier.address)
        window.open(`https://maps.google.com/maps?q=${encodedAddress}`, '_blank')
      }
    },

    createOrder() {
      // Navigate to order creation or show modal
      alert(`Create order for ${this.supplier.name} - Coming soon!`)
    },

    viewPaymentHistory() {
      alert('Payment history - Coming soon!')
    },

    viewDocuments() {
      alert('View documents - Coming soon!')
    },

    scheduleVisit() {
      alert('Schedule visit - Coming soon!')
    },

    exportSupplierData(format = 'csv') {
      const supplierData = [{
        'Supplier Name': this.supplier.name,
        'Contact Person': this.supplier.contactPerson || '',
        'Email': this.supplier.email || '',
        'Phone': this.supplier.phone || '',
        'Address': this.supplier.address || '',
        'Type': this.getSupplierTypeLabel(this.supplier.type),
        'Status': this.supplier.status,
        'Rating': this.supplier.rating || 0,
        'Purchase Orders': this.supplier.purchaseOrders || 0,
        'Total Spent': this.getTotalSpent(),
        'Created Date': this.formatDate(this.supplier.createdAt),
        'Last Updated': this.formatDate(this.supplier.updatedAt)
      }]

      const csvContent = [
        Object.keys(supplierData[0]).join(','),
        ...supplierData.map(row => Object.values(row).map(value => `"${value}"`).join(','))
      ].join('\n')

      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `supplier_${this.supplier.name.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.${format}`
      a.click()
      window.URL.revokeObjectURL(url)
    },

    exportSupplierReport() {
      alert('Export full report - Coming soon!')
    },

    viewOrder(order) {
      alert(`View order ${order.id} - Coming soon!`)
    },

    editOrder(order) {
      alert(`Edit order ${order.id} - Coming soon!`)
    },

    deleteOrder(order) {
      if (confirm(`Are you sure you want to delete order ${order.id}?`)) {
        this.orders = this.orders.filter(o => o.id !== order.id)
        this.filterOrders()
        this.successMessage = `Order ${order.id} deleted successfully`
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      }
    },

    duplicateOrder(order) {
      alert(`Duplicate order ${order.id} - Coming soon!`)
    },

    trackOrder(order) {
      alert(`Track order ${order.id} - Coming soon!`)
    },

    bulkExportOrders() {
      alert(`Export ${this.selectedOrders.length} selected orders - Coming soon!`)
    },

    bulkUpdateStatus() {
      alert(`Update status for ${this.selectedOrders.length} selected orders - Coming soon!`)
    },

    bulkDeleteOrders() {
      if (confirm(`Are you sure you want to delete ${this.selectedOrders.length} selected orders?`)) {
        this.orders = this.orders.filter(o => !this.selectedOrders.includes(o.id))
        this.selectedOrders = []
        this.selectAllOrders = false
        this.filterOrders()
        this.successMessage = 'Selected orders deleted successfully'
        
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
      }
    },

    toggleNotesEdit() {
      if (this.editingNotes) {
        this.saveNotes()
      } else {
        this.editingNotes = true
      }
    },

    saveNotes() {
      this.supplier.notes = this.editableNotes
      this.editingNotes = false
      this.successMessage = 'Notes updated successfully'
      
      setTimeout(() => {
        this.successMessage = null
      }, 2000)
    },

    cancelNotesEdit() {
      this.editableNotes = this.supplier.notes
      this.editingNotes = false
    },

    getSupplierTypeLabel(type) {
      const labels = {
        'food': 'Food & Beverages',
        'packaging': 'Packaging Materials',
        'equipment': 'Equipment & Tools',
        'services': 'Services',
        'raw_materials': 'Raw Materials',
        'other': 'Other'
      }
      return labels[type] || 'Not specified'
    },

    getActiveOrders() {
      return this.orders.filter(order => 
        order.status === 'Active' || order.status === 'Pending'
      ).length
    },

    getTotalSpent() {
      return this.orders
        .filter(order => order.status === 'Received')
        .reduce((total, order) => total + order.total, 0)
    },

    getDaysActive() {
      if (!this.supplier?.createdAt) return 0
      const createdDate = new Date(this.supplier.createdAt)
      const today = new Date()
      const diffTime = Math.abs(today - createdDate)
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    },

    formatCurrency(amount) {
      return new Intl.NumberFormat('en-PH', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(amount || 0)
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },

    getStatusBadgeClass(status) {
      const classes = {
        active: 'bg-success',
        inactive: 'bg-danger',
        pending: 'bg-warning'
      }
      return classes[status] || 'bg-secondary'
    },

    formatStatus(status) {
      return status.charAt(0).toUpperCase() + status.slice(1)
    },

    getOrderStatusClass(status) {
      const classes = {
        'Received': 'bg-success',
        'Pending': 'bg-warning',
        'Cancelled': 'bg-danger',
        'Active': 'bg-primary'
      }
      return classes[status] || 'bg-secondary'
    }
  }
}
</script>

<style scoped>
.supplier-details-page {
  background-color: var(--neutral-light);
  min-height: 100vh;
  padding: 1.5rem;
}

.page-header {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.header-actions {
  flex-wrap: wrap;
  gap: 0.5rem;
}

.supplier-info-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: none;
  border-radius: 12px;
  overflow: hidden;
}

.supplier-logo {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.status-badge {
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
}

.info-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--neutral-light);
}

.info-item:last-child {
  margin-bottom: 0;
  border-bottom: none;
  padding-bottom: 0;
}

.info-item label {
  font-weight: 500;
  color: var(--tertiary-medium);
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
}

.info-item span {
  color: var(--tertiary-dark);
  font-weight: 500;
  display: flex;
  align-items: center;
}

.address-text {
  line-height: 1.4;
}

.stats-card, .quick-actions-card, .orders-card, .activity-card, .notes-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: none;
  border-radius: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: var(--neutral-light);
  border-radius: 8px;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--tertiary-medium);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.orders-table {
  font-size: 0.9rem;
}

.orders-table th {
  font-weight: 600;
  color: var(--tertiary-dark);
  border-bottom: 2px solid var(--neutral-light);
}

.orders-table td {
  vertical-align: middle;
  border-top: 1px solid var(--neutral-light);
}

.order-id {
  font-family: 'Monaco', 'Menlo', monospace;
  font-weight: 600;
  color: var(--primary);
}

.amount {
  text-align: right;
}

.order-status {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.timeline {
  position: relative;
}

.timeline-item {
  display: flex;
  margin-bottom: 1.5rem;
  position: relative;
}

.timeline-item:last-child {
  margin-bottom: 0;
}

.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 30px;
  bottom: -24px;
  width: 2px;
  background-color: var(--neutral-medium);
}

.timeline-marker {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 1rem;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.timeline-content {
  flex-grow: 1;
}

.timeline-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.25rem;
}

.notes-content {
  color: var(--tertiary-dark);
  line-height: 1.6;
  background: var(--neutral-light);
  padding: 1rem;
  border-radius: 8px;
  font-style: italic;
}

.modern-modal {
  border-radius: 16px;
  border: none;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
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

.form-label.required::after {
  content: '*';
  color: var(--error);
  margin-left: 4px;
}

/* Color classes */
.text-primary-dark {
  color: var(--primary-dark) !important;
}

.text-tertiary-medium {
  color: var(--tertiary-medium) !important;
}

.text-tertiary-dark {
  color: var(--tertiary-dark) !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .header-actions {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .timeline-item {
    flex-direction: column;
  }
  
  .timeline-marker {
    margin-bottom: 0.5rem;
    align-self: flex-start;
  }
}
</style>