// composables/useExport.js
import { ref, reactive } from 'vue'

export function useExport() {
  // State
  const showExportModal = ref(false)
  const selectedExportFormat = ref('')
  
  const exportOptions = reactive({
    includeInactive: false,
    includeDetails: true
  })

  // Methods
  const openExportModal = () => {
    showExportModal.value = true
  }

  const closeExportModal = () => {
    showExportModal.value = false
    selectedExportFormat.value = ''
  }

  const handleExport = (suppliers) => {
    if (!selectedExportFormat.value) return

    try {
      const exportData = exportOptions.includeInactive 
        ? suppliers 
        : suppliers.filter(s => s.status === 'active')

      const headers = ['Name', 'Email', 'Phone', 'Address', 'Status', 'Purchase Orders', 'Type']
      const csvContent = [
        headers.join(','),
        ...exportData.map(supplier => [
          `"${supplier.name}"`,
          supplier.email || '',
          supplier.phone || '',
          `"${supplier.address || ''}"`,
          supplier.status,
          supplier.purchaseOrders,
          supplier.type || ''
        ].join(','))
      ].join('\n')

      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `suppliers_${new Date().toISOString().split('T')[0]}.${selectedExportFormat.value}`
      a.click()
      window.URL.revokeObjectURL(url)

      closeExportModal()
      return { success: true, message: `Suppliers exported successfully as ${selectedExportFormat.value.toUpperCase()}` }
      
    } catch (error) {
      console.error('Error exporting suppliers:', error)
      return { success: false, error: `Failed to export suppliers: ${error.message}` }
    }
  }

  return {
    // State
    showExportModal,
    selectedExportFormat,
    exportOptions,
    
    // Methods
    openExportModal,
    closeExportModal,
    handleExport
  }
}