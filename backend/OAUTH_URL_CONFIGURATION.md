# OAuth URL Configuration Guide

## Step 1: Add OAuth Views Import

Add this to the top of your `backend/app/urls.py` file with the other imports:

```python
from .kpi_views.oauth_views import (
    GoogleLoginView,
    GoogleCallbackView,
    FacebookLoginView,
    FacebookCallbackView,
    OAuthDisconnectView
)
```

## Step 2: Add OAuth URL Patterns

Add these URL patterns to your `urlpatterns` list in `backend/app/urls.py`.

**IMPORTANT**: Add these routes right after your existing authentication routes (around line 295-307).

```python
urlpatterns = [
    # ... existing routes ...
    
    # ========== AUTHENTICATION ==========
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh-token'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    path('auth/verify-token/', VerifyTokenView.as_view(), name='verify-token'),
    
    # ========== OAUTH AUTHENTICATION (NEW) ==========
    # Google OAuth
    path('auth/google/', GoogleLoginView.as_view(), name='google-login'),
    path('auth/google/callback/', GoogleCallbackView.as_view(), name='google-callback'),
    
    # Facebook OAuth
    path('auth/facebook/', FacebookLoginView.as_view(), name='facebook-login'),
    path('auth/facebook/callback/', FacebookCallbackView.as_view(), name='facebook-callback'),
    
    # OAuth Management
    path('auth/oauth/disconnect/', OAuthDisconnectView.as_view(), name='oauth-disconnect'),
    
    # ========== CUSTOMER AUTHENTICATION ==========
    path('auth/customer/login/', CustomerLoginView.as_view(), name='customer-login'),
    # ... rest of customer auth routes ...
    
    # ... rest of your routes ...
]
```

## Complete Import Section Example

Here's how your import section should look after adding OAuth views:

```python
from django.urls import path

from .kpi_views.session_views import (
    SessionLogsView,
    # ... other session views ...
)

from .kpi_views.authentication_views import (
    LoginView,
    LogoutView,
    RefreshTokenView,
    CurrentUserView,
    VerifyTokenView,
)

# NEW: OAuth views import
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
    # ... other customer views ...
)

# ... rest of your imports ...
```

## Testing the URLs

After adding the routes, you can test them:

### 1. Check if routes are registered
```bash
python manage.py show_urls | grep oauth
```

### 2. Test OAuth initiation (in browser)
```
http://localhost:8000/api/v1/auth/google/
http://localhost:8000/api/v1/auth/facebook/
```

These should redirect you to the respective OAuth provider's login page.

### 3. Test callback URLs
The callback URLs will be called automatically by Google/Facebook after user authorization:
```
http://localhost:8000/api/v1/auth/google/callback/?code=...
http://localhost:8000/api/v1/auth/facebook/callback/?code=...
```

## Frontend Routes

Also add the OAuth callback route to your Vue.js router (`frontend/src/router/index.js`):

```javascript
import OAuthCallback from '@/pages/OAuthCallback.vue'

const routes = [
  // ... existing routes ...
  
  {
    path: '/auth/callback',
    name: 'OAuthCallback',
    component: OAuthCallback,
    meta: {
      requiresAuth: false,
      title: 'Completing Login...'
    }
  },
  
  // ... rest of your routes ...
]
```

## CORS Configuration

Make sure your CORS settings allow the frontend URL. In your Django settings:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Vue dev server
    'http://localhost:3000',  # Alternative port
    # Add your production URLs here
]

CORS_ALLOW_CREDENTIALS = True
```

## Next Steps

1. ✅ Add OAuth view imports to `urls.py`
2. ✅ Add OAuth URL patterns to `urlpatterns`
3. ✅ Configure environment variables (see `OAUTH_ENV_EXAMPLE.txt`)
4. ✅ Set up Google OAuth credentials
5. ✅ Set up Facebook OAuth credentials
6. ✅ Install required packages: `pip install -r requirements.txt`
7. ✅ Test OAuth flow in browser
8. ✅ Integrate OAuth buttons in your login page

## Troubleshooting

### "No module named 'google.oauth2'"
Run: `pip install google-auth google-auth-oauthlib`

### "Redirect URI mismatch"
- Ensure the redirect URI in your OAuth provider settings exactly matches the one in your .env file
- Include the port number in development (e.g., `:8000`)
- Make sure there are no trailing slashes mismatches

### "CSRF verification failed"
- OAuth views use `AllowAny` permission, so this shouldn't happen
- If it does, check your CORS settings

### Frontend can't reach backend
- Check that CORS_ALLOWED_ORIGINS includes your frontend URL
- Verify your API_BASE_URL in frontend environment variables
- Check that the backend server is running on the expected port

