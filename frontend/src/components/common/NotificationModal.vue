<template>
  <transition name="notification" appear>
    <div v-if="show" class="notification-overlay" @click="handleOverlayClick">
      <div class="notification-container" :class="notificationClass" @click.stop>
        <div class="notification-header">
          <div class="notification-icon">
            <!-- Success Icon -->
            <svg v-if="type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22,4 12,14.01 9,11.01"/>
            </svg>
            
            <!-- Error Icon -->
            <svg v-else-if="type === 'error'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            
            <!-- Info Icon -->
            <svg v-else-if="type === 'info'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="16" x2="12" y2="12"/>
              <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
          </div>
          
          <div class="notification-content">
            <h3 class="notification-title">{{ title }}</h3>
            <p class="notification-message">{{ message }}</p>
          </div>
          
          <button v-if="showCloseButton" class="close-button" @click="$emit('close')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        
        <!-- Details Section (for bulk operations) -->
        <div v-if="details && (details.successful || details.failed)" class="notification-details">
          <div v-if="details.successful > 0" class="detail-item success-detail">
            <svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20,6 9,17 4,12"/>
            </svg>
            <span>{{ details.successful }} product{{ details.successful > 1 ? 's' : '' }} created successfully</span>
          </div>
          
          <div v-if="details.failed > 0" class="detail-item error-detail">
            <svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            <span>{{ details.failed }} product{{ details.failed > 1 ? 's' : '' }} failed to create</span>
          </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="notification-actions">
          <button 
            v-if="type === 'success'" 
            class="action-btn primary-btn" 
            @click="$emit('confirm')"
          >
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Add More Products
          </button>
          
          <button 
            v-if="type === 'error'" 
            class="action-btn primary-btn" 
            @click="$emit('retry')"
          >
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
              <path d="M3 3v5h5"/>
              <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/>
              <path d="M21 21v-5h-5"/>
            </svg>
            Try Again
          </button>
          
          <button class="action-btn secondary-btn" @click="$emit('close')">
            Close
          </button>
        </div>
        
        <!-- Auto-close Progress Bar -->
        <div v-if="autoClose && showProgress" class="progress-container">
          <div class="progress-bar" :style="{ width: `${progress}%` }"></div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'NotificationModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'success',
      validator: (value) => ['success', 'error', 'info', 'warning'].includes(value)
    },
    title: {
      type: String,
      required: true
    },
    message: {
      type: String,
      required: true
    },
    details: {
      type: Object,
      default: null
    },
    showCloseButton: {
      type: Boolean,
      default: true
    },
    autoClose: {
      type: Boolean,
      default: true
    },
    duration: {
      type: Number,
      default: 5000
    },
    showProgress: {
      type: Boolean,
      default: true
    },
    closeOnOverlay: {
      type: Boolean,
      default: true
    }
  },
  emits: ['close', 'confirm', 'retry'],
  data() {
    return {
      progress: 100,
      timer: null,
      progressTimer: null
    }
  },
  computed: {
    notificationClass() {
      return `notification-${this.type}`
    }
  },
  watch: {
    show(newVal) {
      if (newVal && this.autoClose) {
        this.startAutoClose()
      } else {
        this.clearTimers()
      }
    }
  },
  methods: {
    handleOverlayClick() {
      if (this.closeOnOverlay) {
        this.$emit('close')
      }
    },
    
    startAutoClose() {
      this.clearTimers()
      
      if (this.showProgress) {
        this.progress = 100
        this.progressTimer = setInterval(() => {
          this.progress -= (100 / (this.duration / 100))
          if (this.progress <= 0) {
            this.progress = 0
            clearInterval(this.progressTimer)
          }
        }, 100)
      }
      
      this.timer = setTimeout(() => {
        this.$emit('close')
      }, this.duration)
    },
    
    clearTimers() {
      if (this.timer) {
        clearTimeout(this.timer)
        this.timer = null
      }
      if (this.progressTimer) {
        clearInterval(this.progressTimer)
        this.progressTimer = null
      }
    }
  },
  mounted() {
    if (this.show && this.autoClose) {
      this.startAutoClose()
    }
  },
  beforeUnmount() {
    this.clearTimers()
  }
}
</script>

