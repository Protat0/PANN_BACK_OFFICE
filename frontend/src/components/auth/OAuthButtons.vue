<template>
  <div class="oauth-container">
    <!-- Divider with "OR" text -->
    <div v-if="showDivider" class="oauth-divider">
      <span>{{ dividerText }}</span>
    </div>

    <!-- OAuth Buttons -->
    <div class="oauth-buttons">
      <!-- Google Login Button -->
      <button
        @click="handleGoogleLogin"
        class="oauth-button google-button"
        :disabled="isLoading"
      >
        <svg class="oauth-icon" viewBox="0 0 24 24">
          <path
            fill="#4285F4"
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
          />
          <path
            fill="#34A853"
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          />
          <path
            fill="#FBBC05"
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
          />
          <path
            fill="#EA4335"
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
          />
        </svg>
        <span>{{ googleButtonText }}</span>
      </button>

      <!-- Facebook Login Button -->
      <button
        @click="handleFacebookLogin"
        class="oauth-button facebook-button"
        :disabled="isLoading"
      >
        <svg class="oauth-icon" viewBox="0 0 24 24">
          <path
            fill="#1877F2"
            d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"
          />
        </svg>
        <span>{{ facebookButtonText }}</span>
      </button>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="oauth-error">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useOAuth } from '@/composables/api/useOAuth';

// Props
const props = defineProps({
  showDivider: {
    type: Boolean,
    default: true
  },
  dividerText: {
    type: String,
    default: 'OR'
  },
  googleButtonText: {
    type: String,
    default: 'Continue with Google'
  },
  facebookButtonText: {
    type: String,
    default: 'Continue with Facebook'
  }
});

// Composable
const { loginWithGoogle, loginWithFacebook, isLoading, error } = useOAuth();

// Handlers
const handleGoogleLogin = () => {
  loginWithGoogle();
};

const handleFacebookLogin = () => {
  loginWithFacebook();
};
</script>

<style scoped>
.oauth-container {
  width: 100%;
  margin: 1rem 0;
}

.oauth-divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 1.5rem 0;
}

.oauth-divider::before,
.oauth-divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e0e0e0;
}

.oauth-divider span {
  padding: 0 1rem;
  color: #666;
  font-size: 0.875rem;
  font-weight: 500;
}

.oauth-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.oauth-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  color: #333;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.oauth-button:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #d0d0d0;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.oauth-button:active:not(:disabled) {
  transform: translateY(0);
}

.oauth-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.oauth-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.google-button:hover:not(:disabled) {
  background: #f8f9fa;
}

.facebook-button:hover:not(:disabled) {
  background: #f0f5ff;
}

.oauth-error {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 6px;
}

.oauth-error p {
  margin: 0;
  color: #c33;
  font-size: 0.875rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .oauth-button {
    font-size: 0.875rem;
    padding: 0.65rem 0.875rem;
  }

  .oauth-icon {
    width: 18px;
    height: 18px;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .oauth-button {
    background: #2a2a2a;
    border-color: #444;
    color: #e0e0e0;
  }

  .oauth-button:hover:not(:disabled) {
    background: #333;
    border-color: #555;
  }

  .oauth-divider::before,
  .oauth-divider::after {
    border-bottom-color: #444;
  }

  .oauth-divider span {
    color: #999;
  }
}
</style>


