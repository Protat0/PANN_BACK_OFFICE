<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <div class="header-info">
          <h2>Column Visibility</h2>
          <p class="header-subtitle">Customize which columns are visible in your table</p>
        </div>
        <button class="close-btn" @click="$emit('close')">
          ✕
        </button>
      </div>

      <div class="modal-body">
        <!-- Quick Actions -->
        <div class="quick-actions">
          <button @click="selectAll" class="btn btn-primary">
            Show All
          </button>
          <button @click="selectNone" class="btn btn-secondary">
            Hide All
          </button>
          <button @click="resetToDefault" class="btn btn-info">
            Reset Default
          </button>
        </div>

        <!-- Column Groups -->
        <div class="column-groups">
          <!-- Essential Columns (Always Required) -->
          <div class="column-group">
            <h3 class="group-title">
              <svg class="group-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <circle cx="12" cy="16" r="1"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              Essential Columns
              <small>(Always visible)</small>
            </h3>
            <div class="columns-grid">
              <div 
                v-for="column in essentialColumns" 
                :key="column.key"
                class="column-item essential"
              >
                <div class="column-checkbox">
                  <input 
                    type="checkbox" 
                    :id="`col-${column.key}`"
                    :checked="true"
                    disabled
                  />
                  <label :for="`col-${column.key}`" class="column-label">
                    <div class="column-info">
                      <span class="column-name">{{ column.name }}</span>
                      <span class="column-description">{{ column.description }}</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Basic Information -->
          <div class="column-group">
            <h3 class="group-title">
              <svg class="group-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14,2 14,8 20,8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10,9 9,9 8,9"/>
              </svg>
              Basic Information
            </h3>
            <div class="columns-grid">
              <div 
                v-for="column in basicColumns" 
                :key="column.key"
                class="column-item"
                :class="{ active: visibleColumns[column.key] }"
              >
                <div class="column-checkbox">
                  <input 
                    type="checkbox" 
                    :id="`col-${column.key}`"
                    v-model="visibleColumns[column.key]"
                    @change="updateColumnVisibility"
                  />
                  <label :for="`col-${column.key}`" class="column-label">
                    <div class="column-info">
                      <span class="column-name">{{ column.name }}</span>
                      <span class="column-description">{{ column.description }}</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Financial Information -->
          <div class="column-group">
            <h3 class="group-title">
              <svg class="group-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="1" x2="12" y2="23"/>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              </svg>
              Financial Information
            </h3>
            <div class="columns-grid">
              <div 
                v-for="column in financialColumns" 
                :key="column.key"
                class="column-item"
                :class="{ active: visibleColumns[column.key] }"
              >
                <div class="column-checkbox">
                  <input 
                    type="checkbox" 
                    :id="`col-${column.key}`"
                    v-model="visibleColumns[column.key]"
                    @change="updateColumnVisibility"
                  />
                  <label :for="`col-${column.key}`" class="column-label">
                    <div class="column-info">
                      <span class="column-name">{{ column.name }}</span>
                      <span class="column-description">{{ column.description }}</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Status & Dates -->
          <div class="column-group">
            <h3 class="group-title">
              <svg class="group-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
              Status & Dates
            </h3>
            <div class="columns-grid">
              <div 
                v-for="column in statusColumns" 
                :key="column.key"
                class="column-item"
                :class="{ active: visibleColumns[column.key] }"
              >
                <div class="column-checkbox">
                  <input 
                    type="checkbox" 
                    :id="`col-${column.key}`"
                    v-model="visibleColumns[column.key]"
                    @change="updateColumnVisibility"
                  />
                  <label :for="`col-${column.key}`" class="column-label">
                    <div class="column-info">
                      <span class="column-name">{{ column.name }}</span>
                      <span class="column-description">{{ column.description }}</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Summary -->
        <div class="summary-section">
          <div class="summary-card">
            <h4>Current Selection</h4>
            <p>
              <strong>{{ visibleColumnCount }}</strong> of {{ totalColumns }} columns visible
            </p>
            <div class="visible-columns-list">
              <span 
                v-for="columnKey in visibleColumnKeys" 
                :key="columnKey"
                class="column-tag"
              >
                {{ getColumnName(columnKey) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="cancelChanges" class="btn btn-secondary">
          Cancel
        </button>
        <button @click="applyChanges" class="btn btn-primary">
          Apply Changes
        </button>
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
    handleOverlayClick() {
      this.$emit('close')
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
  }
}
</script>

<style scoped>
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
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 800px;
  width: 95%;
  max-height: 90vh;
  overflow: hidden;
  animation: slideIn 0.3s ease;
  display: flex;
  flex-direction: column;
}

