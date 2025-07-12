<template>
  <div class="table-container">
    <div class="table-responsive">
      <table class="table table-hover data-table">
        <thead class="table-header table-header-sticky">
          <slot name="header"></slot>
        </thead>
        <tbody>
          <slot name="body"></slot>
        </tbody>
      </table>
    </div>
    
    <!-- Add this pagination section -->
    <div v-if="showPagination && totalPages > 1" class="pagination-container">
      <div class="d-flex justify-content-between align-items-center">
        <div class="pagination-info">
          <small style="color: var(--tertiary-medium);">
            Showing {{ startItem }}-{{ endItem }} of {{ totalItems }} items
          </small>
        </div>
        
        <nav aria-label="Table pagination">
          <ul class="pagination pagination-sm mb-0">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <button 
                class="page-link page-link-icon" 
                @click="previousPage" 
                :disabled="currentPage === 1"
                aria-label="Previous page"
              >
                <ChevronLeft :size="16" />
              </button>
            </li>
            
            <li 
              v-for="page in totalPages" 
              :key="page"
              class="page-item" 
              :class="{ active: page === currentPage }"
            >
              <button class="page-link" @click="goToPage(page)">
                {{ page }}
              </button>
            </li>
            
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <button 
                class="page-link page-link-icon" 
                @click="nextPage" 
                :disabled="currentPage === totalPages"
                aria-label="Next page"
              >
                <ChevronRight :size="16" />
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </div>
</template>

<script>
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

export default {
  name: 'DataTable',
  components: {
    ChevronLeft,
    ChevronRight
  },

  props: {
    // Pagination props
    itemsPerPage: {
      type: Number,
      default: 10
    },
    showPagination: {
      type: Boolean,
      default: true
    },
    totalItems: {
      type: Number,
      default: 0
    },
    currentPage: {
      type: Number,
      default: 1
    }
  },
  emits: ['page-changed'],
  computed: {
    totalPages() {
      return Math.ceil(this.totalItems / this.itemsPerPage)
    },
    startItem() {
      return (this.currentPage - 1) * this.itemsPerPage + 1
    },
    endItem() {
      return Math.min(this.currentPage * this.itemsPerPage, this.totalItems)
    }
  },
  methods: {

    handleScroll(event) {
      const scrollTop = event.target.scrollTop
      const tableContainer = event.target
      
      if (scrollTop > 0) {
        tableContainer.classList.add('scrolled')
      } else {
        tableContainer.classList.remove('scrolled')
      }
    },

    goToPage(page) {

      console.log('goToPage called with:', page) // Add debug
      console.log('Current page:', this.currentPage) // Add debug
      console.log('Total pages:', this.totalPages) // Add debug

      if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
        console.log('Emitting page-changed event') 
        this.$emit('page-changed', page)
      }
    },
    previousPage() {
      this.goToPage(this.currentPage - 1)
    },
    nextPage() {
      this.goToPage(this.currentPage + 1)
    }
  }
}
</script>

<style scoped>
.table-container {
  background: white;
  border-radius: 0.75rem;
  /* Much harder drop shadow on all sides */
  box-shadow: 
    0 20px 25px -5px rgba(0, 0, 0, 0.25),
    0 10px 10px -5px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.table-responsive {
  border-radius: 0.75rem;
}

.data-table {
  margin-bottom: 0;
  border-collapse: separate;
  border-spacing: 0;
}

/* Header Styling */
.table-header {
  background-color: var(--primary-medium) !important;
  color: white !important;
}

.data-table :deep(.table-header th) {
  padding: 1rem;
  font-weight: 600;
  font-size: 0.875rem;
  letter-spacing: 0.025em;
  border: none !important;
  color: white !important;
  text-transform: uppercase;
  position: relative;
  background-color: var(--primary-medium) !important;
}

.data-table :deep(.table-header th:first-child) {
  border-top-left-radius: 0.75rem;
}

.data-table :deep(.table-header th:last-child) {
  border-top-right-radius: 0.75rem;
}

/* Body Styling */
.data-table :deep(tbody td) {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--neutral-light);
  font-size: 0.875rem;
  color: var(--tertiary-dark);
  vertical-align: middle;
}

.data-table :deep(tbody tr:last-child td) {
  border-bottom: none;
}

.data-table :deep(tbody tr:hover) {
  background-color: var(--neutral-light);
}

.data-table :deep(tbody tr.table-primary) {
  background-color: var(--primary-light);
}

.data-table :deep(tbody tr.text-muted) {
  opacity: 0.6;
}

/* Action Button Base Styles */
.data-table :deep(.action-btn) {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  border-width: 1.5px;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
  padding: 0;
  margin: 0 1px;
  /* Harder drop shadow for action buttons */
  box-shadow: 0 3px 6px 0 rgba(0, 0, 0, 0.12);
}

