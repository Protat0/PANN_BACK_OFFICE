// services/apiCustomers.js - Updated to match backend CustomerService
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
                   error.response?.data?.detail ||
                   error.message || 
                   'An unexpected error occurred';
    
    console.error('Customer API Error:', {
      status: error.response?.status,
      data: error.response?.data,
      message
    });
    
    throw new Error(message);
  }

  // CUSTOMER CRUD OPERATIONS

  /**
   * Get all customers with pagination and filters
   * @param {Object} params - Query parameters (page, limit, status, etc.)
   * @returns {Promise<Object>} Customers data with pagination
   */
  async getCustomers(params = {}) {
    try {
      console.log('Fetching customers with params:', params);
      const response = await api.get('/customers/', { params });
      return this.handleResponse(response);
    } catch (error) {
      console.error('Error fetching customers:', error);
      this.handleError(error);
    }
  }

  /**
   * Get customer by ID
   * @param {string} customerId - Customer ID (CUST-##### format)
   * @returns {Promise<Object>} Customer data
   */
  async getCustomer(customerId) {
    try {
      console.log(`Fetching customer with ID: ${customerId}`);
      const response = await api.get(`/customers/${customerId}/`);
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
      console.log('Creating new customer:', customerData);
      const response = await api.post('/customers/', customerData);
      return this.handleResponse(response);
    } catch (error) {
      console.error('Error creating customer:', error);
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
      const response = await api.put(`/customers/${customerId}/`, customerData);
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error updating customer ${customerId}:`, error);
      this.handleError(error);
    }
  }

  /**
   * Delete customer (soft delete)
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

  // SEARCH AND FILTERING

  /**
   * Search customers by query
   * @param {string} query - Search query
   * @returns {Promise<Array>} Filtered customers
   */
  async searchCustomers(query) {
    try {
      console.log(`Searching customers with query: ${query}`);
      const response = await api.get('/customers/search/', { 
        params: { search: query } 
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error('Error searching customers:', error);
      this.handleError(error);
    }
  }

  /**
   * Get customers by status
   * @param {string} status - Customer status (active, inactive)
   * @returns {Promise<Object>} Customers with specified status
   */
  async getCustomersByStatus(status) {
    try {
      console.log(`Fetching customers with status: ${status}`);
      const response = await api.get('/customers/', { 
        params: { status } 
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error fetching customers by status ${status}:`, error);
      this.handleError(error);
    }
  }

  // LOYALTY POINTS MANAGEMENT

  /**
   * Update customer loyalty points
   * @param {string} customerId - Customer ID
   * @param {number} points - Points to add
   * @param {string} reason - Reason for point addition
   * @returns {Promise<Object>} Updated customer
   */
  async updateLoyaltyPoints(customerId, points, reason = 'Manual adjustment') {
    try {
      console.log(`Updating loyalty points for customer ${customerId}: +${points}`);
      const response = await api.patch(`/customers/${customerId}/loyalty/`, { 
        points_to_add: points,
        reason: reason
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error updating loyalty points for customer ${customerId}:`, error);
      this.handleError(error);
    }
  }

  // CUSTOMER ANALYTICS

  /**
   * Get customer statistics
   * @returns {Promise<Object>} Customer statistics
   */
  async getCustomerStatistics() {
    try {
      console.log('Fetching customer statistics');
      const response = await api.get('/customers/statistics/');
      return this.handleResponse(response);
    } catch (error) {
      console.error('Error fetching customer statistics:', error);
      this.handleError(error);
    }
  }

  // RESTORE AND HARD DELETE (for admin functions)

  /**
   * Restore deleted customer
   * @param {string} customerId - Customer ID
   * @returns {Promise<Object>} Restored customer
   */
  async restoreCustomer(customerId) {
    try {
      console.log(`Restoring customer ${customerId}`);
      const response = await api.patch(`/customers/${customerId}/restore/`);
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error restoring customer ${customerId}:`, error);
      this.handleError(error);
    }
  }

  /**
   * Permanently delete customer
   * @param {string} customerId - Customer ID
   * @param {string} confirmationToken - Confirmation token
   * @returns {Promise<Object>} Deletion confirmation
   */
  async hardDeleteCustomer(customerId, confirmationToken) {
    try {
      console.log(`Permanently deleting customer ${customerId}`);
      const response = await api.delete(`/customers/${customerId}/hard/`, {
        data: { confirmation_token: confirmationToken }
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error(`Error permanently deleting customer ${customerId}:`, error);
      this.handleError(error);
    }
  }

  // BULK OPERATIONS

  /**
   * Delete multiple customers
   * @param {Array} customerIds - Array of customer IDs
   * @returns {Promise<Object>} Deletion results
   */
  async deleteMultipleCustomers(customerIds) {
    try {
      console.log('Deleting multiple customers:', customerIds);
      const response = await api.delete('/customers/bulk/', { 
        data: { customer_ids: customerIds } 
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error('Error deleting multiple customers:', error);
      this.handleError(error);
    }
  }
}

// Create and export singleton instance
const customerApiService = new CustomerApiService();

export default customerApiService;