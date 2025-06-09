<template>
  <div class="app-layout">
    <!-- Sidebar Component -->
    <Sidebar 
      @menu-changed="handleMenuChange"
      @show-profile="handleShowProfile"
      @logout="handleLogout"
    />
    
    <!-- Main Content Area -->
    <main class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <!-- Header Bar -->
      <header class="content-header">
        <h1>{{ currentPageTitle }}</h1>
        
        <!-- Header Right Section with Notifications -->
        <div class="header-right">
          <!-- Notification Bell -->
          <NotificationBell />
          
          <!-- User Info -->
         
        </div>
      </header>

      <!-- Page Content - This will now show the routed component -->
      <div class="page-content">
        <router-view />
      </div>
    </main>

    <!-- Profile Modal (if needed) -->
    <div v-if="showProfileModal" class="modal-overlay" @click="closeProfileModal">
      <div class="modal-content" @click.stop>
        <h2>My Profile</h2>
        <div class="profile-info">
          <p><strong>User:</strong> {{ userInfo.full_name || 'N/A' }}</p>
          <p><strong>Email:</strong> {{ userInfo.email || 'N/A' }}</p>
          <p><strong>Role:</strong> {{ userInfo.role || 'N/A' }}</p>
        </div>
        <button @click="closeProfileModal">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
import Sidebar from '../components/Sidebar.vue'
import NotificationBell from '../components/NotificationsBell.vue'

export default {
  name: 'MainLayout',
  components: {
    Sidebar,
    NotificationBell
  },
  data() {
    return {
      sidebarCollapsed: false,
      showProfileModal: false
    }
  },
  computed: {
    currentPageTitle() {
      const titles = {
        '/dashboard': 'Dashboard',
        '/accounts': 'User Accounts',
        '/customers': 'Customers',
        '/products': 'Products',
        '/categories': 'Categories',
        '/logs': 'Inventory Logs',
        '/suppliers': 'Suppliers',
        '/promotions': 'Promotions',
        '/sales-by-item': 'Sales by Item',
        '/sales-by-category': 'Sales by Category',
        '/notifications': 'Notifications'  // Added notifications page title
      }
      return titles[this.$route.path] || 'PANN POS System'
    },
    userInfo() {
      const userData = localStorage.getItem('userData')
      return userData ? JSON.parse(userData) : {}
    },
    userInitials() {
      const name = this.userInfo.full_name || this.userInfo.username || 'U'
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    }
  },
  methods: {
    handleMenuChange(menu) {
      console.log('Menu changed to:', menu)
      // Navigate using router instead of changing currentPage
      this.$router.push(`/${menu}`)
    },
    handleShowProfile() {
      console.log('Show profile modal')
      this.showProfileModal = true
    },
    closeProfileModal() {
      this.showProfileModal = false
    },
    async handleLogout() {
      console.log('User logging out')
      
      try {
        // Call logout API
        const token = localStorage.getItem('authToken')
        if (token) {
          await fetch('http://localhost:8000/api/v1/auth/logout/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            }
          })
        }
      } catch (error) {
        console.error('Logout API error:', error)
      } finally {
        // Clear stored data
        localStorage.removeItem('authToken')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('userData')
        
        // Redirect to login
        this.$router.push('/login')
      }
    }
  },
  beforeRouteEnter(to, from, next) {
    // Check if user is authenticated before entering any protected route
    const token = localStorage.getItem('authToken')
    if (token) {
      next()
    } else {
      next('/login')
    }
  }
}
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: all 0.3s ease;
}

.content-header {
  background: white;
  padding: 2rem 2.5rem;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-header h1 {
  color: #1f2937;
  font-size: 1.875rem;
  font-weight: 600;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: #f3f4f6;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
}

.user-name {
  font-weight: 500;
  color: #374151;
  display: none;
}

.page-content {
  flex: 1;
  padding: 2.5rem;
  overflow-y: auto;
  overflow-x: hidden;
  width: 100%;
  min-width: 0;
  background-color: #f9fafb;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 400px;
  width: 90%;
}

.modal-content h2 {
  margin-bottom: 1rem;
  color: #1f2937;
}

.profile-info {
  margin: 1rem 0;
}

.profile-info p {
  margin-bottom: 0.5rem;
  color: #6b7280;
}

.modal-content button {
  background-color: #6366f1;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 1rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.modal-content button:hover {
  background-color: #4f46e5;
}

/* Responsive design */
@media (min-width: 768px) {
  .user-name {
    display: block;
  }
}

@media (max-width: 1024px) {
  .page-content {
    padding: 2rem;
  }
  
  .content-header {
    padding: 1.5rem 2rem;
  }
}

@media (max-width: 768px) {
  .page-content {
    padding: 1.5rem;
  }
  
  .content-header {
    padding: 1rem 1.5rem;
  }
  
  .content-header h1 {
    font-size: 1.5rem;
  }
  
  .header-right {
    gap: 0.5rem;
  }
  
  .user-avatar {
    width: 36px;
    height: 36px;
  }
}

@media (max-width: 480px) {
  .page-content {
    padding: 1rem;
  }
  
  .content-header {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-right {
    justify-content: space-between;
  }
}
</style>  