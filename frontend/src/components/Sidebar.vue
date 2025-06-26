<template>
  <div class="sidebar" :class="{ 'collapsed': isCollapsed }">
    <!-- Header Section -->
    <div class="sidebar-header">
      <div class="logo">
        <img src="../assets/Logo_1.png" alt="PANN" class="logo-img" />
        <span v-if="!isCollapsed" class="text-blue">PANNTECH</span>
      </div>
      <div class="toggle-container">
        <button @click="toggleSidebar" class="toggle-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Profile Section -->
    <div class="profile-section">
      <div class="profile-item" @click="showProfile">
        <div class="profile-avatar">
          <img src="../assets/avatar.svg" alt="Profile" />
        </div>
        <span v-if="!isCollapsed" class="profile-text">My Profile</span>
        <svg v-if="!isCollapsed" class="profile-settings" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1 1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
      </div>
    </div>

    <!-- Navigation Menu -->
    <nav class="sidebar-nav">
      <ul class="nav-list">
        <!-- Dashboard -->
        <li class="nav-item" :class="{ active: activeMenu === 'dashboard' }">
          <a href="#" @click="setActiveMenu('dashboard')" class="nav-link">
            <svg class="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
            </svg>
            <span v-if="!isCollapsed" class="nav-text">Dashboard</span>
          </a>
        </li>

        <!-- Inventory -->
        <li class="nav-item" :class="{ active: activeMenu === 'inventory', expanded: expandedMenus.includes('inventory') }">
          <a href="#" @click="handleNavClick('inventory', $event)" class="nav-link">
            <svg class="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            </svg>
            <span v-if="!isCollapsed" class="nav-text">Inventory</span>
            <svg v-if="!isCollapsed" class="expand-icon" :class="{ rotated: expandedMenus.includes('inventory') }" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="6,9 12,15 18,9"/>
            </svg>
          </a>
          <ul v-if="!isCollapsed && expandedMenus.includes('inventory')" class="submenu">
            <li><a href="#" @click="setActiveMenu('products')" :class="{ active: activeMenu === 'products' }">Products</a></li>
            <li><a href="#" @click="setActiveMenu('categories')" :class="{ active: activeMenu === 'categories' }">Categories</a></li>
            <li><a href="#" @click="setActiveMenu('logs')" :class="{ active: activeMenu === 'logs' }">Logs</a></li>
          </ul>
        </li>

        <!-- Suppliers -->
        <li class="nav-item" :class="{ active: activeMenu === 'suppliers' }">
          <a href="#" @click="setActiveMenu('suppliers')" class="nav-link">
            <svg class="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            <span v-if="!isCollapsed" class="nav-text">Suppliers</span>
          </a>
        </li>

        <!-- Accounts -->
        <li class="nav-item" :class="{ active: activeMenu === 'accounts' }">
          <a href="#" @click="setActiveMenu('accounts')" class="nav-link">
            <svg class="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <span v-if="!isCollapsed" class="nav-text">Accounts</span>
          </a>
        </li>

        <!-- Promotions -->
        <li class="nav-item" :class="{ active: activeMenu === 'promotions' }">
          <a href="#" @click="setActiveMenu('promotions')" class="nav-link">
            <svg class="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="3"/>
              <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1"/>
            </svg>
            <span v-if="!isCollapsed" class="nav-text">Promotions</span>
          </a>
        </li>

        <!-- Reports -->
        <li class="nav-item" :class="{ active: activeMenu === 'reports', expanded: expandedMenus.includes('reports') }">
          <a href="#" @click="handleNavClick('reports', $event)" class="nav-link">
            <svg class="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14,2 14,8 20,8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10,9 9,9 8,9"/>
            </svg>
            <span v-if="!isCollapsed" class="nav-text">Reports</span>
            <svg v-if="!isCollapsed" class="expand-icon" :class="{ rotated: expandedMenus.includes('reports') }" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="6,9 12,15 18,9"/>
            </svg>
          </a>
          <ul v-if="!isCollapsed && expandedMenus.includes('reports')" class="submenu">
            <li><a href="#" @click="setActiveMenu('sales-by-item')" :class="{ active: activeMenu === 'sales-by-item' }">Sales by Item</a></li>
            <li><a href="#" @click="setActiveMenu('sales-by-category')" :class="{ active: activeMenu === 'sales-by-category' }">Sales by Category</a></li>
          </ul>
        </li>

        <!-- Customers -->
        <li class="nav-item" :class="{ active: activeMenu === 'customers' }">
          <a href="#" @click="setActiveMenu('customers')" class="nav-link">
            <svg class="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            <span v-if="!isCollapsed" class="nav-text">Customers</span>
          </a>
        </li>
      </ul>
    </nav>

    <!-- Logout Button -->
    <div class="sidebar-footer">
      <button @click="logout" class="logout-btn">
        <svg class="logout-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16,17 21,12 16,7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        <span v-if="!isCollapsed" class="logout-text">Logout</span>
      </button>
    </div>

    <!-- Dropdown Bubble for Collapsed Sidebar -->
    <div v-if="isCollapsed && showBubble" class="dropdown-bubble" :style="bubblePosition">
      <div class="bubble-header">{{ bubbleTitle }}</div>
      <ul class="bubble-menu">
        <li v-for="item in bubbleItems" :key="item.key">
          <a href="#" @click="selectBubbleItem(item.key)" :class="{ active: activeMenu === item.key }">
            {{ item.label }}
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Sidebar',
  data() {
    return {
      isCollapsed: false,
      activeMenu: 'dashboard',
      expandedMenus: [],
      showBubble: false,
      bubbleTitle: '',
      bubbleItems: [],
      bubblePosition: { top: '0px', left: '70px' }
    }
  },
  methods: {
    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed;
      if (this.isCollapsed) {
        this.expandedMenus = [];
        this.showBubble = false;
      }
    },
    setActiveMenu(menu) {
      this.activeMenu = menu;
      this.showBubble = false;
      this.$emit('menu-changed', menu);
    },
    handleNavClick(menu, event) {
      if (!this.isCollapsed) {
        this.toggleSubmenu(menu);
      } else {
        this.showDropdownBubble(menu, event);
      }
    },
    toggleSubmenu(menu) {
      if (this.isCollapsed) return;
      
      const index = this.expandedMenus.indexOf(menu);
      if (index > -1) {
        this.expandedMenus.splice(index, 1);
      } else {
        this.expandedMenus.push(menu);
      }
    },
    showDropdownBubble(menu, event) {
      if (!this.isCollapsed) return;
      
      const menuItems = {
        'inventory': {
          title: 'Inventory',
          items: [
            { key: 'products', label: 'Products' },
            { key: 'categories', label: 'Categories' },
            { key: 'logs', label: 'Logs' }
          ]
        },
        'reports': {
          title: 'Reports',
          items: [
            { key: 'sales-by-item', label: 'Sales by Item' },
            { key: 'sales-by-category', label: 'Sales by Category' }
          ]
        }
      };

      if (menuItems[menu]) {
        const rect = event.target.closest('.nav-link').getBoundingClientRect();
        this.bubblePosition = {
          top: `${rect.top}px`,
          left: '70px'
        };
        this.bubbleTitle = menuItems[menu].title;
        this.bubbleItems = menuItems[menu].items;
        this.showBubble = true;
      } else {
        this.setActiveMenu(menu);
      }
    },
    selectBubbleItem(item) {
      this.setActiveMenu(item);
    },
    showProfile() {
      this.showBubble = false;
      this.$emit('show-profile');
    },
    logout() {
      this.showBubble = false;
      this.$emit('logout');
    }
  },
  mounted() {
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.sidebar') && !e.target.closest('.dropdown-bubble')) {
        this.showBubble = false;
      }
    });
  }
}
</script>

