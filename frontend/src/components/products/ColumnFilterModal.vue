<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" @click="handleOverlayClick">
    <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content" @click.stop>
        <div class="modal-header bg-light">
          <div>
            <h5 class="modal-title text-primary-dark fw-semibold">Column Visibility</h5>
            <p class="text-tertiary-medium small mb-0">Customize which columns are visible in your table</p>
          </div>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>

        <div class="modal-body">
          <!-- Quick Actions -->
          <div class="d-flex gap-3 mb-4 pb-3 border-bottom">
            <button @click="selectAll" class="btn btn-primary btn-md">
              Show All
            </button>
            <button @click="selectNone" class="btn btn-secondary btn-md">
              Hide All
            </button>
            <button @click="resetToDefault" class="btn btn-info btn-md">
              Reset Default
            </button>
          </div>

          <!-- Column Groups -->
          <div class="column-groups">
            <!-- Essential Columns (Always Required) -->
            <div class="mb-4">
              <h6 class="d-flex align-items-center gap-2 mb-3 text-tertiary-dark fw-semibold">
                <svg class="text-primary" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <circle cx="12" cy="16" r="1"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                Essential Columns
                <small class="text-tertiary-medium fw-normal ms-2">(Always visible)</small>
              </h6>
              <div class="row g-3">
                <div 
                  v-for="column in essentialColumns" 
                  :key="column.key"
                  class="col-12 col-md-6"
                >
                  <div class="card border-tertiary-medium bg-tertiary-light opacity-75">
                    <div class="card-body p-3">
                      <div class="form-check">
                        <input 
                          class="form-check-input" 
                          type="checkbox" 
                          :id="`col-${column.key}`"
                          :checked="true"
                          disabled
                        />
                        <label class="form-check-label d-flex flex-column" :for="`col-${column.key}`">
                          <span class="fw-semibold text-tertiary-dark">{{ column.name }}</span>
                          <small class="text-tertiary-medium">{{ column.description }}</small>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Basic Information -->
            <div class="mb-4">
              <h6 class="d-flex align-items-center gap-2 mb-3 text-tertiary-dark fw-semibold">
                <svg class="text-primary" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14,2 14,8 20,8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10,9 9,9 8,9"/>
                </svg>
                Basic Information
              </h6>
              <div class="row g-3">
                <div 
                  v-for="column in basicColumns" 
                  :key="column.key"
                  class="col-12 col-md-6"
                >
                  <div class="card column-card" :class="{ 'border-primary bg-primary-light': visibleColumns[column.key] }">
                    <div class="card-body p-3">
                      <div class="form-check">
                        <input 
                          class="form-check-input" 
                          type="checkbox" 
                          :id="`col-${column.key}`"
                          v-model="visibleColumns[column.key]"
                          @change="updateColumnVisibility"
                        />
                        <label class="form-check-label d-flex flex-column" :for="`col-${column.key}`">
                          <span class="fw-semibold text-tertiary-dark">{{ column.name }}</span>
                          <small class="text-tertiary-medium">{{ column.description }}</small>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Financial Information -->
            <div class="mb-4">
              <h6 class="d-flex align-items-center gap-2 mb-3 text-tertiary-dark fw-semibold">
                <svg class="text-primary" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="1" x2="12" y2="23"/>
                  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                </svg>
                Financial Information
              </h6>
              <div class="row g-3">
                <div 
                  v-for="column in financialColumns" 
                  :key="column.key"
                  class="col-12 col-md-6"
                >
                  <div class="card column-card" :class="{ 'border-primary bg-primary-light': visibleColumns[column.key] }">
                    <div class="card-body p-3">
                      <div class="form-check">
                        <input 
                          class="form-check-input" 
                          type="checkbox" 
                          :id="`col-${column.key}`"
                          v-model="visibleColumns[column.key]"
                          @change="updateColumnVisibility"
                        />
                        <label class="form-check-label d-flex flex-column" :for="`col-${column.key}`">
                          <span class="fw-semibold text-tertiary-dark">{{ column.name }}</span>
                          <small class="text-tertiary-medium">{{ column.description }}</small>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Status & Dates -->
            <div class="mb-4">
              <h6 class="d-flex align-items-center gap-2 mb-3 text-tertiary-dark fw-semibold">
                <svg class="text-primary" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                  <line x1="16" y1="2" x2="16" y2="6"/>
                  <line x1="8" y1="2" x2="8" y2="6"/>
                  <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
                Status & Dates
              </h6>
              <div class="row g-3">
                <div 
                  v-for="column in statusColumns" 
                  :key="column.key"
                  class="col-12 col-md-6"
                >
                  <div class="card column-card" :class="{ 'border-primary bg-primary-light': visibleColumns[column.key] }">
                    <div class="card-body p-3">
                      <div class="form-check">
                        <input 
                          class="form-check-input" 
                          type="checkbox" 
                          :id="`col-${column.key}`"
                          v-model="visibleColumns[column.key]"
                          @change="updateColumnVisibility"
                        />
                        <label class="form-check-label d-flex flex-column" :for="`col-${column.key}`">
                          <span class="fw-semibold text-tertiary-dark">{{ column.name }}</span>
                          <small class="text-tertiary-medium">{{ column.description }}</small>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Summary -->
          <div class="mt-4 pt-4 border-top">
            <div class="card border-primary bg-primary-light">
              <div class="card-body">
                <h6 class="card-title text-primary-dark fw-semibold">Current Selection</h6>
                <p class="text-primary-dark small mb-3">
                  <strong>{{ visibleColumnCount }}</strong> of {{ totalColumns }} columns visible
                </p>
                <div class="d-flex flex-wrap gap-2">
                  <span 
                    v-for="columnKey in visibleColumnKeys" 
                    :key="columnKey"
                    class="badge bg-primary"
                  >
                    {{ getColumnName(columnKey) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer bg-light">
          <button @click="cancelChanges" class="btn btn-secondary btn-md">
            Cancel
          </button>
          <button @click="applyChanges" class="btn btn-primary btn-md">
            Apply Changes
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ColumnFilterModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    currentVisibleColumns: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'apply'],
  data() {
    return {
      visibleColumns: {},
      originalColumns: {},
      
      // Essential columns (always visible)
      essentialColumns: [
        {
          key: 'checkbox',
          name: 'Selection',
          description: 'Select multiple items'
        },
        {
          key: 'productName',
          name: 'Product Name',
          description: 'Primary product identifier'
        },
        {
          key: 'actions',
          name: 'Actions',
          description: 'Edit, view, delete options'
        }
      ],
      
      // Basic information columns
      basicColumns: [
        {
          key: 'id',
          name: 'Product ID',
          description: 'Unique product identifier'
        },
        {
          key: 'sku',
          name: 'SKU',
          description: 'Stock keeping unit code'
        },
        {
          key: 'category',
          name: 'Category',
          description: 'Product category'
        },
        {
          key: 'stock',
          name: 'Stock Level',
          description: 'Current inventory count'
        }
      ],
      
      // Financial information columns
      financialColumns: [
        {
          key: 'costPrice',
          name: 'Cost Price',
          description: 'Purchase cost per unit'
        },
        {
          key: 'sellingPrice',
          name: 'Selling Price',
          description: 'Retail price per unit'
        }
      ],
      
      // Status and date columns
      statusColumns: [
        {
          key: 'status',
          name: 'Status',
          description: 'Active/inactive state'
        },
        {
          key: 'expiryDate',
          name: 'Expiry Date',
          description: 'Product expiration date'
        }
      ]
    }
  },
  computed: {
    allColumns() {
      return [
        ...this.essentialColumns,
        ...this.basicColumns,
        ...this.financialColumns,
        ...this.statusColumns
      ]
    },
    totalColumns() {
      return this.basicColumns.length + this.financialColumns.length + this.statusColumns.length
    },
    visibleColumnCount() {
      return Object.values(this.visibleColumns).filter(visible => visible).length
    },
    visibleColumnKeys() {
      return Object.keys(this.visibleColumns).filter(key => this.visibleColumns[key])
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        this.initializeColumns()
        // Add Bootstrap modal backdrop
        document.body.classList.add('modal-open')
      } else {
        document.body.classList.remove('modal-open')
      }
    },
    currentVisibleColumns: {
      handler() {
        if (this.show) {
          this.initializeColumns()
        }
      },
      deep: true
    }
  },
  methods: {
    handleOverlayClick(e) {
      if (e.target.classList.contains('modal')) {
        this.$emit('close')
      }
    },
    
    initializeColumns() {
      // Create a copy of current visible columns
      this.visibleColumns = { ...this.currentVisibleColumns }
      this.originalColumns = { ...this.currentVisibleColumns }
    },
    
    updateColumnVisibility() {
      // This method is called when any checkbox changes
      // Could add validation here if needed
    },
    
    selectAll() {
      this.basicColumns.forEach(col => {
        this.visibleColumns[col.key] = true
      })
      this.financialColumns.forEach(col => {
        this.visibleColumns[col.key] = true
      })
      this.statusColumns.forEach(col => {
        this.visibleColumns[col.key] = true
      })
    },
    
    selectNone() {
      this.basicColumns.forEach(col => {
        this.visibleColumns[col.key] = false
      })
      this.financialColumns.forEach(col => {
        this.visibleColumns[col.key] = false
      })
      this.statusColumns.forEach(col => {
        this.visibleColumns[col.key] = false
      })
    },
    
    resetToDefault() {
      // Default visible columns
      const defaultColumns = {
        id: false,
        sku: true,
        category: true,
        stock: true,
        costPrice: false,
        sellingPrice: true,
        status: true,
        expiryDate: true
      }
      
      this.visibleColumns = { ...defaultColumns }
    },
    
    getColumnName(columnKey) {
      const column = this.allColumns.find(col => col.key === columnKey)
      return column ? column.name : columnKey
    },
    
    cancelChanges() {
      this.visibleColumns = { ...this.originalColumns }
      this.$emit('close')
    },
    
    applyChanges() {
      this.$emit('apply', { ...this.visibleColumns })
      this.$emit('close')
    }
  },
  
  mounted() {
    this.handleEscape = (e) => {
      if (e.key === 'Escape' && this.show) {
        this.cancelChanges()
      }
    }
    
    document.addEventListener('keydown', this.handleEscape)
  },

  beforeUnmount() {
    if (this.handleEscape) {
      document.removeEventListener('keydown', this.handleEscape)
    }
    // Clean up modal state
    document.body.classList.remove('modal-open')
  }
}
</script>

