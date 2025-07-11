<template>
  <div class="customers-page">
    <div class="page-header">
      <h1 class="page-title">Customer Management</h1>
    </div>

    <!-- KPI Cards Row -->
    <div class="kpi-cards-container">
      <CardTemplate
        title="Active Users"
        :value="activeUsersCount"
        border-color="info"
        subtitle="Total Active Users"
        change=""
        change-type="positive"
        variant=""
        class="kpi-card"
      />
      <CardTemplate
        title="Monthly New Users"
        :value="monthlyUsersCount"
        border-color="success"
        subtitle="This month's new users"
        change=""
        change-type="positive"
        variant=""
        class="kpi-card"
      />
      <CardTemplate
        title="Daily Customer Logins"
        :value="dailyUsersCount"
        border-color="danger"
        subtitle="Last 24 hours"
        change=""
        change-type="positive"
        variant=""
        class="kpi-card"
      />
    </div>

    <!-- Header Section -->
    <div class="search-section-wrapper">
      <!-- Search Bar and Action Buttons in same row -->
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

          <button 
            class="btn btn-danger" 
            @click="deleteSelected" 
            :disabled="selectedCustomers.length === 0 || loading"
          >
            Delete Selected ({{ selectedCustomers.length }})
          </button>
          <button class="btn btn-success" @click="showAddCustomerModal">
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
        <button class="btn btn-primary" @click="refreshData" :disabled="loading">
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
            <th>Address</th>
            <th>Loyalty Points</th>
            <th>Date Created</th>
            <th class="actions-column">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="customer in filteredCustomers" 
            :key="customer._id || customer.customer_id"
            :class="{ 
              'selected': selectedCustomers.includes(customer._id || customer.customer_id),
              'refreshing': loading 
            }"
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
                <button 
                  class="btn btn-outline-secondary btn-icon-only btn-xs" 
                  @click="editCustomer(customer)"
                  data-bs-toggle="tooltip"
                  title="Edit"
                  :disabled="loading"
                >
                  <Edit :size="14" />
                </button>
                <button 
                  class="btn btn-outline-primary btn-icon-only btn-xs" 
                  @click="viewCustomer(customer)"
                  data-bs-toggle="tooltip"
                  title="View"
                  :disabled="loading"
                >
                  <Eye :size="14" />
                </button>
                <button 
                  class="btn btn-outline-danger btn-icon-only btn-xs" 
                  @click="deleteCustomer(customer)"
                  data-bs-toggle="tooltip"
                  title="Delete"
                  :disabled="loading"
                >
                  <Trash2 :size="14" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && filteredCustomers.length === 0 && !error" class="empty-state">
      <div class="card">
        <div class="card-body text-center py-5">
          <i class="bi bi-people" style="font-size: 3rem; color: #6b7280;"></i>
          <p class="mt-3 mb-3">
            <span v-if="searchQuery">No customers found matching "{{ searchQuery }}"</span>
            <span v-else-if="customers.length === 0">No customers found</span>
            <span v-else>All customers are currently hidden by filters</span>
          </p>
          <div class="d-flex gap-2 justify-content-center">
            <button v-if="!searchQuery && customers.length === 0" class="btn btn-primary" @click="showAddCustomerModal">
              <i class="bi bi-person-plus"></i>
              Add First Customer
            </button>
            <button v-if="searchQuery" class="btn btn-secondary" @click="clearSearch">
              <i class="bi bi-funnel"></i>
              Clear Search
            </button>
            <button class="btn btn-info" @click="refreshData">
              <i class="bi bi-arrow-clockwise"></i>
              Refresh Data
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Customer Modal (Add/Edit) with Validation -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h2>{{ isEditMode ? 'Edit Customer' : 'Add New Customer' }}</h2>
        
        <form @submit.prevent="saveCustomer" class="customer-form">
          <div class="form-group">
            <label for="username">Username:</label>
            <input 
              id="username"
              v-model="customerForm.username" 
              type="text" 
              required 
              :disabled="formLoading"
              :class="{ 'error': validationErrors.username }"
              @input="validateField('username', $event.target.value)"
              @blur="validateField('username', $event.target.value)"
            />
            <div v-if="validationErrors.username" class="field-error">
              {{ validationErrors.username }}
            </div>
          </div>
          
          <div class="form-group">
            <label for="full_name">Full Name:</label>
            <input 
              id="full_name"
              v-model="customerForm.full_name" 
              type="text" 
              required 
              :disabled="formLoading"
              :class="{ 'error': validationErrors.full_name }"
              @input="validateField('full_name', $event.target.value)"
              @blur="validateField('full_name', $event.target.value)"
            />
            <div v-if="validationErrors.full_name" class="field-error">
              {{ validationErrors.full_name }}
            </div>
          </div>

          <div class="form-group">
            <label for="email">Email:</label>
            <input 
              id="email"
              v-model="customerForm.email" 
              type="email" 
              required 
              :disabled="formLoading"
              :class="{ 'error': validationErrors.email }"
              @input="validateField('email', $event.target.value)"
              @blur="validateField('email', $event.target.value)"
            />
            <div v-if="validationErrors.email" class="field-error">
              {{ validationErrors.email }}
            </div>
          </div>

          <div class="form-group">
            <label for="phone">Phone:</label>
            <input 
              id="phone"
              v-model="customerForm.phone" 
              type="tel" 
              :disabled="formLoading"
              :class="{ 'error': validationErrors.phone }"
              @input="validateField('phone', $event.target.value)"
              @blur="validateField('phone', $event.target.value)"
            />
            <div v-if="validationErrors.phone" class="field-error">
              {{ validationErrors.phone }}
            </div>
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
              :class="{ 'error': validationErrors.loyalty_points }"
              @input="validateField('loyalty_points', $event.target.value)"
              @blur="validateField('loyalty_points', $event.target.value)"
            />
            <div v-if="validationErrors.loyalty_points" class="field-error">
              {{ validationErrors.loyalty_points }}
            </div>
          </div>

          <!-- Overall form error -->
          <div v-if="formError" class="form-error">
            {{ formError }}
          </div>

          <!-- Validation loading indicator -->
          <div v-if="isValidating" class="validation-loading">
            <span>Validating...</span>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" :disabled="formLoading">
              Cancel
            </button>
            <button 
              type="submit" 
              :disabled="formLoading || hasValidationErrors || isValidating" 
              class="btn-primary"
            >
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
import CustomerApiService from '../services/apiCustomers.js'
import CardTemplate from '@/components/common/CardTemplate.vue'
import { Edit, Eye, Trash2, Lock, Unlock } from 'lucide-vue-next'

