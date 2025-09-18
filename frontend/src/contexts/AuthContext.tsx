import React, { createContext, useContext, useEffect, useState } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { auth, isSupabaseConfigured } from '../lib/supabase'
import { clearUserTokens } from '../services/tokenManager'
import { createUserVault, getUserVaultInfo } from '../services/userVaultApi'

interface AuthContextType {
  user: User | null
  session: Session | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<{ error: any }>
  signUp: (email: string, password: string, name?: string) => Promise<{ error: any }>
  signOut: () => Promise<void>
  signInWithOAuth: (provider: 'google' | 'github' | 'discord' | 'twitter') => Promise<{ error: any }>
  getValidGoogleToken: () => Promise<string | null>
  refreshGoogleToken: () => Promise<{ token: string | null; error: any }>
  // New user vault methods
  getUserId: () => string | null
  initializeUserVault: () => Promise<void>
  hasUserVault: () => Promise<boolean>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    console.log('AuthProvider useEffect - isSupabaseConfigured:', isSupabaseConfigured);
    
    // Require proper Supabase configuration - no demo mode
    if (!isSupabaseConfigured) {
      throw new Error('� Supabase configuration is required. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY environment variables.')
    }

    console.log('✅ Supabase is configured, checking session');

    // Get initial session from Supabase
    const getInitialSession = async () => {
      try {
        // Check if this is an OAuth callback by looking for fragments in URL
        const hashParams = new URLSearchParams(window.location.hash.substring(1));
        const searchParams = new URLSearchParams(window.location.search);
        
        if (hashParams.get('access_token') || searchParams.get('code')) {
          console.log('🔄 OAuth callback detected, exchanging tokens...');
        }
        
        const { data: { session }, error } = await auth.getCurrentSession()
        
        if (error) {
          console.error('Session error:', error);
        }
        
        setSession(session)
        setUser(session?.user ?? null)
        
        // Clean up URL after OAuth callback
        if (hashParams.get('access_token') || searchParams.get('code')) {
          window.history.replaceState({}, document.title, window.location.pathname);
        }
      } catch (error) {
        console.error('Error getting initial session:', error)
      } finally {
        setLoading(false)
      }
    }

    // Only get initial session if Supabase is configured
    if (isSupabaseConfigured) {
      getInitialSession()
    }

