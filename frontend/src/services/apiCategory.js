import { api } from './api.js';

class CategoryApiService {
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
 
  async CategoryData(params = {}) {
    try {
        console.log("This API call is getting all Category");
        const response = await api.get('/category/dataview', { params });
        
        // Return the data from the response
        return response.data;
        
    } catch (error) {
        console.error("Error fetching all category data:", error);
        throw error; // Re-throw so calling code can handle it
    }
  }
}

const categoryApiService = new CategoryApiService();
export default categoryApiService;

// Also export the class if needed for multiple instances
export { CategoryApiService };