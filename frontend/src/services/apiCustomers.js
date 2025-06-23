// services/apiProducts.js - UPDATED VERSION
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

  // PRODUCT CRUD OPERATIONS
  
  /**
   * Get all products with optional query parameters
   * @param {Object} params - Query parameters (page, limit, search, category, include_deleted, etc.)
   * @returns {Promise<Object>} Products list with pagination info
   */
 
  async ActiveUser(params = {}) {
    try {
        console.log("This API call is getting Active Users");
        const response = await api.get('/customerkpi', { params });
        
        // Return the data from the response
        return response.data;
        
    } catch (error) {
        console.error("Error fetching active users:", error);
        throw error; // Re-throw so calling code can handle it
    }
}

  async MonthlyUser(params = {}) {
    try{
        console.log("This API calls the Monthly Users");
        const response = await api.get('/customerkpimonthly', { params });
        return response.data;
    }catch (error){
      console.error("Error fetching monthly users:", error);
      throw error
    }

  }

  async DailyUser(params = {}) {
    try{
        console.log("This API calls the Daily Users");
        const response = await api.get('/customerkpidaily', { params });
        return response.data;
    }catch (error){
      console.error("Error fetching monthly users:", error);
      throw error
    }

  }

}

// Create and export singleton instance
const customerApiService = new CustomerApiService();

export default customerApiService;