.data-table :deep(.action-btn:hover) {
  transform: translateY(-2px);
  /* Much harder shadow on hover */
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.25);
}

.data-table :deep(.action-btn:active) {
  transform: translateY(0);
}

.data-table :deep(.action-btn svg) {
  transition: transform 0.2s ease;
}

.data-table :deep(.action-btn:hover svg) {
  transform: scale(1.1);
}

/* Action Button Color Overrides using colors.css */
.data-table :deep(.action-btn-edit) {
  --bs-btn-color: var(--secondary);
  --bs-btn-border-color: var(--secondary);
  --bs-btn-hover-color: var(--secondary-dark);
  --bs-btn-hover-bg: var(--secondary-light);
  --bs-btn-hover-border-color: var(--secondary-dark);
  --bs-btn-active-color: var(--secondary-dark);
  --bs-btn-active-bg: var(--secondary-medium);
  --bs-btn-active-border-color: var(--secondary-dark);
}

.data-table :deep(.action-btn-view) {
  --bs-btn-color: var(--primary);
  --bs-btn-border-color: var(--primary);
  --bs-btn-hover-color: var(--primary-dark);
  --bs-btn-hover-bg: var(--primary-light);
  --bs-btn-hover-border-color: var(--primary-dark);
  --bs-btn-active-color: var(--primary-dark);
  --bs-btn-active-bg: var(--primary-medium);
  --bs-btn-active-border-color: var(--primary-dark);
}

.data-table :deep(.action-btn-stock) {
  --bs-btn-color: var(--info);
  --bs-btn-border-color: var(--info);
  --bs-btn-hover-color: var(--info-dark);
  --bs-btn-hover-bg: var(--info-light);
  --bs-btn-hover-border-color: var(--info-dark);
  --bs-btn-active-color: var(--info-dark);
  --bs-btn-active-bg: var(--info-medium);
  --bs-btn-active-border-color: var(--info-dark);
}

.data-table :deep(.action-btn-status) {
  --bs-btn-color: var(--success);
  --bs-btn-border-color: var(--success);
  --bs-btn-hover-color: var(--success-dark);
  --bs-btn-hover-bg: var(--success-light);
  --bs-btn-hover-border-color: var(--success-dark);
  --bs-btn-active-color: var(--success-dark);
  --bs-btn-active-bg: var(--success-medium);
  --bs-btn-active-border-color: var(--success-dark);
}

.data-table :deep(.action-btn-status-inactive) {
  --bs-btn-color: var(--tertiary-medium);
  --bs-btn-border-color: var(--tertiary-medium);
  --bs-btn-hover-color: var(--tertiary-dark);
  --bs-btn-hover-bg: var(--neutral-medium);
  --bs-btn-hover-border-color: var(--tertiary-dark);
  --bs-btn-active-color: var(--tertiary-dark);
  --bs-btn-active-bg: var(--neutral-dark);
  --bs-btn-active-border-color: var(--tertiary-dark);
}

.data-table :deep(.action-btn-delete) {
  --bs-btn-color: var(--error);
  --bs-btn-border-color: var(--error);
  --bs-btn-hover-color: var(--error-dark);
  --bs-btn-hover-bg: var(--error-light);
  --bs-btn-hover-border-color: var(--error-dark);
  --bs-btn-active-color: var(--error-dark);
  --bs-btn-active-bg: var(--error-medium);
  --bs-btn-active-border-color: var(--error-dark);
}

.data-table :deep(.action-btn-duplicate) {
  --bs-btn-color: var(--secondary-medium);
  --bs-btn-border-color: var(--secondary-medium);
  --bs-btn-hover-color: var(--secondary-dark);
  --bs-btn-hover-bg: var(--secondary-light);
  --bs-btn-hover-border-color: var(--secondary-dark);
}

.data-table :deep(.action-btn-archive) {
  --bs-btn-color: var(--neutral-dark);
  --bs-btn-border-color: var(--neutral-dark);
  --bs-btn-hover-color: var(--tertiary-dark);
  --bs-btn-hover-bg: var(--neutral-medium);
  --bs-btn-hover-border-color: var(--tertiary-dark);
}

.data-table :deep(.action-btn-restore) {
  --bs-btn-color: var(--success-medium);
  --bs-btn-border-color: var(--success-medium);
  --bs-btn-hover-color: var(--success-dark);
  --bs-btn-hover-bg: var(--success-light);
  --bs-btn-hover-border-color: var(--success-dark);
}

