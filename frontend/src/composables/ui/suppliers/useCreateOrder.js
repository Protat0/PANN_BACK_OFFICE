// composables/ui/suppliers/useCreateOrder.js
import { ref } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export function useCreateOrder() {
  const showCreateOrderModal = ref(false)
  const selectedSupplier = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const openCreateOrderModal = (supplier) => {
    selectedSupplier.value = supplier
    showCreateOrderModal.value = true
  }

  const closeCreateOrderModal = () => {
    showCreateOrderModal.value = false
    selectedSupplier.value = null
    error.value = null
  }

  const handleOrderSave = async (orderData) => {
    loading.value = true
    error.value = null

    try {
      // Validate we have a supplier
      if (!selectedSupplier.value?.id) {
        throw new Error('No supplier selected')
      }

      // SAVE supplier name BEFORE closing modal
      const supplierName = selectedSupplier.value.name
      const supplierId = selectedSupplier.value.id

      // Transform frontend data to backend format
      const backendOrderData = {
        order_id: orderData.id || orderData.orderId,
        status: orderData.status || 'pending',
        order_date: orderData.orderDate || new Date().toISOString(),
        expected_delivery_date: orderData.expectedDate,
        priority: orderData.priority || 'normal',
        description: orderData.description || '',
        notes: orderData.notes || '',
        shipping_cost: orderData.shippingCost || 0,
        tax_rate: 12,
        subtotal: orderData.subtotal,
        tax_amount: orderData.tax,
        total_cost: orderData.total,
        items: orderData.items.map((item, index) => ({
          product_id: item.productId || `TEMP-${Date.now()}-${index}`,
          product_name: item.name,
          quantity: item.quantity,
          unit: item.unit || 'pcs',
          unit_price: item.unitPrice || 0,
          notes: item.notes || ''
        }))
      }

      // POST to backend
      const response = await api.post(
        `/suppliers/${supplierId}/orders/`,
        backendOrderData
      )

      console.log('Order created:', response.data)

      // Close modal AFTER saving supplier name
      closeCreateOrderModal()

      // Use the saved supplier name instead of accessing selectedSupplier
      return {
        success: true,
        message: `Purchase order ${orderData.id} created successfully for ${supplierName}`,
        orderId: orderData.id,
        total: orderData.total,
        data: response.data
      }

    } catch (err) {
      console.error('Error creating order:', err)
      
      let errorMessage = 'Failed to create purchase order'
      
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error
      } else if (err.message) {
        errorMessage = err.message
      }
      
      error.value = errorMessage

      return {
        success: false,
        error: errorMessage
      }

    } finally {
      loading.value = false
    }
  }

  return {
    showCreateOrderModal,
    selectedSupplier,
    loading,
    error,
    openCreateOrderModal,
    closeCreateOrderModal,
    handleOrderSave
  }
}