# OAuth Quick Start Guide
## Google & Facebook Login Integration

This guide will help you quickly implement OAuth login in your POS system.

---

## 📋 Prerequisites

- Django backend with MongoDB
- Vue.js frontend
- Google Developer account
- Facebook Developer account

---

## 🚀 Implementation Steps

### Step 1: Install Required Packages (5 minutes)

```bash
cd backend
pip install google-auth==2.35.0 google-auth-oauthlib==1.2.1 google-auth-httplib2==0.2.0 requests-oauthlib==2.0.0
```

Or simply run:
```bash
pip install -r requirements.txt
```

### Step 2: Get OAuth Credentials (10 minutes)

#### Google OAuth:
1. Go to https://console.cloud.google.com/
2. Create/select project
3. Enable "Google+ API" or "Google Identity"
4. Create OAuth 2.0 Client ID credentials
5. Add authorized redirect URI: `http://localhost:8000/api/v1/auth/google/callback/`
6. Copy **Client ID** and **Client Secret**

#### Facebook OAuth:
1. Go to https://developers.facebook.com/
2. Create/select app
3. Add "Facebook Login" product
4. Add OAuth Redirect URI: `http://localhost:8000/api/v1/auth/facebook/callback/`
5. Copy **App ID** and **App Secret**

### Step 3: Configure Environment Variables (2 minutes)

Add to your `.env` file (or create one in backend folder):

```env
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback/

# Facebook OAuth
FACEBOOK_APP_ID=your-app-id
FACEBOOK_APP_SECRET=your-app-secret
FACEBOOK_REDIRECT_URI=http://localhost:8000/api/v1/auth/facebook/callback/

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

### Step 4: Update Django URLs (3 minutes)

**File:** `backend/app/urls.py`

Add this import at the top:
```python
from .kpi_views.oauth_views import (
    GoogleLoginView,
    GoogleCallbackView,
    FacebookLoginView,
    FacebookCallbackView,
    OAuthDisconnectView
)
```

Add these routes after your existing authentication routes:
```python
# OAuth Authentication
path('auth/google/', GoogleLoginView.as_view(), name='google-login'),
path('auth/google/callback/', GoogleCallbackView.as_view(), name='google-callback'),
path('auth/facebook/', FacebookLoginView.as_view(), name='facebook-login'),
path('auth/facebook/callback/', FacebookCallbackView.as_view(), name='facebook-callback'),
path('auth/oauth/disconnect/', OAuthDisconnectView.as_view(), name='oauth-disconnect'),
```

### Step 5: Add Frontend Route (2 minutes)

**File:** `frontend/src/router/index.js`

```javascript
import OAuthCallback from '@/pages/OAuthCallback.vue'

const routes = [
  // ... existing routes ...
  
  {
    path: '/auth/callback',
    name: 'OAuthCallback',
    component: OAuthCallback,
    meta: { requiresAuth: false }
  }
]
```

### Step 6: Use OAuth in Login Page (5 minutes)

**File:** `frontend/src/pages/Login.vue` (or your login page)

```vue
<template>
  <div class="login-page">
    <!-- Your existing login form -->
    
    <!-- Add OAuth Buttons -->
    <OAuthButtons 
      googleButtonText="Sign in with Google"
      facebookButtonText="Sign in with Facebook"
    />
  </div>
</template>

<script setup>
import OAuthButtons from '@/components/auth/OAuthButtons.vue'
</script>
```

### Step 7: Test the Integration (5 minutes)

1. **Start your backend:**
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Start your frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test Google Login:**
   - Go to your login page
   - Click "Sign in with Google"
   - Authorize the app
   - You should be redirected back and logged in

4. **Test Facebook Login:**
   - Click "Sign in with Facebook"
   - Authorize the app
   - You should be redirected back and logged in

---

## 🔍 OAuth Flow Diagram

```
┌─────────────┐
│   User      │
│ (Browser)   │
└──────┬──────┘
       │ 1. Clicks "Sign in with Google/Facebook"
       ▼
┌─────────────────────────────────────────┐
│  Frontend (Vue.js)                      │
│  Redirects to: /api/v1/auth/google/     │
└──────┬──────────────────────────────────┘
       │ 2. GET /api/v1/auth/google/
       ▼
┌─────────────────────────────────────────┐
│  Backend (Django)                       │
│  GoogleLoginView                        │
│  Redirects to Google OAuth              │
└──────┬──────────────────────────────────┘
       │ 3. Redirect to accounts.google.com
       ▼