.data-table :deep(.action-btn-download) {
  --bs-btn-color: var(--info-medium);
  --bs-btn-border-color: var(--info-medium);
  --bs-btn-hover-color: var(--info-dark);
  --bs-btn-hover-bg: var(--info-light);
  --bs-btn-hover-border-color: var(--info-dark);
}

.data-table :deep(.action-btn-share) {
  --bs-btn-color: var(--primary-medium);
  --bs-btn-border-color: var(--primary-medium);
  --bs-btn-hover-color: var(--primary-dark);
  --bs-btn-hover-bg: var(--primary-light);
  --bs-btn-hover-border-color: var(--primary-dark);
}

.data-table :deep(.action-btn-settings) {
  --bs-btn-color: var(--tertiary-dark);
  --bs-btn-border-color: var(--tertiary-dark);
  --bs-btn-hover-color: var(--tertiary-dark);
  --bs-btn-hover-bg: var(--neutral-light);
  --bs-btn-hover-border-color: var(--tertiary-dark);
}

.data-table :deep(.action-btn-history) {
  --bs-btn-color: var(--info-dark);
  --bs-btn-border-color: var(--info-dark);
  --bs-btn-hover-color: var(--info-dark);
  --bs-btn-hover-bg: var(--info-light);
  --bs-btn-hover-border-color: var(--info-dark);
}

.data-table :deep(.action-btn-favorite) {
  --bs-btn-color: #ffc107;
  --bs-btn-border-color: #ffc107;
  --bs-btn-hover-color: #f57c00;
  --bs-btn-hover-bg: #fff3cd;
  --bs-btn-hover-border-color: #f57c00;
}

.data-table :deep(.action-btn-print) {
  --bs-btn-color: var(--neutral-dark);
  --bs-btn-border-color: var(--neutral-dark);
  --bs-btn-hover-color: var(--tertiary-dark);
  --bs-btn-hover-bg: var(--neutral-light);
  --bs-btn-hover-border-color: var(--tertiary-dark);
}

.data-table :deep(.action-btn-email) {
  --bs-btn-color: #17a2b8;
  --bs-btn-border-color: #17a2b8;
  --bs-btn-hover-color: #138496;
  --bs-btn-hover-bg: #d1ecf1;
  --bs-btn-hover-border-color: #138496;
}

.data-table :deep(.action-btn-copy) {
  --bs-btn-color: var(--secondary-dark);
  --bs-btn-border-color: var(--secondary-dark);
  --bs-btn-hover-color: var(--secondary-dark);
  --bs-btn-hover-bg: var(--secondary-light);
  --bs-btn-hover-border-color: var(--secondary-dark);
}

.data-table :deep(.action-btn-move) {
  --bs-btn-color: var(--primary-dark);
  --bs-btn-border-color: var(--primary-dark);
  --bs-btn-hover-color: var(--primary-dark);
  --bs-btn-hover-bg: var(--primary-light);
  --bs-btn-hover-border-color: var(--primary-dark);
}

.data-table :deep(.action-btn-export) {
  --bs-btn-color: var(--success-dark);
  --bs-btn-border-color: var(--success-dark);
  --bs-btn-hover-color: var(--success-dark);
  --bs-btn-hover-bg: var(--success-light);
  --bs-btn-hover-border-color: var(--success-dark);
}

.data-table :deep(.action-btn-import) {
  --bs-btn-color: var(--info-dark);
  --bs-btn-border-color: var(--info-dark);
  --bs-btn-hover-color: var(--info-dark);
  --bs-btn-hover-bg: var(--info-light);
  --bs-btn-hover-border-color: var(--info-dark);
}

.data-table :deep(.action-btn-approve) {
  --bs-btn-color: var(--success);
  --bs-btn-border-color: var(--success);
  --bs-btn-hover-color: var(--success-dark);
  --bs-btn-hover-bg: var(--success-light);
  --bs-btn-hover-border-color: var(--success-dark);
}

.data-table :deep(.action-btn-reject) {
  --bs-btn-color: var(--error);
  --bs-btn-border-color: var(--error);
  --bs-btn-hover-color: var(--error-dark);
  --bs-btn-hover-bg: var(--error-light);
  --bs-btn-hover-border-color: var(--error-dark);
}

.data-table :deep(.action-btn-pause) {
  --bs-btn-color: #ffc107;
  --bs-btn-border-color: #ffc107;
  --bs-btn-hover-color: #f57c00;
  --bs-btn-hover-bg: #fff3cd;
  --bs-btn-hover-border-color: #f57c00;
}

.data-table :deep(.action-btn-play) {
  --bs-btn-color: var(--success);
  --bs-btn-border-color: var(--success);
  --bs-btn-hover-color: var(--success-dark);
  --bs-btn-hover-bg: var(--success-light);
  --bs-btn-hover-border-color: var(--success-dark);
}

