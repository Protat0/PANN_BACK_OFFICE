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
      <div class="header-actions d-flex gap-2" v-if="!loading && supplier">
        <button class="btn btn-primary" @click="editSupplier">
          <Edit :size="16" class="me-1" />
          Edit Supplier
        </button>
        <button class="btn btn-primary" @click="createOrder">
          <ShoppingCart :size="16" class="me-1" />
          New Order
        </button>
        <button class="btn btn-success" @click="openReceiveStockModal">
          <Package :size="16" class="me-1" />
          Receive Stock
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-tertiary-medium">Loading supplier details...</p>
    </div>

    <!-- Quick Stats Card - Moved to Top -->
    <div v-if="!loading && !error && supplier" class="card stats-card mb-4">
      <div class="card-header">
        <h5 class="card-title mb-0">
          <BarChart3 :size="18" class="me-2" />
          Quick Statistics
        </h5>
      </div>
      <div class="card-body">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number text-primary">{{ supplier.purchaseOrders || 0 }}</div>
            <div class="stat-label">Total Orders</div>
          </div>
          <div class="stat-item clickable-stat" @click="openActiveOrdersModal">
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
              :style="{ width: ((supplier.rating || 4.5) / 5 * 100) + '%' }">
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Supplier Details Content -->
    <div v-if="!loading && !error && supplier" class="row">
      <!-- Left Column - Supplier Info Card with Notes -->
      <div class="col-lg-4">
        <!-- Main Info Card with Integrated Notes -->
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
            <!-- Contact Information -->
            <div class="section-header">
              <h6 class="fw-bold text-tertiary-dark mb-3">
                <User :size="16" class="me-2" />
                Contact Information
              </h6>
            </div>
            
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

            <!-- Business Information -->
            <div class="section-divider"></div>
            <div class="section-header">
              <h6 class="fw-bold text-tertiary-dark mb-3">
                <Building :size="16" class="me-2" />
                Business Information
              </h6>
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
            <div class="info-item">
              <label>
                <Clock :size="16" class="me-2" />
                Last Updated:
              </label>
              <span>{{ formatDate(supplier.updatedAt) }}</span>
            </div>

            <!-- Additional Notes Section - Integrated -->
            <div class="section-divider"></div>
            <div class="section-header">
              <div class="d-flex justify-content-between align-items-center">
                <h6 class="fw-bold text-tertiary-dark mb-0">
                  <FileText :size="16" class="me-2" />
                  Additional Notes
                </h6>
                <button class="btn btn-outline-secondary btn-sm" @click="toggleNotesEdit">
                  <Edit :size="14" class="me-1" />
                  {{ editingNotes ? 'Save' : 'Edit' }}
                </button>
              </div>
            </div>

            <div class="mt-3">
              <div v-if="!editingNotes" class="notes-content">
                {{ supplier.notes || 'No additional notes available' }}
              </div>
              <div v-else>
                <textarea 
                  class="form-control" 
                  v-model="editableNotes" 
                  rows="3"
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

      <!-- Right Column - Orders and Activity -->
      <div class="col-lg-8">
        <!-- Orders Section -->
        <div class="card orders-card mb-4">
          <div class="card-header">
            <div class="d-flex justify-content-between align-items-center">
              <h5 class="card-title mb-0">
                <Package :size="18" class="me-2" />
                Stock Receipt History
                <span class="badge bg-secondary ms-2">{{ filteredOrders.length }}</span>
              </h5>
              <div class="d-flex gap-2 align-items-center" v-if="orders.length > 0">
                <select class="form-select form-select-sm" v-model="orderStatusFilter" @change="filterOrders">
                  <option value="all">All Receipts</option>
                  <option value="pending delivery">Pending Delivery</option>
                  <option value="received">Received</option>
                  <option value="partially received">Partially Received</option>
                  <option value="depleted">Depleted</option>
                </select>
                <div class="dropdown" ref="sortDropdownRef">
                  <button 
                    class="btn btn-outline-secondary btn-sm dropdown-toggle" 
                    type="button" 
                    @click="toggleSortDropdown"
                    :class="{ 'active': showSortDropdown }"
                  >
                    <Filter :size="14" />
                  </button>
                  <ul class="dropdown-menu" :class="{ 'show': showSortDropdown }">
                    <li><a class="dropdown-item" href="#" @click.prevent="handleSort('date')">Sort by Date</a></li>
                    <li><a class="dropdown-item" href="#" @click.prevent="handleSort('amount')">Sort by Amount</a></li>
                    <li><a class="dropdown-item" href="#" @click.prevent="handleSort('status')">Sort by Status</a></li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive" v-if="orders.length > 0">
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
                        {{ order.items?.length || 0 }} item(s)
                        <br>
                        <small class="text-muted">{{ order.quantity }} total quantity</small>
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
                          @click="viewReceipt(order)" 
                          title="View Receipt Details"
                        >
                          <Eye :size="14" />
                        </button>
                        <button 
                          class="btn btn-outline-warning btn-sm" 
                          @click="editBatchDetails(order)" 
                          title="Edit Order Details"
                          :disabled="order.status === 'Received' || order.status === 'Depleted'"
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
                </tbody>
              </table>
            </div>
            
            <!-- Empty State -->
            <div v-if="orders.length === 0" class="text-center text-muted py-5">
              <Package :size="48" class="text-muted mb-3" />
              <div>
                <h6 class="text-muted">No stock receipts found</h6>
                <p class="mb-3">No stock has been received from this supplier yet.</p>
                <button class="btn btn-primary btn-sm" @click="openReceiveStockModal">
                  <Plus :size="16" class="me-1" />
                  Receive First Stock
                </button>
              </div>
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
            <div class="timeline" v-if="recentActivity.length > 0">
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
            </div>
            
            <!-- Empty Timeline State -->
            <div v-if="recentActivity.length === 0" class="text-center py-4">
              <Clock :size="32" class="text-muted mb-2" />
              <p class="text-muted">No recent activity</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Show message if no supplier found -->
    <div v-if="!loading && !error && !supplier" class="alert alert-warning text-center">
      <h5>Supplier Not Found</h5>
      <p>No supplier found with ID: {{ supplierId }}</p>
      <button class="btn btn-primary" @click="goBack">Go Back to Suppliers</button>
    </div>

    <!-- Create Order Modal -->
    <CreateOrderModal
      v-if="showCreateOrderModal && supplier"
      :show="showCreateOrderModal"
      :supplier="supplier"
      @close="closeCreateOrderModal"
      @saved="handleOrderSave"
    />

    <!-- Receive Stock Modal (Shows ALL pending batches for bulk receiving) -->
    <ReceiveStockModal
      v-if="showReceiveStockModal && supplier"
      :show="showReceiveStockModal"
      :supplier="supplier"
      @close="closeReceiveStockModal"
      @received="handleStockReceived"
    />

    <!-- Batch Details Modal (View only) -->
    <BatchDetailsModal
      v-if="showBatchDetailsModal"
      :show="showBatchDetailsModal"
      :receipt="selectedReceiptForView"
      @close="closeBatchDetailsModal"
    />

    <!-- Edit Batch Details Modal -->
    <EditBatchDetailsModal
      v-if="showEditBatchDetailsModal && supplier"
      :show="showEditBatchDetailsModal"
      :receipt="selectedReceiptForEdit"
      :supplier="supplier"
      @close="closeEditBatchDetailsModal"
      @saved="handleBatchDetailsUpdated"
    />

    <!-- Active Orders Modal -->
    <ActiveOrdersModal
      v-if="showActiveOrdersModal && supplier"
      :show="showActiveOrdersModal"
      :orders="getActiveOrdersForModal()"
      :supplier="supplier"
      :loading="false"
      @close="closeActiveOrdersModal"
    />

    <!-- Order Details Modal -->
    <OrderDetailsModal
      v-if="selectedOrderForView"
      :show="showOrderDetailsModal"
      :order="selectedOrderForView"
      :can-edit="selectedOrderForView.status !== 'Received' && selectedOrderForView.status !== 'Cancelled'"
      :initial-mode="orderModalMode"
      @close="closeOrderDetailsModal"
      @save="handleOrderUpdate"
      @edit-mode-changed="handleOrderEditModeChanged"
    />

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
  MoreVertical,
  Star,
  Copy,
  PhoneCall,
  Send,
  Navigation,
  FileText,
  Trash2,
  Package,
  Eye,
  Filter,
  AlertTriangle,
  Activity,
  CreditCard
} from 'lucide-vue-next'
import CreateOrderModal from '@/components/suppliers/CreateOrderModal.vue'
import ReceiveStockModal from '@/components/suppliers/ReceiveStockModal.vue'
import BatchDetailsModal from '@/components/suppliers/BatchDetailsModal.vue'
import EditBatchDetailsModal from '@/components/suppliers/EditBatchDetailsModal.vue'
import OrderDetailsModal from '@/components/suppliers/OrderDetailsModal.vue'
import ActiveOrdersModal from '@/components/suppliers/ActiveOrdersModal.vue'
import { useToast } from '@/composables/ui/useToast'
import { useAuth } from '@/composables/auth/useAuth'
import { useProducts } from '@/composables/api/useProducts'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export default {
  name: 'SupplierDetails',
  components: {
    ArrowLeft,
    Edit,
    Plus,
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
    MoreVertical,
    Star,
    Copy,
    PhoneCall,
    Send,
    Navigation,
    FileText,
    Trash2,
    Package,
    Eye,
    Filter,
    AlertTriangle,
    Activity,
    CreditCard,
    CreateOrderModal,
    ReceiveStockModal,
    BatchDetailsModal,
    EditBatchDetailsModal,
    OrderDetailsModal,
    ActiveOrdersModal
  },
  props: {
    supplierId: {
      type: [String, Number],
      required: true
    }
  },
  setup() {
    const { user } = useAuth()
    const { success, error: showError } = useToast()
    const { fetchProductById } = useProducts()
    
    return {
      user,
      success,
      showError,
      fetchProductById
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
      saving: false,
      deleting: false,
      orderStatusFilter: 'all',
      selectedOrders: [],
      selectAllOrders: false,

      showCreateOrderModal: false,
      showReceiveStockModal: false,
      showBatchDetailsModal: false,
      showEditBatchDetailsModal: false,
      showActiveOrdersModal: false,
      selectedReceiptForView: null,
      selectedReceiptForEdit: null,
      showOrderDetailsModal: false,
      selectedOrderForView: null,
      orderModalMode: 'view',
      
      showEditModal: false,
      showDeleteModal: false,
      showSortDropdown: false,
      sortDropdownRef: null,
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
      
      editingNotes: false,
      editableNotes: ''
    }
  },
  async mounted() {
    await this.fetchSupplierDetails()
    
    // Add click outside listener for sort dropdown
    document.addEventListener('click', this.handleClickOutside)
  },
  
  beforeUnmount() {
    // Clean up click outside listener
    document.removeEventListener('click', this.handleClickOutside)
  },
  watch: {
    supplierId: {
      handler(newId, oldId) {
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
        const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || localStorage.getItem('authToken') || sessionStorage.getItem('authToken')
        
        // ===== STEP 1: Fetch Supplier Info =====
        const supplierResponse = await axios.get(
          `${API_BASE_URL}/suppliers/${this.supplierId}/`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        )
        
        const backendSupplier = supplierResponse.data
        console.log('✅ Supplier loaded:', backendSupplier.supplier_name)
        
        // ===== STEP 2: Fetch Batches for this Supplier =====
        let batchesList = []
        try {
          const batchesResponse = await axios.get(
            `${API_BASE_URL}/batches/by-supplier/${this.supplierId}/`,
            {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            }
          )
          
          console.log('=== BATCHES RESPONSE DEBUG ===')
          console.log('Response data:', batchesResponse.data)
          console.log('Type:', typeof batchesResponse.data)
          console.log('Is array?', Array.isArray(batchesResponse.data))
          console.log('==============================')
          
          // Handle different response formats
          const rawBatches = batchesResponse.data.batches || batchesResponse.data || []
          
          // Ensure it's always an array
          if (Array.isArray(rawBatches)) {
            batchesList = rawBatches
          } else if (rawBatches.data && Array.isArray(rawBatches.data)) {
            batchesList = rawBatches.data
          } else {
            console.warn('⚠️ Batches response is not an array:', rawBatches)
            batchesList = []
          }
          
          console.log(`📦 Found ${batchesList.length} batches`)
          
        } catch (batchesError) {
          console.error('❌ Error fetching batches:', batchesError)
          if (batchesError.response?.status === 404) {
            console.warn('⚠️ Batches endpoint returned 404 - batches will be empty')
          }
          batchesList = []
        }
        
        // ===== STEP 3: Map Supplier Data =====
        this.supplier = {
          id: backendSupplier._id,
          name: backendSupplier.supplier_name,
          contactPerson: backendSupplier.contact_person || '',
          email: backendSupplier.email || '',
          phone: backendSupplier.phone_number || '',
          address: backendSupplier.address || '',
          purchaseOrders: 0, // Will be set after grouping batches into orders
          status: backendSupplier.isDeleted ? 'inactive' : 'active',
          type: backendSupplier.type || 'food',
          rating: 4.5,
          isFavorite: false,
          notes: backendSupplier.notes || '',
          createdAt: backendSupplier.created_at,
          updatedAt: backendSupplier.updated_at
        }
        
        // ===== STEP 4: Group Batches by Date to Create "Receipts" =====
        // Safety check
        if (!Array.isArray(batchesList)) {
          console.error('❌ batchesList is not an array:', batchesList)
          batchesList = []
        }
        
        // If no batches, set empty orders
        if (batchesList.length === 0) {
          console.log('ℹ️ No batches found for this supplier')
          this.orders = []
          this.filteredOrders = []
          this.editableNotes = this.supplier.notes
          this.recentActivity = [
            {
              id: 1,
              type: 'supplier_updated',
              title: 'Supplier Information Updated',
              description: 'Contact details updated',
              user: 'Admin User',
              date: backendSupplier.updated_at
            }
          ]
          
          console.log('=== SUMMARY (No Batches) ===')
          console.log('Supplier:', this.supplier.name)
          console.log('Stock Receipts: 0')
          console.log('============================')
          return
        }
        
        // Group batches by receipt (either date_received for completed or expected_delivery_date for pending)
        const batchesByDate = {}
        batchesList.forEach(batch => {
          // For pending orders, group by expected_delivery_date
          // For received orders, group by date_received
          let dateKey
          if (batch.date_received) {
            dateKey = typeof batch.date_received === 'string' ? batch.date_received.split('T')[0] : new Date(batch.date_received).toISOString().split('T')[0]
          } else if (batch.expected_delivery_date) {
            dateKey = typeof batch.expected_delivery_date === 'string' ? batch.expected_delivery_date.split('T')[0] : new Date(batch.expected_delivery_date).toISOString().split('T')[0]
          } else {
            dateKey = batch.created_at.split('T')[0]
          }
          
          if (!batchesByDate[dateKey]) {
            batchesByDate[dateKey] = []
          }
          batchesByDate[dateKey].push(batch)
        })
        
        // ===== STEP 4.5: Enrich batches with product details for complete category info =====
        const enrichedBatchesByDate = {}
        for (const [dateKey, batches] of Object.entries(batchesByDate)) {
          enrichedBatchesByDate[dateKey] = await Promise.all(
            batches.map(async (batch) => {
              try {
                // Always fetch product details to get category info (don't rely on batch fields)
                if (batch.product_id) {
                  const productResponse = await this.fetchProductById(batch.product_id)
                  const product = productResponse.data
                  
                  if (product) {
                    return {
                      ...batch,
                      // Get product name and category info from product, not from batch
                      product_name: product.product_name || product.name || batch.product_id || 'Unknown Product',
                      category_id: product.category_id || '',
                      category_name: product.category_name || '',
                      subcategory_name: product.subcategory_name || ''
                    }
                  }
                }
                
                return batch
              } catch (err) {
                console.warn(`Failed to fetch product details for batch ${batch._id}:`, err)
                return batch
              }
            })
          )
        }
        
        // Convert grouped batches to "orders" format
        this.orders = Object.entries(enrichedBatchesByDate).map(([date, batches]) => {
          const totalCost = batches.reduce((sum, b) => sum + ((b.cost_price || 0) * (b.quantity_received || 0)), 0)
          const totalQuantity = batches.reduce((sum, b) => sum + (b.quantity_received || 0), 0)
          
          let receiptId = `SR-${date.replace(/-/g, '')}`
          const firstBatchNotes = batches[0].notes || ''
          const receiptMatch = firstBatchNotes.match(/Receipt:\s*([^\|]+)/)
          if (receiptMatch) {
            receiptId = receiptMatch[1].trim()
          }
          
          // Get expected_delivery_date and date_received from first batch
          const firstBatch = batches[0]
          const expectedDate = firstBatch.expected_delivery_date ? 
            (typeof firstBatch.expected_delivery_date === 'string' ? firstBatch.expected_delivery_date.split('T')[0] : new Date(firstBatch.expected_delivery_date).toISOString().split('T')[0]) : 
            date
          const receivedDate = firstBatch.date_received ? 
            (typeof firstBatch.date_received === 'string' ? firstBatch.date_received.split('T')[0] : new Date(firstBatch.date_received).toISOString().split('T')[0]) : 
            null
          
          return {
            id: receiptId,
            date: firstBatch.created_at ? firstBatch.created_at.split('T')[0] : date, // Order date (when PO was created)
            quantity: totalQuantity,
            total: totalCost,
            expectedDate: expectedDate, // Expected delivery date
            receivedDate: receivedDate, // Actual received date (null for pending)
            status: this.getReceiptStatus(batches),
            description: `Stock receipt with ${batches.length} item(s)`,
            notes: firstBatchNotes,
            priority: 'normal',
            subtotal: totalCost,
            tax: 0,
            shippingCost: 0,
            taxRate: 0,
            items: batches.map(batch => ({
              name: batch.product_name || batch.product_id || 'Unknown Product',
              quantity: batch.quantity_received,
              unit: 'pcs',
              unitPrice: batch.cost_price || 0,
              totalPrice: (batch.cost_price || 0) * (batch.quantity_received || 0),
              notes: batch.notes || '',
              productId: batch.product_id,
              product_name: batch.product_name || 'Unknown Product', // Add product_name for ActiveOrdersModal
              batchNumber: batch.batch_number,  // ✅ Pass batch number for activation
              batchId: batch._id,  // ✅ Pass batch ID 
              expiryDate: batch.expiry_date,
              quantityRemaining: batch.quantity_remaining,
              // ✅ Enhanced category info from product details
              categoryId: batch.category_id || '',
              categoryName: batch.category_name || '',
              subcategoryName: batch.subcategory_name || ''
            })),
            orderHistory: [{
              id: batches[0].created_at,
              type: 'stock_received',
              title: 'Stock Received',
              description: `Received ${batches.length} batch(es) containing ${totalQuantity} units`,
              user: 'System',
              date: batches[0].created_at
            }]
          }
        }).sort((a, b) => new Date(b.date) - new Date(a.date))
        
        // Update total orders count after grouping
        this.supplier.purchaseOrders = this.orders.length
        
        this.filteredOrders = [...this.orders]
        this.editableNotes = this.supplier.notes
        
        this.recentActivity = [
          {
            id: 1,
            type: 'supplier_updated',
            title: 'Supplier Information Updated',
            description: 'Contact details updated',
            user: 'Admin User',
            date: backendSupplier.updated_at
          }
        ]
        
        console.log('=== SUMMARY ===')
        console.log('Supplier:', this.supplier.name)
        console.log('Stock Receipts:', this.orders.length)
        console.log('Total Batches:', batchesList.length)
        console.log('First Receipt:', this.orders[0])
        console.log('===============')
        
      } catch (error) {
        console.error('Error fetching supplier details:', error)
        
        if (error.response?.status === 404) {
          this.error = `Supplier with ID ${this.supplierId} not found`
          this.showError(`Supplier with ID ${this.supplierId} not found`)
        } else {
          this.error = error.response?.data?.error || `Failed to load supplier details: ${error.message}`
          this.showError(this.error)
        }
      } finally {
        this.loading = false
      }
    },

    getReceiptStatus(batches) {
      if (!batches || batches.length === 0) return 'Unknown'
      
      const allPending = batches.every(b => b.status === 'pending')
      const allActive = batches.every(b => b.status === 'active')
      const allInactive = batches.every(b => b.status === 'inactive')
      const hasPending = batches.some(b => b.status === 'pending')
      
      if (allPending) return 'Pending Delivery'
      if (allActive) return 'Received'
      if (allInactive) return 'Depleted'
      if (hasPending) return 'Partially Received'
      
      return 'Mixed Status'
    },

    openReceiveStockModal() {
      // Open the "Receive Stock" modal that shows ALL pending batches
      this.showReceiveStockModal = true
    },

    closeReceiveStockModal() {
      this.showReceiveStockModal = false
    },

    openActiveOrdersModal() {
      // Open the "Active Orders" modal that shows pending orders for this supplier
      this.showActiveOrdersModal = true
    },

    closeActiveOrdersModal() {
      this.showActiveOrdersModal = false
    },
    
    async handleStockReceived(results) {
      console.log('✅ Stock received:', results)
      
      if (results.successful?.length > 0) {
        this.success(`Successfully received ${results.successful.length} batch(es)`)
      }
      
      if (results.failed?.length > 0) {
        this.showError(`Failed to receive ${results.failed.length} batch(es)`)
      }
      
      // Refresh supplier details to show updated batches
      await this.fetchSupplierDetails()
    },


    createOrder() {
      this.openCreateOrderModal()
    },

    openCreateOrderModal() {
      this.showCreateOrderModal = true
    },

    closeCreateOrderModal() {
      this.showCreateOrderModal = false
    },

    async handleOrderSave(result) {
      console.log('✅ Order created:', result)
      
      const { successful, failed } = result.results
      
      if (successful.length > 0) {
        this.success(`Successfully created ${successful.length} pending order(s)`)
      }
      
      if (failed.length > 0) {
        this.showError(`Failed to create ${failed.length} order(s)`)
      }
      
      // Refresh supplier details to show new batches
      await this.fetchSupplierDetails()
    },

    canReceiveOrder(order) {
      return order.status === 'Pending' || order.status === 'Active'
    },


    viewReceipt(receipt) {
      console.log('Viewing receipt:', receipt)
      this.selectedReceiptForView = receipt
      this.showBatchDetailsModal = true
    },
    
    closeBatchDetailsModal() {
      this.showBatchDetailsModal = false
      this.selectedReceiptForView = null
    },

    editBatchDetails(receipt) {
      console.log('📝 Editing batch details for receipt:', receipt)
      console.log('Receipt has', receipt.items?.length || 0, 'items')
      console.log('Order Date (created_at):', receipt.date)
      console.log('Expected Delivery:', receipt.expectedDate)
      this.selectedReceiptForEdit = receipt
      this.showEditBatchDetailsModal = true
    },
    
    closeEditBatchDetailsModal() {
      this.showEditBatchDetailsModal = false
      this.selectedReceiptForEdit = null
    },

    async handleBatchDetailsUpdated(updatedReceipt) {
      console.log('✅ Batch details updated:', updatedReceipt)
      this.success('Purchase order updated successfully')
      
      // Refresh supplier details to show updated batches
      await this.fetchSupplierDetails()
    },

    goBack() {
      this.$router.push({ name: 'Suppliers' })
    },


    callSupplier() {
      if (this.supplier?.phone) {
        window.open(`tel:${this.supplier.phone}`)
        this.success(`Calling ${this.supplier.name}...`)
      } else {
        this.showError('No phone number available for this supplier')
      }
    },

    emailSupplier() {
      if (this.supplier?.email) {
        window.open(`mailto:${this.supplier.email}`)
        this.success(`Opening email to ${this.supplier.name}...`)
      } else {
        this.showError('No email address available for this supplier')
      }
    },

    openMaps() {
      if (this.supplier?.address) {
        const encodedAddress = encodeURIComponent(this.supplier.address)
        window.open(`https://maps.google.com/maps?q=${encodedAddress}`, '_blank')
        this.success('Opening location in Google Maps...')
      } else {
        this.showError('No address available for this supplier')
      }
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
        const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || localStorage.getItem('authToken') || sessionStorage.getItem('authToken')
        
        const backendData = {
          supplier_name: this.editForm.name,
          contact_person: this.editForm.contactPerson,
          email: this.editForm.email,
          phone_number: this.editForm.phone,
          address: this.editForm.address,
          type: this.editForm.type,
          notes: this.editForm.notes
        }
        
        const response = await axios.put(
          `${API_BASE_URL}/suppliers/${this.supplier.id}/`,
          backendData,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        )
        
        const updated = response.data
        this.supplier = {
          id: updated._id,
          name: updated.supplier_name,
          contactPerson: updated.contact_person || '',
          email: updated.email || '',
          phone: updated.phone_number || '',
          address: updated.address || '',
          purchaseOrders: updated.purchase_orders?.length || 0,
          status: updated.isDeleted ? 'inactive' : 'active',
          type: updated.type || 'food',
          rating: this.supplier.rating,
          isFavorite: this.supplier.isFavorite,
          notes: updated.notes || '',
          createdAt: updated.created_at,
          updatedAt: updated.updated_at
        }
        
        this.closeEditModal()
        
        // Show success toast instead of setting successMessage
        this.success(`${this.supplier.name} has been updated successfully!`)
        
      } catch (error) {
        console.error('Error updating supplier:', error)
        const errorMessage = error.response?.data?.error || `Failed to update supplier: ${error.message}`
        
        // Show error toast instead of setting error
        this.showError(errorMessage)
        
      } finally {
        this.saving = false
      }
    },


    toggleFavorite() {
      this.supplier.isFavorite = !this.supplier.isFavorite
      
      // Show toast instead of setting successMessage
      this.success(`${this.supplier.name} ${this.supplier.isFavorite ? 'added to' : 'removed from'} favorites`)
    },

    duplicateSupplier() {
      this.showError('Duplicate supplier functionality coming soon!')
    },

    deleteSupplier() {
      this.showDeleteModal = true
    },

    async confirmDeleteSupplier() {
      this.deleting = true
      
      try {
        const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || localStorage.getItem('authToken') || sessionStorage.getItem('authToken')
        
        await axios.delete(
          `${API_BASE_URL}/suppliers/${this.supplier.id}/`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        )
        
        this.showDeleteModal = false
        
        // Show success toast
        this.success(`${this.supplier.name} has been deleted successfully`)
        
        setTimeout(() => {
          this.goBack()
        }, 1500)
        
      } catch (error) {
        console.error('Error deleting supplier:', error)
        const errorMessage = error.response?.data?.error || `Failed to delete supplier: ${error.message}`
        
        // Show error toast instead of setting error
        this.showError(errorMessage)
        
      } finally {
        this.deleting = false
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

    toggleSortDropdown(event) {
      if (event) {
        event.stopPropagation()
      }
      this.showSortDropdown = !this.showSortDropdown
    },

    closeSortDropdown() {
      this.showSortDropdown = false
    },

    handleClickOutside(event) {
      if (this.$refs.sortDropdownRef && !this.$refs.sortDropdownRef.contains(event.target)) {
        this.closeSortDropdown()
      }
    },

    handleSort(criteria) {
      this.sortOrders(criteria)
      this.closeSortDropdown()
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
      
      // Show toast for feedback
      this.success(`Orders sorted by ${criteria}`)
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

    viewOrder(order) {
      console.log('=== VIEWING ORDER ===')
      console.log('Order being passed to modal:', order)
      console.log('Order items:', order.items)
      console.log('Items length:', order.items?.length)
      console.log('Items structure:', order.items?.[0])
      console.log('===================')
      
      this.selectedOrderForView = order
      this.orderModalMode = 'view'
      this.showOrderDetailsModal = true
    },

    editOrder(order) {
      this.selectedOrderForView = order
      this.orderModalMode = 'edit'
      this.showOrderDetailsModal = true
    },

    closeOrderDetailsModal() {
      this.showOrderDetailsModal = false
      this.selectedOrderForView = null
      this.orderModalMode = 'view'
    },

    deleteOrder(order) {
      if (confirm(`Are you sure you want to delete order ${order.id}?`)) {
        this.orders = this.orders.filter(o => o.id !== order.id)
        this.filterOrders()
        
        // Show success toast instead of setting successMessage
        this.success(`Order ${order.id} deleted successfully`)
      }
    },

    duplicateOrder(order) {
      this.showError(`Duplicate order ${order.id} feature coming soon!`)
    },

    trackOrder(order) {
      this.showError(`Track order ${order.id} feature coming soon!`)
    },

    handleOrderUpdate(updatedOrder) {
      const index = this.orders.findIndex(o => o.id === updatedOrder.id)
      if (index !== -1) {
        this.orders[index] = updatedOrder
        this.filterOrders()
        
        // Show success toast instead of setting successMessage
        this.success(`Order ${updatedOrder.id} updated successfully`)
      }
      
      this.closeOrderDetailsModal()
    },

    handleOrderEditModeChanged(isEditMode) {
      // Edit mode changed
    },

    bulkExportOrders() {
      this.showError(`Export ${this.selectedOrders.length} selected orders feature coming soon!`)
    },

    bulkUpdateStatus() {
      this.showError(`Update status for ${this.selectedOrders.length} selected orders feature coming soon!`)
    },

    bulkDeleteOrders() {
      if (confirm(`Are you sure you want to delete ${this.selectedOrders.length} selected orders?`)) {
        this.orders = this.orders.filter(o => !this.selectedOrders.includes(o.id))
        this.selectedOrders = []
        this.selectAllOrders = false
        this.filterOrders()
        
        // Show success toast instead of setting successMessage
        this.success('Selected orders deleted successfully')
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
      
      // Show success toast instead of setting successMessage
      this.success('Notes updated successfully')
    },

    cancelNotesEdit() {
      this.editableNotes = this.supplier.notes
      this.editingNotes = false
    },

    getOrderStatusClass(status) {
      const classes = {
        'Received': 'bg-success',
        'Pending Delivery': 'bg-warning',
        'Partially Received': 'bg-info',
        'Pending': 'bg-warning',
        'Partial': 'bg-info',
        'Cancelled': 'bg-danger',
        'Active': 'bg-primary',
        'Depleted': 'bg-secondary'
      }
      return classes[status] || 'bg-secondary'
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
      // Count orders that are currently pending (not yet received)
      return this.orders.filter(order => 
        order.status === 'Pending Delivery' || order.status === 'Partially Received'
      ).length
    },

    getActiveOrdersForModal() {
      console.log('🔍 Getting active orders for modal...')
      console.log('All orders:', this.orders.length)
      console.log('Orders with statuses:', this.orders.map(o => ({ id: o.id, status: o.status })))
      
      // Filter for pending orders (both Pending Delivery and Partially Received)
      const activeOrders = this.orders.filter(order => {
        const isActive = order.status === 'Pending Delivery' || order.status === 'Partially Received'
        console.log(`Order ${order.id}: status=${order.status}, isActive=${isActive}`)
        return isActive
      })
      
      console.log('Active orders found:', activeOrders.length)
      
      // Transform the orders to match the format expected by ActiveOrdersModal
      const transformedOrders = activeOrders.map(order => {
        console.log(`Transforming order ${order.id} with ${order.items?.length || 0} items`)
        
        return {
          id: order.id,
          supplier: this.supplier.name,
          supplierId: this.supplier.id,
          supplierEmail: this.supplier.email || 'N/A',
          orderDate: order.date, // Map date to orderDate
          expectedDelivery: order.expectedDate, // Map expectedDate to expectedDelivery
          deliveredDate: order.receivedDate, // Map receivedDate to deliveredDate
          totalAmount: order.total, // Map total to totalAmount
          status: order.status,
          items: order.items.map(item => {
            console.log(`Item: name="${item.name}", product_name="${item.product_name}", productId="${item.productId}"`)
            return {
              name: item.name || item.product_name || item.productId || 'Unknown Product',
              product_name: item.name || item.product_name || 'Unknown Product',
              product_id: item.productId,
              quantity: item.quantity,
              unitPrice: item.unitPrice,
              totalPrice: item.totalPrice,
              batchNumber: item.batchNumber,
              batchId: item.batchId,
              expiryDate: item.expiryDate,
              quantityRemaining: item.quantityRemaining
            }
          }),
          description: order.description,
          notes: order.notes
        }
      })
      
      console.log('Transformed orders:', transformedOrders.length)
      return transformedOrders
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
    }
  }
}
</script>

<style scoped>
@import '@/assets/styles/colors.css';

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

.dropdown-menu-modern {
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border: 1px solid var(--neutral-medium);
  padding: 0.75rem 0;
  min-width: 280px;
}

.dropdown-menu-modern .dropdown-item {
  padding: 0.75rem 1.25rem;
  display: flex;
  align-items: center;
  color: var(--tertiary-dark);
  transition: all 0.2s ease;
}

.dropdown-menu-modern .dropdown-item:hover {
  background-color: var(--neutral-light);
  color: var(--primary);
  transform: translateX(2px);
}

.dropdown-menu-modern .dropdown-item.disabled {
  color: var(--neutral-medium);
  cursor: not-allowed;
  opacity: 0.6;
}

/* Fix for sort dropdown in Stock Receipt History */
.dropdown {
  position: relative;
}

.dropdown-menu {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 1000;
  min-width: 160px;
  padding: 0.5rem 0;
  margin: 0.125rem 0 0;
  font-size: 0.875rem;
  color: #212529;
  text-align: left;
  list-style: none;
  background-color: #fff;
  background-clip: padding-box;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 0.375rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.175);
}

.dropdown-menu.show {
  display: block !important;
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 0.5rem 1rem;
  clear: both;
  font-weight: 400;
  color: #212529;
  text-align: inherit;
  text-decoration: none;
  white-space: nowrap;
  background-color: transparent;
  border: 0;
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;
}

.dropdown-item:hover,
.dropdown-item:focus {
  color: #1e2125;
  background-color: #e9ecef;
}

.btn.active {
  background-color: var(--primary);
  border-color: var(--primary);
  color: white;
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

.section-header {
  margin-bottom: 1rem;
}

.section-divider {
  height: 1px;
  background-color: var(--neutral-medium);
  margin: 1.5rem 0;
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

.stats-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: none;
  border-radius: 12px;
}

.orders-card, .activity-card, .notes-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: none;
  border-radius: 12px;
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
  padding: 0.75rem;
  border-radius: 8px;
  font-style: italic;
  border: 1px solid var(--neutral-medium);
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: var(--neutral-light);
  border-radius: 8px;
  border: 1px solid var(--neutral-medium);
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

.clickable-stat {
  cursor: pointer;
  transition: all 0.2s ease;
}

.clickable-stat:hover {
  background-color: var(--primary-light);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

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
@media (max-width: 992px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .header-actions {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .dropdown-menu-modern {
    width: 100%;
    min-width: unset;
  }
  
  .supplier-details-page {
    padding: 1rem;
  }
}

@media (max-width: 576px) {
  .page-header {
    padding: 1rem;
  }
  
  .section-divider {
    margin: 1rem 0;
  }
}
</style>