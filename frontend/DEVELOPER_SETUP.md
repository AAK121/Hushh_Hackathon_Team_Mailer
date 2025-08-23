# 🔧 Developer Setup Guide - Google OAuth for Your App

## 🚨 **IMMEDIATE ISSUE**: Google Verification Process

The error you're seeing ("Access blocked: ozuayvppkblkhodyjepd.supabase.co has not completed the Google verification process") happens because your app is in "testing" mode in Google Cloud Console.

## 🚀 **STEP 1: Google Cloud Console Setup**

### A. Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/
2. **Create a new project** or select existing one
3. Name it something like "Gmail-like App" or "Hushh Frontend"

### B. Enable Required APIs
Go to **APIs & Services > Library** and enable:
- ✅ **Google Calendar API**
- ✅ **Gmail API** 
- ✅ **Google+ API** (for user info)

### C. Configure OAuth Consent Screen
1. Go to **APIs & Services > OAuth consent screen**
2. Choose **External** (for testing with any Google account)
3. Fill out the form:
   ```
   App name: Your Gmail-like App
   User support email: chaitanyad3shkar@gmail.com
   Developer contact: chaitanyad3shkar@gmail.com
   ```
4. **Add your email to Test users**:
   - In OAuth consent screen settings
   - Go to "Test users" section
   - Add: chaitanyad3shkar@gmail.com
5. **Add scopes**:
   - https://www.googleapis.com/auth/userinfo.email
   - https://www.googleapis.com/auth/userinfo.profile
   - https://www.googleapis.com/auth/calendar.events
   - https://www.googleapis.com/auth/gmail.readonly

### D. Create OAuth 2.0 Credentials
1. Go to **APIs & Services > Credentials**
2. Click **+ CREATE CREDENTIALS > OAuth 2.0 Client IDs**
3. Configure:
   ```
   Application type: Web application
   Name: Gmail-like App Client
   
   Authorized JavaScript origins:
   - http://localhost:5173
   - http://localhost:5174
   - https://ozuayvppkblkhodyjepd.supabase.co
   
   Authorized redirect URIs:
   - https://ozuayvppkblkhodyjepd.supabase.co/auth/v1/callback
   - http://localhost:5173
   - http://localhost:5174
   ```
4. **SAVE and copy** the Client ID and Client Secret

## 🚀 **STEP 2: Configure Supabase Dashboard**

### A. Add Google OAuth Provider
1. Go to: https://supabase.com/dashboard/project/ozuayvppkblkhodyjepd
2. Navigate to **Authentication > Providers**
3. Find **Google** and click the toggle to enable it
4. Configure:
   ```
   Client ID: [Paste from Google Cloud Console]
   Client Secret: [Paste from Google Cloud Console]
   
   Redirect URL: https://ozuayvppkblkhodyjepd.supabase.co/auth/v1/callback
   ```

### B. Advanced Settings (Optional but Recommended)
In the Google provider settings:
- ✅ **Skip nonce check**: Enable
- ✅ **Allow manual linking**: Enable

## 🚀 **STEP 3: Test Authentication**

### A. Clear Browser Data
1. Open browser dev tools (F12)
2. Go to **Application > Storage > Clear storage**
3. Clear everything for localhost:5173

### B. Test the Flow
1. Start your app: `npm run dev`
2. Click "Sign in with Google"
3. You should now see the Google consent screen
4. **Grant all permissions** when prompted

## 🔍 **QUICK FIX: Add Yourself as Test User**

The immediate issue is that your app is in testing mode. Here's the quick fix:

1. **Google Cloud Console > OAuth consent screen**
2. **Test users section**
3. **Add your email**: chaitanyad3shkar@gmail.com
4. **Save**

This will allow YOU to test the app immediately while it's in testing mode.

## 📋 **Verification Checklist**

- [ ] Google Cloud project created
- [ ] Calendar API enabled
- [ ] OAuth consent screen configured
- [ ] YOUR EMAIL added as test user
- [ ] OAuth 2.0 credentials created
- [ ] Supabase Google provider configured
- [ ] Browser cache cleared
- [ ] Test authentication flow

## 🎯 **Expected Result**

After these steps:
1. ✅ Google sign-in will work without the "Access blocked" error
2. ✅ You'll see consent screen asking for calendar permissions
3. ✅ Calendar integration will work properly
4. ✅ You can create calendar events from your app

## 🚨 **For Production Later**

To make this available to all users (not just test users):
1. Complete Google's app verification process
2. Provide privacy policy and terms of service
3. Submit for Google review

But for development and testing, adding yourself as a test user is sufficient!

---

**IMMEDIATE ACTION**: Add chaitanyad3shkar@gmail.com as a test user in Google Cloud Console OAuth consent screen. This will fix the "Access blocked" error right away.
