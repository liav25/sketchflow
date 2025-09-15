'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createClient } from '@/utils/supabase/client';

export default function AuthCallback() {
  const router = useRouter();
  const supabase = createClient();

  useEffect(() => {
    const run = async () => {
      console.log('[AuthCallback] Processing auth callback...');
      console.log('[AuthCallback] Current URL:', window.location.href);
      console.log('[AuthCallback] URL params:', new URL(window.location.href).searchParams.toString());
      
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      console.log('[AuthCallback] Auth code present:', !!code);
      
      try {
        if (code) {
          // PKCE/code flow
          const { data, error } = await supabase.auth.exchangeCodeForSession(window.location.href);
          console.log('[AuthCallback] Code exchange result:', { 
            hasSession: !!data.session, 
            userId: data.session?.user?.id,
            email: data.session?.user?.email,
            error 
          });
          if (error) {
            console.error('[AuthCallback] Auth callback error:', error);
          }
        } else {
          // Implicit flow (tokens in URL hash)
          const hashParams = new URLSearchParams(window.location.hash.slice(1));
          const access_token = hashParams.get('access_token');
          const refresh_token = hashParams.get('refresh_token');
          console.log('[AuthCallback] Implicit flow tokens found:', !!access_token);
          if (access_token && refresh_token) {
            const { data, error } = await supabase.auth.setSession({
              access_token,
              refresh_token,
            });
            console.log('[AuthCallback] setSession result:', {
              hasSession: !!data.session,
              userId: data.session?.user?.id,
              email: data.session?.user?.email,
              error,
            });
            if (error) console.error('[AuthCallback] setSession error:', error);
          } else {
            // As a fallback, allow supabase-js to detect session in URL if possible
            const { data: s } = await supabase.auth.getSession();
            console.log('[AuthCallback] getSession (no code/hash) result:', { hasSession: !!s.session });
          }
        }
      } catch (e) {
        console.error('[AuthCallback] Auth processing error:', e);
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
