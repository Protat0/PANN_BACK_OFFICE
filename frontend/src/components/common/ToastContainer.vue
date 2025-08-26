<template>
  <Teleport to="body">
    <div
      v-if="toasts.length > 0"
      class="toast-container"
      aria-live="polite"
      aria-label="Notifications"
    >
      <TransitionGroup
        name="toast-list"
        tag="div"
        class="toast-list"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'toast-notification',
            `toast-${toast.type}`,
            { 'toast-dismissible': toast.dismissible }
          ]"
          role="alert"
          aria-live="polite"
        >
          <!-- Icon Section -->
          <div class="toast-icon">
            <CheckCircle v-if="toast.type === 'success'" :size="20" />
            <AlertCircle v-else-if="toast.type === 'error'" :size="20" />
            <AlertTriangle v-else-if="toast.type === 'warning'" :size="20" />
            <Info v-else :size="20" />
          </div>
          
          <!-- Content Section -->
          <div class="toast-content">
            <div class="toast-message">{{ toast.message }}</div>
          </div>
          
          <!-- Close Button -->
          <button
            v-if="toast.dismissible"
            class="toast-close"
            type="button"
            aria-label="Close notification"
            @click="removeToast(toast.id)"
          >
            <X :size="16" />
          </button>
          
          <!-- Progress Bar -->
          <div
            v-if="toast.showProgressBar && !toast.persistent"
            class="toast-progress-container"
          >
            <div
              class="toast-progress-bar"
              :style="{ 
                animationDuration: `${toast.duration}ms`,
                animationPlayState: toast.paused ? 'paused' : 'running'
              }"
            ></div>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script>
import { useToast } from '@/composables/useToast.js'
import { CheckCircle, AlertCircle, AlertTriangle, Info, X } from 'lucide-vue-next'

export default {
  name: 'ToastContainer',
  components: {
    CheckCircle,
    AlertCircle,
    AlertTriangle,
    Info,
    X
  },
  setup() {
    const { toasts, removeToast } = useToast()
    
    return {
      toasts,
      removeToast
    }
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 9999;
  pointer-events: none;
}

.toast-list {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.toast-list > * {
  pointer-events: auto;
}

.toast-notification {
  position: relative;
  display: flex;
  align-items: center;
  min-width: 300px;
  max-width: 500px;
  padding: 1rem 1.25rem;
  background-color: var(--surface-elevated);
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border-left: 4px solid;
  overflow: hidden;
  transition: all 0.3s ease;
}

/* Toast Types */
.toast-success {
  border-left-color: var(--status-success);
  background-color: #f0f9f4;
}

.toast-error {
  border-left-color: var(--status-error);
  background-color: #fef2f2;
}

.toast-warning {
  border-left-color: var(--status-warning);
  background-color: #fffbeb;
}

.toast-info {
  border-left-color: var(--status-info);
  background-color: #f0f4ff;
}

/* Dark theme adjustments */
.dark-theme .toast-success {
  background-color: rgba(34, 197, 94, 0.1);
}

.dark-theme .toast-error {
  background-color: rgba(239, 68, 68, 0.1);
}

.dark-theme .toast-warning {
  background-color: rgba(245, 158, 11, 0.1);
}

.dark-theme .toast-info {
  background-color: rgba(59, 130, 246, 0.1);
}

/* Icon Section */
.toast-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 0.75rem;
}

.toast-success .toast-icon {
  color: var(--status-success);
}

.toast-error .toast-icon {
  color: var(--status-error);
}

.toast-warning .toast-icon {
  color: var(--status-warning);
}

.toast-info .toast-icon {
  color: var(--status-info);
}

/* Content Section */
.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-message {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--tertiary-dark);
  line-height: 1.4;
  word-wrap: break-word;
}

/* Close Button */
.toast-close {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  margin-left: 0.75rem;
  background: none;
  border: none;
  border-radius: 0.25rem;
  color: var(--tertiary-medium);
  cursor: pointer;
  transition: all 0.2s ease;
}

.toast-close:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: var(--tertiary-dark);
}

.toast-close:focus {
  outline: 2px solid var(--border-accent);
  outline-offset: 1px;
}

/* Progress Bar Container */
.toast-progress-container {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background-color: rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.dark-theme .toast-progress-container {
  background-color: rgba(255, 255, 255, 0.1);
}

/* Progress Bar Animation - Right to Left Movement */
.toast-progress-bar {
  height: 100%;
  width: 100%;
  transform-origin: right center;
  animation: progress-right-to-left linear forwards;
}

/* Use width-based animation for clearer right-to-left movement */
@keyframes progress-right-to-left {
  0% {
    width: 100%;
  }
  100% {
    width: 0%;
  }
}

/* Alternative transform-based animation (more performant) */
@keyframes progress-shrink-right {
  0% {
    transform: scaleX(1);
  }
  100% {
    transform: scaleX(0);
  }
}

/* Progress bar colors with fallbacks */
.toast-success .toast-progress-bar {
  background-color: var(--status-success, #22c55e);
}

.toast-error .toast-progress-bar {
  background-color: var(--status-error, #ef4444);
}

.toast-warning .toast-progress-bar {
  background-color: var(--status-warning, #f59e0b);
}

.toast-info .toast-progress-bar {
  background-color: var(--status-info, #3b82f6);
}

/* Toast Transitions */
.toast-list-move,
.toast-list-enter-active,
.toast-list-leave-active {
  transition: all 0.3s ease;
}

.toast-list-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}

.toast-list-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}

.toast-list-leave-active {
  position: absolute;
  right: 0;
}

/* Hover to pause progress */
.toast-notification:hover .toast-progress-bar {
  animation-play-state: paused;
}

/* Responsive Design */
@media (max-width: 576px) {
  .toast-container {
    top: 0.5rem;
    right: 0.5rem;
    left: 0.5rem;
  }
  
  .toast-notification {
    min-width: 100%;
    max-width: 100%;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .toast-notification,
  .toast-progress-bar,
  .toast-list-move,
  .toast-list-enter-active,
  .toast-list-leave-active {
    animation: none !important;
    transition: none !important;
  }
}
</style>