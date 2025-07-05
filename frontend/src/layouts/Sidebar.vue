<template>
  <div class="sidebar-container" :class="{ 'collapsed': isCollapsed }">
    <!-- Sidebar Header -->
    <div class="sidebar-header">
      <div class="brand-container" v-if="!isCollapsed">
        <div class="brand-logo">
          <div class="logo-circle">
            <span class="logo-text">P</span>
          </div>
        </div>
        <div class="brand-info">
          <h5 class="brand-title">PANNTECH</h5>
          <small class="brand-subtitle">POS & Inventory</small>
        </div>
      </div>
      
      <!-- Toggle Button Row in expanded mode -->
      <div class="toggle-row" v-if="!isCollapsed">
        <button 
          class="btn btn-icon-only btn-sm sidebar-toggle"
          @click="toggleSidebar"
          :title="isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'"
        >
          <Menu :size="16" />
        </button>
      </div>
      
      <!-- Collapsed mode layout -->
      <div class="collapsed-layout" v-else>
        <!-- Stacked logo and button vertically -->
        <div class="collapsed-header-row">
          <div class="logo-circle">
            <span class="logo-text">P</span>
          </div>
          <button 
            class="btn btn-icon-only btn-sm sidebar-toggle collapsed-toggle"
            @click="toggleSidebar"
            :title="isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'"
          >
            <Menu :size="16" />
          </button>
        </div>
      </div>
    </div>

    <!-- User Profile Section -->
    <div class="user-profile" v-if="!isCollapsed">
      <div class="profile-card">
        <div class="profile-avatar">
          <User :size="20" class="text-primary" />
        </div>
        <div class="profile-info">
          <span class="profile-name">My Profile</span>
          <small class="profile-role">Administrator</small>
        </div>
        <button class="btn btn-icon-only btn-xs profile-settings">
          <Settings :size="14" />
        </button>
      </div>
    </div>

    <!-- Navigation Menu -->
    <nav class="sidebar-nav">
      <ul class="nav-list">
        <!-- Dashboard -->
        <li class="nav-item">
          <router-link 
            to="/dashboard" 
            class="nav-link"
            :class="{ 'active': isActiveRoute('/dashboard') }"
          >
            <LayoutDashboard :size="18" class="nav-icon" />
            <span class="nav-text" v-if="!isCollapsed">Dashboard</span>
            <div class="nav-indicator" v-if="isActiveRoute('/dashboard')"></div>
          </router-link>
        </li>

        <!-- Inventory Section -->
        <li class="nav-item">
          <button 
            class="nav-link nav-button"
            :class="{ 'active': showInventorySubmenu }"
            @click="toggleInventorySubmenu"
          >
            <Package :size="18" class="nav-icon" />
            <span class="nav-text" v-if="!isCollapsed">Inventory</span>
            <ChevronDown 
              :size="14" 
              class="nav-chevron" 
              :class="{ 'rotated': showInventorySubmenu }"
              v-if="!isCollapsed"
            />
          </button>
          
          <!-- Inventory Submenu -->
          <ul class="nav-submenu" v-if="showInventorySubmenu && !isCollapsed">
            <li class="nav-subitem">
              <router-link to="/products" class="nav-sublink">
                <Box :size="16" class="nav-subicon" />
                Products
              </router-link>
            </li>
            <li class="nav-subitem">
              <router-link to="/categories" class="nav-sublink">
                <FolderOpen :size="16" class="nav-subicon" />
                Categories
              </router-link>
            </li>
            <li class="nav-subitem">
              <router-link to="/logs" class="nav-sublink">
                <FileText :size="16" class="nav-subicon" />
                Logs
              </router-link>
            </li>
          </ul>
        </li>

        <!-- Suppliers -->
        <li class="nav-item">
          <router-link 
            to="/suppliers" 
            class="nav-link"
            :class="{ 'active': isActiveRoute('/suppliers') }"
          >
            <Truck :size="18" class="nav-icon" />
            <span class="nav-text" v-if="!isCollapsed">Suppliers</span>
            <div class="nav-indicator" v-if="isActiveRoute('/suppliers')"></div>
          </router-link>
        </li>

        <!-- Accounts -->
        <li class="nav-item">
          <router-link 
            to="/accounts" 
            class="nav-link"
            :class="{ 'active': isActiveRoute('/accounts') }"
          >
            <Users :size="18" class="nav-icon" />
            <span class="nav-text" v-if="!isCollapsed">Accounts</span>
            <div class="nav-indicator" v-if="isActiveRoute('/accounts')"></div>
          </router-link>
        </li>

        <!-- Promotions -->
        <li class="nav-item">
          <router-link 
            to="/promotions" 
            class="nav-link"
            :class="{ 'active': isActiveRoute('/promotions') }"
          >
            <Tag :size="18" class="nav-icon" />
            <span class="nav-text" v-if="!isCollapsed">Promotions</span>
            <div class="nav-indicator" v-if="isActiveRoute('/promotions')"></div>
          </router-link>
        </li>

        <!-- Reports Section -->
        <li class="nav-item">
          <button 
            class="nav-link nav-button"
            :class="{ 'active': showReportsSubmenu }"
            @click="toggleReportsSubmenu"
          >
            <BarChart3 :size="18" class="nav-icon" />
            <span class="nav-text" v-if="!isCollapsed">Reports</span>
            <ChevronDown 
              :size="14" 
              class="nav-chevron" 
              :class="{ 'rotated': showReportsSubmenu }"
              v-if="!isCollapsed"
            />
          </button>
          
          <!-- Reports Submenu -->
          <ul class="nav-submenu" v-if="showReportsSubmenu && !isCollapsed">
            <li class="nav-subitem">
              <router-link to="/salesbyitem" class="nav-sublink">
                <TrendingUp :size="16" class="nav-subicon" />
                Sales By Items
              </router-link>
            </li>
            <li class="nav-subitem">
              <router-link to="/salesbycategory" class="nav-sublink">
                <PieChart :size="16" class="nav-subicon" />
                Sales By Categories
              </router-link>
            </li>
          </ul>
        </li>

        <!-- Customers -->
        <li class="nav-item">
          <router-link 
            to="/customers" 
            class="nav-link"
            :class="{ 'active': isActiveRoute('/customers') }"
          >
            <UserCheck :size="18" class="nav-icon" />
            <span class="nav-text" v-if="!isCollapsed">Customers</span>
            <div class="nav-indicator" v-if="isActiveRoute('/customers')"></div>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- Sidebar Footer -->
    <div class="sidebar-footer">
      <button 
        class="btn btn-delete btn-md w-100"
        @click="handleLogout"
        v-if="!isCollapsed"
      >
        <LogOut :size="16" />
        Logout
      </button>
      <button 
        class="btn btn-delete btn-icon-only btn-md"
        @click="handleLogout"
        v-else
        title="Logout"
      >
        <LogOut :size="16" />
      </button>
    </div>
  </div>
