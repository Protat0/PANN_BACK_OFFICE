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
          <small class="text-tertiary">
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
/* ==========================================================================
   TABLE CONTAINER - SEMANTIC THEME SYSTEM
   ========================================================================== */

.table-container {
  border-radius: 0.75rem;
  overflow: hidden;
  @apply surface-card shadow-lg transition-theme;
}

.table-responsive {
  border-radius: 0.75rem;
}

.data-table {
  margin-bottom: 0;
  border-collapse: separate;
  border-spacing: 0;
  @apply text-primary;
}

/* ==========================================================================
   HEADER STYLING - SEMANTIC
   ========================================================================== */

.table-header {
  background-color: var(--secondary) !important;
  color: var(--text-inverse) !important;
}

.data-table :deep(.table-header th) {
  padding: 1rem;
  font-weight: 600;
  font-size: 0.875rem;
  letter-spacing: 0.025em;
  border: none !important;
  color: var(--text-inverse) !important;
  text-transform: uppercase;
  position: relative;
  background-color: var(--secondary) !important;
}

.data-table :deep(.table-header th:first-child) {
  border-top-left-radius: 0.75rem;
}

.data-table :deep(.table-header th:last-child) {
  border-top-right-radius: 0.75rem;
}

/* ==========================================================================
   BODY STYLING - SEMANTIC
   ========================================================================== */

.data-table :deep(tbody td) {
  padding: 0.875rem 1rem;
  font-size: 0.875rem;
  vertical-align: middle;
  @apply border-bottom-theme text-primary surface-primary transition-theme;
}

.data-table :deep(tbody tr:last-child td) {
  border-bottom: none;
}

.data-table :deep(tbody tr:hover) {
  @apply hover-surface;
}

.data-table :deep(tbody tr:hover td) {
  @apply hover-surface;
}

.data-table :deep(tbody tr.table-primary) {
  @apply state-selected;
}

.data-table :deep(tbody tr.text-muted) {
  opacity: 0.6;
}

/* ==========================================================================
   ACTION BUTTON STYLES - SEMANTIC
   ========================================================================== */

.data-table :deep(.action-btn) {
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  border-width: 1.5px;
  position: relative;
  overflow: hidden;
  padding: 0;
  margin: 0 1px;
  @apply shadow-sm transition-all-theme;
}

.data-table :deep(.action-btn:hover) {
  transform: translateY(-2px);
  @apply shadow-md;
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

/* Action Button Color Variants - Semantic */
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

/* ==========================================================================
   BADGE AND STATUS STYLING - SEMANTIC
   ========================================================================== */

.data-table :deep(.badge) {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.375rem 0.75rem;
  @apply surface-tertiary text-primary border-theme;
}

.data-table :deep(.text-tertiary-dark) {
  @apply text-primary;
}

.data-table :deep(.text-tertiary-medium) {
  @apply text-secondary;
}

.data-table :deep(.text-primary-dark) {
  @apply text-accent;
}

/* ==========================================================================
   PAGINATION CONTAINER - SEMANTIC
   ========================================================================== */

.pagination-container {
  padding: 1rem;
  @apply border-top-theme surface-secondary shadow-sm transition-theme;
  box-shadow: inset 0 2px 4px 0 var(--shadow-sm);
}

.pagination-info {
  font-size: 0.875rem;
}

.pagination .page-link {
  padding: 0.375rem 0.75rem;
  @apply text-accent border-theme surface-primary shadow-sm transition-all-theme;
}

.pagination .page-link:hover {
  transform: translateY(-2px);
  @apply text-accent state-hover border-accent shadow-md;
}

.pagination .page-item.active .page-link {
  background-color: var(--secondary);
  border-color: var(--secondary);
  @apply text-inverse shadow-md;
}

.pagination .page-item.disabled .page-link {
  @apply text-disabled surface-tertiary border-secondary;
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

/* ==========================================================================
   STICKY HEADER - SEMANTIC
   ========================================================================== */

.table-header-sticky {
  position: sticky;
  top: 0;
  z-index: 2;
  background-color: var(--secondary) !important;
  @apply shadow-md;
}

.table-header-sticky th {
  position: relative;
  background-color: var(--secondary) !important;
}

/* Add shadow when scrolling for better visual separation */
.table-header-sticky::after {
  content: '';
  position: absolute;
  bottom: -3px;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(to bottom, var(--shadow-lg), transparent);
  opacity: 0;
  transition: opacity 0.2s ease;
}

/* Enhanced scroll shadow effect */
.table-responsive.scrolled .table-header-sticky::after {
  opacity: 1;
}

/* ==========================================================================
   CHECKBOX STYLING - SEMANTIC
   ========================================================================== */

.data-table :deep(.form-check-input) {
  border-width: 2px !important;
  width: 1.1em;
  height: 1.1em;
  @apply border-primary surface-primary shadow-sm transition-all-theme;
}

.data-table :deep(.form-check-input:hover) {
  @apply border-accent shadow-md;
}

.data-table :deep(.form-check-input:focus) {
  @apply border-accent focus-ring-theme;
}

.data-table :deep(.form-check-input:checked) {
  background-color: var(--secondary) !important;
  border-color: var(--secondary) !important;
  border-width: 2px !important;
  @apply shadow-md;
}

.data-table :deep(.form-check-input:indeterminate) {
  background-color: var(--secondary) !important;
  border-color: var(--secondary) !important;
  border-width: 2px !important;
  @apply shadow-md;
}

/* ==========================================================================
   RESPONSIVE DESIGN
   ========================================================================== */

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

/* ==========================================================================
   ACCESSIBILITY & REDUCED MOTION
   ========================================================================== */

@media (prefers-reduced-motion: reduce) {
  .data-table :deep(.action-btn),
  .pagination .page-link,
  .page-link-icon {
    transition: none !important;
  }
  
  .data-table :deep(.action-btn:hover),
  .pagination .page-link:hover,
  .page-link-icon:hover {
    transform: none !important;
  }
}
</style>