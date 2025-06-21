<template>
  <div class="table-container">
    <div class="table-responsive">
      <table class="table table-hover data-table">
        <thead class="table-header">
          <slot name="header"></slot>
        </thead>
        <tbody>
          <slot name="body"></slot>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataTable'
}
</script>

<style scoped>
.table-container {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
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
  width: 24px;
  height: 24px;
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
}

.data-table :deep(.action-btn:hover) {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
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
</style>