// ============ ADVANCED CACHING SYSTEM ============
class CustomerCache {
  constructor() {
    this.customers = new Map()
    this.kpiData = new Map()
    this.metadata = {
      lastUpdate: null,
      hitCount: 0,
      missCount: 0,
      enabled: true
    }
    this.ttl = 5 * 60 * 1000 // 5 minutes cache TTL
  }

  // Check if cache entry is still valid
  isValid(timestamp) {
    return timestamp && (Date.now() - timestamp < this.ttl)
  }

  // Get customers from cache
  getCustomers() {
    const cached = this.customers.get('all')
    if (cached && this.isValid(cached.timestamp)) {
      this.metadata.hitCount++
      console.log('🎯 Cache HIT: Customers loaded from cache')
      return cached.data
    }
    this.metadata.missCount++
    console.log('❌ Cache MISS: Customers not in cache or expired')
    return null
  }

  // Store customers in cache
  setCustomers(data) {
    this.customers.set('all', {
      data: data,
      timestamp: Date.now()
    })
    this.metadata.lastUpdate = Date.now()
    console.log('💾 Cache SET: Customers cached successfully')
  }

  // Get KPI data from cache
  getKPI(type) {
    const cached = this.kpiData.get(type)
    if (cached && this.isValid(cached.timestamp)) {
      this.metadata.hitCount++
      console.log(`🎯 Cache HIT: ${type} KPI loaded from cache`)
      return cached.data
    }
    this.metadata.missCount++
    console.log(`❌ Cache MISS: ${type} KPI not in cache or expired`)
    return null
  }

  // Store KPI data in cache
  setKPI(type, data) {
    this.kpiData.set(type, {
      data: data,
      timestamp: Date.now()
    })
    console.log(`💾 Cache SET: ${type} KPI cached successfully`)
  }

  // Get cache statistics
  getStats() {
    const total = this.metadata.hitCount + this.metadata.missCount
    const hitRate = total > 0 ? Math.round((this.metadata.hitCount / total) * 100) : 0
    
    return {
      enabled: this.metadata.enabled,
      hitRate: hitRate,
      lastUpdate: this.metadata.lastUpdate,
      size: this.customers.size + this.kpiData.size,
      hitCount: this.metadata.hitCount,
      missCount: this.metadata.missCount
    }
  }

  // Clear all cache
  clear() {
    this.customers.clear()
    this.kpiData.clear()
    this.metadata.hitCount = 0
    this.metadata.missCount = 0
    this.metadata.lastUpdate = null
    console.log('🗑️ Cache CLEARED: All cached data removed')
  }

