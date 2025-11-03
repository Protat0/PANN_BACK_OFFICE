import { ref, computed } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export function useOnlineOrders() {
  // ================================================================
  // REACTIVE STATE
  // ================================================================
  
  const orders = ref([])
  const currentOrder = ref(null)
  const orderStatistics = ref(null)
  
  const isLoading = ref(false)
  const isUpdating = ref(false)
  const error = ref(null)
  
  // ================================================================
  // COMPUTED PROPERTIES
  // ================================================================
  
  const hasOrders = computed(() => orders.value.length > 0)
  const totalOrders = computed(() => orders.value.length)
  
  const pendingOrders = computed(() => 
    orders.value.filter(order => order.order_status === 'pending')
  )
  
  const processingOrders = computed(() => 
    orders.value.filter(order => ['confirmed', 'preparing'].includes(order.order_status))
  )
  
  const completedOrders = computed(() => 
    orders.value.filter(order => ['delivered', 'completed'].includes(order.order_status))
  )
  
  const cancelledOrders = computed(() => 
    orders.value.filter(order => order.order_status === 'cancelled')
  )
  
  // ================================================================
  // API METHODS
  // ================================================================
  
  /**
   * Get authentication headers
   */
  const getAuthHeaders = () => {
    const token = localStorage.getItem('token')
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }
  
  /**
   * Fetch all orders
   */
  const fetchOrders = async (filters = {}) => {
    try {
      isLoading.value = true
      error.value = null
      
      const params = new URLSearchParams()
      if (filters.status) params.append('status', filters.status)
      if (filters.payment_status) params.append('payment_status', filters.payment_status)
      if (filters.customer_id) params.append('customer_id', filters.customer_id)
      if (filters.start_date) params.append('start_date', filters.start_date)
      if (filters.end_date) params.append('end_date', filters.end_date)
      if (filters.limit) params.append('limit', filters.limit)
      
      const queryString = params.toString()
      const url = `${API_BASE_URL}/online-orders/all/${queryString ? '?' + queryString : ''}`
      
      const response = await axios.get(url, {
        headers: getAuthHeaders()
      })
      
      if (Array.isArray(response.data)) {
        orders.value = response.data
      } else {
        orders.value = []
      }
      
      return response.data
    } catch (err) {
      console.error('Error fetching orders:', err)
      error.value = err.response?.data?.error || err.message || 'Failed to fetch orders'
      return []
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get specific order by ID
   */
  const fetchOrderById = async (orderId) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await axios.get(`${API_BASE_URL}/online-orders/${orderId}/`, {
        headers: getAuthHeaders()
      })
      
      currentOrder.value = response.data
      return response.data
    } catch (err) {
      console.error('Error fetching order:', err)
      error.value = err.response?.data?.error || err.message || 'Failed to fetch order'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get orders for specific customer
   */
  const fetchCustomerOrders = async (customerId, filters = {}) => {
    try {
      isLoading.value = true
      error.value = null
      
      const params = new URLSearchParams()
      if (filters.status) params.append('status', filters.status)
      if (filters.limit) params.append('limit', filters.limit)
      
      const queryString = params.toString()
      const url = `${API_BASE_URL}/online-orders/customer/${customerId}/${queryString ? '?' + queryString : ''}`
      
      const response = await axios.get(url, {
        headers: getAuthHeaders()
      })
      
      return response.data
    } catch (err) {
      console.error('Error fetching customer orders:', err)
      error.value = err.response?.data?.error || err.message || 'Failed to fetch customer orders'
      return []
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Update order status
   */
  const updateOrderStatus = async (orderId, status, notes = '', updatedBy = null) => {
    try {
      isUpdating.value = true
      error.value = null
      
      const response = await axios.post(
        `${API_BASE_URL}/online-orders/${orderId}/status/`,
        {
          status,
          notes,
          updated_by: updatedBy
        },
        {
          headers: getAuthHeaders()
        }
      )
      
      // Update local order if it exists
      const orderIndex = orders.value.findIndex(o => o.order_id === orderId)
      if (orderIndex !== -1) {
        orders.value[orderIndex] = response.data
      }
      
      if (currentOrder.value && currentOrder.value.order_id === orderId) {
        currentOrder.value = response.data
      }
      
      return response.data
    } catch (err) {
      console.error('Error updating order status:', err)
      error.value = err.response?.data?.error || err.message || 'Failed to update order status'
      throw err
    } finally {
      isUpdating.value = false
    }
  }
  
  /**
   * Update payment status
   */
  const updatePaymentStatus = async (orderId, paymentStatus, paymentReference = '', confirmedBy = null) => {
    try {
      isUpdating.value = true
      error.value = null
      
      const response = await axios.post(
        `${API_BASE_URL}/online-orders/${orderId}/payment/`,
        {
          payment_status: paymentStatus,
          payment_reference: paymentReference,
          confirmed_by: confirmedBy
        },
        {
          headers: getAuthHeaders()
        }
      )
      
      // Update local order
      const orderIndex = orders.value.findIndex(o => o.order_id === orderId)
      if (orderIndex !== -1) {
        orders.value[orderIndex] = response.data
      }
      
      if (currentOrder.value && currentOrder.value.order_id === orderId) {
        currentOrder.value = response.data
      }
      
      return response.data
    } catch (err) {
      console.error('Error updating payment status:', err)
      error.value = err.response?.data?.error || err.message || 'Failed to update payment status'
      throw err
    } finally {
      isUpdating.value = false
    }
  }
  
  /**
   * Mark order as ready for delivery
   */
  const markReadyForDelivery = async (orderId, preparedBy = null, deliveryNotes = '') => {
    try {
      isUpdating.value = true
      error.value = null
      
      const response = await axios.post(
        `${API_BASE_URL}/online-orders/${orderId}/ready/`,
        {
          prepared_by: preparedBy,
          delivery_notes: deliveryNotes
        },
        {
          headers: getAuthHeaders()
        }
      )
      
      // Update local order
      const orderIndex = orders.value.findIndex(o => o.order_id === orderId)
      if (orderIndex !== -1) {
        orders.value[orderIndex] = response.data
      }
      
      if (currentOrder.value && currentOrder.value.order_id === orderId) {
        currentOrder.value = response.data
      }
      
      return response.data
    } catch (err) {
      console.error('Error marking order ready:', err)
      error.value = err.response?.data?.error || err.message || 'Failed to mark order ready'
      throw err
    } finally {
      isUpdating.value = false
    }
  }
  
  /**
   * Complete order (mark as delivered)
   */
  const completeOrder = async (orderId, completedBy = null, deliveryPerson = '') => {
    try {
      isUpdating.value = true
      error.value = null
      
      const response = await axios.post(
        `${API_BASE_URL}/online-orders/${orderId}/complete/`,
        {
          completed_by: completedBy,
          delivery_person: deliveryPerson
        },
        {
          headers: getAuthHeaders()
        }
      )
      
      // Update local order
      const orderIndex = orders.value.findIndex(o => o.order_id === orderId)
      if (orderIndex !== -1) {
        orders.value[orderIndex] = response.data
      }
      
      if (currentOrder.value && currentOrder.value.order_id === orderId) {
        currentOrder.value = response.data
      }
      
      return response.data
    } catch (err) {
      console.error('Error completing order:', err)
      error.value = err.response?.data?.error || err.message || 'Failed to complete order'
      throw err
    } finally {
      isUpdating.value = false
    }
  }
  
  /**
   * Cancel order
   */
  const cancelOrder = async (orderId, cancellationReason, cancelledBy = null) => {
    try {
      isUpdating.value = true
      error.value = null
      
      const response = await axios.post(
        `${API_BASE_URL}/online-orders/${orderId}/cancel/`,
        {
          cancellation_reason: cancellationReason,
          cancelled_by: cancelledBy
        },
        {
          headers: getAuthHeaders()
        }
      )
      
      // Update local order
      const orderIndex = orders.value.findIndex(o => o.order_id === orderId)
      if (orderIndex !== -1) {
        orders.value[orderIndex] = response.data
      }
      
      if (currentOrder.value && currentOrder.value.order_id === orderId) {
        currentOrder.value = response.data
      }
      
      return response.data
    } catch (err) {
      console.error('Error cancelling order:', err)
      error.value = err.response?.data?.error || err.message || 'Failed to cancel order'
      throw err
    } finally {
      isUpdating.value = false
    }
  }
  
  /**
   * Get orders by status
   */
  const fetchOrdersByStatus = async (status, limit = 50) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await axios.get(
        `${API_BASE_URL}/online-orders/status/${status}/?limit=${limit}`,
        {
          headers: getAuthHeaders()
        }
      )
      
      return response.data
    } catch (err) {
      console.error('Error fetching orders by status:', err)
      error.value = err.response?.data?.error || err.message || 'Failed to fetch orders by status'
      return []
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get pending orders
   */
  const fetchPendingOrders = async () => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await axios.get(`${API_BASE_URL}/online-orders/pending/`, {
        headers: getAuthHeaders()
      })
      
      return response.data
    } catch (err) {
      console.error('Error fetching pending orders:', err)
      error.value = err.response?.data?.error || err.message || 'Failed to fetch pending orders'
      return []
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get processing orders
   */
  const fetchProcessingOrders = async () => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await axios.get(`${API_BASE_URL}/online-orders/processing/`, {
        headers: getAuthHeaders()
      })
      
      return response.data
    } catch (err) {
      console.error('Error fetching processing orders:', err)
      error.value = err.response?.data?.error || err.message || 'Failed to fetch processing orders'
      return []
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get order summary for date range
   */
  const fetchOrderSummary = async (startDate, endDate) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await axios.get(
        `${API_BASE_URL}/online-orders/summary/?start_date=${startDate}&end_date=${endDate}`,
        {
          headers: getAuthHeaders()
        }
      )
      
      orderStatistics.value = response.data
      return response.data
    } catch (err) {
      console.error('Error fetching order summary:', err)
      error.value = err.response?.data?.error || err.message || 'Failed to fetch order summary'
      return null
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Clear error
   */
  const clearError = () => {
    error.value = null
  }
  
  /**
   * Clear current order
   */
  const clearCurrentOrder = () => {
    currentOrder.value = null
  }
  
  // ================================================================
  // RETURN COMPOSABLE
  // ================================================================
  
  return {
    // State
    orders,
    currentOrder,
    orderStatistics,
    isLoading,
    isUpdating,
    error,
    
    // Computed
    hasOrders,
    totalOrders,
    pendingOrders,
    processingOrders,
    completedOrders,
    cancelledOrders,
    
    // Methods
    fetchOrders,
    fetchOrderById,
    fetchCustomerOrders,
    updateOrderStatus,
    updatePaymentStatus,
    markReadyForDelivery,
    completeOrder,
    cancelOrder,
    fetchOrdersByStatus,
    fetchPendingOrders,
    fetchProcessingOrders,
    fetchOrderSummary,
    clearError,
    clearCurrentOrder
  }
}

