# 🔧 Calendar Integration Troubleshooting

## "No Access Token Available" Error

This error means the Google Calendar integration isn't properly configured. Here's how to fix it:

## 🚨 **Step 1: Configure Google Cloud Console**

### A. Create/Configure Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable these APIs in **APIs & Services > Library**:
   - ✅ Google Calendar API
   - ✅ Gmail API (optional)
   - ✅ Google+ API

### B. Create OAuth 2.0 Credentials
1. Go to **APIs & Services > Credentials**
2. Click **+ CREATE CREDENTIALS > OAuth 2.0 Client IDs**
3. Configure:
   ```
   Application type: Web application
   Name: Gmail-like App
   
   Authorized JavaScript origins:
   - http://localhost:5173
   - http://localhost:5174
   - https://yourdomain.com (for production)
   
   Authorized redirect URIs:
   - https://ozuayvppkblkhodyjepd.supabase.co/auth/v1/callback
   - http://localhost:5173
   - http://localhost:5174
   ```
4. **Save** and copy the Client ID and Client Secret

## 🚨 **Step 2: Configure Supabase Dashboard**

### A. Set up Google OAuth Provider
1. Go to [Supabase Dashboard](https://supabase.com/dashboard) → Your Project
2. Navigate to **Authentication > Providers**
3. Find **Google** and click **Configure**
4. Enable the provider and configure:
   ```
   Client ID: [Your Google OAuth Client ID from Step 1]
   Client Secret: [Your Google OAuth Client Secret from Step 1]
   
   Redirect URL: https://ozuayvppkblkhodyjepd.supabase.co/auth/v1/callback
   ```

### B. Configure OAuth Scopes
In the Google provider settings, add these scopes:
```
https://www.googleapis.com/auth/userinfo.email
https://www.googleapis.com/auth/userinfo.profile
https://www.googleapis.com/auth/calendar.events
https://www.googleapis.com/auth/gmail.readonly
```

### C. Additional Settings
- ✅ **Skip nonce check**: Enabled
- ✅ **Allow manual linking**: Enabled

## 🚨 **Step 3: Test the Authentication Flow**

### A. Clear Browser Data
1. Clear cookies and localStorage for your app
2. Sign out completely from your app

### B. Test Google Sign-In
1. Click "Sign in with Google" 
2. **Important**: You should see a consent screen asking for:
   - ✅ Access to your email
   - ✅ Access to your Google Calendar
3. Grant all permissions

### C. Verify Token Access
After signing in, open browser dev tools and run:
```javascript
// Check if user is authenticated with Google
const session = await window.supabase?.auth.getSession();
console.log('Provider:', session?.data?.session?.user?.app_metadata?.provider);
console.log('Has provider token:', !!session?.data?.session?.provider_token);
```

## 🔍 **Common Issues & Solutions**

### Issue: "User signed in with email/password"
**Solution**: User must sign out and use "Sign in with Google" button

### Issue: "Google provider not configured"
**Solution**: Complete Step 2 above - configure Google OAuth in Supabase

### Issue: "Calendar scopes not granted"
**Solution**: 
1. User needs to sign out and sign in again
2. Ensure consent screen shows calendar permissions
3. Check Supabase provider configuration includes calendar scopes

### Issue: "Token expired"
**Solution**: Supabase should auto-refresh, but user may need to sign in again

### Issue: "CORS errors"
**Solution**: 
1. Add your domain to Google OAuth authorized origins
2. Check Supabase CORS settings

## 📋 **Quick Verification Checklist**

- [ ] Google Cloud project created with Calendar API enabled
- [ ] OAuth 2.0 credentials created with correct redirect URIs
- [ ] Supabase Google provider configured with correct Client ID/Secret
- [ ] Calendar scopes added to Supabase provider configuration
- [ ] User signed out and signed back in with Google
- [ ] Consent screen showed calendar permissions
- [ ] Browser dev tools shows provider_token exists

## 🚀 **Testing Steps**

1. **Start fresh**: Clear browser data and sign out
2. **Sign in with Google**: Must use Google OAuth, not email/password
3. **Grant permissions**: Consent screen should ask for calendar access
4. **Test calendar**: Go to Calendar page and try creating an event

## 📞 **Still Having Issues?**

If you're still getting "No access token available":

1. **Check Supabase logs**: Go to your Supabase dashboard → Logs
2. **Check browser console**: Look for authentication errors
3. **Verify environment**: Ensure `.env` has correct Supabase URL/keys
4. **Test with fresh browser**: Try incognito/private mode

## 🔗 **Useful Resources**

- [Supabase Google OAuth Guide](https://supabase.com/docs/guides/auth/social-login/auth-google)
- [Google Calendar API Documentation](https://developers.google.com/calendar/api/guides/overview)
- [OAuth 2.0 Scopes for Google APIs](https://developers.google.com/identity/protocols/oauth2/scopes)

---

The integration should work perfectly once these steps are completed! The frontend code is already properly configured to handle the OAuth flow and API calls.
