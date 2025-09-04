// composables/useImportSuppliers.js
import { ref } from 'vue'

export function useImportSuppliers() {
  // State
  const showImportModal = ref(false)

  // Methods
  const openImportModal = () => {
    showImportModal.value = true
  }

  const closeImportModal = () => {
    showImportModal.value = false
  }

  const handleImportSave = (importedSuppliers, existingSuppliers) => {
    // Add imported suppliers to existing array
    importedSuppliers.forEach(supplier => {
      existingSuppliers.push(supplier)
    })
    
    closeImportModal()
    
    return {
      success: true,
      message: `Successfully imported ${importedSuppliers.length} supplier(s) from file`,
      count: importedSuppliers.length
    }
  }

  return {
    // State
    showImportModal,
    
    // Methods
    openImportModal,
    closeImportModal,
    handleImportSave
  }
}