@keyframes slideIn {
  from { 
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to { 
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--neutral);
  background: var(--neutral-light);
  border-radius: 12px 12px 0 0;
}

.header-info h2 {
  margin: 0 0 0.5rem 0;
  color: var(--primary-dark);
  font-size: 1.5rem;
  font-weight: 600;
}

.header-subtitle {
  margin: 0;
  color: var(--tertiary-medium);
  font-size: 0.875rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--tertiary-medium);
  padding: 0.25rem;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background-color: var(--neutral-medium);
  color: var(--tertiary-dark);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
}

.quick-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--neutral);
}

.column-groups {
  margin-bottom: 2rem;
}

.column-group {
  margin-bottom: 2rem;
}

.group-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--tertiary-dark);
}

.group-title small {
  font-size: 0.75rem;
  color: var(--tertiary-medium);
  font-weight: 400;
  margin-left: 0.5rem;
}

.group-icon {
  width: 18px;
  height: 18px;
  color: var(--primary);
  stroke-width: 1.5;
}

.columns-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.column-item {
  background: var(--neutral-light);
  border: 2px solid var(--neutral);
  border-radius: 0.75rem;
  padding: 1rem;
  transition: all 0.2s ease;
  cursor: pointer;
}

.column-item:hover {
  border-color: var(--primary-light);
  background: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(115, 146, 226, 0.1);
}

.column-item.active {
  border-color: var(--primary);
  background: var(--primary-light);
}

.column-item.essential {
  border-color: var(--tertiary-medium);
  background: var(--tertiary-light);
  opacity: 0.7;
  cursor: not-allowed;
}

.column-item.essential:hover {
  transform: none;
  box-shadow: none;
}

.column-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.column-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--primary);
  cursor: pointer;
  margin-top: 0.125rem;
}

.column-checkbox input[type="checkbox"]:disabled {
  cursor: not-allowed;
}

.column-label {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
  flex: 1;
}

.column-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.column-name {
  font-weight: 600;
  color: var(--tertiary-dark);
  font-size: 0.9375rem;
}

.column-description {
  font-size: 0.8125rem;
  color: var(--tertiary-medium);
  line-height: 1.4;
}

.summary-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--neutral);
}

.summary-card {
  background: var(--primary-light);
  border: 1px solid var(--primary);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.summary-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--primary-dark);
  font-size: 1rem;
  font-weight: 600;
}

.summary-card p {
  margin: 0 0 1rem 0;
  color: var(--primary-dark);
  font-size: 0.875rem;
}

.visible-columns-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.column-tag {
  background: var(--primary);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1.5rem 2rem;
  border-top: 1px solid var(--neutral);
  background: var(--neutral-light);
  border-radius: 0 0 12px 12px;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background-color: var(--primary);
  color: white;
}

.btn-primary:hover {
  background-color: var(--primary-dark);
  transform: translateY(-1px);
}

.btn-secondary {
  background-color: var(--neutral-medium);
  color: var(--tertiary-dark);
  border: 1px solid var(--neutral-dark);
}

.btn-secondary:hover {
  background-color: var(--neutral-dark);
}

.btn-info {
  background-color: var(--info);
  color: white;
}

.btn-info:hover {
  background-color: var(--info-dark);
}

/* Responsive Design */
@media (max-width: 768px) {
  .modal-content {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }

  .modal-header {
    padding: 1rem 1.5rem;
  }

  .modal-body {
    padding: 1rem 1.5rem;
  }

  .quick-actions {
    flex-direction: column;
  }

  .columns-grid {
    grid-template-columns: 1fr;
  }

  .modal-footer {
    padding: 1rem 1.5rem;
    flex-direction: column-reverse;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}

/* Custom scrollbar */
.modal-body::-webkit-scrollbar {
  width: 8px;
}

.modal-body::-webkit-scrollbar-track {
  background: var(--neutral-light);
  border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: var(--neutral-medium);
  border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: var(--neutral-dark);
}
</style>