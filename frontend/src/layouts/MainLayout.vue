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
        <div class="header-content">
          <h1>{{ currentPageTitle }}</h1>
          
          <!-- Header Right Section with Notifications -->
          <div class="header-right">
            <!-- Notification Bell -->
            <NotificationBell />
            
         
          </div>
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

    <!-- Toast Container - Add this for global toast notifications -->
    <ToastContainer />
  </div>
</template>

<script>
import { useToast } from '../composables/useToast.js'
import Sidebar from '../components/Sidebar.vue'
import NotificationBell from '@/components/NotificationBell.vue'
import ToastContainer from '@/components/common/ToastContainer.vue'

export default {
  name: 'MainLayout',
  components: {
    Sidebar,
    NotificationBell,
    ToastContainer
  },
  setup() {
    // Make toast available globally in this layout if needed
    const { success, error, warning, info } = useToast()
    
    return {
      toast: { success, error, warning, info }
    }
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
        '/products/bulk': 'Add Products (Bulk)',
        '/categories': 'Categories',
        '/logs': 'Inventory Logs',
        '/suppliers': 'Suppliers',
        '/promotions': 'Promotions',
        '/sales-by-item': 'Sales by Item',
        '/sales-by-category': 'Sales by Category'
      }
      
      // Handle dynamic product detail routes
      if (this.$route.path.startsWith('/products/') && this.$route.path !== '/products/bulk') {
        return 'Product Details'
      }
      
      return titles[this.$route.path] || 'Product Details'
    },
    userInfo() {
      const userData = localStorage.getItem('userData')
      return userData ? JSON.parse(userData) : {}
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
      
      // Show logout toast
      const logoutToastId = this.toast.loading('Logging out...')
      
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
        
        // Success toast
        this.toast.dismiss(logoutToastId)
        this.toast.success('Successfully logged out', { duration: 2000 })
        
      } catch (error) {
        console.error('Logout API error:', error)
        this.toast.dismiss(logoutToastId)
        this.toast.warning('Logged out with connection issues', { duration: 3000 })
      } finally {
        // Clear stored data
        localStorage.removeItem('authToken')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('userData')
        
        // Small delay to show the toast before redirecting
        setTimeout(() => {
          // Redirect to login
          this.$router.push('/login')
        }, 1500)
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
  },
  mounted() {
    // Show welcome toast when user first loads the app (optional)
    const userData = this.userInfo
    if (userData.full_name) {
      this.toast.success(`Welcome back, ${userData.full_name}!`, {
        duration: 3000
      })
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
  position: relative; /* Added for toast positioning */
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
  /* Match sidebar header height: logo + toggle section + padding */
  height: 100px; /* This matches the sidebar header total height */
  padding: 0 2.5rem;
  border-bottom: 1px solid var(--neutral-medium);
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
  display: flex;
  align-items: center; /* Center the title vertically */
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.content-header h1 {
  color: var(--tertiary-dark);
  font-size: 1.875rem;
  font-weight: 600;
  margin: 0;
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-name {
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
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
  color: var(--tertiary-dark);
}

.profile-info {
  margin: 1rem 0;
}

.profile-info p {
  margin-bottom: 0.5rem;
  color: var(--tertiary-medium);
}

.modal-content button {
  background-color: var(--primary);
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
  background-color: var(--primary-dark);
}

/* Responsive design */
@media (max-width: 1024px) {
  .page-content {
    padding: 2rem;
  }
  
  .content-header {
    padding: 0 2rem;
  }
  
  .header-right {
    gap: 0.75rem;
  }
}

@media (max-width: 768px) {
  .page-content {
    padding: 1.5rem;
  }
  
  .content-header {
    padding: 0 1.5rem;
    height: 80px; /* Slightly smaller on mobile */
  }
  
  .content-header h1 {
    font-size: 1.5rem;
  }
  
  .header-right {
    gap: 0.5rem;
  }
  
  .user-name {
    display: none; /* Hide user name on smaller screens */
  }
}

@media (max-width: 480px) {
  .page-content {
    padding: 1rem;
  }
  
  .content-header {
    padding: 0 1rem;
    height: 70px; /* Even smaller on very small screens */
  }
  
  .content-header h1 {
    font-size: 1.25rem;
  }
  
  .header-content {
    flex-direction: row; /* Keep horizontal layout */
  }
  
  .content-header h1 {
    font-size: 1.25rem;
  }
}

/* Toast Container positioning adjustments for layout */
/* The toast container will automatically position itself in the top-right */
/* but we need to ensure it doesn't interfere with our sidebar layout */
:deep(.toast-container) {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 10000; /* Higher than modals and sidebar */
}

/* Adjust toast positioning on mobile to account for potential sidebars */
@media (max-width: 768px) {
  :deep(.toast-container) {
    top: 0.5rem;
    right: 0.5rem;
    left: 0.5rem;
    right: 0.5rem;
  }
}
</style>