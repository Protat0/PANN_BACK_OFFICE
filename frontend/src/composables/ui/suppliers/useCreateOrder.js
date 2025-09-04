// composables/useCreateOrder.js
import { ref } from 'vue'

export function useCreateOrder() {
  // State
  const showCreateOrderModal = ref(false)
  const selectedSupplier = ref(null)

  // Methods
  const openCreateOrderModal = (supplier) => {
    selectedSupplier.value = supplier
    showCreateOrderModal.value = true
  }

  const closeCreateOrderModal = () => {
    showCreateOrderModal.value = false
    selectedSupplier.value = null
  }

  const handleOrderSave = (orderData, suppliersArray) => {
    try {
      // Find the supplier and increment their purchase orders count
      const supplierIndex = suppliersArray.findIndex(s => s.id === orderData.supplierId)
      if (supplierIndex !== -1) {
        suppliersArray[supplierIndex].purchaseOrders = (suppliersArray[supplierIndex].purchaseOrders || 0) + 1
      }

      // Here you would typically save to your orders database/array
      // For now, we'll just simulate success
      
      closeCreateOrderModal()
      
      return {
        success: true,
        message: `Purchase order ${orderData.id} created successfully for ${orderData.supplierName}`,
        orderId: orderData.id,
        total: orderData.total
      }
    } catch (error) {
      console.error('Error creating order:', error)
      return {
        success: false,
        error: `Failed to create order: ${error.message}`
      }
    }
  }

  return {
    // State
    showCreateOrderModal,
    selectedSupplier,
    
    // Methods
    openCreateOrderModal,
    closeCreateOrderModal,
    handleOrderSave
  }
}