    // Listen for auth changes (only if Supabase is configured)
    if (isSupabaseConfigured) {
      const { data: { subscription } } = auth.onAuthStateChange(
        async (event, session) => {
          console.log('Auth state changed:', event, session)
          setSession(session)
          setUser(session?.user ?? null)
          setLoading(false)
        }
      )

      return () => subscription.unsubscribe()
    }
  }, [])

  const signIn = async (email: string, password: string) => {
    try {
      setLoading(true)
      
      // Use Supabase authentication only
      const { error } = await auth.signIn(email, password)
      
      if (error) {
        console.error('Sign in error:', error)
        return { error }
      }

      return { error: null }
    } catch (error) {
      console.error('Sign in error:', error)
      return { error }
    } finally {
      setLoading(false)
    }
  }

  const signUp = async (email: string, password: string, name?: string) => {
    try {
      setLoading(true)
      
      // Use Supabase authentication only
      const { error } = await auth.signUp(email, password, {
        data: { name }
      })
      
      if (error) {
        console.error('Sign up error:', error)
        return { error }
      }

      return { error: null }
    } catch (error) {
      console.error('Sign up error:', error)
      return { error }
    } finally {
      setLoading(false)
    }
  }

  const signOut = async () => {
    try {
      setLoading(true)
      
      // Use Supabase authentication only
      const { error } = await auth.signOut()
      if (error) {
        console.error('Sign out error:', error)
      }
    } catch (error) {
      console.error('Sign out error:', error)
    } finally {
      setLoading(false)
    }
  }

  const signInWithOAuth = async (provider: 'google' | 'github' | 'discord' | 'twitter') => {
    try {
      // Use Supabase OAuth only
      const { error } = await auth.signInWithOAuth(provider);
      
      if (error) {
        console.error('OAuth sign in error:', error)
        return { error }
      }

      return { error: null }
    } catch (error) {
      console.error('OAuth sign in error:', error)
      return { error }
    }
  }

  const getValidGoogleToken = async (): Promise<string | null> => {
    try {
      if (!isSupabaseConfigured || !session) {
        console.log('No session or Supabase not configured');
        return null;
      }

      // Check if we have a Google provider token
      const googleTokenData = session.provider_token;
      
      if (!googleTokenData) {
        console.log('No Google token found in session');
        return null;
      }

      // Check token expiration (Google tokens typically expire in 1 hour)
      const tokenExpiry = session.expires_at;
      const now = Math.floor(Date.now() / 1000);
      
      // If token expires within 5 minutes, refresh it
      if (tokenExpiry && (tokenExpiry - now) < 300) {
        console.log('Token expiring soon, attempting refresh...');
        const refreshResult = await refreshGoogleToken();
        return refreshResult.token;
      }

      return googleTokenData;
    } catch (error) {
      console.error('Error getting valid Google token:', error);
      return null;
    }
  };

  const refreshGoogleToken = async (): Promise<{ token: string | null; error: any }> => {
    try {
      if (!isSupabaseConfigured || !session) {
        return { token: null, error: { message: 'No session available' } };
      }

      const refreshToken = session.provider_refresh_token;
      
      if (!refreshToken) {
        return { token: null, error: { message: 'No refresh token available' } };
      }

      console.log('Refreshing Google token...');

      // Use Google's token refresh endpoint
      const response = await fetch('https://oauth2.googleapis.com/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID || '',
          refresh_token: refreshToken,
          grant_type: 'refresh_token',
        }),
      });

      if (!response.ok) {
        const errorData = await response.text();
        console.error('Token refresh failed:', errorData);
        return { token: null, error: { message: 'Token refresh failed', details: errorData } };
      }

      const tokenData = await response.json();
      
      // Update the session with new token - this might require custom handling
      // since Supabase doesn't directly support updating provider tokens
      if (tokenData.access_token) {
        console.log('Google token refreshed successfully');
        
        // Store the new token temporarily in session storage for immediate use
        sessionStorage.setItem('google_access_token', tokenData.access_token);
        sessionStorage.setItem('google_token_expiry', String(Date.now() + (tokenData.expires_in * 1000)));
        
        return { token: tokenData.access_token, error: null };
      }

      return { token: null, error: { message: 'No access token in response' } };
    } catch (error) {
      console.error('Error refreshing Google token:', error);
      return { token: null, error };
    }
  };

  // New user vault methods
  const getUserId = (): string | null => {
    return user?.id || null;
  };

  const initializeUserVault = async (): Promise<void> => {
    const userId = getUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    try {
      // Check if user vault already exists
      const vaultInfo = await getUserVaultInfo(userId);
      
      if (vaultInfo.result.total_vaults === 0) {
        // Create default vault for new user
        await createUserVault(userId, 'default', 'Default user vault');
        console.log('✅ Created default vault for user:', userId);
      } else {
        console.log('🏛️ User vault already exists for:', userId);
      }
    } catch (error) {
      console.error('Error initializing user vault:', error);
      throw error;
    }
  };

  const hasUserVault = async (): Promise<boolean> => {
    const userId = getUserId();
    if (!userId) {
      return false;
    }

    try {
      const vaultInfo = await getUserVaultInfo(userId);
      return vaultInfo.result.total_vaults > 0;
    } catch (error) {
      console.error('Error checking user vault:', error);
      return false;
    }
  };

  // Initialize user vault when user logs in
  useEffect(() => {
    if (user && !loading) {
      initializeUserVault().catch(console.error);
    }
  }, [user, loading]);

  // Clear tokens when user logs out
  const signOutWithCleanup = async (): Promise<void> => {
    const userId = getUserId();
    if (userId) {
      clearUserTokens(userId);
    }
    await signOut();
  };

  const value: AuthContextType = {
    user,
    session,
    loading,
    signIn,
    signUp,
    signOut: signOutWithCleanup,
    signInWithOAuth,
    getValidGoogleToken,
    refreshGoogleToken,
    getUserId,
    initializeUserVault,
    hasUserVault
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