.data-table :deep(.action-btn-stop) {
  --bs-btn-color: var(--error);
  --bs-btn-border-color: var(--error);
  --bs-btn-hover-color: var(--error-dark);
  --bs-btn-hover-bg: var(--error-light);
  --bs-btn-hover-border-color: var(--error-dark);
}

/* Badge and Status Styling */
.data-table :deep(.badge) {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.375rem 0.75rem;
}

.data-table :deep(.text-tertiary-dark) {
  color: var(--tertiary-dark) !important;
}

.data-table :deep(.text-tertiary-medium) {
  color: var(--tertiary-medium) !important;
}

.data-table :deep(.text-primary-dark) {
  color: var(--primary-dark) !important;
}

/* Pagination Container with Shadow */
.pagination-container {
  padding: 1rem;
  border-top: 1px solid var(--neutral-light);
  background-color: #FAFAFA; /* Lighter than global background */
  /* Harder inner shadow for depth */
  box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.12);
}

.pagination-info {
  font-size: 0.875rem;
}

.pagination .page-link {
  color: var(--primary);
  border-color: var(--neutral);
  padding: 0.375rem 0.75rem;
  /* Harder shadow for pagination buttons */
  box-shadow: 0 3px 6px 0 rgba(0, 0, 0, 0.12);
  transition: all 0.2s ease;
}

.pagination .page-link:hover {
  color: var(--primary-dark);
  background-color: var(--primary-light);
  border-color: var(--primary);
  /* Much harder shadow on hover */
  box-shadow: 0 6px 12px 0 rgba(0, 0, 0, 0.18);
  transform: translateY(-2px);
}

.pagination .page-item.active .page-link {
  background-color: var(--primary);
  border-color: var(--primary);
  color: white;
  /* Hardest shadow for active state */
  box-shadow: 0 8px 16px 0 rgba(0, 0, 0, 0.25);
}

.pagination .page-item.disabled .page-link {
  color: var(--tertiary-medium);
  background-color: var(--neutral-light);
  border-color: var(--neutral);
  box-shadow: none;
}

.page-link-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.375rem 0.5rem;
  min-width: 32px;
}

.page-link-icon:hover:not(:disabled) {
  transform: translateY(-2px) translateX(1px);
}

.page-item.disabled .page-link-icon {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-link-icon svg {
  transition: transform 0.2s ease;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .table-responsive {
    border-radius: 0.75rem;
  }
  
  .data-table {
    min-width: 1000px;
  }
}

@media (max-width: 768px) {
  .data-table :deep(th),
  .data-table :deep(td) {
    padding: 0.75rem 0.5rem;
    font-size: 0.8125rem;
  }
  
  .data-table :deep(.action-btn) {
    width: 22px;
    height: 22px;
    margin: 0;
  }
  
  .data-table :deep(.action-btn svg) {
    width: 12px;
    height: 12px;
  }
}

@media (max-width: 576px) {
  .data-table :deep(.action-btn) {
    width: 20px;
    height: 20px;
  }
  
  .data-table :deep(.action-btn svg) {
    width: 10px;
    height: 10px;
  }
}

.table-header-sticky {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: var(--primary-medium) !important;
  /* Harder shadow for sticky header */
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.15);
}

.table-header-sticky th {
  position: relative;
  background-color: var(--primary-medium) !important;
}

/* Add shadow when scrolling for better visual separation */
.table-header-sticky::after {
  content: '';
  position: absolute;
  bottom: -3px;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.15), transparent);
  opacity: 0;
  transition: opacity 0.2s ease;
}

/* Enhanced scroll shadow effect */
.table-responsive.scrolled .table-header-sticky::after {
  opacity: 1;
}

/* Checkbox Styling - Thicker Outlines for Better Clarity */
.data-table :deep(.form-check-input) {
  border-width: 2px !important;
  border-color: var(--neutral-dark) !important;
  width: 1.1em;
  height: 1.1em;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.08);
}

.data-table :deep(.form-check-input:hover) {
  border-color: var(--primary) !important;
  box-shadow: 0 3px 6px 0 rgba(0, 0, 0, 0.12);
}

.data-table :deep(.form-check-input:focus) {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(115, 146, 226, 0.25) !important;
}

.data-table :deep(.form-check-input:checked) {
  background-color: var(--primary) !important;
  border-color: var(--primary) !important;
  border-width: 2px !important;
  box-shadow: 0 3px 6px 0 rgba(0, 0, 0, 0.15);
}

.data-table :deep(.form-check-input:indeterminate) {
  background-color: var(--primary) !important;
  border-color: var(--primary) !important;
  border-width: 2px !important;
  box-shadow: 0 3px 6px 0 rgba(0, 0, 0, 0.15);
}
</style>