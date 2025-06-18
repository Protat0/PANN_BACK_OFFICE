<template>
  <div class="promotions">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">Promotions</h1>
      <div class="header-actions">
        <button 
          class="btn btn-secondary" 
          @click="handleDelete" 
          :disabled="selectedRows.length === 0"
        >
          Delete Selected ({{ selectedRows.length }})
        </button>
        <button class="btn btn-success" @click="handleAddPromo">
          Add Promo
        </button>
        <button class="btn btn-primary" @click="handleExport">
          Export
        </button>
        <button class="btn btn-info" @click="handleRefresh">
          Refresh
        </button>
      </div>
    </div>

    <!-- Promotions Table using DataTable component -->
    <DataTable>
      <template #header>
        <tr>
          <th class="checkbox-header">
            <input 
              type="checkbox" 
              class="table-checkbox" 
              @change="handleSelectAll"
              v-model="selectAll"
            >
          </th>
          <th>ID</th>
          <th>Name</th>
          <th>Discount Type</th>
          <th>Discount Value</th>
          <th>Products</th>
          <th>Start Date</th>
          <th>End Date</th>
          <th>Actions</th>
        </tr>
      </template>

      <template #body>
        <tr 
          v-for="(promo, index) in promotions" 
          :key="promo.id"
          :class="{ 'selected': selectedRows.includes(promo.id) }"
        >
          <td class="checkbox-cell">
            <input 
              type="checkbox" 
              class="table-checkbox" 
              :value="promo.id"
              v-model="selectedRows"
            >
          </td>
          <td class="id-cell">{{ promo.id }}</td>
          <td class="name-cell">{{ promo.name }}</td>
          <td class="discount-type-cell">
            <span class="badge badge-discount-type" :class="getDiscountTypeClass(promo.discountType)">
              {{ promo.discountType }}
            </span>
          </td>
          <td class="discount-value-cell">{{ promo.discountValue }}</td>
          <td class="products-cell">
            <span class="badge badge-products" :class="getProductsClass(promo.products)">
              {{ promo.products }}
            </span>
          </td>
          <td class="date-cell">{{ formatDate(promo.startDate) }}</td>
          <td class="date-cell">{{ formatDate(promo.endDate) }}</td>
          <td class="actions-cell">
            <div class="action-buttons">
              <button class="action-btn edit-btn" @click="handleEdit(promo)" title="Edit">
                ✏️
              </button>
              <button class="action-btn view-btn" @click="handleView(promo)" title="View">
                👁️
              </button>
              <button class="action-btn lock-btn" @click="handleToggleStatus(promo)" :title="promo.status === 'active' ? 'Deactivate' : 'Activate'">
                {{ promo.status === 'active' ? '🔒' : '🔓' }}
              </button>
              <button class="action-btn delete-btn" @click="handleDeleteSingle(promo)" title="Delete">
                🗑️
              </button>
            </div>
          </td>
        </tr>
      </template>
    </DataTable>
  </div>
</template>

<script>
import DataTable from '../components/TableTemplate.vue'