</template>

<script>
import { 
  LayoutDashboard,
  Package,
  Truck,
  Users,
  Tag,
  BarChart3,
  UserCheck,
  User,
  Settings,
  Menu,
  X,
  ChevronDown,
  TrendingUp,
  PieChart,
  LogOut,
  Box,
  FolderOpen,
  FileText
} from 'lucide-vue-next'

export default {
  name: 'ModernSidebar',
  components: {
    LayoutDashboard,
    Package,
    Truck,
    Users,
    Tag,
    BarChart3,
    UserCheck,
    User,
    Settings,
    Menu,
    X,
    ChevronDown,
    TrendingUp,
    PieChart,
    LogOut,
    Box,
    FolderOpen,
    FileText
  },
  data() {
    return {
      isCollapsed: false,
      showInventorySubmenu: false,
      showReportsSubmenu: false
    }
  },
  methods: {
    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed
      // Emit event to parent component
      this.$emit('sidebar-toggled', this.isCollapsed)
    },
    
    toggleInventorySubmenu() {
      this.showInventorySubmenu = !this.showInventorySubmenu
    },
    
    toggleReportsSubmenu() {
      this.showReportsSubmenu = !this.showReportsSubmenu
    },
    
    isActiveRoute(route) {
      return this.$route.path.startsWith(route)
    },
    
    handleLogout() {
      // Add your logout logic here
      const confirmed = confirm('Are you sure you want to logout?')
      if (confirmed) {
        // Clear authentication
        localStorage.removeItem('auth_token')
        // Redirect to login
        this.$router.push('/login')
      }
    }
  },
  
  mounted() {
    // Load collapsed state from localStorage
    const savedState = localStorage.getItem('sidebar-collapsed')
    if (savedState !== null) {
      this.isCollapsed = JSON.parse(savedState)
      // Emit initial state to parent
      this.$emit('sidebar-toggled', this.isCollapsed)
    }
  },
  
  watch: {
    isCollapsed(newValue) {
      // Save collapsed state to localStorage
      localStorage.setItem('sidebar-collapsed', JSON.stringify(newValue))
    }
  }
}
</script>

<style scoped>
/* Sidebar Container - Fixed positioning */
.sidebar-container {
  width: 280px;
  height: 100vh;
  background-color: white;
  border-right: 1px solid var(--neutral);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  /* Enhanced shadow */
  box-shadow: 
    0 10px 15px -3px rgba(0, 0, 0, 0.15),
    0 4px 6px -2px rgba(0, 0, 0, 0.08);
}

.sidebar-container.collapsed {
  width: 80px;
}

/* Sidebar Header */
.sidebar-header {
  padding: 1.5rem 1rem;
  border-bottom: 1px solid var(--neutral);
  background-color: white;
  flex-shrink: 0;
}

.brand-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  justify-content: center;
  position: relative;
}

.brand-logo {
  position: absolute;
  left: 1rem;
}