<style scoped>
.sidebar {
  width: 250px;
  height: 100vh;
  background: #ffffff;
  border-right: 1px solid var(--neutral-medium);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  position: relative;
  flex-shrink: 0;
  z-index: 1000;
}

.sidebar.collapsed {
  width: 70px;
}

.sidebar-header {
  /* Fixed height to match main content header */
  height: 100px;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--neutral-medium);
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.75rem;
  box-sizing: border-box;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  justify-content: center;
}

.logo-img {
  width: 32px;
  height: 32px;
  border-radius: 8px;
}

/* .logo-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--primary);
} */

.toggle-container {
  display: flex;
  justify-content: flex-end;
}

.sidebar.collapsed .toggle-container {
  justify-content: center;
}

.toggle-btn {
  background: none;
  border: none;
  color: var(--neutral-dark);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background-color 0.2s;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-btn:hover {
  background-color: var(--neutral-light);
}

.profile-section {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--neutral-medium);
}

.sidebar.collapsed .profile-section {
  padding: 1rem 0.75rem;
}

.profile-item {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.sidebar.collapsed .profile-item {
  padding: 0.375rem;
  justify-content: center;
}

.profile-item:hover {
  background-color: var(--neutral-light);
}

.profile-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  background-color: var(--neutral-medium);
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-text {
  flex: 1;
  font-size: 0.875rem;
  color: var(--tertiary-dark);
  font-weight: 500;
}

.profile-settings {
  color: var(--neutral-dark);
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem 0;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin: 0.25rem 0;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.625rem 1rem;
  color: var(--neutral-dark);
  text-decoration: none;
  transition: all 0.2s;
  position: relative;
  margin: 0 0.75rem;
  border-radius: 8px;
}

.sidebar.collapsed .nav-link {
  justify-content: center;
  padding: 0.625rem;
  margin: 0 0.5rem;
}

.nav-link:hover {
  background-color: var(--neutral-light);
  color: var(--tertiary-dark);
}

.nav-item.active > .nav-link {
  background-color: var(--primary);
  color: white;
}

.nav-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
}

