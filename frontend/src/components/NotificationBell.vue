<!-- components/NotificationBell.vue -->
<template>
  <div class="notification-container">
    <!-- Notification Bell Icon -->
    <button 
      class="notification-bell"
      @click="toggleDropdown"
      :class="{ 'has-notifications': unreadCount > 0 }"
    >
      <span class="bell-icon">
        🔔
      </span>
      
      <!-- Notification Badge -->   
      <span 
        v-if="unreadCount > 0" 
        class="notification-badge"
      >
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>

    <!-- Notification Dropdown -->
    <div 
      v-if="showDropdown" 
      class="notification-dropdown"
      @click.stop
    >
      <!-- Header -->
      <div class="dropdown-header">
        <h3>Recent Notifications</h3>
        <div class="header-actions">
          <button 
            v-if="unreadCount > 0"
            @click="markAllAsRead"
            class="mark-all-read"
            :disabled="markingAllAsRead"
          >
            {{ markingAllAsRead ? 'Marking...' : 'Mark all read' }}
          </button>
          <button @click="showDropdown = false" class="close-btn">
            ✕
          </button>
        </div>
      </div>

      <!-- Notification List -->
      <div class="notification-list">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading notifications...</p>
        </div>

        <div v-else-if="notifications.length === 0" class="empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" class="empty-icon">
            <path d="M12 2C13.1 2 14 2.9 14 4C14 4.74 13.6 5.39 13 5.73V7C13 10.97 16.03 14 20 14V16C20 16.55 19.55 17 19 17H5C4.45 17 4 16.55 4 16V14C7.97 14 11 10.97 11 7V5.73C10.4 5.39 10 4.74 10 4C10 2.9 10.9 2 12 2Z" fill="#d1d5db"/>
          </svg>
          <p>No recent notifications</p>
        </div>

        <div v-else>
          <div 
            v-for="notification in notifications" 
            :key="notification.id"
            class="notification-item"
            :class="{ 
              'unread': !notification.is_read,
              [`priority-${notification.priority}`]: true 
            }"
            @click="markAsRead(notification)"
          >
            <!-- Priority Indicator -->
            <div class="priority-indicator" :class="`priority-${notification.priority}`"></div>
            
            <!-- Notification Content -->
            <div class="notification-content">
              <div class="notification-header">
                <h4>{{ notification.title }}</h4>
                <span class="time-ago">{{ formatTimeAgo(notification.created_at) }}</span>
              </div>
              <p class="notification-message">{{ notification.message }}</p>
              <div class="notification-meta">
                <span class="notification-type">{{ notification.notification_type || 'System' }}</span>
                <span class="priority-badge" :class="`priority-${notification.priority}`">
                  {{ formatPriority(notification.priority) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="dropdown-footer">
        <button @click="viewAllNotifications" class="view-all-btn">
          View All Notifications
        </button>
      </div>
    </div>

    <!-- Overlay to close dropdown -->
    <div 
      v-if="showDropdown" 
      class="notification-overlay"
      @click="showDropdown = false"
    ></div>

    <!-- Full Notifications Modal -->
    <div v-if="showFullModal" class="full-modal-overlay" @click="closeFullModal">
      <div class="full-modal-content" @click.stop>
        <!-- Modal Header -->
        <div class="modal-header">
          <h2>All Notifications</h2>
          <div class="header-actions">
            <!-- Bulk Actions for Unread Notifications -->
            <button 
              v-if="unreadModalCount > 0"
              @click="markAllModalAsRead"
              class="bulk-action-btn mark-all-read-btn"
              :disabled="markingAllAsRead"
            >
              {{ markingAllAsRead ? 'Marking...' : `Mark all ${unreadModalCount} as read` }}
            </button>
            <button @click="closeFullModal" class="modal-close-btn">
              ✕
            </button>
          </div>
        </div>

        <!-- Modal Filters -->
        <div class="modal-filters">
          <div class="filter-group">
            <label>Filter:</label>
            <select v-model="modalFilter" @change="applyModalFilters">
              <option value="all">All Notifications</option>
              <option value="unread">Unread Only</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Priority:</label>
            <select v-model="priorityFilter" @change="applyModalFilters">
              <option value="">All Priorities</option>
              <option value="urgent">Urgent</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Type:</label>
            <select v-model="typeFilter" @change="applyModalFilters">
              <option value="">All Types</option>
              <option value="system">System</option>
              <option value="inventory">Inventory</option>
              <option value="order">Order</option>
              <option value="payment">Payment</option>
              <option value="promotion">Promotion</option>
              <option value="alert">Alert</option>
            </select>
          </div>
        </div>

        <!-- Modal Content -->
        <div class="modal-body">
          <div v-if="modalLoading" class="loading-state">
            <div class="spinner"></div>
            <p>Loading all notifications...</p>
          </div>

          <div v-else-if="filteredModalNotifications.length === 0" class="empty-state">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" class="empty-icon">
              <path d="M12 2C13.1 2 14 2.9 14 4C14 4.74 13.6 5.39 13 5.73V7C13 10.97 16.03 14 20 14V16C20 16.55 19.55 17 19 17H5C4.45 17 4 16.55 4 16V14C7.97 14 11 10.97 11 7V5.73C10.4 5.39 10 4.74 10 4C10 2.9 10.9 2 12 2Z" fill="#d1d5db"/>
            </svg>
            <h3>No notifications found</h3>
            <p>{{ getEmptyStateMessage() }}</p>
          </div>

          <div v-else class="modal-notifications-list">
            <!-- Pagination Info -->
            <div v-if="pagination.total_count > 0" class="pagination-info">
              Showing {{ filteredModalNotifications.length }} of {{ pagination.total_count }} notifications
              <span v-if="pagination.total_pages > 1">
                (Page {{ pagination.current_page }} of {{ pagination.total_pages }})
              </span>
            </div>

            <div 
              v-for="notification in filteredModalNotifications" 
              :key="notification.id"
              class="modal-notification-item"
              :class="{ 
                'unread': !notification.is_read,
                [`priority-${notification.priority}`]: true,
                'archiving': notification.isArchiving
              }"
            >
              <!-- Priority Indicator -->
              <div class="priority-indicator" :class="`priority-${notification.priority}`"></div>
              
              <!-- Notification Content -->
              <div class="notification-content">
                <div class="notification-header">
                  <h4>{{ notification.title }}</h4>
                  <div class="notification-actions">
                    <span class="time-ago">{{ formatTimeAgo(notification.created_at) }}</span>
                    <button 
                      v-if="!notification.is_read"
                      @click="markAsRead(notification)"
                      class="action-btn mark-read-btn"
                      title="Mark as read"
                      :disabled="notification.isMarkingRead"
                    >
                      {{ notification.isMarkingRead ? '...' : '✓' }}
                    </button>
                    <!-- Archive Button (X) -->
                    <button 
                      @click="archiveNotification(notification)"
                      class="action-btn archive-btn"
                      title="Archive notification"
                      :disabled="notification.isArchiving"
                    >
                      {{ notification.isArchiving ? '...' : '✕' }}
                    </button>
                  </div>
                </div>
                <p class="notification-message">{{ notification.message }}</p>
                <div class="notification-meta">
                  <span class="notification-type">{{ notification.notification_type || 'System' }}</span>
                  <span class="priority-badge" :class="`priority-${notification.priority}`">
                    {{ formatPriority(notification.priority) }}
                  </span>
                  <span v-if="notification.metadata && notification.metadata.source" class="notification-source">
                    {{ notification.metadata.source }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Load More Button (if paginated) -->
            <div v-if="pagination.has_next" class="load-more-container">
              <button @click="loadMoreNotifications" class="load-more-btn" :disabled="loadingMore">
                {{ loadingMore ? 'Loading...' : 'Load More' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer">
          <div class="footer-stats">
            <span class="stat-item">Total: {{ pagination.total_count || 0 }}</span>
            <span class="stat-item">Unread: {{ unreadModalCount }}</span>
            <span class="stat-item">Showing: {{ filteredModalNotifications.length }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotificationBell',
  data() {
    return {
      notifications: [],
      allNotifications: [],
      filteredModalNotifications: [],
      unreadCount: 0,
      showDropdown: false,
      showFullModal: false,
      loading: false,
      modalLoading: false,
      loadingMore: false,
      markingAllAsRead: false,
      pollInterval: null,
      modalFilter: 'all',
      priorityFilter: '',
      typeFilter: '',
      pagination: {
        current_page: 1,
        total_pages: 1,
        total_count: 0,
        per_page: 50,
        has_next: false,
        has_previous: false
      }
    }
  },
  computed: {
    unreadModalCount() {
      return this.filteredModalNotifications.filter(n => !n.is_read).length;
    }
  },
  mounted() {
    // Uncomment for debugging
    this.fetchNotifications()
    this.startPolling()
  },
  beforeUnmount() {
    this.stopPolling()
  },
  methods: {
    // ================================================================
    // DATA FETCHING METHODS
    // ================================================================
    
    async fetchNotifications() {
      this.loading = true
      try {
        const response = await fetch('http://localhost:8000/api/notifications/recent', {
          headers: {
            'Content-Type': 'application/json'
          }
        })

        console.log('Recent notifications API Response status:', response.status)
        
        if (response.ok) {
          const result = await response.json()
          console.log('Recent notifications response:', result)
          
          if (result.success) {
            this.notifications = result.data || []
            this.updateUnreadCount()
          } else {
            console.error('API returned error:', result.message)
            this.notifications = []
          }
        } else {
          console.error('Failed to fetch recent notifications:', response.status, await response.text())
          this.notifications = []
        }
      } catch (error) {
        console.error('Error fetching recent notifications:', error)
        this.notifications = []
      } finally {
        this.loading = false
      }
    },

    async fetchAllNotifications() {
      this.modalLoading = true
      try {
        const response = await fetch('http://localhost:8000/api/notifications/all/?page=1&limit=50', {
          headers: {
            'Content-Type': 'application/json'
          }
        })

        if (response.ok) {
          const result = await response.json()
          console.log('All notifications response:', result)
          
          if (result.success) {
            this.allNotifications = result.data || []
            this.pagination = result.pagination || this.pagination
            this.applyModalFilters()
          } else {
            console.error('API returned error:', result.message)
            this.allNotifications = []
          }
        } else {
          console.error('Failed to fetch all notifications:', response.status, await response.text())
          this.allNotifications = []
        }
      } catch (error) {
        console.error('Error fetching all notifications:', error)
        this.allNotifications = []
      } finally {
        this.modalLoading = false
      }
    },

    async loadMoreNotifications() {
      if (!this.pagination.has_next || this.loadingMore) return
      
      this.loadingMore = true
      try {
        const nextPage = this.pagination.current_page + 1
        const response = await fetch(`http://localhost:8000/api/notifications/all/?page=${nextPage}&limit=50`, {
          headers: {
            'Content-Type': 'application/json'
          }
        })

        if (response.ok) {
          const result = await response.json()
          
          if (result.success) {
            this.allNotifications = [...this.allNotifications, ...(result.data || [])]
            this.pagination = result.pagination || this.pagination
            this.applyModalFilters()
          }
        }
      } catch (error) {
        console.error('Error loading more notifications:', error)
      } finally {
        this.loadingMore = false
      }
    },

    // ================================================================
    // UI STATE MANAGEMENT
    // ================================================================
    
    updateUnreadCount() {
      this.unreadCount = this.notifications.filter(n => !n.is_read).length
    },

    toggleDropdown() {
      this.showDropdown = !this.showDropdown
      if (this.showDropdown) {
        this.fetchNotifications() // Always fetch fresh data when opening dropdown
      }
    },

    viewAllNotifications() {
      console.log('Opening modal...')
      this.showDropdown = false
      this.showFullModal = true
      this.fetchAllNotifications()
    },

    closeFullModal() {
      console.log('Closing modal...')
      this.showFullModal = false
      this.modalFilter = 'all'
      this.priorityFilter = ''
      this.typeFilter = ''
      this.pagination.current_page = 1
    },

    // ================================================================
    // NOTIFICATION ACTIONS - INDIVIDUAL
    // ================================================================
    
    async markAsRead(notification) {
      if (notification.is_read) return

      const notificationId = notification.id || notification._id;
      
      // Vue 3 way - direct assignment
      notification.isMarkingRead = true;

      try {
        const response = await fetch(
          `http://localhost:8000/api/notifications/${notificationId}/mark-read/`,
          {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );

        if (response.ok) {
          notification.is_read = true
          this.updateUnreadCount()
          
          // Also update in modal notifications if exists
          const modalNotification = this.allNotifications.find(n => (n.id || n._id) === (notification.id || notification._id))
          if (modalNotification) {
            modalNotification.is_read = true
          }
          this.applyModalFilters()
        } else {
          console.error('Failed to mark notification as read:', await response.text())
        }
      } catch (error) {
        console.error('Error marking notification as read:', error)
      } finally {
        // Vue 3 way - direct assignment
        notification.isMarkingRead = false;
      }
    },

    async archiveNotification(notification) {
      console.log('🗂️ === FRONTEND ARCHIVE DEBUG ===');
      
      // Get the correct ID - handle both _id and id
      const notificationId = notification.id || notification._id;
      
      console.log('📋 Notification object:', notification);
      console.log('🆔 Using ID:', notificationId);
      
      if (!notificationId) {
        console.error('❌ No valid ID found for notification');
        return;
      }

      // Vue 3 way - direct assignment
      notification.isArchiving = true;

      try {
        const url = `http://localhost:8000/api/notifications/${notificationId}/archive/`;
        console.log('🌐 Archive URL:', url);
        
        const response = await fetch(url, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json'
          }
        });

        console.log('📡 Response status:', response.status);
        console.log('✅ Response ok:', response.ok);

        if (response.ok) {
          const result = await response.json();
          console.log('🎉 Archive success:', result);
          
          // Remove from both arrays using the correct ID
          this.notifications = this.notifications.filter(n => (n.id || n._id) !== notificationId);
          this.allNotifications = this.allNotifications.filter(n => (n.id || n._id) !== notificationId);
          
          // Update counts and refresh filters
          this.updateUnreadCount();
          this.applyModalFilters();
          
          console.log('✅ Archive completed successfully');
        } else {
          const errorText = await response.text();
          console.error('❌ Archive failed:', errorText);
          await this.deleteNotificationFallback(notification);
        }
      } catch (error) {
        console.error('💥 Archive error:', error);
        await this.deleteNotificationFallback(notification);
      } finally {
        // Vue 3 way - direct assignment
        notification.isArchiving = false;
      }
    },

    // ================================================================
    // NOTIFICATION ACTIONS - BULK
    // ================================================================
    
    async markAllAsRead() {
      if (this.unreadCount === 0) return
      
      this.markingAllAsRead = true
      try {
        const response = await fetch('http://localhost:8000/api/notifications/mark-all-read/', {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json'
          }
        })

        if (response.ok) {
          const result = await response.json()
          console.log('Mark all as read response:', result)
          
          // Update all notifications to read status
          this.notifications.forEach(notification => {
            notification.is_read = true
          })
          
          this.allNotifications.forEach(notification => {
            notification.is_read = true
          })
          
          // Update counts
          this.unreadCount = 0
          this.applyModalFilters()
          
        } else {
          console.error('Failed to mark all as read:', await response.text())
          await this.fallbackMarkAllAsRead()
        }
      } catch (error) {
        console.error('Error marking all notifications as read:', error)
        await this.fallbackMarkAllAsRead()
      } finally {
        this.markingAllAsRead = false
      }
    },

    async markAllModalAsRead() {
      if (this.unreadModalCount === 0) return
      
      this.markingAllAsRead = true
      try {
        const response = await fetch('http://localhost:8000/api/notifications/mark-all-read/', {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json'
          }
        })

        if (response.ok) {
          const result = await response.json()
          console.log('Modal mark all as read response:', result)
          
          // Update all notifications to read status
          this.allNotifications.forEach(notification => {
            notification.is_read = true
          })
          
          this.notifications.forEach(notification => {
            notification.is_read = true
          })
          
          // Update counts and refresh filters
          this.unreadCount = 0
          this.applyModalFilters()
          
        } else {
          console.error('Failed to mark all as read:', await response.text())
        }
      } catch (error) {
        console.error('Error marking all notifications as read:', error)
      } finally {
        this.markingAllAsRead = false
      }
    },

    // ================================================================
    // FALLBACK METHODS
    // ================================================================
    
    async fallbackMarkAllAsRead() {
      const unreadNotifications = this.notifications.filter(n => !n.is_read)
      for (const notification of unreadNotifications) {
        await this.markAsRead(notification)
      }
    },

    async deleteNotificationFallback(notification) {
      try {
        const notificationId = notification.id || notification._id;
        const response = await fetch(`http://localhost:8000/api/notifications/${notificationId}/delete/`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          // Remove from both arrays using consistent ID matching
          this.notifications = this.notifications.filter(n => (n.id || n._id) !== notificationId)
          this.allNotifications = this.allNotifications.filter(n => (n.id || n._id) !== notificationId)
          
          // Update counts and refresh filters
          this.updateUnreadCount()
          this.applyModalFilters()
          
          console.log(`Notification ${notificationId} deleted as fallback`)
        } else {
          console.error('Delete fallback also failed:', await response.text())
        }
      } catch (error) {
        console.error('Delete fallback error:', error)
      }
    },

    // ================================================================
    // FILTERING AND SEARCH
    // ================================================================
    
    applyModalFilters() {
      console.log('Applying filters:', this.modalFilter, this.priorityFilter, this.typeFilter)
      let filtered = [...this.allNotifications]

      // Apply read/unread filter
      if (this.modalFilter === 'unread') {
        filtered = filtered.filter(n => !n.is_read)
      } else if (this.modalFilter === 'today') {
        const today = new Date()
        today.setHours(0, 0, 0, 0)
        filtered = filtered.filter(n => {
          const notificationDate = new Date(n.created_at)
          return notificationDate >= today
        })
      } else if (this.modalFilter === 'week') {
        const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        filtered = filtered.filter(n => {
          const notificationDate = new Date(n.created_at)
          return notificationDate >= weekAgo
        })
      }

      // Apply priority filter
      if (this.priorityFilter) {
        filtered = filtered.filter(n => n.priority === this.priorityFilter)
      }

      // Apply type filter
      if (this.typeFilter) {
        filtered = filtered.filter(n => n.notification_type === this.typeFilter)
      }

      this.filteredModalNotifications = filtered
      console.log('Filtered notifications:', this.filteredModalNotifications.length)
    },

    // ================================================================
    // POLLING AND BACKGROUND UPDATES
    // ================================================================
    
    startPolling() {
      // Poll for new notifications every 30 seconds
      this.pollInterval = setInterval(() => {
        if (!this.showDropdown && !this.showFullModal) {
          this.fetchNotifications()
        }
      }, 30000)
    },

    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },

    // ================================================================
    // UTILITY METHODS
    // ================================================================
    
    formatTimeAgo(dateString) {
      const now = new Date()
      const notificationDate = new Date(dateString)
      const diffInSeconds = Math.floor((now - notificationDate) / 1000)

      if (diffInSeconds < 60) {
        return 'Just now'
      } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60)
        return `${minutes}m ago`
      } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600)
        return `${hours}h ago`
      } else {
        const days = Math.floor(diffInSeconds / 86400)
        return `${days}d ago`
      }
    },

    formatPriority(priority) {
      const priorities = {
        low: 'Low',
        medium: 'Medium',
        high: 'High',
        urgent: 'Urgent'
      }
      return priorities[priority] || priority
    },

    getEmptyStateMessage() {
      if (this.modalFilter === 'unread') {
        return "You're all caught up! No unread notifications."
      } else if (this.modalFilter === 'today') {
        return "No notifications from today."
      } else if (this.modalFilter === 'week') {
        return "No notifications from this week."
      } else if (this.priorityFilter) {
        return `No ${this.priorityFilter} priority notifications found.`
      } else if (this.typeFilter) {
        return `No ${this.typeFilter} notifications found.`
      }
      return "You're all caught up!"
    }
  }
}
</script>

