/**
 * OAuth Authentication Composable
 * Handles Google and Facebook OAuth login
 */

import { ref } from 'vue';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export function useOAuth() {
  const isLoading = ref(false);
  const error = ref(null);

  /**
   * Initiate Google OAuth login
   * Redirects to backend which then redirects to Google
   */
  const loginWithGoogle = () => {
    isLoading.value = true;
    error.value = null;
    
    // Redirect to backend OAuth endpoint
    window.location.href = `${API_BASE_URL}/auth/google/`;
  };

  /**
   * Initiate Facebook OAuth login
   * Redirects to backend which then redirects to Facebook
   */
  const loginWithFacebook = () => {
    isLoading.value = true;
    error.value = null;
    
    // Redirect to backend OAuth endpoint
    window.location.href = `${API_BASE_URL}/auth/facebook/`;
  };

  /**
   * Handle OAuth callback
   * Called when user is redirected back from OAuth provider
   * 
   * @param {URLSearchParams} params - URL search params containing tokens
   * @returns {Object} - { success, accessToken, refreshToken, error }
   */
  const handleOAuthCallback = (params) => {
    const success = params.get('success') === 'true';
    const accessToken = params.get('access_token');
    const refreshToken = params.get('refresh_token');
    const errorMessage = params.get('error');

    if (success && accessToken) {
      // Store tokens in localStorage
      localStorage.setItem('access_token', accessToken);
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
      }

      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;

      return {
        success: true,
        accessToken,
        refreshToken,
        error: null
      };
    } else {
      return {
        success: false,
        accessToken: null,
        refreshToken: null,
        error: errorMessage || 'OAuth authentication failed'
      };
    }
  };

  /**
   * Disconnect OAuth provider from account
   * Requires user to have a password set as fallback
   * 
   * @param {string} userType - 'customer' or 'user'
   * @returns {Promise<Object>}
   */
  const disconnectOAuth = async (userType = 'customer') => {
    isLoading.value = true;
    error.value = null;

    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await axios.post(
        `${API_BASE_URL}/auth/oauth/disconnect/`,
        { user_type: userType },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      isLoading.value = false;
      return {
        success: true,
        message: response.data.message,
        error: null
      };

    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to disconnect OAuth';
      error.value = errorMessage;
      isLoading.value = false;

      return {
        success: false,
        message: null,
        error: errorMessage
      };
    }
  };

  /**
   * Check if user is authenticated via OAuth
   * @returns {boolean}
   */
  const isOAuthUser = () => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    return !!user.oauth_provider;
  };

  /**
   * Get OAuth provider name
   * @returns {string|null} - 'google', 'facebook', or null
   */
  const getOAuthProvider = () => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    return user.oauth_provider || null;
  };

  return {
    isLoading,
    error,
    loginWithGoogle,
    loginWithFacebook,
    handleOAuthCallback,
    disconnectOAuth,
    isOAuthUser,
    getOAuthProvider
  };
}