  // Disable cache
  disable() {
    this.metadata.enabled = false
    this.clear()
  }

  // Enable cache
  enable() {
    this.metadata.enabled = true
  }
}

export default {
  name: 'CustomersPage',
  components: {
    CardTemplate,
    Edit,
    Eye,
    Trash2,
    Lock,
    Unlock
  },
  data() {
    return {
      customers: [],
      filteredCustomers: [],
      selectedCustomers: [],
      loading: false,
      error: null,
      successMessage: null,
      searchQuery: '',
      exporting: false,
      
      // Enhanced refresh tracking
      lastRefresh: null,
      refreshProgress: '',
      refreshStartTime: null,
      
      // Auto-refresh functionality (Logs page system)
      autoRefreshEnabled: true, // Enable by default for "automatic" branding
      autoRefreshInterval: 30000, // 30 seconds (base interval)
      baseRefreshInterval: 30000, // Store original interval
      autoRefreshTimer: null,
      countdown: 30,
      countdownTimer: null,
      
      // Connection health tracking
      connectionLost: false,
      consecutiveErrors: 0,
      lastSuccessfulLoad: null,
      
      // Smart refresh rate tracking
      recentActivity: [], // Track recent entries for smart adjustment
      
      // Performance optimizations
      filterDebounceTimer: null,
      lastLoadTime: null,
      newEntryIds: new Set(),
      
      // Cache system
      cache: new CustomerCache(),
      
      // Modal states
      showModal: false,
      showViewModal: false,
      isEditMode: false,
      formLoading: false,
      formError: null,
      selectedCustomer: null,
      
      // KPI Cards
      activeUsersCount: 'Loading...',
      monthlyUsersCount: 'Loading...',
      dailyUsersCount: 'Loading...',

      // Validation states
      validationErrors: {},
      isValidating: false,

      // Customer form data
      customerForm: {
        username: '',
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
    },
    hasValidationErrors() {
      return Object.keys(this.validationErrors).length > 0
    }
  },
  methods: {
    // ============ VALIDATION METHODS ============
    checkEmailDuplicate(email, excludeId = null) {
      if (!email) return false
      
      return this.customers.some(customer => {
        const customerId = customer._id || customer.customer_id
        const isDifferentCustomer = excludeId ? customerId !== excludeId : true
        return customer.email && 
               customer.email.toLowerCase() === email.toLowerCase() && 
               isDifferentCustomer
      })
    },

    checkUsernameDuplicate(username, excludeId = null) {
      if (!username) return false
      
      return this.customers.some(customer => {
        const customerId = customer._id || customer.customer_id
        const isDifferentCustomer = excludeId ? customerId !== excludeId : true
        return customer.username && 
               customer.username.toLowerCase() === username.toLowerCase() && 
               isDifferentCustomer
      })
    },

    validateField(fieldName, value) {
      const errors = { ...this.validationErrors }
      const excludeId = this.isEditMode ? 
        (this.selectedCustomer._id || this.selectedCustomer.customer_id) : null

      switch (fieldName) {
        case 'email':
          if (!value) {
            errors.email = 'Email is required'
          } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            errors.email = 'Please enter a valid email address'
          } else if (this.checkEmailDuplicate(value, excludeId)) {
            errors.email = 'This email is already registered'
          } else {
            delete errors.email
          }
          break

        case 'username':
          if (!value) {
            errors.username = 'Username is required'
          } else if (value.length < 3) {
            errors.username = 'Username must be at least 3 characters long'
          } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            errors.username = 'Username can only contain letters, numbers, and underscores'
          } else if (this.checkUsernameDuplicate(value, excludeId)) {
            errors.username = 'This username is already taken'
          } else {
            delete errors.username
          }
          break

        case 'full_name':
          if (!value) {
            errors.full_name = 'Full name is required'
          } else if (value.length < 2) {
            errors.full_name = 'Full name must be at least 2 characters long'
          } else {
            delete errors.full_name
          }
          break

        case 'phone':
          if (value && !/^[\+]?[\d\s\-\(\)]+$/.test(value)) {
            errors.phone = 'Please enter a valid phone number'
          } else {
            delete errors.phone
          }
          break

        case 'loyalty_points':
          if (value !== undefined && value !== null && value < 0) {
            errors.loyalty_points = 'Loyalty points cannot be negative'
          } else {
            delete errors.loyalty_points
          }
          break
      }

      this.validationErrors = errors
      return !errors[fieldName]
    },

    validateForm() {
      this.validationErrors = {}
      
      const fieldsToValidate = ['email', 'username', 'full_name', 'phone', 'loyalty_points']
      
      for (const field of fieldsToValidate) {
        this.validateField(field, this.customerForm[field])
      }

      return Object.keys(this.validationErrors).length === 0
    },

    clearValidation() {
      this.validationErrors = {}
    },

    // ============ ENHANCED DATA FETCHING WITH LOGS PAGE SYSTEM ============
    async fetchCustomers(isAutoRefresh = false, isEmergencyReconnect = false) {
      // Prevent multiple simultaneous requests
      if (this.loading && !isAutoRefresh && !isEmergencyReconnect) return
      
      // Check cache first (only for non-emergency requests)
      if (!isEmergencyReconnect && this.cache.metadata.enabled) {
        const cachedCustomers = this.cache.getCustomers()
        if (cachedCustomers && !isAutoRefresh) {
          this.customers = cachedCustomers
          this.filteredCustomers = cachedCustomers
          console.log('✅ Customers loaded from cache instantly')
          return
        }
      }

      this.loading = true
      if (!isEmergencyReconnect) {
        this.error = null
      }
      this.refreshStartTime = Date.now()
      
      try {
        const previousLength = this.customers.length
        
        // Simulate progress updates
        const progressInterval = setInterval(() => {
          if (!this.loading) {
            clearInterval(progressInterval)
            return
          }
          
          const elapsed = Date.now() - this.refreshStartTime
          if (elapsed < 1000) {
            this.refreshProgress = 'Connecting to server...'
          } else if (elapsed < 2000) {
            this.refreshProgress = 'Fetching customer data...'
          } else {
            this.refreshProgress = 'Processing customer records...'
          }
        }, 500)
        
        console.log(`📡 Fetching customers from API... (${isAutoRefresh ? 'auto-refresh' : isEmergencyReconnect ? 'emergency-reconnect' : 'manual'})`)
        const data = await apiService.getCustomers()
        
        // Clear progress interval
        clearInterval(progressInterval)
        
        // Connection health tracking
        this.connectionLost = false
        this.consecutiveErrors = 0
        this.lastSuccessfulLoad = Date.now()
        this.error = null
        
        // Smart refresh rate adjustment
        this.trackActivityAndAdjustRefreshRate(data, previousLength)
        
        // Track new entries for highlighting
        if (isAutoRefresh && this.customers.length > 0) {
          const existingIds = new Set(this.customers.map(customer => customer._id || customer.customer_id))
          data.forEach(customer => {
            const id = customer._id || customer.customer_id
            if (!existingIds.has(id)) {
              this.newEntryIds.add(id)
              // Track for activity analysis
              this.recentActivity.push({
                timestamp: Date.now(),
                customerId: id
              })
            }
          })
          
          // Clear new entry highlights after 5 seconds
          setTimeout(() => {
            this.newEntryIds.clear()
          }, 5000)
        }
        
        // Store in cache
        if (this.cache.metadata.enabled) {
          this.cache.setCustomers(data)
        }
        
        this.customers = data
        this.filteredCustomers = data
        this.lastRefresh = new Date()
        this.lastLoadTime = Date.now()
        
        console.log(`✅ Customers loaded successfully: ${data.length} customers`)
        
      } catch (error) {
        console.error('❌ Error fetching customers:', error)
        
        // Handle connection errors
        this.consecutiveErrors++
        this.error = this.getDetailedErrorMessage(error)
        
        // Mark connection as lost after 3 consecutive errors
        if (this.consecutiveErrors >= 3) {
          this.connectionLost = true
          console.log('Connection marked as lost after 3 consecutive errors')
        }
        
        // Slow down refresh rate when experiencing errors
        if (this.consecutiveErrors >= 2) {
          this.autoRefreshInterval = Math.min(this.baseRefreshInterval * 2, 120000) // Max 2 minutes
          console.log(`Slowing refresh rate to ${this.autoRefreshInterval / 1000}s due to errors`)
        }
        
        // Don't clear data on auto-refresh failures
        if (!isAutoRefresh) {
          this.customers = []
          this.filteredCustomers = []
        }
      } finally {
        this.loading = false
        this.refreshProgress = ''
      }
    },

    async loadKPIData(isAutoRefresh = false) {
      try {
        // Load all KPI data in parallel for better performance
        const [activeResult, monthlyResult, dailyResult] = await Promise.allSettled([
          CustomerApiService.ActiveUser(),
          CustomerApiService.MonthlyUser(),
          CustomerApiService.DailyUser()
        ])
        
        // Handle Active Users
        if (activeResult.status === 'fulfilled') {
          const activeCustomers = activeResult.value.active_customers || []
          if (Array.isArray(activeCustomers)) {
            // Filter for customers only
            const customerUsers = activeCustomers.filter(user => user.role === 'customer')
            this.activeUsersCount = customerUsers.length.toString()
          } else {
            // If it's already a count, use it directly
            this.activeUsersCount = activeCustomers.toString() || '0'
          }
        } else {
          console.error('Failed to load active users:', activeResult.reason)
          this.activeUsersCount = 'Error'
        }
        
        // Handle Monthly Users
        if (monthlyResult.status === 'fulfilled') {
          const monthlyCustomers = monthlyResult.value.monthly_customers || []
          if (Array.isArray(monthlyCustomers)) {
            // Filter for customers only
            const customerUsers = monthlyCustomers.filter(user => user.role === 'customer')
            this.monthlyUsersCount = customerUsers.length.toString()
          } else {
            // If it's already a count, use it directly
            this.monthlyUsersCount = monthlyCustomers.toString() || '0'
          }
        } else {
          console.error('Failed to load monthly users:', monthlyResult.reason)
          this.monthlyUsersCount = 'Error'
        }
        
        // Handle Daily Users
        if (dailyResult.status === 'fulfilled') {
          const dailyCustomers = dailyResult.value.daily_customers || []
          if (Array.isArray(dailyCustomers)) {
            // Filter for customers only
            const customerUsers = dailyCustomers.filter(user => user.role === 'customer')
            this.dailyUsersCount = customerUsers.length.toString()
          } else {
            // If it's already a count, use it directly
            this.dailyUsersCount = dailyCustomers.toString() || '0'
          }
        } else {
          console.error('Failed to load daily users:', dailyResult.reason)
          this.dailyUsersCount = 'Error'
        }
        
        console.log(`✅ KPI data loading completed (${isAutoRefresh ? 'auto-refresh' : 'manual'})`)
        
      } catch (error) {
        console.error('❌ Error loading KPI data:', error)
        this.activeUsersCount = 'Error'
        this.monthlyUsersCount = 'Error'
        this.dailyUsersCount = 'Error'
      }
    },

    // Smart refresh rate adjustment based on activity
    trackActivityAndAdjustRefreshRate(newData, previousLength) {
      const now = Date.now()
      
      // Clean old activity data (older than 5 minutes)
      this.recentActivity = this.recentActivity.filter(
        activity => now - activity.timestamp < 300000
      )
      
      // Count recent activity (last 2 minutes)
      const recentCount = this.recentActivity.filter(
        activity => now - activity.timestamp < 120000
      ).length
      
      // Adjust refresh rate based on activity
      if (recentCount >= 10) {
        // High activity: refresh every 10 seconds
        this.autoRefreshInterval = 10000
        console.log('High activity detected: refresh rate increased to 10s')
      } else if (recentCount >= 5) {
        // Medium activity: refresh every 20 seconds
        this.autoRefreshInterval = 20000
        console.log('Medium activity detected: refresh rate set to 20s')
      } else if (recentCount === 0 && this.recentActivity.length === 0) {
        // No activity: refresh every 60 seconds
        this.autoRefreshInterval = 60000
        console.log('No activity detected: refresh rate decreased to 60s')
      } else {
        // Normal activity: use base interval
        this.autoRefreshInterval = this.baseRefreshInterval
      }
      
      // Restart auto-refresh with new interval if it's running
      if (this.autoRefreshEnabled && this.autoRefreshTimer) {
        this.startAutoRefresh()
      }
    },

    // Emergency reconnect method
    async emergencyReconnect() {
      console.log('Emergency reconnect initiated')
      this.consecutiveErrors = 0
      this.connectionLost = false
      await Promise.all([
        this.loadKPIData(false),
        this.fetchCustomers(false, true)
      ])
      
      // Restart auto-refresh if it was stopped
      if (!this.autoRefreshEnabled) {
        this.autoRefreshEnabled = true
        this.startAutoRefresh()
      }
    },

    // Connection status methods
    getConnectionStatus() {
      if (this.connectionLost) return 'connection-lost'
      if (this.consecutiveErrors > 0) return 'connection-unstable'
      if (this.lastSuccessfulLoad && (Date.now() - this.lastSuccessfulLoad < 60000)) return 'connection-good'
      return 'connection-unknown'
    },

    getConnectionIcon() {
      switch (this.getConnectionStatus()) {
        case 'connection-good': return 'bi bi-wifi text-success'
        case 'connection-unstable': return 'bi bi-wifi-1 text-warning'
        case 'connection-lost': return 'bi bi-wifi-off text-danger'
        default: return 'bi bi-wifi text-muted'
      }
    },

    getConnectionText() {
      switch (this.getConnectionStatus()) {
        case 'connection-good': return 'Connected'
        case 'connection-unstable': return 'Unstable'
        case 'connection-lost': return 'Connection Lost'
        default: return 'Connecting...'
      }
    },

    getDetailedErrorMessage(error) {
      if (error.name === 'NetworkError' || error.message.includes('fetch')) {
        return 'Network connection failed. Please check your internet connection and try again.'
      } else if (error.status === 401) {
        return 'Authentication failed. Please log in again.'
      } else if (error.status === 403) {
        return 'Access denied. You do not have permission to view customer data.'
      } else if (error.status === 500) {
        return 'Server error occurred. Please try again later.'
      }
      return `Failed to load customers: ${error.message || 'Unknown error occurred'}`
    },

    // ============ LOGS PAGE AUTO-REFRESH SYSTEM ============
    toggleAutoRefresh() {
      if (this.autoRefreshEnabled) {
        this.autoRefreshEnabled = false
        this.stopAutoRefresh()
        console.log('Auto-refresh disabled by user')
      } else {
        this.autoRefreshEnabled = true
        this.startAutoRefresh()
        console.log('Auto-refresh enabled by user')
      }
    },
    
    startAutoRefresh() {
      this.stopAutoRefresh() // Clear any existing timers
      
      // Start countdown
      this.countdown = this.autoRefreshInterval / 1000
      this.countdownTimer = setInterval(() => {
        this.countdown--
        if (this.countdown <= 0) {
          this.countdown = this.autoRefreshInterval / 1000
        }
      }, 1000)
      
      // Start auto-refresh timer
      this.autoRefreshTimer = setInterval(() => {
        Promise.all([
          this.loadKPIData(true),
          this.fetchCustomers(true)
        ])
      }, this.autoRefreshInterval)
      
      console.log(`Auto-refresh started (${this.autoRefreshInterval / 1000}s interval)`)
    },
    
    stopAutoRefresh() {
      if (this.autoRefreshTimer) {
        clearInterval(this.autoRefreshTimer)
        this.autoRefreshTimer = null
      }
      
      if (this.countdownTimer) {
        clearInterval(this.countdownTimer)
        this.countdownTimer = null
      }
      
      console.log('Auto-refresh stopped')
    },

    // ============ ENHANCED REFRESH SYSTEM ============
    async refreshData() {
      console.log('=== COMPREHENSIVE CUSTOMER DATA REFRESH INITIATED ===')
      
      // Clear any existing messages
      this.successMessage = null
      this.error = null
      
      // Preserve current customer selections and search state
      const currentSelections = [...this.selectedCustomers]
      const currentSearch = this.searchQuery
      
      console.log('Preserving current state:', {
        selections: currentSelections,
        search: currentSearch
      })
      
      try {
        // Set loading state
        this.loading = true
        this.refreshStartTime = Date.now()
        
        // Clear cache for fresh data
        if (this.cache.metadata.enabled) {
          this.cache.clear()
          console.log('🗑️ Cache cleared for fresh data')
        }
        
        // Simulate progress updates
        const progressInterval = setInterval(() => {
          if (!this.loading) {
            clearInterval(progressInterval)
            return
          }
          
          const elapsed = Date.now() - this.refreshStartTime
          if (elapsed < 1000) {
            this.refreshProgress = 'Refreshing KPI data...'
          } else if (elapsed < 2000) {
            this.refreshProgress = 'Processing customer data...'
          } else {
            this.refreshProgress = 'Finalizing data...'
          }
        }, 500)
        
        // Refresh both KPI and customer data in parallel
        await Promise.all([
          this.loadKPIData(false),
          this.fetchCustomers(false)
        ])
        
        // Clear progress interval
        clearInterval(progressInterval)
        
        // Restore user state
        this.selectedCustomers = currentSelections.filter(customerId => 
          this.customers.some(customer => 
            (customer._id === customerId) || (customer.customer_id === customerId)
          )
        )
        
        // Restore search and reapply search filter
        this.searchQuery = currentSearch
        this.handleSearch()
        
        // Show success message
        this.successMessage = `Data refreshed successfully! ${this.customers.length} customers and KPI metrics updated.`
        
        console.log('✅ Comprehensive refresh completed successfully')
        console.log('Final state:', {
          totalCustomers: this.customers.length,
          filteredCustomers: this.filteredCustomers.length,
          selectedCustomers: this.selectedCustomers.length
        })
        
        // Auto-clear success message
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
        
      } catch (error) {
        console.error('❌ Comprehensive refresh failed:', error)
        this.error = this.getDetailedErrorMessage(error)
      } finally {
        this.loading = false
        this.refreshProgress = ''
      }
    },

    // ============ CACHE MANAGEMENT METHODS ============
    formatCacheTime(timestamp) {
      if (!timestamp) return 'Never'
      
      const now = Date.now()
      const diff = now - timestamp
      const minutes = Math.floor(diff / 60000)
      const seconds = Math.floor((diff % 60000) / 1000)
      
      if (minutes > 0) {
        return `${minutes}m ${seconds}s ago`
      } else {
        return `${seconds}s ago`
      }
    },

    // ============ EXISTING METHODS (OPTIMIZED) ============
    handleSearch() {
      // Debounced search for better performance
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout)
      }
      
      this.searchTimeout = setTimeout(() => {
        this.performSearch()
      }, 300) // 300ms debounce
    },

    performSearch() {
      if (!this.searchQuery.trim()) {
        this.filteredCustomers = this.customers
        return
      }

      const query = this.searchQuery.toLowerCase()
      const startTime = performance.now()
      
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

      const endTime = performance.now()
      console.log(`🔍 Search completed in ${(endTime - startTime).toFixed(2)}ms`)
      
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
        
        // Clear cache and refresh for accurate data
        this.cache.clear()
        await this.fetchCustomers()
      } else {
        this.error = 'Failed to delete customers'
      }

      this.loading = false
      
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
        
        // Clear cache and refresh for accurate data
        this.cache.clear()
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
        username: '',
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
      this.clearValidation()
      this.showModal = true
    },

    editCustomer(customer) {
      this.isEditMode = true
      this.selectedCustomer = customer
      this.customerForm = {
        username: customer.username || '',
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
      this.clearValidation()
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
      this.clearValidation()
    },

    closeViewModal() {
      this.showViewModal = false
      this.selectedCustomer = null
    },

    async saveCustomer() {
      this.formLoading = true
      this.formError = null

      try {
        // Validate form before saving
        const isValid = this.validateForm()
        
        if (!isValid) {
          const errorMessages = Object.values(this.validationErrors)
          this.formError = errorMessages.join(', ')
          this.formLoading = false
          return
        }

        // Proceed with saving if validation passes
        if (this.isEditMode) {
          const customerId = this.selectedCustomer._id || this.selectedCustomer.customer_id
          await apiService.updateCustomer(customerId, this.customerForm)
          this.successMessage = `Customer "${this.customerForm.full_name}" updated successfully`
        } else {
          await apiService.createCustomer(this.customerForm)
          this.successMessage = `Customer "${this.customerForm.full_name}" created successfully`
        }

        this.closeModal()
        
        // Clear cache and refresh for accurate data
        this.cache.clear()
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
      this.exporting = true
      
      try {
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
      } finally {
        this.exporting = false
      }
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
    console.log('=== CUSTOMERS COMPONENT MOUNTED ===')
    
    // Load KPI data and customer data in parallel with caching
    await Promise.all([
      this.loadKPIData(),
      this.fetchCustomers()
    ])
    
    // Force scroll to top
    window.scrollTo(0, 0)
    
    this.$nextTick(() => {
      window.scrollTo(0, 0)
    })
    
    console.log('✅ Component initialization complete')
  },

  beforeUnmount() {
    // Clear any pending timeouts
    if (this.searchTimeout) {
      clearTimeout(this.searchTimeout)
    }
    
    console.log('🧹 Component cleanup complete')
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

/* Cache Status Indicator */
.refresh-indicator {
  margin-bottom: 1rem;
}

/* Enhanced Refresh Progress */

/* Enhanced table row states */
.customers-table tbody tr.refreshing {
  opacity: 0.7;
  transition: opacity 0.3s ease;
}

/* KPI Cards Container */
.kpi-cards-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.kpi-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.kpi-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  gap: 2rem;
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

.btn-info {
  background-color: #06b6d4;
  color: white;
}

.btn-info:hover:not(:disabled) {
  background-color: #0891b2;
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

.table-container {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.customers-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.customers-table thead {
  background-color: #567cdc;
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

/* Column width definitions */
.checkbox-column {
  width: 40px;
  text-align: center;
}

.id-column {
  width: 80px;
  font-weight: 500;
  color: #6366f1;
  font-family: monospace;
  text-align: center;
  font-size: 0.75rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.name-column {
  width: 150px;
  max-width: 150px;
  font-weight: 500;
  color: #1e293b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.email-column {
  width: 180px;
  max-width: 180px;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.phone-column {
  width: 120px;
  max-width: 120px;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.address-column {
  width: 200px;
  max-width: 200px;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.points-column {
  width: 100px;
  font-weight: 500;
  text-align: center;
  color: #1e293b;
}

.date-column {
  width: 120px;
  color: #64748b;
  font-size: 0.8125rem;
}

.actions-column {
  width: 140px;
  text-align: center;
  vertical-align: middle;
}

/* Action Button Styles */
.btn-xs {
  padding: 0.25rem 0.4rem;
  font-size: 0.75rem;
  line-height: 1;
  border-radius: 0.375rem;
}

.btn-icon-only {
  padding: 0.35rem;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 1px solid;
}

.btn-outline-secondary {
  color: #6b7280;
  border-color: #d1d5db;
  background-color: transparent;
}

.btn-outline-secondary:hover:not(:disabled) {
  color: #374151;
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

.btn-outline-primary {
  color: #3b82f6;
  border-color: #93c5fd;
  background-color: transparent;
}

.btn-outline-primary:hover:not(:disabled) {
  color: #ffffff;
  background-color: #3b82f6;
  border-color: #3b82f6;
}

.btn-outline-danger {
  color: #ef4444;
  border-color: #fca5a5;
  background-color: transparent;
}

.btn-outline-danger:hover:not(:disabled) {
  color: #ffffff;
  background-color: #ef4444;
  border-color: #ef4444;
}

.action-buttons {
  display: flex;
  gap: 0.375rem;
  justify-content: center;
  align-items: center;
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
  transition: all 0.2s ease;
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

/* Validation Styles */
.form-group input.error {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.form-group input.error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
}

.field-error {
  color: #ef4444;
  font-size: 0.75rem;
  margin-top: 0.25rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.field-error::before {
  content: "⚠";
  font-size: 0.875rem;
}

.validation-loading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0.5rem 0;
}

.validation-loading::before {
  content: "";
  width: 16px;
  height: 16px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.form-error {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  margin: 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-error::before {
  content: "❌";
  font-size: 1rem;
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

.form-actions button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #e5e7eb;
  color: #9ca3af;
}

.form-actions button.btn-primary {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.form-actions button.btn-primary:disabled {
  background-color: #e5e7eb;
  color: #9ca3af;
  border-color: #e5e7eb;
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
  color: #1e293b;
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
  
  .kpi-cards-container {
    grid-template-columns: 1fr;
    gap: 1rem;
    margin-bottom: 1.5rem;
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
}

@media (max-width: 768px) {
  .kpi-cards-container {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

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

  .field-error {
    font-size: 0.7rem;
  }
  
  .validation-loading {
    font-size: 0.8125rem;
  }
  
  .form-error {
    font-size: 0.8125rem;
    padding: 0.5rem;
  }
}

@media (max-width: 640px) {
  .kpi-cards-container {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .page-header {
    gap: 0.75rem;
  }

  .header-actions {
    grid-template-columns: repeat(2, 1fr);
    display: grid;
    gap: 0.5rem;
  }

  .btn {
    font-size: 0.75rem;
    padding: 0.5rem 0.75rem;
  }
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

.flex-grow-1 {
  flex-grow: 1 !important;
}

.gap-2 {
  gap: 0.5rem !important;
}

.me-2 {
  margin-right: 0.5rem !important;
}

.mt-1 {
  margin-top: 0.25rem !important;
}

.mt-3 {
  margin-top: 1rem !important;
}

.mb-3 {
  margin-bottom: 1rem !important;
}

.py-5 {
  padding-top: 3rem !important;
  padding-bottom: 3rem !important;
}

.text-center {
  text-align: center !important;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8125rem;
  border-radius: 0.25rem;
}

.btn-outline-secondary {
  color: #6c757d;
  border-color: #6c757d;
  background-color: transparent;
}

.btn-outline-secondary:hover:not(:disabled) {
  color: #fff;
  background-color: #6c757d;
  border-color: #6c757d;
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

.card {
  position: relative;
  display: flex;
  flex-direction: column;
  min-width: 0;
  word-wrap: break-word;
  background-color: #fff;
  background-clip: border-box;
  border: 1px solid rgba(0, 0, 0, 0.125);
  border-radius: 0.375rem;
}

.card-body {
  flex: 1 1 auto;
  padding: 1rem;
}
</style>