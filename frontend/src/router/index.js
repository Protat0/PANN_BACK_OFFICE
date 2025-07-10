import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

// Import authentication and layout components
import Login from '../pages/Login.vue'
import MainLayout from '../layouts/MainLayout.vue'

// Import your page components
import Dashboard from '../pages/Dashboard.vue'
import Accounts from '../pages/Accounts.vue'
import Customers from '../pages/Customers.vue'
import Products from '@/pages/inventory/Products.vue'
import ProductBulkEntry from '@/pages/inventory/ProductBulkEntry.vue'
import ProductDetails from '@/pages/inventory/ProductDetails.vue'
import Categories from '@/pages/inventory/Categories.vue'
import CategoryDetails from '@/pages/inventory/CategoryDetails.vue'
import SalesByItem from '@/pages/reports/SalesByItem.vue'
import SalesByCategory from '@/pages/reports/SalesByCategory.vue'
import UncategorizedProducts from '@/components/categories/UncategorizedProducts.vue'
import Logs from '@/pages/Logs.vue'
import AllNotifications from '@/pages/notifications/AllNotifications.vue'

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
          props: true // This passes the route params as props to the component
        },
        {
          path: 'categories',
          name: 'Categories',
          component: Categories
        },
        {
          path: 'category/:id', // Change this line
          name: 'Category Details',
          component: CategoryDetails,
          props: true
        },
        {
          path: 'home',
          name: 'home',
          component: HomeView
        },
        {
          path: 'salesbyitem',
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
  next()
})

export default router