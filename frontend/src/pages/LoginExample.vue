<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <!-- Logo/Header -->
        <div class="login-header">
          <h1>Welcome Back</h1>
          <p>Sign in to your account</p>
        </div>

        <!-- OAuth Login Buttons -->
        <OAuthButtons
          :showDivider="false"
          googleButtonText="Sign in with Google"
          facebookButtonText="Sign in with Facebook"
        />

        <!-- Divider -->
        <div class="divider">
          <span>Or continue with email</span>
        </div>

        <!-- Traditional Login Form -->
        <form @submit.prevent="handleLogin" class="login-form">
          <!-- Email Input -->
          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="email"
              type="email"
              placeholder="Enter your email"
              required
              :disabled="isLoading"
            />
          </div>

          <!-- Password Input -->
          <div class="form-group">
            <label for="password">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="Enter your password"
              required
              :disabled="isLoading"
            />
          </div>

          <!-- Remember Me & Forgot Password -->
          <div class="form-options">
            <label class="checkbox-label">
              <input type="checkbox" v-model="rememberMe" />
              <span>Remember me</span>
            </label>
            <router-link to="/forgot-password" class="forgot-link">
              Forgot password?
            </router-link>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="error-message">
            {{ error }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            class="submit-button"
            :disabled="isLoading"
          >
            <span v-if="!isLoading">Sign In</span>
            <span v-else>Signing in...</span>
          </button>
        </form>

        <!-- Sign Up Link -->
        <div class="signup-link">
          Don't have an account?
          <router-link to="/register">Sign up</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import OAuthButtons from '@/components/auth/OAuthButtons.vue';
import axios from 'axios';

const router = useRouter();

// Form data
const email = ref('');
const password = ref('');
const rememberMe = ref(false);
const isLoading = ref(false);
const error = ref(null);

// Handle traditional login
const handleLogin = async () => {
  error.value = null;
  isLoading.value = true;

  try {
    const response = await axios.post('/auth/login/', {
      email: email.value,
      password: password.value
    });

    if (response.data.success || response.data.access_token) {
      // Store tokens
      const accessToken = response.data.access_token;
      const refreshToken = response.data.refresh_token;

      localStorage.setItem('access_token', accessToken);
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
      }

      // Store user data
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }

      // Set default axios header
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;

      // Redirect to dashboard
      router.push('/dashboard');
    } else {
      error.value = 'Login failed. Please try again.';
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Invalid email or password';
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.login-container {
  width: 100%;
  max-width: 450px;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  padding: 2.5rem;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-header h1 {
  margin: 0 0 0.5rem;
  color: #333;
  font-size: 1.875rem;
  font-weight: 700;
}

.login-header p {
  margin: 0;
  color: #666;
  font-size: 0.95rem;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 1.5rem 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e0e0e0;
}

.divider span {
  padding: 0 1rem;
  color: #666;
  font-size: 0.875rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: #333;
  font-size: 0.875rem;
  font-weight: 600;
}

.form-group input {
  padding: 0.75rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: #666;
  font-size: 0.875rem;
}

.checkbox-label input[type="checkbox"] {
  cursor: pointer;
}

.forgot-link {
  color: #667eea;
  font-size: 0.875rem;
  text-decoration: none;
  font-weight: 500;
}

.forgot-link:hover {
  text-decoration: underline;
}

.error-message {
  padding: 0.75rem;
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 6px;
  color: #c33;
  font-size: 0.875rem;
  text-align: center;
}

.submit-button {
  padding: 0.875rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 0.5rem;
}

.submit-button:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.submit-button:active:not(:disabled) {
  transform: translateY(0);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.signup-link {
  text-align: center;
  margin-top: 1.5rem;
  color: #666;
  font-size: 0.95rem;
}

.signup-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.signup-link a:hover {
  text-decoration: underline;
}

/* Responsive Design */
@media (max-width: 768px) {
  .login-card {
    padding: 2rem;
  }

  .login-header h1 {
    font-size: 1.5rem;
  }

  .form-options {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
}
</style>

