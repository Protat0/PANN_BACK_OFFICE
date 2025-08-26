<template>
  <div id="app">
    <!-- This will show either Login page or the main app based on authentication -->
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  mounted() {
    // Check authentication status when app loads
    this.checkAuthStatus()
  },
  methods: {
    checkAuthStatus() {
      const token = localStorage.getItem('authToken')  
      const currentPath = this.$route.path
      
      console.log('App mounted - Current path:', currentPath)
      console.log('App mounted - Has token:', !!token)
      console.log('App mounted - Token key used:', 'authToken')  // ✅ Update log message
      
      // If no token and not on login page, redirect to login
      if (!token && currentPath !== '/login') {
        console.log('No auth token, redirecting to login')
        this.$router.push('/login')
      }
      
      // If has token and on login page, redirect to dashboard
      if (token && currentPath === '/login') {
        console.log('Already authenticated, redirecting to dashboard')
        this.$router.push('/dashboard')
      }
    }
  }
}
</script>

<style>
/* Global reset */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow-x: hidden;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f9fafb;
}

#app {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
}
</style>