┌─────────────────────────────────────────┐
│  Google OAuth                           │
│  User logs in and authorizes            │
└──────┬──────────────────────────────────┘
       │ 4. Redirect with code
       ▼
┌─────────────────────────────────────────┐
│  Backend (Django)                       │
│  GoogleCallbackView                     │
│  - Verifies code with Google            │
│  - Gets user info                       │
│  - Creates/finds user in MongoDB        │
│  - Generates JWT tokens                 │
│  - Redirects to frontend with tokens    │
└──────┬──────────────────────────────────┘
       │ 5. Redirect to /auth/callback?tokens
       ▼
┌─────────────────────────────────────────┐
│  Frontend (Vue.js)                      │
│  OAuthCallback.vue                      │
│  - Stores tokens in localStorage        │
│  - Redirects to dashboard               │
└──────┬──────────────────────────────────┘
       │ 6. User is logged in!
       ▼
┌─────────────┐
│  Dashboard  │
└─────────────┘
```

---

## 📁 Files Created

### Backend Files:
- ✅ `backend/app/services/oauth_service.py` - OAuth service layer
- ✅ `backend/app/kpi_views/oauth_views.py` - OAuth API endpoints
- ✅ `backend/settings/base.py` - Updated with OAuth config
- ✅ `backend/requirements.txt` - Updated with OAuth packages
- ✅ `backend/OAUTH_IMPLEMENTATION_GUIDE.md` - Detailed implementation guide
- ✅ `backend/OAUTH_URL_CONFIGURATION.md` - URL setup guide
- ✅ `backend/OAUTH_ENV_EXAMPLE.txt` - Environment variables example

### Frontend Files:
- ✅ `frontend/src/composables/api/useOAuth.js` - OAuth composable
- ✅ `frontend/src/components/auth/OAuthButtons.vue` - OAuth login buttons
- ✅ `frontend/src/pages/OAuthCallback.vue` - OAuth callback handler
- ✅ `frontend/src/pages/LoginExample.vue` - Example login page with OAuth

---

## 🔐 Security Checklist

- [ ] Never commit OAuth secrets to Git
- [ ] Use HTTPS in production
- [ ] Validate OAuth tokens on server-side
- [ ] Implement rate limiting on OAuth endpoints
- [ ] Set proper CORS headers
- [ ] Use environment variables for all secrets
- [ ] Enable CSRF protection
- [ ] Regularly rotate OAuth secrets
- [ ] Monitor OAuth usage for suspicious activity
- [ ] Implement account linking for existing users

---

## 🐛 Common Issues & Solutions

### Issue: "Redirect URI mismatch"
**Solution:** Ensure redirect URIs in provider settings match exactly (including port and trailing slash)

### Issue: "Invalid client credentials"
**Solution:** Double-check Client ID/Secret in .env file

### Issue: "CORS error"
**Solution:** Add frontend URL to CORS_ALLOWED_ORIGINS in Django settings

### Issue: "Module 'google.oauth2' not found"
**Solution:** Run `pip install google-auth google-auth-oauthlib`

### Issue: "OAuth works but user not created"
**Solution:** Check MongoDB connection and collection permissions

### Issue: "User already exists with email"
**Solution:** The system will automatically link OAuth to existing account

---

## 📚 Additional Resources

- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Facebook Login Documentation](https://developers.facebook.com/docs/facebook-login)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vue.js Documentation](https://vuejs.org/)

---

## 🎉 You're Done!

Your OAuth integration is now complete. Users can now sign in using their Google or Facebook accounts!

### What's Next?

1. **Customize the OAuth buttons** - Match your app's design
2. **Add more providers** - Twitter, GitHub, LinkedIn, etc.
3. **Implement account linking** - Let users connect multiple OAuth providers
4. **Add profile pictures** - Use OAuth profile pictures
5. **Email verification** - Send welcome emails to new OAuth users
6. **Analytics** - Track OAuth sign-ups vs traditional sign-ups

---

## 💡 Need Help?

- Check the detailed `OAUTH_IMPLEMENTATION_GUIDE.md`
- Review `OAUTH_URL_CONFIGURATION.md` for URL setup
- Look at `LoginExample.vue` for integration examples
- Check Django logs for backend errors
- Use browser console for frontend errors

---

**Total Implementation Time: ~30 minutes** ⏱️

Happy coding! 🚀