<style scoped>
/* Override Bootstrap modal background */
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

/* Custom styles for color variables */
.text-primary-dark {
  color: var(--primary-dark) !important;
}

.text-tertiary-medium {
  color: var(--tertiary-medium) !important;
}

.text-tertiary-dark {
  color: var(--tertiary-dark) !important;
}

.bg-primary-light {
  background-color: var(--primary-light) !important;
}

.bg-tertiary-light {
  background-color: var(--tertiary-light) !important;
}

.border-primary {
  border-color: var(--primary) !important;
}

.border-tertiary-medium {
  border-color: var(--tertiary-medium) !important;
}

.text-primary {
  color: var(--primary) !important;
}

.bg-primary {
  background-color: var(--primary) !important;
}

/* Column card hover effects */
.column-card {
  background-color: var(--neutral-light);
  border: 2px solid var(--neutral);
  transition: all 0.2s ease;
  cursor: pointer;
}

.column-card:hover {
  border-color: var(--primary-light);
  background-color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(115, 146, 226, 0.1);
}

/* Custom form check styling to match design */
.form-check {
  padding-left: 2rem;
}

.form-check-input {
  width: 1.125rem;
  height: 1.125rem;
  margin-top: 0.125rem;
  border-color: var(--neutral-dark);
}

.form-check-input:checked {
  background-color: var(--primary);
  border-color: var(--primary);
}

