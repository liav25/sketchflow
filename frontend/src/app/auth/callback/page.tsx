'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabaseClient';

export default function AuthCallback() {
  const router = useRouter();

  useEffect(() => {
    const run = async () => {
      console.log('[AuthCallback] Processing auth callback...');
      console.log('[AuthCallback] Current URL:', window.location.href);
      console.log('[AuthCallback] URL params:', new URL(window.location.href).searchParams.toString());
      
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      console.log('[AuthCallback] Auth code present:', !!code);
      
      try {
        // Try the newer method first
        const { data, error } = await supabase.auth.exchangeCodeForSession(window.location.href);
        console.log('[AuthCallback] Code exchange result:', { 
          hasSession: !!data.session, 
          userId: data.session?.user?.id,
          email: data.session?.user?.email,
          error 
        });
        
        if (error) {
          console.error('[AuthCallback] Auth callback error:', error);
          // If exchange failed, try getting session directly
          const { data: sessionData } = await supabase.auth.getSession();
          console.log('[AuthCallback] Direct session check:', {
            hasSession: !!sessionData.session,
            userId: sessionData.session?.user?.id,
            email: sessionData.session?.user?.email
          });
        } else {
          console.log('[AuthCallback] Successfully exchanged code for session');
        }
      } catch (e) {
        console.error('[AuthCallback] Auth exchange error:', e);
        
        // Fallback: try to get current session
        try {
          const { data: sessionData } = await supabase.auth.getSession();
          console.log('[AuthCallback] Fallback session check:', {
            hasSession: !!sessionData.session,
            userId: sessionData.session?.user?.id,
            email: sessionData.session?.user?.email
          });
        } catch (fallbackError) {
          console.error('[AuthCallback] Fallback session check failed:', fallbackError);
        }
      }
      
      const redirectTarget = sessionStorage.getItem('sf.redirect') || '/';
      console.log('[AuthCallback] Redirecting to:', redirectTarget);
      
      // Wait longer for auth state to propagate properly
      setTimeout(() => {
        sessionStorage.removeItem('sf.redirect');
        console.log('[AuthCallback] Executing redirect now');
        router.replace(redirectTarget);
      }, 500);
    };
    run();
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-neutral-600">Signing you in…</p>
    </div>
  );
}