<style scoped>
/* Existing styles preserved... */
.notification-container {
  position: relative;
}

.notification-bell {
  position: relative;
  background: none;
  border: none;
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #6b7280;
}

.notification-bell:hover {
  background-color: #f3f4f6;
  color: #374151;
}

.notification-bell.has-notifications {
  color: #6366f1;
}

.bell-icon {
  font-size: 24px;
}

.notification-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background-color: #ef4444;
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 0.75rem;
  font-weight: 600;
  min-width: 18px;
  text-align: center;
  line-height: 1.2;
}

.notification-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border: 1px solid #e5e7eb;
  width: 400px;
  max-height: 500px;
  z-index: 1000;
  overflow: hidden;
}

.notification-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.dropdown-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.mark-all-read {
  background: none;
  border: none;
  color: #6366f1;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.mark-all-read:hover:not(:disabled) {
  background-color: #e0e7ff;
}

.mark-all-read:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.close-btn {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background-color: #f3f4f6;
  color: #374151;
}

.notification-list {
  max-height: 350px;
  overflow-y: auto;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #6b7280;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  margin-bottom: 0.5rem;
}

.notification-item {
  display: flex;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.notification-item:hover {
  background-color: #f9fafb;
}

.notification-item.unread {
  background-color: #eff6ff;
}

.notification-item.unread:hover {
  background-color: #dbeafe;
}

.priority-indicator {
  width: 4px;
  border-radius: 2px;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.priority-indicator.priority-low {
  background-color: #10b981;
}

.priority-indicator.priority-medium {
  background-color: #f59e0b;
}

.priority-indicator.priority-high {
  background-color: #ef4444;
}

.priority-indicator.priority-urgent {
  background-color: #dc2626;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 0.5rem;
}

.notification-header h4 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.4;
}

.time-ago {
  font-size: 0.75rem;
  color: #6b7280;
  flex-shrink: 0;
  margin-left: 0.5rem;
}

.notification-message {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: #4b5563;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-meta {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.notification-type {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: capitalize;
}

.priority-badge {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-weight: 500;
}

.priority-badge.priority-low {
  background-color: #d1fae5;
  color: #065f46;
}

.priority-badge.priority-medium {
  background-color: #fef3c7;
  color: #92400e;
}

.priority-badge.priority-high {
  background-color: #fee2e2;
  color: #991b1b;
}

.priority-badge.priority-urgent {
  background-color: #fecaca;
  color: #7f1d1d;
}

.dropdown-footer {
  padding: 0.75rem 1.25rem;
  border-top: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.view-all-btn {
  width: 100%;
  background-color: #6366f1;
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.view-all-btn:hover {
  background-color: #4f46e5;
}

/* Full Modal Styles */
.full-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  padding: 1rem;
}

.full-modal-content {
  background: white;
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
}

.modal-header .header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

/* Enhanced Bulk Action Button */
.bulk-action-btn {
  background: #6366f1;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.bulk-action-btn:hover:not(:disabled) {
  background: #4f46e5;
  transform: translateY(-1px);
}

.bulk-action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.mark-all-read-btn {
  background: #10b981;
}

.mark-all-read-btn:hover:not(:disabled) {
  background: #059669;
}

.modal-close-btn {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close-btn:hover {
  background-color: #f3f4f6;
  color: #374151;
}

.modal-filters {
  display: flex;
  gap: 1rem;
  padding: 1rem 2rem;
  border-bottom: 1px solid #f3f4f6;
  background-color: white;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.filter-group select {
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  background: white;
  cursor: pointer;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
}

.modal-notifications-list {
  padding: 0 2rem;
}

.pagination-info {
  padding: 1rem 0;
  font-size: 0.875rem;
  color: #6b7280;
  border-bottom: 1px solid #f3f4f6;
  margin-bottom: 1rem;
}

.modal-notification-item {
  display: flex;
  padding: 1.5rem 0;
  border-bottom: 1px solid #f3f4f6;
  transition: all 0.2s;
  position: relative;
}

.modal-notification-item:hover {
  background-color: #f9fafb;
  margin: 0 -2rem;
  padding-left: 2rem;
  padding-right: 2rem;
}

.modal-notification-item.unread {
  background-color: #eff6ff;
}

.modal-notification-item.unread:hover {
  background-color: #dbeafe;
  margin: 0 -2rem;
  padding-left: 2rem;
  padding-right: 2rem;
}

.modal-notification-item.archiving {
  opacity: 0.6;
  transform: scale(0.98);
}

.modal-notification-item .notification-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 0.75rem;
}

.modal-notification-item .notification-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Enhanced Action Buttons */
.action-btn {
  background: none;
  border: 1px solid;
  border-radius: 6px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.2s;
  font-weight: 500;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mark-read-btn {
  color: #10b981;
  border-color: #10b981;
  background: white;
}

.mark-read-btn:hover:not(:disabled) {
  color: white;
  background: #10b981;
  transform: scale(1.05);
}

.archive-btn {
  color: #ef4444;
  border-color: #ef4444;
  background: white;
}

.archive-btn:hover:not(:disabled) {
  color: white;
  background: #ef4444;
  transform: scale(1.05);
}

.notification-source {
  font-size: 0.75rem;
  color: #9ca3af;
  background: #f3f4f6;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
}

.load-more-container {
  text-align: center;
  padding: 2rem 0;
}

.load-more-btn {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.load-more-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.load-more-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1.5rem 2rem;
  border-top: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.footer-stats {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.stat-item {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.stat-item:first-child {
  color: #374151;
}

@media (max-width: 768px) {
  .full-modal-content {
    max-width: 95vw;
    max-height: 95vh;
  }
  
  .modal-header {
    padding: 1rem 1.5rem;
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .modal-header .header-actions {
    justify-content: space-between;
  }
  
  .modal-filters {
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem 1.5rem;
  }
  
  .modal-notifications-list {
    padding: 0 1.5rem;
  }
  
  .modal-footer {
    padding: 1rem 1.5rem;
  }
  
  .footer-stats {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
  
  .notification-actions {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .bulk-action-btn {
    font-size: 0.75rem;
    padding: 0.4rem 0.8rem;
  }
}
</style>