/* Collapsed mode layout */
.collapsed-layout {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.toggle-row {
  display: flex;
  justify-content: flex-end; /* Right align the button in expanded mode */
}

.collapsed-header-row {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  gap: 0.5rem;
}

.logo-row {
  display: flex;
  justify-content: center;
  width: 100%;
  margin-bottom: 0.75rem;
}

.button-row {
  display: flex;
  justify-content: flex-end; /* Right align the button */
  width: 100%;
  padding-right: 0.25rem; /* Small padding from edge */
}

/* Collapsed toggle button styling */
.collapsed-toggle {
  margin: 0; /* Remove any default margins */
}

.logo-circle {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 8px rgba(115, 146, 226, 0.3);
}

.logo-text {
  font-weight: 700;
  font-size: 1.25rem;
  color: white;
}

.brand-title {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--primary-dark);
  margin: 0;
}

.brand-subtitle {
  color: var(--tertiary-medium);
  font-size: 0.75rem;
}

.sidebar-toggle {
  background-color: var(--neutral-light);
  border-color: var(--neutral);
  color: var(--tertiary-dark);
}

.sidebar-toggle:hover {
  background-color: var(--primary-light);
  border-color: var(--primary);
  color: var(--primary-dark);
}

/* User Profile */
.user-profile {
  padding: 1rem;
  border-bottom: 1px solid var(--neutral);
  flex-shrink: 0;
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background-color: var(--neutral-light);
  border-radius: 0.75rem;
  border: 1px solid var(--neutral);
  transition: all 0.2s ease;
}

.profile-card:hover {
  background-color: var(--primary-light);
  border-color: var(--primary);
}

.profile-avatar {
  width: 36px;
  height: 36px;
  background-color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--primary-light);
}

.profile-name {
  font-weight: 600;
  color: var(--tertiary-dark);
  font-size: 0.875rem;
}

.profile-role {
  color: var(--tertiary-medium);
  font-size: 0.75rem;
}

.profile-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.profile-settings {
  background-color: transparent;
  border-color: var(--neutral);
  color: var(--tertiary-medium);
}

.profile-settings:hover {
  background-color: var(--primary-light);
  border-color: var(--primary);
  color: var(--primary-dark);
}

/* Navigation */
.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
  overflow-x: hidden; /* Prevent horizontal scroll */
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin: 0.25rem 0.75rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  text-decoration: none;
  color: var(--tertiary-dark);
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  position: relative;
  border: 1px solid transparent;
}

.nav-button {
  background: none;
  border: 1px solid transparent;
  width: 100%;
  text-align: left;
  cursor: pointer;
}

.nav-link:hover {
  background-color: var(--primary-light);
  color: var(--primary-dark);
  border-color: var(--primary);
  transform: translateX(2px);
  box-shadow: 0 2px 4px rgba(115, 146, 226, 0.15);
}

.nav-link.active {
  background-color: var(--primary);
  color: white;
  border-color: var(--primary-dark);
  box-shadow: 0 4px 8px rgba(115, 146, 226, 0.3);
}

.nav-icon {
  flex-shrink: 0;
}

.nav-text {
  flex: 1;
  white-space: nowrap; /* Prevent text wrapping */
}

.nav-chevron {
  transition: transform 0.2s ease;
}

.nav-chevron.rotated {
  transform: rotate(180deg);
}

.nav-indicator {
  position: absolute;
  right: -1px;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 24px;
  background-color: white;
  border-radius: 2px 0 0 2px;
  box-shadow: -2px 0 4px rgba(0, 0, 0, 0.1);
}

/* Submenu */
.nav-submenu {
  list-style: none;
  padding: 0.5rem 0 0;
  margin: 0;
  margin-left: 2.5rem;
}

.nav-subitem {
  margin: 0.125rem 0;
}

.nav-sublink {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  text-decoration: none;
  color: var(--tertiary-medium);
  font-size: 0.8125rem;
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.nav-sublink:hover {
  background-color: var(--primary-light);
  color: var(--primary-dark);
}

.nav-subicon {
  flex-shrink: 0;
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid var(--neutral);
  background-color: white;
  flex-shrink: 0;
}

/* Collapsed State Adjustments */
.sidebar-container.collapsed .nav-link {
  justify-content: center;
  padding: 0.75rem;
}

.sidebar-container.collapsed .nav-item {
  margin: 0.25rem 0.5rem;
}

/* Enhanced Button Shadows for Sidebar */
.sidebar-container .btn {
  box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
}

.sidebar-container .btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.15);
}

/* Responsive Design */
@media (max-width: 768px) {
  .sidebar-container {
    transform: translateX(-100%);
  }
  
  .sidebar-container.mobile-open {
    transform: translateX(0);
  }
  
  .sidebar-container.collapsed {
    width: 280px;
  }
}

/* Scrollbar Styling */
.sidebar-nav::-webkit-scrollbar {
  width: 6px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: var(--neutral-light);
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: var(--neutral);
  border-radius: 3px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: var(--tertiary-medium);
}
</style>