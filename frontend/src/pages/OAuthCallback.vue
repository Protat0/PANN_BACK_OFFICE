<template>
  <div class="oauth-callback-container">
    <div class="callback-card">
      <!-- Loading State -->
      <div v-if="isProcessing" class="processing-state">
        <div class="spinner"></div>
        <h2>Completing your login...</h2>
        <p>Please wait while we finalize your authentication</p>
      </div>

      <!-- Success State -->
      <div v-else-if="success" class="success-state">
        <div class="success-icon">✓</div>
        <h2>Login Successful!</h2>
        <p>Redirecting you to the dashboard...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">✗</div>
        <h2>Login Failed</h2>
        <p>{{ error }}</p>
        <button @click="goToLogin" class="retry-button">
          Back to Login
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useOAuth } from '@/composables/api/useOAuth';
import axios from 'axios';

const router = useRouter();
const route = useRoute();

const { handleOAuthCallback } = useOAuth();

const isProcessing = ref(true);
const success = ref(false);
const error = ref(null);

onMounted(async () => {
  // Get URL parameters
  const params = new URLSearchParams(window.location.search);

  // Process OAuth callback
  const result = handleOAuthCallback(params);

  if (result.success) {
    success.value = true;
    
    // Fetch user profile
    try {
      const response = await axios.get('/auth/me/', {
        headers: {
          'Authorization': `Bearer ${result.accessToken}`
        }
      });

      if (response.data.success) {
        // Store user data
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        // Redirect to dashboard after 1.5 seconds
        setTimeout(() => {
          router.push('/dashboard');
        }, 1500);
      } else {
        throw new Error('Failed to fetch user profile');
      }
    } catch (err) {
      console.error('Failed to fetch user profile:', err);
      // Still redirect to dashboard, profile will be fetched there
      setTimeout(() => {
        router.push('/dashboard');
      }, 1500);
    }
  } else {
    error.value = result.error;
    isProcessing.value = false;
  }
});

const goToLogin = () => {
  router.push('/login');
};
</script>

<style scoped>
.oauth-callback-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.callback-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  padding: 3rem;
  max-width: 450px;
  width: 100%;
  text-align: center;
}

/* Processing State */
.processing-state h2 {
  margin: 1.5rem 0 0.5rem;
  color: #333;
  font-size: 1.5rem;
}

.processing-state p {
  color: #666;
  margin: 0;
}

.spinner {
  width: 60px;
  height: 60px;
  margin: 0 auto;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Success State */
.success-state .success-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1rem;
  background: #4caf50;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  font-weight: bold;
  animation: scaleIn 0.5s ease;
}

@keyframes scaleIn {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.success-state h2 {
  margin: 0 0 0.5rem;
  color: #333;
  font-size: 1.5rem;
}

.success-state p {
  color: #666;
  margin: 0;
}

/* Error State */
.error-state .error-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1rem;
  background: #f44336;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  font-weight: bold;
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-10px);
  }
  75% {
    transform: translateX(10px);
  }
}

.error-state h2 {
  margin: 0 0 0.5rem;
  color: #333;
  font-size: 1.5rem;
}

.error-state p {
  color: #666;
  margin: 0 0 1.5rem;
}

.retry-button {
  padding: 0.75rem 2rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-button:hover {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.retry-button:active {
  transform: translateY(0);
}

/* Responsive Design */
@media (max-width: 768px) {
  .callback-card {
    padding: 2rem;
  }

  .processing-state h2,
  .success-state h2,
  .error-state h2 {
    font-size: 1.25rem;
  }

  .success-icon,
  .error-icon {
    width: 60px;
    height: 60px;
    font-size: 2.5rem;
  }
}
</style>

