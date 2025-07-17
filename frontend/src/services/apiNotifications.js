import { api } from './api.js';

class NotificationsAPI {
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
 
  async DisplayLogs(params = {}) {
    try {
        console.log("This API call is getting All the SessionLogsData");
        const response = await api.get('/session-logs/display/');
        
        // Return the data from the response
        return response.data;
        
    } catch (error) {
        console.error("Error fetching active users:", error);
        throw error; // Re-throw so calling code can handle it
    }
  }

  async DisplayNotifs(params = {}) {
    try {
        console.log("This API call is getting All the Notifications");
        
        // Add include_archived=true to get ALL notifications for total count
        const response = await api.get('/notifications/all/?include_archived=true');
        
        // Log the response structure for debugging
        console.log('API response structure:', response);
        
        // Return the response directly since it already has the correct structure
        return response.data;
        
    } catch (error) {
        console.error("Error fetching all notifications:", error);
        throw error;
    }
  }


}

// Create and export singleton instance
const apiNotifications = new NotificationsAPI();

export default apiNotifications;