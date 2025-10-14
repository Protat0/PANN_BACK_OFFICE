// services/apiUsers.js
import { api } from './api'

/**
 * User Management API Client
 * Base URL: /api/v1/users/
 * All methods automatically include authentication via api.js interceptor
 */
class UserApiService {
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
    
    console.error('User API Error:', {
      status: error.response?.status,
      data: error.response?.data,
      message
    });
    
    throw new Error(message);
  }

  /**
   * Get all users with pagination and filters
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number (default: 1)
   * @param {number} params.limit - Items per page (default: 50)
   * @param {string} params.status - Filter by status (active, disabled)
   * @param {boolean} params.include_deleted - Include soft-deleted users
   */
  async getAll(params = {}) {
    try {
      const response = await api.get('/users/', { params });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get user by ID
   * @param {string} userId - User ID (USER-####)
   * @param {boolean} includeDeleted - Include if soft-deleted
   */
  async getById(userId, includeDeleted = false) {
    try {
      const params = includeDeleted ? { include_deleted: true } : {};
      const response = await api.get(`/users/${userId}/`, { params });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get user by email
   * @param {string} email - User email
   * @param {boolean} includeDeleted - Include if soft-deleted
   */
  async getByEmail(email, includeDeleted = false) {
    try {
      const params = includeDeleted ? { include_deleted: true } : {};
      const response = await api.get(`/users/email/${email}/`, { params });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get user by username
   * @param {string} username - Username
   * @param {boolean} includeDeleted - Include if soft-deleted
   */
  async getByUsername(username, includeDeleted = false) {
    try {
      const params = includeDeleted ? { include_deleted: true } : {};
      const response = await api.get(`/users/username/${username}/`, { params });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get all soft-deleted users
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number
   * @param {number} params.limit - Items per page
   */
  async getDeleted(params = {}) {
    try {
      const response = await api.get('/users/deleted/', { params });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Create new user
   * @param {Object} userData - User data
   * @param {string} userData.username - Username
   * @param {string} userData.email - Email
   * @param {string} userData.password - Password
   * @param {string} userData.full_name - Full name
   * @param {string} userData.role - Role (admin, employee, etc.)
   * @param {string} userData.status - Status (active, disabled)
   */
  async create(userData) {
    try {
      const response = await api.post('/users/', userData);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Update user
   * @param {string} userId - User ID (USER-####)
   * @param {Object} userData - Updated user data
   */
  async update(userId, userData) {
    try {
      const response = await api.put(`/users/${userId}/`, userData);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Soft delete user (can be restored)
   * @param {string} userId - User ID (USER-####)
   */
  async softDelete(userId) {
    try {
      const response = await api.delete(`/users/${userId}/`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Restore soft-deleted user
   * @param {string} userId - User ID (USER-####)
   */
  async restore(userId) {
    try {
      const response = await api.post(`/users/${userId}/restore/`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Permanently delete user (IRREVERSIBLE)
   * @param {string} userId - User ID (USER-####)
   */
  async hardDelete(userId) {
    try {
      const response = await api.delete(`/users/${userId}/hard-delete/?confirm=yes`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }
}

// Create and export singleton instance
const userApiService = new UserApiService();

export default userApiService;