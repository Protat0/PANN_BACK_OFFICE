// composables/useBulkSuppliers.js
import { ref } from 'vue'

export function useBulkSuppliers() {
  // State
  const showBulkModal = ref(false)

  // Methods
  const openBulkModal = () => {
    showBulkModal.value = true
  }

  const closeBulkModal = () => {
    showBulkModal.value = false
  }

  const handleBulkSave = (newSuppliers, existingSuppliers) => {
    // Add new suppliers to existing array
    newSuppliers.forEach(supplier => {
      existingSuppliers.push(supplier)
    })
    
    closeBulkModal()
    
    return {
      success: true,
      message: `Successfully added ${newSuppliers.length} supplier(s)`,
      count: newSuppliers.length
    }
  }

  return {
    // State
    showBulkModal,
    
    // Methods
    openBulkModal,
    closeBulkModal,
    handleBulkSave
  }
}