.form-check-input:focus {
  border-color: var(--primary-light);
  box-shadow: 0 0 0 0.2rem rgba(115, 146, 226, 0.25);
}

.form-check-label {
  cursor: pointer;
}

/* Badge customization */
.badge {
  font-weight: 500;
  padding: 0.375rem 0.625rem;
}

/* Modal customizations */
.modal-dialog {
  max-width: 800px;
}

.modal-content {
  border: none;
  border-radius: 0.75rem;
  overflow: hidden;
}

.modal-header,
.modal-footer {
  border-color: var(--neutral);
}

.modal-header {
  background-color: var(--neutral-light);
}

.modal-footer {
  background-color: var(--neutral-light);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .modal-dialog {
    margin: 0.5rem;
  }
  
  .btn {
    width: 100%;
  }
  
  .modal-footer {
    flex-direction: column-reverse;
    gap: 0.5rem;
  }
  
  .d-flex.gap-3 {
    flex-direction: column;
  }
}

/* Animation for modal appearance */
.modal.show {
  animation: fadeIn 0.3s ease;
}

.modal-dialog {
  animation: slideIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { 
    transform: translate(0, -20px) scale(0.95);
    opacity: 0;
  }
  to { 
    transform: translate(0, 0) scale(1);
    opacity: 1;
  }
}
</style>