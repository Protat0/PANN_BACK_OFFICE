# OAuth Implementation Guide (Google & Facebook)

## Overview
This guide explains how to add Google and Facebook OAuth login to your POS system.

## Step 1: Install Required Packages

Add these to your `requirements.txt`:
```
google-auth==2.35.0
google-auth-oauthlib==1.2.1
google-auth-httplib2==0.2.0
facebook-sdk==3.1.0
requests-oauthlib==2.0.0
```

Then run:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 facebook-sdk requests-oauthlib
```

## Step 2: Get OAuth Credentials

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Configure consent screen
6. Add authorized redirect URIs:
   - `http://localhost:8000/api/v1/auth/google/callback/` (development)
   - `https://yourdomain.com/api/v1/auth/google/callback/` (production)
7. Copy your **Client ID** and **Client Secret**

### Facebook OAuth Setup
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app or select existing one
3. Add "Facebook Login" product
4. Configure OAuth redirect URIs:
   - `http://localhost:8000/api/v1/auth/facebook/callback/` (development)
   - `https://yourdomain.com/api/v1/auth/facebook/callback/` (production)
5. Copy your **App ID** and **App Secret**

## Step 3: Environment Variables

Add to your `.env` file or settings:
```env
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback/

# Facebook OAuth
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
FACEBOOK_REDIRECT_URI=http://localhost:8000/api/v1/auth/facebook/callback/

# Frontend URL (for redirecting after OAuth)
FRONTEND_URL=http://localhost:5173
```

## Step 4: Backend Implementation

The following files have been created:
- `backend/app/services/oauth_service.py` - OAuth service layer
- `backend/app/kpi_views/oauth_views.py` - OAuth API endpoints

## Step 5: Update URLs

Add OAuth routes to your `backend/app/urls.py`:
```python
from .kpi_views.oauth_views import (
    GoogleLoginView, 
    GoogleCallbackView,
    FacebookLoginView,
    FacebookCallbackView
)

urlpatterns = [
    # ... existing patterns ...
    
    # OAuth endpoints
    path('auth/google/', GoogleLoginView.as_view(), name='google-login'),
    path('auth/google/callback/', GoogleCallbackView.as_view(), name='google-callback'),
    path('auth/facebook/', FacebookLoginView.as_view(), name='facebook-login'),
    path('auth/facebook/callback/', FacebookCallbackView.as_view(), name='facebook-callback'),
]
```

## Step 6: Frontend Implementation

### Vue.js Component for OAuth Login

Create a login component with OAuth buttons:
```vue
<template>
  <div class="oauth-login">
    <button @click="loginWithGoogle" class="google-btn">
      <i class="fab fa-google"></i>
      Continue with Google
    </button>
    
    <button @click="loginWithFacebook" class="facebook-btn">
      <i class="fab fa-facebook"></i>
      Continue with Facebook
    </button>
  </div>
</template>

<script>
export default {
  methods: {
    loginWithGoogle() {
      window.location.href = 'http://localhost:8000/api/v1/auth/google/';
    },
    loginWithFacebook() {
      window.location.href = 'http://localhost:8000/api/v1/auth/facebook/';
    }
  }
}
</script>
```

## Step 7: User Model Update

Your User model already has a `source` field which is perfect! OAuth users will have:
- `source: 'google'` or `source: 'facebook'`
- `password: ''` (empty, since they use OAuth)
- `oauth_id: 'unique-id-from-provider'` (add this field)

## Step 8: Testing

1. Start your backend server
2. Click "Continue with Google" or "Continue with Facebook"
3. Complete OAuth flow in popup
4. Backend creates/finds user and returns JWT token
5. Frontend stores token and redirects to dashboard

## Security Notes

- Always use HTTPS in production
- Keep OAuth secrets secure (never commit to Git)
- Validate tokens on server-side
- Implement CSRF protection
- Set proper CORS headers
- Add rate limiting to OAuth endpoints

## Troubleshooting

### "Redirect URI mismatch"
- Ensure redirect URIs match exactly in provider settings
- Include the port number in development URLs
- Use HTTPS in production

### "Invalid client"
- Check that Client ID and Secret are correct
- Verify the OAuth app is enabled
- Check that the API is enabled (Google+ API for Google)

### User already exists with email
- Implement account linking logic
- Prompt user to merge accounts
- Or require unique email per provider

## Production Deployment

1. Update redirect URIs to production URLs
2. Use environment variables for secrets
3. Enable HTTPS
4. Update CORS settings
5. Test thoroughly before launch

