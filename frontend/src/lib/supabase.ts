import { createClient } from '@supabase/supabase-js'

// Supabase configuration
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// Check if environment variables are properly configured
const isConfigured = supabaseUrl && 
  supabaseAnonKey && 
  supabaseUrl !== 'your_supabase_project_url_here' &&
  supabaseAnonKey !== 'your_supabase_anon_key_here' &&
  supabaseUrl.startsWith('https://');

console.log('Supabase configuration check:');
console.log('- URL:', supabaseUrl);
console.log('- Key present:', !!supabaseAnonKey);
console.log('- Is configured:', isConfigured);

if (!isConfigured) {
  console.warn('⚠️ Supabase not configured. Please add your Supabase credentials to .env file');
  console.warn('Current VITE_SUPABASE_URL:', supabaseUrl);
  console.warn('Current VITE_SUPABASE_ANON_KEY:', supabaseAnonKey ? '[PRESENT]' : '[MISSING]');
} else {
  console.log('✅ Supabase configuration is valid');
}

// Create Supabase client
export const supabase = isConfigured 
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true
      }
    })
  : null;

// Types for authentication
export interface AuthUser {
  id: string
  email: string
  name?: string
  avatar_url?: string
  created_at: string
}

// Auth helper functions
export const auth = {
  // Sign up with email and password
  signUp: async (email: string, password: string, options?: { 
    data?: { name?: string } 
  }) => {
    if (!supabase) {
      return { data: null, error: { message: 'Supabase not configured' } };
    }
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: options?.data || {}
      }
    })
    return { data, error }
  },

  // Sign in with email and password
  signIn: async (email: string, password: string) => {
    if (!supabase) {
      return { data: null, error: { message: 'Supabase not configured' } };
    }
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })
    return { data, error }
  },

  // Sign in with OAuth providers (Google, GitHub, etc.)
  signInWithOAuth: async (provider: 'google' | 'github' | 'discord' | 'twitter') => {
    if (!supabase) {
      return { data: null, error: { message: 'Supabase not configured' } };
    }
    
    // For Google, request additional scopes for Calendar and Gmail with offline access
    const options = provider === 'google' ? {
      redirectTo: `${window.location.origin}`,
      scopes: 'https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
      queryParams: {
        access_type: 'offline',
        prompt: 'consent' // Use the modern OAuth 2.0 parameter instead of deprecated approval_prompt
      }
    } : {
      redirectTo: `${window.location.origin}`
    };
    
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider,
      options
    })
    return { data, error }
  },

  // Sign out
  signOut: async () => {
    if (!supabase) {
      return { error: { message: 'Supabase not configured' } };
    }
    const { error } = await supabase.auth.signOut()
    return { error }
  },

  // Get current user
  getCurrentUser: () => {
    if (!supabase) {
      return Promise.resolve({ data: { user: null }, error: { message: 'Supabase not configured' } });
    }
    return supabase.auth.getUser()
  },

  // Get current session
  getCurrentSession: () => {
    if (!supabase) {
      return Promise.resolve({ data: { session: null }, error: { message: 'Supabase not configured' } });
    }
    return supabase.auth.getSession()
  },

  // Listen to auth state changes
  onAuthStateChange: (callback: (event: string, session: any) => void) => {
    if (!supabase) {
      return { data: { subscription: { unsubscribe: () => {} } } };
    }
    return supabase.auth.onAuthStateChange(callback)
  },

  // Reset password
  resetPassword: async (email: string) => {
    if (!supabase) {
      return { data: null, error: { message: 'Supabase not configured' } };
    }
    const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`
    })
    return { data, error }
  }
}

export default supabase

// Export configuration status for components to check
export const isSupabaseConfigured = isConfigured;
