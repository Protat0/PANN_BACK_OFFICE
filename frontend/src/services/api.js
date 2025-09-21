// services/api.js
import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
});

console.log('API Config:', {
  viteApiUrl: import.meta.env.VITE_API_URL,
  baseURL: api.defaults.baseURL,
  env: import.meta.env
});

// Request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage or sessionStorage
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add timestamp to prevent caching issues
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      };
    }
    
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 Unauthorized errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Attempt to refresh token
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/refresh/`, {
            refresh_token: refreshToken
          });
          
          const { access_token } = response.data;
          localStorage.setItem('authToken', access_token);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        sessionStorage.removeItem('authToken');
        
        // Redirect to login page
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    // Handle network errors
    if (!error.response) {
      console.error('Network error:', error.message);
      
      // Check if it's an offline scenario
      if (!navigator.onLine) {
        return Promise.reject({
          message: 'No internet connection. Request will be synced when online.',
          offline: true,
          originalRequest: originalRequest
        });
      }
    }
    
    // Handle other error status codes
    if (error.response) {
      switch (error.response.status) {
        case 400:
          console.error('Bad Request:', error.response.data);
          break;
        case 403:
          console.error('Forbidden:', error.response.data);
          break;
        case 404:
          console.error('Not Found:', error.response.data);
          break;
        case 500:
          console.error('Server Error:', error.response.data);
          break;
        default:
          console.error('API Error:', error.response.data);
      }
    }
    
    return Promise.reject(error);
  }
);

// API Service Class
class ApiService {
  // Helper method to handle responses
  handleResponse(response) {
    return response.data;
  }

  // Helper method to handle errors
  handleError(error) {
  console.log('=== FULL ERROR DEBUG ===')
  console.log('Error object:', error)
  console.log('Response status:', error.response?.status)
  
  // Force expansion of the response data object
  if (error.response?.data) {
    console.log('Response data keys:', Object.keys(error.response.data))
    console.log('Response data values:', Object.values(error.response.data))
    
    // Try different ways to see the data
    for (const [key, value] of Object.entries(error.response.data)) {
      console.log(`${key}:`, value)
    }
  }
  
  console.log('Raw response text:', error.response?.request?.responseText)
  console.log('========================')
  
  const message = error.response?.data?.error || 
                 error.response?.data?.message ||
                 JSON.stringify(error.response?.data) ||
                 error.message || 
                 'An unexpected error occurred'
  
  throw new Error(message)
}

  // AUTH METHODS
  async login(email, password) {
    try {
      const response = await api.post('/auth/login/', { email, password });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async logout() {
    try {
      const response = await api.post('/auth/logout/');
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async refreshToken(refreshToken) {
    try {
      const response = await api.post('/auth/refresh/', { refresh_token: refreshToken });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me/');
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async verifyToken(token) {
    try {
      const response = await api.post('/auth/verify-token/', { token });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  // USER METHODS
  async getUsers(params = {}) {
    try {
      const response = await api.get('/users/', { params });
      
      return {
        users: response.data.users || [],
        pagination: {
          current_page: response.data.page || 1,
          total_pages: Math.ceil((response.data.total || 0) / (params.limit || 50)),
          total_items: response.data.total || 0,
          items_per_page: params.limit || 50,
          has_next: response.data.has_more || false,
          has_previous: (response.data.page || 1) > 1
        }
      };
    } catch (error) {
      this.handleError(error);
    }
  }

  async getUser(userId) {
    try {
      const response = await api.get(`/users/${userId}/`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async createUser(userData) {
    try {
      const response = await api.post('/users/', userData);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async updateUser(userId, userData) {
    try {
      const response = await api.put(`/users/${userId}/`, userData);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async deleteUser(userId) {
    try {
      const response = await api.delete(`/users/${userId}/`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async getUserByEmail(email) {
    try {
      const response = await api.get(`/users/email/${email}/`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async getUserByUsername(username) {
    try {
      const response = await api.get(`/users/username/${username}/`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  // CUSTOMER METHODS
  async getCustomers() {
    try {
      console.log('Making API call to get customers...');
      const response = await api.get('/customers/');
      console.log('Customers API response:', response);
      return this.handleResponse(response);
    } catch (error) {
      console.error('Error in getCustomers:', error);
      this.handleError(error);
    }
  }

  async getCustomer(customerId) {
    try {
      const response = await api.get(`/customers/${customerId}/`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async createCustomer(customerData) {
    try {
      const response = await api.post('/customers/', customerData);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async updateCustomer(customerId, customerData) {
    try {
      const response = await api.put(`/customers/${customerId}/`, customerData);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async deleteCustomer(customerId) {
    try {
      const response = await api.delete(`/customers/${customerId}/`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  // SESSION METHODS
  async getActiveSessions() {
    try {
      const response = await api.get('/sessions/active/');
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async getUserSessions(userId) {
    try {
      const response = await api.get(`/sessions/user/${userId}/`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async getSessionStatistics() {
    try {
      const response = await api.get('/sessions/statistics/');
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async getSessionLogs() {
    try {
      const response = await api.get('/session-logs/');
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  // SYSTEM METHODS
  async getSystemStatus() {
    try {
      const response = await api.get('/');
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async healthCheck() {
    try {
      const response = await api.get('/health/');
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }
}

// Create and export singleton instance
const apiService = new ApiService();

// Also export the axios instance for direct use if needed
export { api };
export default apiService;