'use client';

import { useAuth } from './AuthProvider';

export function SignInButton({ className = '' }: { className?: string }) {
  const { signInWithGoogle } = useAuth();
  
  const handleSignIn = async () => {
    console.log('[SignInButton] Sign in button clicked');
    console.log('[SignInButton] Current location:', {
      pathname: window.location.pathname,
      search: window.location.search,
      origin: window.location.origin,
      href: window.location.href
    });
    
    // Store redirect target before starting OAuth
    const redirectPath = window.location.pathname + window.location.search;
    console.log('[SignInButton] Storing redirect path:', redirectPath);
    sessionStorage.setItem('sf.redirect', redirectPath);
    
    try {
      console.log('[SignInButton] Calling signInWithGoogle...');
      await signInWithGoogle();
      console.log('[SignInButton] signInWithGoogle completed');
    } catch (error) {
      console.error('[SignInButton] Error during sign in:', error);
    }
  };
  
  return (
    <button
      className={`btn-secondary ${className}`}
      onClick={handleSignIn}
    >
      Sign In
    </button>
  );
}

export function SignOutButton({ className = '' }: { className?: string }) {
  const { signOut } = useAuth();
  
  const handleSignOut = async () => {
    console.log('[SignOutButton] Sign out button clicked');
    try {
      console.log('[SignOutButton] Calling signOut...');
      await signOut();
      console.log('[SignOutButton] signOut completed');
    } catch (error) {
      console.error('[SignOutButton] Error during sign out:', error);
    }
  };
  
  return (
    <button className={`btn-secondary ${className}`} onClick={handleSignOut}>
      Sign Out
    </button>
  );
}