<style scoped>
.notification-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.notification-container {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 500px;
  width: 100%;
  overflow: hidden;
  position: relative;
  color: var(--tertiary-dark);
}

/* Notification Types */
.notification-success {
  border-top: 4px solid var(--success);
}

.notification-error {
  border-top: 4px solid var(--error);
}

.notification-info {
  border-top: 4px solid var(--info);
}

.notification-warning {
  border-top: 4px solid #f59e0b;
}

.notification-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.5rem;
}

.notification-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-success .notification-icon {
  background-color: var(--success-light);
  color: var(--success-dark);
}

.notification-error .notification-icon {
  background-color: var(--error-light);
  color: var(--error-dark);
}

.notification-info .notification-icon {
  background-color: var(--info-light);
  color: var(--info-dark);
}

.notification-warning .notification-icon {
  background-color: #fef3c7;
  color: #92400e;
}

.notification-icon svg {
  width: 24px;
  height: 24px;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--tertiary-dark);
  margin: 0 0 0.5rem 0;
  line-height: 1.3;
}

.notification-message {
  font-size: 0.9375rem;
  color: var(--tertiary-medium);
  margin: 0;
  line-height: 1.5;
}

.close-button {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--tertiary-medium);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background-color: var(--neutral-light);
  color: var(--tertiary-dark);
}

.close-button svg {
  width: 18px;
  height: 18px;
}

.notification-details {
  padding: 0 1.5rem;
  border-top: 1px solid var(--neutral);
  border-bottom: 1px solid var(--neutral);
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0;
  font-size: 0.875rem;
  font-weight: 500;
}

.detail-item:not(:last-child) {
  border-bottom: 1px solid var(--neutral-light);
}

.detail-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.success-detail {
  color: var(--success-dark);
}

.success-detail .detail-icon {
  color: var(--success);
}

.error-detail {
  color: var(--error-dark);
}

.error-detail .detail-icon {
  color: var(--error);
}

.notification-actions {
  display: flex;
  gap: 0.75rem;
  padding: 1.5rem;
  justify-content: flex-end;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: 0.5rem;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.primary-btn {
  background-color: var(--primary);
  color: white;
}

.primary-btn:hover {
  background-color: var(--primary-dark);
}

.secondary-btn {
  background-color: var(--neutral-medium);
  color: var(--tertiary-dark);
  border: 1px solid var(--neutral-medium);
}

.secondary-btn:hover {
  background-color: var(--neutral-dark);
  border-color: var(--neutral-dark);
}

.progress-container {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background-color: var(--neutral-light);
}

.progress-bar {
  height: 100%;
  transition: width 0.1s linear;
}

.notification-success .progress-bar {
  background-color: var(--success);
}

.notification-error .progress-bar {
  background-color: var(--error);
}

.notification-info .progress-bar {
  background-color: var(--info);
}

.notification-warning .progress-bar {
  background-color: #f59e0b;
}

/* Animations */
.notification-enter-active {
  transition: all 0.3s ease;
}

.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(-20px);
}

.notification-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(-20px);
}

/* Success Animation */
.notification-success.notification-enter-active {
  animation: successBounce 0.6s ease;
}

@keyframes successBounce {
  0% {
    opacity: 0;
    transform: scale(0.3) translateY(-50px);
  }
  50% {
    transform: scale(1.05) translateY(-10px);
  }
  70% {
    transform: scale(0.95) translateY(0);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Error Animation */
.notification-error.notification-enter-active {
  animation: errorShake 0.5s ease;
}

@keyframes errorShake {
  0%, 100% {
    opacity: 1;
    transform: translateX(0);
  }
  20%, 60% {
    transform: translateX(-10px);
  }
  40%, 80% {
    transform: translateX(10px);
  }
}

/* Responsive Design */
@media (max-width: 640px) {
  .notification-overlay {
    padding: 0.5rem;
  }
  
  .notification-container {
    max-width: 100%;
  }
  
  .notification-header {
    padding: 1rem;
  }
  
  .notification-details {
    padding: 0 1rem;
  }
  
  .notification-actions {
    padding: 1rem;
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
    justify-content: center;
  }
  
  .notification-title {
    font-size: 1.125rem;
  }
  
  .notification-message {
    font-size: 0.875rem;
  }
}

/* Focus styles for accessibility */
.action-btn:focus,
.close-button:focus {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}
</style>