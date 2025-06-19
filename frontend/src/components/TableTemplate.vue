<template>
  <div class="table-container">
    <table class="data-table">
      <thead>
        <slot name="header"></slot>
      </thead>
      <tbody>
        <slot name="body"></slot>
      </tbody>
    </table>
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

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table :deep(thead) {
  background-color: #4f46e5;
  color: white;
}

.data-table :deep(th) {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.875rem;
  letter-spacing: 0.025em;
}

.data-table :deep(td) {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.875rem;
}

.data-table :deep(tbody tr:hover) {
  background-color: #f8fafc;
}

.data-table :deep(tbody tr.selected) {
  background-color: #ede9fe;
}

.data-table :deep(tbody tr.inactive) {
  opacity: 0.6;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .table-container {
    overflow-x: auto;
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
}
</style>