.nav-text {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 500;
}

.expand-icon {
  transition: transform 0.2s;
  width: 16px;
  height: 16px;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

.submenu {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0.75rem 0;
  background-color: var(--neutral-light);
  border-radius: 10px;
  overflow: hidden;
}

.submenu li {
  margin: 0;
}

.submenu a {
  display: block;
  padding: 0.5rem 1rem 0.5rem 2.5rem;
  color: var(--neutral-dark);
  text-decoration: none;
  font-size: 0.875rem;
  transition: all 0.2s;
  font-weight: 500;
}

.submenu a:hover {
  background-color: var(--neutral);
  color: var(--tertiary-dark);
}

.submenu a.active {
  background-color: var(--primary);
  color: white;
}

.sidebar-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--neutral-medium);
}

.sidebar.collapsed .sidebar-footer {
  padding: 1rem 0.75rem;
  display: flex;
  justify-content: center;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  width: 100%;
  padding: 0.625rem 0.875rem;
  background: none;
  border: 1px solid var(--error);
  border-radius: 8px;
  color: var(--error);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  font-weight: 500;
}

.sidebar.collapsed .logout-btn {
  padding: 0.75rem;
  justify-content: center;
  width: 44px;
  height: 44px;
  min-width: 44px;
}

.logout-btn:hover {
  background-color: var(--error);
  color: white;
}

.logout-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
}

.logout-text {
  flex: 1;
  text-align: left;
}

/* Dropdown Bubble Styles */
.dropdown-bubble {
  position: fixed;
  background: white;
  border: 1px solid var(--neutral-medium);
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  z-index: 2000;
  min-width: 180px;
  padding: 0.5rem 0;
  animation: bubbleIn 0.2s ease-out;
}

@keyframes bubbleIn {
  from {
    opacity: 0;
    transform: translateX(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

.bubble-header {
  padding: 0.75rem 1rem 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--tertiary-dark);
  border-bottom: 1px solid var(--neutral-light);
  margin-bottom: 0.25rem;
}

.bubble-menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.bubble-menu li {
  margin: 0;
}

.bubble-menu a {
  display: block;
  padding: 0.625rem 1rem;
  color: var(--neutral-dark);
  text-decoration: none;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.bubble-menu a:hover {
  background-color: var(--neutral-light);
  color: var(--tertiary-dark);
}

.bubble-menu a.active {
  background-color: var(--primary);
  color: white;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .sidebar-header {
    height: 80px; /* Slightly smaller on mobile to match header */
  }
}

@media (max-width: 480px) {
  .sidebar-header {
    height: 70px; /* Even smaller on very small screens */
  }
}
</style>