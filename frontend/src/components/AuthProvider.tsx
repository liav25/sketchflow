'use client';

import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { supabase } from '@/lib/supabaseClient';

type User = {
  id: string;
  email?: string | null;
};

type AuthContextType = {
  user: User | null;
  loading: boolean;
  signInWithGoogle: (redirectTo?: string) => Promise<void>;
  signOut: () => Promise<void>;
  getAccessToken: () => Promise<string | null>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Log configuration on startup
  console.log('[AuthProvider] Configuration:', {
    supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL,
    hasAnonKey: !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    anonKeyLength: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.length || 0
  });

  useEffect(() => {
    console.log('[AuthProvider] Initializing auth state...');
    
    // Load initial session
    supabase.auth.getSession().then(({ data, error }) => {
      console.log('[AuthProvider] Initial session loaded:', { 
        hasSession: !!data.session, 
        userId: data.session?.user?.id,
        email: data.session?.user?.email,
        error 
      });
      
      const s = data.session;
      const newUser = s ? { id: s.user.id, email: s.user.email } : null;
      console.log('[AuthProvider] Setting initial user:', newUser);
      setUser(newUser);
      setLoading(false);
    });

    const { data: sub } = supabase.auth.onAuthStateChange((event, session) => {
      console.log('[AuthProvider] Auth state changed:', { 
        event, 
        hasSession: !!session,
        userId: session?.user?.id,
        email: session?.user?.email 
      });
      
      const newUser = session ? { id: session.user.id, email: session.user.email } : null;
      console.log('[AuthProvider] Updating user state:', newUser);
      setUser(newUser);
      setLoading(false);
    });
    
    return () => {
      console.log('[AuthProvider] Cleaning up auth subscription');
      sub.subscription.unsubscribe();
    };
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      async signInWithGoogle(redirectTo?: string) {
        const url = redirectTo || `${window.location.origin}/auth/callback`;
        console.log('[AuthProvider] Starting Google sign-in with redirect:', url);
        console.log('[AuthProvider] Current origin:', window.location.origin);
        
        const { data, error } = await supabase.auth.signInWithOAuth({
          provider: 'google',
          options: { redirectTo: url, queryParams: { prompt: 'select_account' } },
        });
        
        console.log('[AuthProvider] Google sign-in result:', { data, error });
        if (error) {
          console.error('[AuthProvider] Sign-in error:', error);
        }
      },
      async signOut() {
        console.log('[AuthProvider] Starting sign out...');
        const { error } = await supabase.auth.signOut();
        console.log('[AuthProvider] Sign out result:', { error });
        if (error) {
          console.error('[AuthProvider] Sign out error:', error);
        }
      },
      async getAccessToken() {
        const { data } = await supabase.auth.getSession();
        return data.session?.access_token ?? null;
      },
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
