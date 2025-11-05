# Complete OAuth Integration Code

This document contains the exact code snippets you need to add to integrate OAuth into your existing application.

---

## 1. Add Imports to `backend/app/urls.py`

**Location:** Top of the file, with other imports

Add this import statement:

```python
from .kpi_views.oauth_views import (
    GoogleLoginView,
    GoogleCallbackView,
    FacebookLoginView,
    FacebookCallbackView,
    OAuthDisconnectView
)
```

### Complete Import Section Example:

```python
from django.urls import path

# ... your existing imports ...

from .kpi_views.authentication_views import (
    LoginView,
    LogoutView,
    RefreshTokenView,
    CurrentUserView,
    VerifyTokenView,
)

# NEW: Add this import
from .kpi_views.oauth_views import (
    GoogleLoginView,
    GoogleCallbackView,
    FacebookLoginView,
    FacebookCallbackView,
    OAuthDisconnectView
)

from .kpi_views.customer_auth_views import (
    CustomerLoginView,
    CustomerRegisterView,
    CustomerLogoutView,
    CustomerProfileView,
    CustomerUpdateProfileView,
    CustomerChangePasswordView,
)

# ... rest of your imports ...
```

---

## 2. Add URL Patterns to `backend/app/urls.py`

**Location:** In the `urlpatterns` list, after line 299 (after auth routes)

```python
urlpatterns = [
    # ... existing routes ...
    
    # ========== AUTHENTICATION ==========
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh-token'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    path('auth/verify-token/', VerifyTokenView.as_view(), name='verify-token'),
    
    # ========== OAUTH AUTHENTICATION (ADD THESE 5 LINES) ==========
    path('auth/google/', GoogleLoginView.as_view(), name='google-login'),
    path('auth/google/callback/', GoogleCallbackView.as_view(), name='google-callback'),
    path('auth/facebook/', FacebookLoginView.as_view(), name='facebook-login'),
    path('auth/facebook/callback/', FacebookCallbackView.as_view(), name='facebook-callback'),
    path('auth/oauth/disconnect/', OAuthDisconnectView.as_view(), name='oauth-disconnect'),
    
    # ========== CUSTOMER AUTHENTICATION ==========
    path('auth/customer/login/', CustomerLoginView.as_view(), name='customer-login'),
    # ... rest of your routes ...
]
```

---

## 3. Add Frontend Route to `frontend/src/router/index.js`

Add this route to your routes array:

```javascript
{
  path: '/auth/callback',
  name: 'OAuthCallback',
  component: () => import('@/pages/OAuthCallback.vue'),
  meta: {
    requiresAuth: false,
    title: 'Completing Login...'
  }
}
```

### Complete Router Example:

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { requiresAuth: false }
  },
  
  // NEW: Add OAuth callback route
  {
    path: '/auth/callback',
    name: 'OAuthCallback',
    component: () => import('@/pages/OAuthCallback.vue'),
    meta: {
      requiresAuth: false,
      title: 'Completing Login...'
    }
  },
  
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  
  // ... rest of your routes ...
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

---

## 4. Update Your Login Page

### Option A: Add to Existing Login Page

**File:** `frontend/src/pages/Login.vue` (or whatever your login page is called)

```vue
<template>
  <div class="login-page">
    <div class="login-card">
      <h1>Welcome Back</h1>
      
      <!-- ADD THIS: OAuth Buttons -->
      <OAuthButtons 
        googleButtonText="Sign in with Google"
        facebookButtonText="Sign in with Facebook"
      />
      
      <div class="divider">
        <span>Or continue with email</span>
      </div>
      
      <!-- Your existing login form -->
      <form @submit.prevent="handleLogin">
        <!-- ... your form fields ... -->
      </form>
    </div>
  </div>
</template>

<script setup>
// ADD THIS IMPORT
import OAuthButtons from '@/components/auth/OAuthButtons.vue'

// ... your existing code ...
</script>
```

### Option B: Use the Complete Example

Use the provided `LoginExample.vue` file as a reference or copy it to your login page.

---

## 5. Environment Variables

### Backend `.env` File

Create or update your `.env` file in the backend directory:

```env
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback/

# Facebook OAuth
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
FACEBOOK_REDIRECT_URI=http://localhost:8000/api/v1/auth/facebook/callback/

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

### Frontend `.env` File (if needed)

If your frontend uses a custom API URL, ensure it's set:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

---

## 6. Install Dependencies

### Backend:

```bash
cd backend
pip install -r requirements.txt
```

Or install packages individually:

```bash
pip install google-auth==2.35.0
pip install google-auth-oauthlib==1.2.1
pip install google-auth-httplib2==0.2.0
pip install requests-oauthlib==2.0.0
```

### Frontend:

No additional packages needed! The OAuth functionality uses the existing axios setup.

---

## 7. API Usage Examples

### Using OAuth Buttons Component

```vue
<template>
  <!-- Basic usage -->
  <OAuthButtons />
  
  <!-- Custom button text -->
  <OAuthButtons 
    googleButtonText="Continue with Google"
    facebookButtonText="Continue with Facebook"
  />
  
  <!-- Without divider -->
  <OAuthButtons :showDivider="false" />
  
  <!-- Custom divider text -->
  <OAuthButtons dividerText="OR" />
