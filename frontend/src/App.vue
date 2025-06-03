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
      </header>

      <!-- Page Content -->
      <div class="page-content">
        <!-- Dashboard Content (default) -->
        <Dashboard v-if="currentPage === 'dashboard'" />
        
        <!-- Inventory Pages -->
        <Products v-else-if="currentPage === 'products'" />
        <Categories v-else-if="currentPage === 'categories'" />
        <Logs v-else-if="currentPage === 'logs'" />
        
        <!-- Other Main Pages -->
        <Suppliers v-else-if="currentPage === 'suppliers'" />
        <Accounts v-else-if="currentPage === 'accounts'" />
        <Promotions v-else-if="currentPage === 'promotions'" />
        <Customers v-else-if="currentPage === 'customers'" />
        
        <!-- Reports Pages -->
        <SalesByItem v-else-if="currentPage === 'sales-by-item'" />
        <SalesByCategory v-else-if="currentPage === 'sales-by-category'" />
        
        <!-- Default fallback -->
        <div v-else class="default-content">
          <h2>Page Not Found</h2>
          <p>The requested page could not be found.</p>
        </div>
      </div>
    </main>

    <!-- Profile Modal (if needed) -->
    <div v-if="showProfileModal" class="modal-overlay" @click="closeProfileModal">
      <div class="modal-content" @click.stop>
        <h2>My Profile</h2>
        <p>Profile information would go here</p>
        <button @click="closeProfileModal">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
import Sidebar from './components/Sidebar.vue'

// Import all page components
import Dashboard from './pages/Dashboard.vue'
import Products from './pages/inventory/Products.vue'
import Categories from './pages/inventory/Categories.vue'
import Logs from './pages/inventory/Logs.vue'
import Suppliers from './pages/Suppliers.vue'
import Accounts from './pages/Accounts.vue'
import Promotions from './pages/Promotions.vue'
import SalesByItem from './pages/reports/SalesByItem.vue'
import SalesByCategory from './pages/reports/SalesByCategory.vue'
import Customers from './pages/Customers.vue'

export default {
  name: 'App',
  components: {
    Sidebar,
    Dashboard,
    Products,
    Categories,
    Logs,
    Suppliers,
    Accounts,
    Promotions,
    SalesByItem,
    SalesByCategory,
    Customers
  },
  data() {
    return {
      currentPage: 'dashboard',
      sidebarCollapsed: false,
      showProfileModal: false
    }
  },
  computed: {
    currentPageTitle() {
      const titles = {
        'dashboard': 'Dashboard',
        'products': 'Products',
        'categories': 'Categories',
        'logs': 'Inventory Logs',
        'suppliers': 'Suppliers',
        'accounts': 'Accounts',
        'promotions': 'Promotions',
        'sales-by-item': 'Sales by Item',
        'sales-by-category': 'Sales by Category',
        'customers': 'Customers'
      }
      return titles[this.currentPage] || 'POS System'
    }
  },
  methods: {
    handleMenuChange(menu) {
      console.log('Menu changed to:', menu)
      this.currentPage = menu
    },
    handleShowProfile() {
      console.log('Show profile modal')
      this.showProfileModal = true
    },
    closeProfileModal() {
      this.showProfileModal = false
    },
    handleLogout() {
      console.log('User logged out')
      alert('Logout functionality would be implemented here')
    }
  }
}
</script>

<style>
/* Global reset - but allow components to add their own padding */
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
}

.content-header h1 {
  color: #1f2937;
  font-size: 1.875rem;
  font-weight: 600;
  margin: 0;
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

.default-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.default-content h2 {
  color: #1f2937;
  margin-bottom: 1rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.default-content p {
  color: #6b7280;
  line-height: 1.6;
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
}

@media (max-width: 480px) {
  .page-content {
    padding: 1rem;
  }
  
  .content-header {
    padding: 1rem;
  }
}
</style>