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

// Request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    
    // Add debug logging
    console.log('🔍 API Interceptor - Token check:', {
      hasToken: !!token,
      tokenPreview: token ? token.substring(0, 20) + '...' : 'NO TOKEN',
      url: config.url,
      headers: config.headers
    });
   
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('✅ API Interceptor - Authorization header added');
    } else {
      console.log('❌ API Interceptor - No token found in localStorage');
    }
   
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
        // Attempt to refresh token using your backend format
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(
            `${api.defaults.baseURL}/auth/refresh/`, 
            { refresh_token: refreshToken }
          );
          
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        // Redirect to login page
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    // Handle network errors
    if (!error.response) {
      console.error('Network error:', error.message);
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

  // Helper method to handle errors - updated for your backend
  handleError(error) {
    // Handle your backend's error format
    const message = error.response?.data?.error || 
                   error.response?.data?.message || 
                   error.response?.data?.detail ||
                   error.message || 
                   'An unexpected error occurred';
    
    // Log the full error for debugging
    console.error('API Error:', {
      status: error.response?.status,
      data: error.response?.data,
      message
    });
    
    throw new Error(message);
  }

  // AUTH METHODS - Updated to match your backend
  async login(email, password) {
    try {
      console.log('🚀 API: Starting login request...')
      const response = await api.post('/auth/login/', { email, password });
      const data = this.handleResponse(response);
      
      console.log('🚀 API: Login response received:', data)
      
      // Store tokens using your backend's format
      if (data.access_token) {
        console.log('🚀 API: Storing access_token:', data.access_token.substring(0, 20) + '...')
        localStorage.setItem('access_token', data.access_token);
      } else {
        console.log('🚀 API: No access_token in response!')
      }
      
      if (data.refresh_token) {
        console.log('🚀 API: Storing refresh_token:', data.refresh_token.substring(0, 20) + '...')
        localStorage.setItem('refresh_token', data.refresh_token);
      } else {
        console.log('🚀 API: No refresh_token in response!')
      }
      
      console.log('🚀 API: Token storage complete')
      console.log('🚀 API: Verify access_token stored:', localStorage.getItem('access_token') ? 'YES' : 'NO')
      
      return data;
    } catch (error) {
      console.error('🚀 API: Login error:', error)
      this.handleError(error);
    }
  }

  // NEW: Get current user - matches your backend's get_current_user method
  async getCurrentUser() {
    try {
      console.log('👤 API: Getting current user...')
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error('No access token available');
      }
      
      // Your backend expects the token in Authorization header
      // The request interceptor will add it automatically
      const response = await api.get('/auth/me/');
      const data = this.handleResponse(response);
      
      console.log('👤 API: Current user data received:', data)
      
      // Your backend's get_current_user returns user info directly
      // Extract the user data from the response
      if (data.user_data) {
        // If backend returns nested user_data
        return {
          id: data.user_id,
          email: data.email,
          role: data.role,
          ...data.user_data
        };
      } else {
        // If backend returns user info directly
        return data;
      }
      
    } catch (error) {
      console.error('👤 API: Get current user error:', error)
      this.handleError(error);
    }
  }

  // NEW: Verify token - matches your backend's verify_token method
  async verifyToken() {
    try {
      console.log('🎫 API: Verifying token...')
      const response = await api.post('/auth/verify-token/');
      return this.handleResponse(response);
    } catch (error) {
      console.error('🎫 API: Token verification error:', error)
      this.handleError(error);
    }
  }

  // Updated logout method
  async logout() {
    try {
      console.log('🚪 API: Logging out...')
      const token = localStorage.getItem('access_token');
      
      if (token) {
        const response = await api.post('/auth/logout/', {}, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        console.log('🚪 API: Logout response:', response.data)
      }
      
      // Clear local storage regardless of API response
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      console.log('🚪 API: Tokens cleared from localStorage')
      
      return { message: 'Logged out successfully' };
    } catch (error) {
      // Clear tokens even if logout API fails
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      console.error('🚪 API: Logout error (tokens cleared anyway):', error)
      
      // Don't throw error for logout - just log it
      return { message: 'Logged out (with API error)' };
    }
  }

  // Updated refresh token method
  async refreshToken() {
    try {
      console.log('🔄 API: Refreshing token...')
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      
      const response = await api.post('/auth/refresh/', { 
        refresh_token: refreshToken 
      });
      
      const data = this.handleResponse(response);
      
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        console.log('🔄 API: New access token stored')
      }
      
      return data;
    } catch (error) {
      console.error('🔄 API: Token refresh error:', error)
      this.handleError(error);
    }
  }

  // NEW: Additional method to validate token (alias for verify)
  async validateToken() {
    return this.verifyToken();
  }

  // USERS METHODS (if you need them later)
  async getUsers(params = {}) {
    try {
      const response = await api.get('/users/', { params });
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }

  async getUserById(userId) {
    try {
      const response = await api.get(`/users/${userId}/`);
      return this.handleResponse(response);
    } catch (error) {
      this.handleError(error);
    }
  }
}

// Create and export singleton instance
const apiService = new ApiService();

export { api };
export default apiService;