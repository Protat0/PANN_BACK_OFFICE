// services/apiProducts.js - UPDATED VERSION
import { api } from './api.js';

class SessionLogsAPI {
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

  async SearchLogs(params = {}) {
    try {
        console.log("This API will fetch specific Log");
        const response = await api.get('/session-logs/display/');
        
        // Return the data from the response
        return response.data;
        
    } catch (error) {
        console.error("Error fetching active users:", error);
        throw error; // Re-throw so calling code can handle it
    }
  }

  async getLogsPaginated(params = {}) {
    const {
      page = 1,
      limit = 25,
      category = 'all',
      search = '',
      startDate = null,
      endDate = null,
      sortBy = 'timestamp',
      sortOrder = 'desc'
    } = params

    const queryParams = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      sortBy,
      sortOrder
    })

    // Add filters only if they're set
    if (category !== 'all') queryParams.append('category', category)
    if (search) queryParams.append('search', search)
    if (startDate) queryParams.append('startDate', startDate)
    if (endDate) queryParams.append('endDate', endDate)

    try {
      const response = await fetch(`${this.baseURL}/paginated?${queryParams}`)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      // Expected server response format:
      // {
      //   logs: [...],
      //   pagination: {
      //     currentPage: 1,
      //     totalPages: 45,
      //     totalRecords: 1123,
      //     hasNext: true,
      //     hasPrev: false
      //   }
      // }
      
      return data
    } catch (error) {
      console.error('Error fetching paginated logs:', error)
      throw error
    }
  }

   async getLogsSince(timestamp, limit = 50) {
    try {
      const response = await fetch(`${this.baseURL}/since?timestamp=${timestamp}&limit=${limit}`)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error fetching incremental logs:', error)
      throw error
    }
  }
  
  async getMultiplePages(startPage, endPage, otherParams = {}) {
    const promises = []
    
    for (let page = startPage; page <= endPage; page++) {
      promises.push(this.getLogsPaginated({ ...otherParams, page }))
    }

    try {
      const results = await Promise.all(promises)
      
      // Combine all logs from different pages
      const allLogs = results.flatMap(result => result.logs || [])
      
      // Return combined result with total pagination info
      return {
        logs: allLogs,
        pagination: results[0]?.pagination || {}
      }
    } catch (error) {
      console.error('Error fetching multiple pages:', error)
      throw error
    }
  }

  async searchLogs(query, options = {}) {
    const {
      page = 1,
      limit = 25,
      fields = ['user_id', 'event_type', 'remarks'],
      exactMatch = false
    } = options

    const queryParams = new URLSearchParams({
      q: query,
      page: page.toString(),
      limit: limit.toString(),
      fields: fields.join(','),
      exact: exactMatch.toString()
    })

    try {
      const response = await fetch(`${this.baseURL}/search?${queryParams}`)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error searching logs:', error)
      throw error
    }
  }

    /**
   * Get combined session and audit logs
   * @param {Object} params - Query parameters (limit, type)
   * @returns {Promise<Object>} Combined logs data
   */
  async DisplayCombinedLogs(params = {}) {
    try {
        console.log("This API call is getting combined session and audit logs");
        
        const queryParams = new URLSearchParams();
        if (params.limit) queryParams.append('limit', params.limit);
        if (params.type) queryParams.append('type', params.type);
        
        const response = await api.get(`/session-logs/combined/?${queryParams}`);
        return response.data;
        
    } catch (error) {
        console.error("Error fetching combined logs:", error);
        throw error;
    }
  }

  /**
   * Get only session logs (existing functionality preserved)
   */
  async DisplaySessionLogsOnly(params = {}) {
    try {
        console.log("This API call is getting session logs only");
        return await this.DisplayCombinedLogs({ ...params, type: 'session' });
    } catch (error) {
        console.error("Error fetching session logs:", error);
        throw error;
    }
  }

  /**
   * Get only audit logs
   */
  async DisplayAuditLogsOnly(params = {}) {
    try {
        console.log("This API call is getting audit logs only");
        return await this.DisplayCombinedLogs({ ...params, type: 'audit' });
    } catch (error) {
        console.error("Error fetching audit logs:", error);
        throw error;
    }
  }

}

// Create and export singleton instance
const apiLogs = new SessionLogsAPI();

export default apiLogs;