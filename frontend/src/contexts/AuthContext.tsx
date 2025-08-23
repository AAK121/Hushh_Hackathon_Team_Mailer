import React, { createContext, useContext, useEffect, useState } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { auth, isSupabaseConfigured } from '../lib/supabase'

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
    
    // If Supabase is not configured, use demo authentication
    if (!isSupabaseConfigured) {
      console.log('🔧 Using demo authentication - Supabase not configured')
      // Check for existing demo session
      const savedUser = localStorage.getItem('hushhmail_demo_user')
      if (savedUser) {
        console.log('Found saved demo user:', savedUser);
        const userData = JSON.parse(savedUser)
        // Create a mock user object compatible with Supabase User type
        const mockUser: User = {
          id: userData.id || 'demo-user-' + Date.now(),
          email: userData.email,
          user_metadata: {
            full_name: userData.name
          },
          app_metadata: {},
          aud: 'authenticated',
          created_at: userData.created_at || new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        setUser(mockUser)
      } else {
        console.log('No saved demo user found');
      }
      setLoading(false)
      return
    }

    console.log('✅ Supabase is configured, clearing demo user and checking session');
    // Clear any demo user data when Supabase is configured
    localStorage.removeItem('hushhmail_demo_user')

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
      
      // Use demo authentication if Supabase is not configured
      if (!isSupabaseConfigured) {
        // Simple validation for demo
        if (!email || !password) {
          return { error: { message: 'Email and password are required' } }
        }
        
        // Create mock user for demo
        const mockUser: User = {
          id: 'demo-user-' + Date.now(),
          email: email,
          user_metadata: {
            full_name: email.split('@')[0].charAt(0).toUpperCase() + email.split('@')[0].slice(1)
          },
          app_metadata: {},
          aud: 'authenticated',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        
        // Save to localStorage for demo persistence
        localStorage.setItem('hushhmail_demo_user', JSON.stringify({
          id: mockUser.id,
          email: mockUser.email,
          name: mockUser.user_metadata.full_name,
          created_at: mockUser.created_at
        }))
        
        setUser(mockUser)
        return { error: null }
      }
      
      // Use Supabase authentication
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
      
      // Use demo authentication if Supabase is not configured
      if (!isSupabaseConfigured) {
        // Simple validation for demo
        if (!email || !password) {
          return { error: { message: 'Email and password are required' } }
        }
        
        // Create mock user for demo
        const mockUser: User = {
          id: 'demo-user-' + Date.now(),
          email: email,
          user_metadata: {
            full_name: name || email.split('@')[0].charAt(0).toUpperCase() + email.split('@')[0].slice(1)
          },
          app_metadata: {},
          aud: 'authenticated',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        
        // Save to localStorage for demo persistence
        localStorage.setItem('hushhmail_demo_user', JSON.stringify({
          id: mockUser.id,
          email: mockUser.email,
          name: mockUser.user_metadata.full_name,
          created_at: mockUser.created_at
        }))
        
        setUser(mockUser)
        return { error: null }
      }
      
      // Use Supabase authentication
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
      
      // Use demo authentication if Supabase is not configured
      if (!isSupabaseConfigured) {
        localStorage.removeItem('hushhmail_demo_user')
        setUser(null)
        setSession(null)
        return
      }
      
      // Use Supabase authentication
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
      // Use demo authentication if Supabase is not configured
      if (!isSupabaseConfigured) {
        return { error: { message: `OAuth with ${provider} requires Supabase configuration. Please add your Supabase credentials to .env file.` } }
      }
      
      // Use Supabase OAuth
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
      const refreshToken = session.provider_refresh_token;
      
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

  const value: AuthContextType = {
    user,
    session,
    loading,
    signIn,
    signUp,
    signOut,
    signInWithOAuth,
    getValidGoogleToken,
    refreshGoogleToken
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