</template>

<script setup>
import OAuthButtons from '@/components/auth/OAuthButtons.vue'
</script>
```

### Using OAuth Composable

```javascript
import { useOAuth } from '@/composables/api/useOAuth'

const { 
  loginWithGoogle, 
  loginWithFacebook, 
  isOAuthUser, 
  getOAuthProvider 
} = useOAuth()

// Check if current user logged in via OAuth
if (isOAuthUser()) {
  console.log('OAuth provider:', getOAuthProvider())
}

// Manual OAuth login (alternative to buttons)
const handleGoogleLogin = () => {
  loginWithGoogle()
}
```

### Disconnect OAuth

```vue
<template>
  <button @click="handleDisconnect">
    Disconnect {{ provider }}
  </button>
</template>

<script setup>
import { useOAuth } from '@/composables/api/useOAuth'

const { disconnectOAuth, getOAuthProvider } = useOAuth()

const provider = getOAuthProvider()

const handleDisconnect = async () => {
  const result = await disconnectOAuth('customer')
  
  if (result.success) {
    alert('OAuth provider disconnected')
    // Redirect or refresh
  } else {
    alert(result.error)
  }
}
</script>
```

---

## 8. Testing Code

### Test OAuth Flow (Backend)

Create a test file `backend/test_oauth.py`:

```python
import requests

# Test Google OAuth initiation
response = requests.get('http://localhost:8000/api/v1/auth/google/')
print(f"Google OAuth redirect: {response.status_code}")
print(f"Redirect URL: {response.url}")

# Test Facebook OAuth initiation
response = requests.get('http://localhost:8000/api/v1/auth/facebook/')
print(f"Facebook OAuth redirect: {response.status_code}")
print(f"Redirect URL: {response.url}")
```

Run: `python backend/test_oauth.py`

### Test Frontend Integration

Add this to your Vue component for testing:

```vue
<template>
  <div>
    <button @click="testOAuth">Test OAuth Setup</button>
    <pre>{{ oauthStatus }}</pre>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useOAuth } from '@/composables/api/useOAuth'

const oauthStatus = ref({})
const { isOAuthUser, getOAuthProvider } = useOAuth()

const testOAuth = () => {
  oauthStatus.value = {
    isOAuthUser: isOAuthUser(),
    provider: getOAuthProvider(),
    hasAccessToken: !!localStorage.getItem('access_token'),
    user: JSON.parse(localStorage.getItem('user') || '{}')
  }
}
</script>
```

---

## 9. Verify Installation

Run these commands to verify everything is set up:

### Backend:

```bash
# Check if OAuth views are imported
cd backend
python manage.py check

# List all URLs (should include OAuth routes)
python manage.py show_urls | grep oauth

# Expected output:
# auth/google/                     google-login
# auth/google/callback/            google-callback
# auth/facebook/                   facebook-login
# auth/facebook/callback/          facebook-callback
# auth/oauth/disconnect/           oauth-disconnect
```

### Frontend:

```bash
# Check if files exist
cd frontend
ls src/composables/api/useOAuth.js
ls src/components/auth/OAuthButtons.vue
ls src/pages/OAuthCallback.vue

# Build (check for errors)
npm run build
```

---

## 10. Production Deployment Code

### Update `.env` for Production:

```env
# Google OAuth (Production)
GOOGLE_CLIENT_ID=your-production-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-production-client-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/auth/google/callback/

# Facebook OAuth (Production)
FACEBOOK_APP_ID=your-production-app-id
FACEBOOK_APP_SECRET=your-production-app-secret
FACEBOOK_REDIRECT_URI=https://yourdomain.com/api/v1/auth/facebook/callback/

# Frontend URL (Production)
FRONTEND_URL=https://yourdomain.com

# Security
DEBUG=False
SECRET_KEY=your-secure-random-secret-key
```

### Update CORS in `settings/production.py`:

```python
CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]

CSRF_TRUSTED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]
```

---

## 🎉 That's It!

You now have all the code needed to implement OAuth. Just:

1. Copy the imports to `urls.py`
2. Copy the URL patterns to `urls.py`
3. Add OAuth buttons to your login page
4. Set up environment variables
5. Install dependencies
6. Test the flow

**Total Lines of Code to Add:** ~20 lines  
**Time Required:** ~15 minutes  

---

## Need Help?

- Detailed guide: `OAUTH_IMPLEMENTATION_GUIDE.md`
- Quick start: `OAUTH_QUICK_START.md`
- URL setup: `OAUTH_URL_CONFIGURATION.md`
- Summary: `OAUTH_IMPLEMENTATION_SUMMARY.md`


