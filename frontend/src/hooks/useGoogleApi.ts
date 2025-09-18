import { useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { googleApiService } from '../services/googleApi';

export const useGoogleApi = () => {
  const { session, refreshGoogleToken } = useAuth();

  useEffect(() => {
    // Set up token refresh callback when auth context is available
    if (refreshGoogleToken) {
      googleApiService.setTokenRefreshCallback(refreshGoogleToken);
    }

    // Set initial token if available
    if (session?.provider_token) {
      const expiresIn = session.expires_at ? (session.expires_at - Math.floor(Date.now() / 1000)) : undefined;
      googleApiService.setToken(
        session.provider_token,
        session.provider_refresh_token || undefined,
        expiresIn
      );
    } else {
      // Also check session storage for refreshed tokens
      const storedToken = sessionStorage.getItem('google_access_token');
      const storedExpiry = sessionStorage.getItem('google_token_expiry');
      
      if (storedToken && storedExpiry) {
        const expiryTime = parseInt(storedExpiry);
        const expiresIn = Math.max(0, (expiryTime - Date.now()) / 1000);
        googleApiService.setToken(storedToken, undefined, expiresIn);
      }
    }
  }, [session, refreshGoogleToken]);

  return {
    googleApi: googleApiService,
    isAuthenticated: !!session?.provider_token || !!sessionStorage.getItem('google_access_token'),
    refreshToken: refreshGoogleToken
  };
};
