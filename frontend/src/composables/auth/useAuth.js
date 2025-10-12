// composables/auth/useAuth.js
import { ref, computed, watch, readonly, nextTick } from 'vue'
import apiService from '@/services/api.js'

export function useAuth() {
  // Reactive state
  const user = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  const tokenRef = ref(localStorage.getItem('access_token'))
 
  // Computed properties
  const token = computed(() => tokenRef.value)
  const refreshToken = computed(() => localStorage.getItem('refresh_token'))
  const isAdmin = computed(() => user.value?.role === 'admin')

  const isAuthenticated = computed(() => {
    const token = localStorage.getItem('access_token')
    return !!token
  })

  // Sync token function
  const syncToken = () => {
    tokenRef.value = localStorage.getItem('access_token')
  }
 
  // Clear authentication state
  const clearAuth = () => {
    console.log('🧹 useAuth: Clearing authentication state')
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    tokenRef.value = null
    error.value = null
  }

  // ✅ NEW: Fetch current user from /auth/me/
  const fetchCurrentUser = async () => {
    console.log('👤 useAuth: Fetching current user...')
    
    if (!token.value) {
      console.log('👤 useAuth: No token available, cannot fetch user')
      return false
    }

    try {
      const userData = await apiService.getCurrentUser()
      user.value = userData
      console.log('👤 useAuth: User data loaded:', userData)
      return true
    } catch (err) {
      console.error('❌ useAuth: Failed to fetch user:', err.message)
      error.value = err.message
      clearAuth()
      return false
    }
  }

  // Initialize user from token on composable creation
  const initializeAuth = async () => {
    console.log('🚀 useAuth: Initializing auth...')
    
    if (token.value && !user.value) {
      console.log('👤 useAuth: Token exists but no user data, fetching user...')
      await fetchCurrentUser() // ✅ Fetch user data
    } else if (token.value && user.value) {
      console.log('👤 useAuth: Token and user both exist, already authenticated')
    }
  }
 
  // Login method
  const login = async (email, password) => {
    console.log('🔐 useAuth: Starting login...')
    isLoading.value = true
    error.value = null

    try {
      const response = await apiService.login(email, password)
      console.log('🔐 useAuth: Login API response:', response)
    
      // Sync token
      syncToken()
      await nextTick()

      // ✅ Fetch full user data after login
      await fetchCurrentUser()
      
      console.log('🎫 useAuth: Auth complete:', {
        tokenExists: !!token.value,
        userExists: !!user.value,
        userId: user.value?._id,
        isAuthenticated: isAuthenticated.value
      })
      
      return true
    } catch (err) {
      console.error('❌ useAuth: Login failed:', err.message)
      error.value = err.message || 'Login failed'
      clearAuth()
      return false
    } finally {
      isLoading.value = false
    }
  }
 
  // Logout method
  const logout = async () => {
    console.log('🚪 useAuth: Starting logout...')
    isLoading.value = true
    error.value = null
   
    try {
      await apiService.logout()
      console.log('✅ useAuth: Logout API successful')
    } catch (err) {
      // Log error but still clear local state
      console.error('⚠️ useAuth: Logout API error (continuing anyway):', err.message)
      error.value = err.message
    } finally {
      clearAuth()
      isLoading.value = false
      console.log('🧹 useAuth: Logout complete, state cleared')
    }
  }
 
  // Refresh token method
  const refresh = async () => {
    console.log('🔄 useAuth: Refreshing token...')
    
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }
   
    try {
      await apiService.refreshToken()
      syncToken() // Sync after refresh
      console.log('✅ useAuth: Token refreshed successfully')
      return true
    } catch (err) {
      console.error('❌ useAuth: Token refresh failed:', err.message)
      error.value = err.message || 'Token refresh failed'
      clearAuth()
      throw err
    }
  }
 
  // Validate current token
  const validateToken = async () => {
    console.log('🎫 useAuth: Validating token...')
    
    if (!token.value) {
      console.log('🎫 useAuth: No token to validate')
      return false
    }
   
    try {
      await apiService.validateToken()
      console.log('✅ useAuth: Token is valid')
      return true
    } catch (err) {
      console.error('❌ useAuth: Token validation failed:', err.message)
      clearAuth()
      return false
    }
  }
 
  // Watch for token changes and initialize user
  watch(token, async (newToken, oldToken) => {
    console.log('🔍 useAuth: Token changed:', { 
      hasNew: !!newToken, 
      hasOld: !!oldToken,
      hasUser: !!user.value 
    })
    
    if (newToken && !user.value) {
      console.log('🚀 useAuth: Token added, initializing auth...')
      await nextTick()
      await initializeAuth()
    } else if (!newToken && user.value) {
      console.log('🧹 useAuth: Token removed, clearing user...')
      user.value = null
    }
  }, { immediate: true })
 
  // Initialize on composable creation
  nextTick(() => {
    initializeAuth()
  })
 
  return {
    // State (readonly to prevent direct mutation)
    user: readonly(user),
    isLoading: readonly(isLoading),
    error: readonly(error),
   
    // Computed
    token,
    refreshToken,
    isAuthenticated,
    isAdmin,
   
    // Methods
    login,
    logout,
    refresh,
    validateToken,
    clearAuth,
    fetchCurrentUser // ✅ Export this in case you need it elsewhere
  }
}