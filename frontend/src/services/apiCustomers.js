// services/apiCustomer.js - COMPLETE VERSION
import { api } from './api.js';

class CustomerApiService {
  // Helper method to handle responses
  handleResponse(response) {
    return response.data;
  }

  // Helper method to handle errors
  handleError(error) {
    const message = error.response?.data?.error || 
                   error.response?.data?.message || 
                   error.message || 
                   'An unexpected error occurred';
    throw new Error(message);
  }

  // KPI METHODS (existing)
  
  /**
   * Get active users count
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Active users data
   */
  async ActiveUser(params = {}) {
    try {
        console.log("This API call is getting Active Users");
        const response = await api.get('/customerkpi', { params });
        return response.data;
    } catch (error) {
        console.error("Error fetching active users:", error);
        throw error;
    }
  }

  /**
   * Get monthly users count
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Monthly users data
   */
  async MonthlyUser(params = {}) {
    try {
        console.log("This API calls the Monthly Users");
        const response = await api.get('/customerkpimonthly', { params });
        return response.data;
    } catch (error) {
      console.error("Error fetching monthly users:", error);
      throw error;
    }
  }

  /**
   * Get daily users count
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Daily users data
   */
  async DailyUser(params = {}) {
    try {
        console.log("This API calls the Daily Users");
        const response = await api.get('/customerkpidaily', { params });
        return response.data;
    } catch (error) {
      console.error("Error fetching daily users:", error);
      throw error;
    }
  }

  // CUSTOMER CRUD OPERATIONS

  /**
   * Get all customers with optional query parameters
   * @param {Object} params - Query parameters (page, limit, search, status, etc.)
   * @returns {Promise<Array>} Customers list
   */
  async getAllCustomers(params = {}) {
    try {
      console.log("Fetching all customers with params:", params);
      const response = await api.get('/customers/', { params });
      return this.handleResponse(response);
    } catch (error) {
      console.error("Error fetching customers:", error);
      this.handleError(error);
    }
  }

