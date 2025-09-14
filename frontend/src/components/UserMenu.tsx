'use client';

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/components/AuthProvider';
import { SignInButton } from '@/components/SignInButton';

export default function UserMenu() {
  const { user, loading, signOut } = useAuth();
  const [open, setOpen] = useState(false);
  const btnRef = useRef<HTMLButtonElement | null>(null);
  const menuRef = useRef<HTMLDivElement | null>(null);

  // Debug logging
  console.log('[UserMenu] Render state:', { 
    hasUser: !!user, 
    userId: user?.id,
    email: user?.email,
    loading 
  });

  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (!open) return;
      const t = e.target as Node;
      if (menuRef.current && !menuRef.current.contains(t) && btnRef.current && !btnRef.current.contains(t)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, [open]);

  if (loading) {
    console.log('[UserMenu] Showing loading state');
    return (
      <div className="w-24 h-9 bg-neutral-100 rounded-lg animate-pulse" aria-hidden />
    );
  }

  if (!user) {
    console.log('[UserMenu] Showing sign-in button - no user');
    return <SignInButton />;
  }

  console.log('[UserMenu] Showing user menu for:', user.email);

  const initial = (user.email?.[0] || '#').toUpperCase();

  return (
    <div className="relative">
      <button
        ref={btnRef}
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 px-3 py-2 border border-brand-muted rounded-xl bg-white hover:bg-neutral-50 text-neutral-800 shadow-sm"
        aria-haspopup="menu"
        aria-expanded={open}
      >
        <div className="w-7 h-7 rounded-full bg-secondary-600 text-white flex items-center justify-center text-sm font-semibold">
          {initial}
        </div>
        <span className="hidden sm:block text-sm font-medium max-w-[160px] truncate">
          {user.email || 'Account'}
        </span>
        <svg className={`w-4 h-4 text-neutral-500 transition-transform ${open ? 'rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 10.94l3.71-3.71a.75.75 0 111.06 1.06l-4.24 4.24a.75.75 0 01-1.06 0L5.21 8.29a.75.75 0 01.02-1.08z" clipRule="evenodd" />
        </svg>
      </button>

      {open && (
        <div
          ref={menuRef}
          role="menu"
          className="absolute right-0 mt-2 w-56 rounded-xl border border-brand-muted bg-white shadow-elevation-4 p-1 z-50"
        >
          <div className="px-3 py-2 text-xs text-neutral-500">Signed in as</div>
          <div className="px-3 pb-2 text-sm font-medium text-neutral-800 truncate">
            {user.email || user.id}
          </div>

          <a
            href="/profile"
            role="menuitem"
            className="block w-full text-left px-3 py-2 rounded-lg text-sm text-neutral-800 hover:bg-neutral-50"
            onClick={() => setOpen(false)}
          >
            Profile
          </a>

          <button
            role="menuitem"
            className="block w-full text-left px-3 py-2 rounded-lg text-sm text-neutral-800 hover:bg-neutral-50"
            onClick={async () => {
              setOpen(false);
              await signOut();
            }}
          >
            Sign out
          </button>
        </div>
      )}
    </div>
  );
}

