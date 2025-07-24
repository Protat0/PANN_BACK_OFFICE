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

  async LoadMoreNotifications(params = {}) {
    try {
      console.log("This API call is getting More Notifications");
      
      // Build query parameters
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page);
      if (params.limit) queryParams.append('limit', params.limit);
      
      // Use the correct endpoint with query parameters
      const endpoint = `/notifications/all/?${queryParams.toString()}`;
      const response = await api.get(endpoint);
      
      // Return the data from the response
      return response.data;
      
    } catch (error) {
      console.error("Error fetching more notifications:", error);
      throw error; // Re-throw so calling code can handle it
    }
  }

  async MarkAsReadNotifications(params = {}) {
    try {
      console.log("This API call marks notification to IsRead");
      
      if (!params.id) {
        throw new Error('Notification ID is required');
      }
      
      const endpoint = `/notifications/${params.id}/mark-read/`;
      // Use PATCH to match your backend expectation
      const response = await api.patch(endpoint);

      return response.data;
      
    } catch (error) {
      console.error("Error marking notification as read:", error);
      throw error; // Re-throw so calling code can handle it
    }
  }

  async archiveNotif(params = {}) { 
    try {
      console.log("This API call marks notification as Archived");
      
      if (!params.id) {
        throw new Error('Notification ID is required');
      }
      
      const endpoint = `/notifications/${params.id}/archive/`; // Fixed: use params.id
      const response = await api.patch(endpoint);

      return response.data;
      
    } catch (error) {
      console.error("Error archiving notification:", error); // Updated error message
      throw error;
    }
  }

  async unarchiveNotif(params = {}) { 
    try {
      console.log("This API call marks notification as Unarchived");
      
      if (!params.id) {
        throw new Error('Notification ID is required');
      }
      
      const endpoint = `/notifications/${params.id}/unarchive/`; // Fixed: use params.id
      const response = await api.patch(endpoint);

      return response.data;
      
    } catch (error) {
      console.error("Error archiving notification:", error); // Updated error message
      throw error;
    }
  }

  async deleteNotif(params = {}) {
    try {
      console.log("This API call deletes notification"); // Fixed message
      
      if (!params.id) {
        throw new Error('Notification ID is required');
      }
      
      const endpoint = `/notifications/${params.id}/delete/`;
      const response = await api.delete(endpoint);

      return response.data;
      
    } catch (error) {
      console.error("Error deleting notification:", error); // Fixed error message
      throw error;
    }
  }

  async markAllReadNotif(params = {}) {
    try {
      console.log("This API call mark read as all notification"); // Fixed message
      
      const endpoint = `/notifications/mark-all-read/`;
      const response = await api.patch(endpoint);

      return response.data;
      
    } catch (error) {
      console.error("Error marking all notifications as read:", error); // Fixed error message
      throw error;
    }
  }

  async deleteNotifFallBack(params = {}){
    try {
      console.log("This API call delete is for Fall back purposes"); // Fixed message
      
      if (!params.id) {
        throw new Error('Notification ID is required');
      }
      
      const endpoint = `/notifications/${params.id}/delete/`;
      const response = await api.delete(endpoint);

      return response.data;
      
    } catch (error) {
      console.error("Error deleting notification:", error); // Fixed error message
      throw error;
    }
  }

}

// Create and export singleton instance
const apiNotifications = new NotificationsAPI();

export default apiNotifications;