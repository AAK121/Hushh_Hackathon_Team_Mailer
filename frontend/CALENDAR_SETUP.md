# Google Calendar Integration Setup

This document explains how to set up Google Calendar integration in your Gmail-like application.

## Frontend Setup (Completed)

✅ **Calendar Service**: Created `src/services/calendarService.ts` with comprehensive Google Calendar API integration
✅ **UI Component**: Created `src/components/CreateCalendarEvent.tsx` with full form interface
✅ **OAuth Configuration**: Updated `src/lib/supabase.ts` with Google Calendar scopes
✅ **Navigation**: Added Calendar button to sidebar and routing in App.tsx

## Supabase Configuration (Required)

### 1. Configure Google OAuth Provider

1. Go to your **Supabase Dashboard** → Project → Authentication → Providers
2. Enable the **Google** provider
3. Configure the following settings:

```
Client ID: [Your Google OAuth Client ID]
Client Secret: [Your Google OAuth Client Secret]
Authorized Redirect URIs: https://[your-project-ref].supabase.co/auth/v1/callback
```

### 2. Add Required OAuth Scopes

In the Google provider configuration, add these scopes:
```
https://www.googleapis.com/auth/calendar.events
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/userinfo.email
https://www.googleapis.com/auth/userinfo.profile
```

### 3. Set OAuth Options

Enable the following options in Google provider:
- ✅ Skip nonce check
- ✅ Allow manual linking

## Google Cloud Console Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Google Calendar API
   - Gmail API
   - Google+ API

### 2. Create OAuth 2.0 Credentials
1. Go to **APIs & Services** → **Credentials**
2. Create **OAuth 2.0 Client ID**
3. Configure:
   ```
   Application type: Web application
   Authorized redirect URIs: 
   - https://[your-project-ref].supabase.co/auth/v1/callback
   - http://localhost:5173 (for development)
   ```

## Backend Integration Options

### Option 1: Supabase Edge Functions (Recommended)

Create a Supabase Edge Function to handle calendar operations:

```sql
-- Create the function in your Supabase SQL editor
create or replace function create_calendar_event(
  event_title text,
  event_description text default null,
  start_time timestamp with time zone,
  end_time timestamp with time zone,
  location text default null,
  attendees text[] default null
) returns json
language plpgsql
security definer
as $$
declare
  user_record auth.users%rowtype;
  access_token text;
  result json;
begin
  -- Get the current user
  select * into user_record from auth.users where id = auth.uid();
  
  if user_record is null then
    return json_build_object('error', 'User not authenticated');
  end if;
  
  -- Extract the provider token (Google access token)
  access_token := user_record.raw_app_meta_data->>'provider_token';
  
  if access_token is null then
    return json_build_object('error', 'No Google access token found');
  end if;
  
  -- Here you would make the HTTP request to Google Calendar API
  -- This requires the http extension: create extension if not exists http;
  
  return json_build_object(
    'success', true,
    'message', 'Calendar event creation initiated',
    'title', event_title
  );
end;
$$;
```

### Option 2: External API Service

If you prefer a separate backend service, the frontend is already configured to call:
- `POST /api/calendar/create-event` for event creation
- Falls back to direct Google API calls if backend is unavailable

## Usage Examples

### Creating a Calendar Event

```typescript
import { calendarService } from './services/calendarService';

const event = {
  title: 'Team Meeting',
  description: 'Weekly team sync',
  startTime: '2024-01-15T10:00:00Z',
  endTime: '2024-01-15T11:00:00Z',
  location: 'Conference Room A',
  attendees: ['john@company.com', 'jane@company.com'],
  timezone: 'America/New_York'
};

const result = await calendarService.createEvent(event);
if (result.success) {
  console.log('Event created:', result.eventId);
} else {
  console.error('Error:', result.error);
}
```

### Checking Calendar Permissions

```typescript
const hasPermissions = await calendarService.hasCalendarPermissions();
if (!hasPermissions) {
  // Prompt user to re-authenticate with calendar scopes
}
```

## Authentication Flow

1. **User clicks "Sign in with Google"**
2. **Supabase redirects to Google OAuth** with calendar scopes
3. **User grants permissions** for email and calendar access
4. **Google redirects back** with access + refresh tokens
5. **Supabase stores tokens** in user session
6. **Frontend can access tokens** via `session.provider_token`
7. **Calendar service uses tokens** to make API calls

## Security Notes

- ✅ Access tokens are automatically refreshed by Supabase
- ✅ Refresh tokens are securely stored in Supabase
- ✅ Frontend only receives access tokens, not refresh tokens
- ✅ All API calls include proper authorization headers
- ✅ Error handling for expired/invalid tokens

## Troubleshooting

### "No access token found"
- Ensure user signed in with Google (not email/password)
- Check that Google provider is properly configured in Supabase
- Verify OAuth scopes include calendar permissions

### "Insufficient permissions"
- User needs to re-authenticate to grant calendar access
- Check Google Cloud Console for enabled APIs
- Verify OAuth scopes in Supabase provider configuration

### CORS Errors
- Ensure your domain is added to Google OAuth authorized origins
- Check Supabase CORS settings for your domain

## Current Status

✅ **Frontend Implementation**: Complete with full UI and service layer
✅ **OAuth Configuration**: Updated with required scopes
✅ **Error Handling**: Comprehensive fallbacks and user feedback
⚠️ **Backend Integration**: Requires Supabase/Google Cloud configuration
⚠️ **Testing**: Needs real OAuth setup to test end-to-end

## Next Steps

1. **Configure Google Cloud Project** with OAuth credentials
2. **Update Supabase** with Google provider settings
3. **Test OAuth flow** with calendar scopes
4. **Implement backend function** (optional) or use direct API calls
5. **Deploy and test** the complete integration

---

The calendar integration is fully implemented on the frontend and ready to work once the OAuth configuration is completed in Supabase and Google Cloud Console.