export default {
  name: 'Promotions',
  components: {
    DataTable
  },
  data() {
    return {
      selectAll: false,
      selectedRows: [],
              promotions: [
        {
          id: '0001',
          name: 'Valentines Day',
          discountType: 'All Items',
          discountValue: '14%',
          products: 'All',
          startDate: '2025-02-12T00:00:00Z',
          endDate: '2025-02-16T00:00:00Z',
          status: 'active'
        },
        {
          id: '0002',
          name: 'Mid Month (Jan)',
          discountType: 'Selected Items',
          discountValue: '5%',
          products: 'Noodles',
          startDate: '2025-01-15T00:00:00Z',
          endDate: '2025-01-17T00:00:00Z',
          status: 'active'
        },
        {
          id: '0003',
          name: 'Sweldo Sale (Jan)',
          discountType: 'Selected Items',
          discountValue: '10%',
          products: 'Snacks',
          startDate: '2025-01-28T00:00:00Z',
          endDate: '2025-01-30T00:00:00Z',
          status: 'inactive'
        },
        {
          id: '0004',
          name: 'Sinulog Sale',
          discountType: 'All',
          discountValue: '10%',
          products: 'All',
          startDate: '2025-01-21T00:00:00Z',
          endDate: '2025-01-21T23:59:59.999Z',
          status: 'active'
        },
        {
          id: '0005',
          name: 'Mid Month (Feb)',
          discountType: 'Selected Items',
          discountValue: '5%',
          products: 'Noodles',
          startDate: '2025-02-15T00:00:00Z',
          endDate: '2025-02-17T00:00:00Z',
          status: 'active'
        },
        {
          id: '0006',
          name: 'Sweldo Sale (Feb)',
          discountType: 'Selected Items',
          discountValue: '10%',
          products: 'Noodles',
          startDate: '2025-02-28T00:00:00Z',
          endDate: '2025-02-28T00:00:00Z',
          status: 'inactive'
        },
        {
          id: '0007',
          name: 'People Power',
          discountType: 'All',
          discountValue: '25%',
          products: 'All',
          startDate: '2025-02-25T00:00:00Z',
          endDate: '2025-02-25T23:59:59.999Z',
          status: 'active'
        },
        {
          id: '0008',
          name: 'Mid Month (Mar)',
          discountType: 'Selected Items',
          discountValue: '5%',
          products: 'Noodles',
          startDate: '2025-03-15T00:00:00Z',
          endDate: '2025-03-17T00:00:00Z',
          status: 'active'
        },
        {
          id: '0009',
          name: 'Sweldo Sale (Mar)',
          discountType: 'Selected Items',
          discountValue: '10%',
          products: 'Noodles',
          startDate: '2025-03-28T00:00:00Z',
          endDate: '2025-03-31T00:00:00Z',
          status: 'active'
        }
      ]
    }
  },
  methods: {
    handleAddPromo() {
      console.log('Add promo clicked')
      // Add modal or navigation logic here
    },
    
    handleDelete() {
      if (this.selectedRows.length === 0) {
        alert('Please select promotions to delete')
        return
      }
      
      // Remove selected promotions from array
      this.promotions = this.promotions.filter(promo => !this.selectedRows.includes(promo.id))
      this.selectedRows = []
      this.selectAll = false
      
      console.log('Deleted promotions')
    },
    
    handleExport() {
      console.log('Export clicked')
      // Add export logic here
    },
    
    handleSelectAll(event) {
      this.selectAll = event.target.checked
      if (this.selectAll) {
        this.selectedRows = this.promotions.map(promo => promo.id)
      } else {
        this.selectedRows = []
      }
    },
    
    handleRowAction(promo) {
      console.log('Row action clicked for:', promo)
      // Add edit/delete/view logic here
    },

    handleEdit(promo) {
      console.log('Edit promo:', promo)
      // Add edit modal logic here
    },

    handleView(promo) {
      console.log('View promo:', promo)
      // Add view modal logic here
    },

    handleToggleStatus(promo) {
      const newStatus = promo.status === 'active' ? 'inactive' : 'active'
      const action = newStatus === 'active' ? 'activate' : 'deactivate'
      
      if (confirm(`Are you sure you want to ${action} "${promo.name}"?`)) {
        // Update status in the array
        const index = this.promotions.findIndex(p => p.id === promo.id)
        if (index !== -1) {
          this.promotions[index].status = newStatus
        }
        console.log(`${action}d promotion:`, promo)
      }
    },

    handleDeleteSingle(promo) {
      if (confirm(`Are you sure you want to delete "${promo.name}"?`)) {
        this.promotions = this.promotions.filter(p => p.id !== promo.id)
        console.log('Deleted single promo:', promo)
      }
    },

    getDiscountTypeClass(discountType) {
      switch (discountType) {
        case 'All Items':
          return 'badge-all-items'
        case 'Selected Items':
          return 'badge-selected-items'
        case 'All':
          return 'badge-all'
        default:
          return 'badge-default'
      }
    },

    getProductsClass(products) {
      switch (products) {
        case 'All':
          return 'badge-products-all'
        case 'Noodles':
          return 'badge-products-noodles'
        case 'Snacks':
          return 'badge-products-snacks'
        default:
          return 'badge-products-default'
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Never'
      
      try {
        const date = new Date(dateString)
        
        if (isNaN(date.getTime())) {
          return 'Invalid Date'
        }
        
        // Format like: 06/12/2025, 09:51 AM
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const year = date.getFullYear()
        
        let hours = date.getHours()
        const minutes = String(date.getMinutes()).padStart(2, '0')
        const ampm = hours >= 12 ? 'PM' : 'AM'
        
        hours = hours % 12
        hours = hours ? hours : 12 // 0 should be 12
        const formattedHours = String(hours).padStart(2, '0')
        
        return `${month}/${day}/${year},\n${formattedHours}:${minutes} ${ampm}`
      } catch (error) {
        console.error('Error formatting date:', error)
        return 'Invalid Date'
      }
    },
  }
}
</script>

<style scoped>
.promotions {
  padding: 0;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  background-color: transparent;
  border: none;
  padding: 0;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.btn {
  padding: 0.5rem 1.25rem;
  border-radius: 0.5rem;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
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

.btn-info {
  background-color: #06b6d4;
  color: white;
}

.btn-info:hover:not(:disabled) {
  background-color: #0891b2;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Table Cell Specific Styles */
.checkbox-header {
  width: 48px;
  text-align: center;
}

.checkbox-cell {
  text-align: center;
}

.id-cell {
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
  color: #3b82f6;
  font-size: 0.8125rem;
  font-weight: 600;
}

.name-cell {
  font-weight: 600;
  color: #111827;
}

.discount-type-cell,
.products-cell {
  padding: 0.75rem 1rem;
}

.discount-value-cell {
  font-weight: 600;
  color: #059669;
  font-size: 1rem;
}

.date-cell {
  color: #6b7280;
  font-size: 0.8125rem;
  line-height: 1.4;
  white-space: pre-line;
}

.actions-cell {
  text-align: center;
  width: 140px;
}

/* Badge Styles */
.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

/* Discount Type Badges */
.badge-discount-type {
  color: white;
}

.badge-all-items {
  background-color: #10b981;
}

.badge-selected-items {
  background-color: #3b82f6;
}

.badge-all {
  background-color: #8b5cf6;
}

.badge-default {
  background-color: #6b7280;
}

/* Products Badges */
.badge-products {
  color: white;
}

.badge-products-all {
  background-color: #f59e0b;
}

.badge-products-noodles {
  background-color: #ef4444;
}

.badge-products-snacks {
  background-color: #06b6d4;
}

.badge-products-default {
  background-color: #6b7280;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
  font-size: 1rem;
}

.action-btn:hover {
  background-color: #e2e8f0;
}

.action-btn.delete-btn:hover {
  background-color: #fee2e2;
}

/* Form Elements */
.table-checkbox {
  width: 1rem;
  height: 1rem;
  color: #3b82f6;
  border-color: #d1d5db;
  border-radius: 0.25rem;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .promotions {
    padding: 1rem;
  }
}

@media (max-width: 900px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .page-title {
    font-size: 1.5rem;
    text-align: center;
  }
}

@media (max-width: 768px) {
  .promotions {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.8125rem;
  }
}
</style>