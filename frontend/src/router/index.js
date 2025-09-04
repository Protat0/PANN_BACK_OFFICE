import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

import Login from '../pages/Login.vue'
import MainLayout from '../layouts/MainLayout.vue'

import Dashboard from '../pages/Dashboard.vue'
import Accounts from '../pages/Accounts.vue'
import Customers from '../pages/Customers.vue'
import Products from '@/pages/inventory/Products.vue'
import ProductBulkEntry from '@/pages/inventory/ProductBulkEntry.vue'
import ProductDetails from '@/pages/inventory/ProductDetails.vue'
import Categories from '@/pages/inventory/Categories.vue'
import CategoryDetails from '@/pages/inventory/CategoryDetails.vue'
import Promotions from '@/pages/Promotions.vue'
import SalesByItem from '@/pages/reports/SalesByItem.vue'
import SalesByCategory from '@/pages/reports/SalesByCategory.vue'
import UncategorizedProducts from '@/components/categories/UncategorizedProducts.vue'
import Logs from '@/pages/Logs.vue'
import AllNotifications from '@/pages/notifications/AllNotifications.vue'
import TesterPage from '@/pages/TesterPage.vue'
import Suppliers from '@/pages/suppliers/Suppliers.vue'
import SupplierDetails from '@/pages/suppliers/SupplierDetails.vue'
import OrdersHistory from '@/pages/suppliers/OrdersHistory.vue'

// Debug components (only for development)
import ToastDebug from '@/pages/ToastDebug.vue'

// Auth guard function
function requireAuth(to, from, next) {
  const token = localStorage.getItem('authToken')
  if (token) {
    next() // User is authenticated, proceed
  } else {
    console.log('Auth required, redirecting to login')
    next('/login') // Redirect to login
  }
}

// Guest guard function (redirect authenticated users away from login)
function requireGuest(to, from, next) {
  const token = localStorage.getItem('authToken')
  if (!token) {
    next() // User is not authenticated, proceed to login
  } else {
    console.log('Already authenticated, redirecting to dashboard')
    next('/dashboard') // Redirect to dashboard if already logged in
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login' // Make Login the default page
    },
    {
      path: '/login',
      name: 'Login',
      component: Login,
      beforeEnter: requireGuest // Only allow access if not logged in
    },
    // Protected routes that use the main layout
    {
      path: '/',
      component: MainLayout,
      beforeEnter: requireAuth,
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: Dashboard
        },
        {
          path: 'accounts',
          name: 'Accounts',
          component: Accounts
        },
        {
          path: 'customers',
          name: 'Customers',
          component: Customers
        },
        // Inventory routes
        {
          path: 'products',
          name: 'Products',
          component: Products
        },
        {
          path: 'products/bulk',
          name: 'ProductBulkEntry',
          component: ProductBulkEntry
        },
        {
          path: 'products/:id',
          name: 'ProductDetails',
          component: ProductDetails,
          props: true
        },
        {
          path: 'categories',
          name: 'Categories',
          component: Categories
        },
        {
          path: 'category/:id',
          name: 'Category Details',
          component: CategoryDetails,
          props: true
        },
        // Suppliers routes
        {
          path: 'suppliers',
          name: 'Suppliers',
          component: Suppliers
        },
        {
          path: 'suppliers/orders',
          name: 'OrdersHistory',
          component: OrdersHistory,
          meta: {
            title: 'Purchase Orders History',
            breadcrumb: [
              { name: 'Dashboard', path: '/dashboard' },
              { name: 'Suppliers', path: '/suppliers' },
              { name: 'Orders History', path: null }
            ]
          }
        },
        {
          path: 'suppliers/:supplierId',
          name: 'SupplierDetails',
          component: SupplierDetails,
          props: true, // This passes the route params as props to the component
          meta: {
            title: 'Supplier Details',
            breadcrumb: [
              { name: 'Dashboard', path: '/dashboard' },
              { name: 'Suppliers', path: '/suppliers' },
              { name: 'Details', path: null }
            ]
          }
        },
        // Debug routes (development only)
        {
          path: 'debug/toast',
          name: 'ToastDebug',
          component: ToastDebug,
          meta: {
            title: 'Toast Debug',
            isDevelopmentOnly: true
          }
        },
        // Other routes
        {
          path: 'home',
          name: 'home',
          component: HomeView
        },
        {
          path: 'promotions',
          name: 'Promotions',
          component: Promotions
        },
        {
          path: 'sales-by-item',
          name: 'SalesByItem',
          component: SalesByItem
        },
        {
          path: 'salesbycategory',
          name: 'SalesByCategory',
          component: SalesByCategory
        },
        {
          path: 'about',
          name: 'about',
          component: () => import('../views/AboutView.vue')
        },
        {
          path: 'logs',
          name: 'Logs',
          component: Logs
        },
        {
          path: 'uncategorized',
          name: 'UncategorizedProducts',
          component: UncategorizedProducts
        },
        {
          path: 'allNotifications',
          name: 'AllNotifications',
          component: AllNotifications
        },
        {
          path: 'tester',
          name: 'TesterPage',
          component: TesterPage
        }
      ]
    },
    // Catch all route - redirect to login
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login'
    }
  ],
})

// Global navigation guard for debugging
router.beforeEach((to, from, next) => {
  console.log(`Navigating from ${from.path} to ${to.path}`)
  
  // Optional: Set page title based on route meta
  if (to.meta && to.meta.title) {
    document.title = `${to.meta.title} - Your App Name`
  }
  
  next()
})

export default router