  /**
   * Get customer by ID
   * @param {string} customerId - Customer ID
   * @returns {Promise<Object>} Customer data
   */
  async getCustomerById(customerId) {
    try {
      console.log(`Fetching customer with ID: ${customerId}`);
      const response = await api.get(`/customers/${customerId}`);
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error fetching customer ${customerId}:`, error);
      this.handleError(error);
    }
  }

  /**
   * Create new customer
   * @param {Object} customerData - Customer data
   * @returns {Promise<Object>} Created customer
   */
  async createCustomer(customerData) {
    try {
      console.log("Creating new customer:", customerData);
      const response = await api.post('/customers/', customerData);
      return this.handleResponse(response);
    } catch (error) {
      console.error("Error creating customer:", error);
      this.handleError(error);
    }
  }

  /**
   * Update customer
   * @param {string} customerId - Customer ID
   * @param {Object} customerData - Updated customer data
   * @returns {Promise<Object>} Updated customer
   */
  async updateCustomer(customerId, customerData) {
    try {
      console.log(`Updating customer ${customerId}:`, customerData);
      const response = await api.put(`/customers/${customerId}/`, customerData);  // Added trailing slash
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error updating customer ${customerId}:`, error);
      this.handleError(error);
    }
  }

  /**
   * Delete customer
   * @param {string} customerId - Customer ID
   * @returns {Promise<Object>} Deletion confirmation
   */
  async deleteCustomer(customerId) {
    try {
      console.log(`Deleting customer with ID: ${customerId}`);
      const response = await api.delete(`/customers/${customerId}/`);
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error deleting customer ${customerId}:`, error);
      this.handleError(error);
    }
  }

  /**
   * Delete multiple customers
   * @param {Array} customerIds - Array of customer IDs
   * @returns {Promise<Object>} Deletion results
   */
  async deleteMultipleCustomers(customerIds) {
    try {
      console.log("Deleting multiple customers:", customerIds);
      const response = await api.delete('/customers/bulk', { 
        data: { customer_ids: customerIds } 
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error("Error deleting multiple customers:", error);
      this.handleError(error);
    }
  }

  // CUSTOMER SEARCH AND FILTERING

  /**
   * Search customers by query
   * @param {string} query - Search query
   * @param {Object} filters - Additional filters
   * @returns {Promise<Array>} Filtered customers
   */
  async searchCustomers(query, filters = {}) {
    try {
      console.log(`Searching customers with query: ${query}`, filters);
      const params = { search: query, ...filters };
      const response = await api.get('/customers/search', { params });
      return this.handleResponse(response);
    } catch (error) {
      console.error("Error searching customers:", error);
      this.handleError(error);
    }
  }

  /**
   * Get customers by status
   * @param {string} status - Customer status (active, inactive)
   * @returns {Promise<Array>} Customers with specified status
   */
  async getCustomersByStatus(status) {
    try {
      console.log(`Fetching customers with status: ${status}`);
      const response = await api.get('/customers', { 
        params: { status } 
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error fetching customers by status ${status}:`, error);
      this.handleError(error);
    }
  }

  /**
   * Get customers by loyalty points range
   * @param {number} minPoints - Minimum points
   * @param {number} maxPoints - Maximum points
   * @returns {Promise<Array>} Customers within points range
   */
  async getCustomersByPointsRange(minPoints, maxPoints) {
    try {
      console.log(`Fetching customers with points between ${minPoints} and ${maxPoints}`);
      const response = await api.get('/customers', { 
        params: { 
          min_points: minPoints, 
          max_points: maxPoints 
        } 
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error("Error fetching customers by points range:", error);
      this.handleError(error);
    }
  }

  // LOYALTY POINTS MANAGEMENT

  /**
   * Update customer loyalty points
   * @param {string} customerId - Customer ID
   * @param {number} points - New points amount
   * @returns {Promise<Object>} Updated customer
   */
  async updateLoyaltyPoints(customerId, points) {
    try {
      console.log(`Updating loyalty points for customer ${customerId}: ${points}`);
      const response = await api.patch(`/customers/${customerId}/points`, { 
        loyalty_points: points 
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error updating loyalty points for customer ${customerId}:`, error);
      this.handleError(error);
    }
  }

  /**
   * Add points to customer
   * @param {string} customerId - Customer ID
   * @param {number} pointsToAdd - Points to add
   * @returns {Promise<Object>} Updated customer
   */
  async addLoyaltyPoints(customerId, pointsToAdd) {
    try {
      console.log(`Adding ${pointsToAdd} points to customer ${customerId}`);
      const response = await api.post(`/customers/${customerId}/points/add`, { 
        points: pointsToAdd 
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error adding points to customer ${customerId}:`, error);
      this.handleError(error);
    }
  }

  /**
   * Redeem points for customer
   * @param {string} customerId - Customer ID
   * @param {number} pointsToRedeem - Points to redeem
   * @returns {Promise<Object>} Updated customer
   */
  async redeemLoyaltyPoints(customerId, pointsToRedeem) {
    try {
      console.log(`Redeeming ${pointsToRedeem} points for customer ${customerId}`);
      const response = await api.post(`/customers/${customerId}/points/redeem`, { 
        points: pointsToRedeem 
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error redeeming points for customer ${customerId}:`, error);
      this.handleError(error);
    }
  }

  // CUSTOMER STATUS MANAGEMENT

  /**
   * Activate customer account
   * @param {string} customerId - Customer ID
   * @returns {Promise<Object>} Updated customer
   */
  async activateCustomer(customerId) {
    try {
      console.log(`Activating customer ${customerId}`);
      const response = await api.patch(`/customers/${customerId}/activate`);
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error activating customer ${customerId}:`, error);
      this.handleError(error);
    }
  }

  /**
   * Deactivate customer account
   * @param {string} customerId - Customer ID
   * @returns {Promise<Object>} Updated customer
   */
  async deactivateCustomer(customerId) {
    try {
      console.log(`Deactivating customer ${customerId}`);
      const response = await api.patch(`/customers/${customerId}/deactivate`);
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error deactivating customer ${customerId}:`, error);
      this.handleError(error);
    }
  }

  // CUSTOMER ORDER HISTORY

  /**
   * Get customer order history
   * @param {string} customerId - Customer ID
   * @param {Object} params - Query parameters (limit, page, date_from, date_to)
   * @returns {Promise<Array>} Customer orders
   */
  async getCustomerOrders(customerId, params = {}) {
    try {
      console.log(`Fetching orders for customer ${customerId}`, params);
      const response = await api.get(`/customers/${customerId}/orders`, { params });
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error fetching orders for customer ${customerId}:`, error);
      this.handleError(error);
    }
  }

  /**
   * Get customer order statistics
   * @param {string} customerId - Customer ID
   * @returns {Promise<Object>} Order statistics
   */
  async getCustomerOrderStats(customerId) {
    try {
      console.log(`Fetching order stats for customer ${customerId}`);
      const response = await api.get(`/customers/${customerId}/stats`);
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error fetching order stats for customer ${customerId}:`, error);
      this.handleError(error);
    }
  }

  // DATA EXPORT/IMPORT

  /**
   * Export customers data
   * @param {Object} filters - Export filters
   * @param {string} format - Export format (csv, xlsx, json)
   * @returns {Promise<Blob>} Export file
   */
  async exportCustomers(filters = {}, format = 'csv') {
    try {
      console.log("Exporting customers data", { filters, format });
      const response = await api.get('/customers/export', {
        params: { ...filters, format },
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error("Error exporting customers:", error);
      this.handleError(error);
    }
  }

  /**
   * Import customers from file
   * @param {File} file - Import file
   * @returns {Promise<Object>} Import results
   */
  async importCustomers(file) {
    try {
      console.log("Importing customers from file:", file.name);
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post('/customers/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error("Error importing customers:", error);
      this.handleError(error);
    }
  }

  // CUSTOMER ANALYTICS

  /**
   * Get customer analytics dashboard data
   * @param {Object} params - Date range and filters
   * @returns {Promise<Object>} Analytics data
   */
  async getCustomerAnalytics(params = {}) {
    try {
      console.log("Fetching customer analytics", params);
      const response = await api.get('/customers/analytics', { params });
      return this.handleResponse(response);
    } catch (error) {
      console.error("Error fetching customer analytics:", error);
      this.handleError(error);
    }
  }

  /**
   * Get top customers by various metrics
   * @param {string} metric - Metric type (orders, spending, points)
   * @param {number} limit - Number of customers to return
   * @returns {Promise<Array>} Top customers
   */
  async getTopCustomers(metric = 'orders', limit = 10) {
    try {
      console.log(`Fetching top ${limit} customers by ${metric}`);
      const response = await api.get('/customers/top', { 
        params: { metric, limit } 
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error("Error fetching top customers:", error);
      this.handleError(error);
    }
  }

  // CUSTOMER COMMUNICATION

  /**
   * Send notification to customer
   * @param {string} customerId - Customer ID
   * @param {Object} notification - Notification data
   * @returns {Promise<Object>} Send result
   */
  async sendNotification(customerId, notification) {
    try {
      console.log(`Sending notification to customer ${customerId}`, notification);
      const response = await api.post(`/customers/${customerId}/notify`, notification);
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error sending notification to customer ${customerId}:`, error);
      this.handleError(error);
    }
  }

  /**
   * Send bulk notifications to multiple customers
   * @param {Array} customerIds - Array of customer IDs
   * @param {Object} notification - Notification data
   * @returns {Promise<Object>} Send results
   */
  async sendBulkNotification(customerIds, notification) {
    try {
      console.log("Sending bulk notification to customers:", customerIds);
      const response = await api.post('/customers/notify/bulk', {
        customer_ids: customerIds,
        ...notification
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error("Error sending bulk notification:", error);
      this.handleError(error);
    }
  }

  async getCustomerStatistics() {
    try {
      console.log("Fetching customer statistics");
      const response = await api.get('/customers/statistics/');
      return this.handleResponse(response);
    } catch (error) {
      console.error("Error fetching customer statistics:", error);
      this.handleError(error);
    }
  }

}

// Create and export singleton instance
const customerApiService = new CustomerApiService();

export default customerApiService;