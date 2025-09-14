'use client';

import { useAuth } from '@/components/AuthProvider';
import { SignInButton, SignOutButton } from '@/components/SignInButton';

export default function ProfilePage() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-64 h-24 bg-neutral-100 rounded-2xl animate-pulse" aria-hidden />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-white border border-brand-muted rounded-2xl p-6 text-center shadow-elevation-3">
          <h1 className="text-2xl font-bold text-secondary-800 mb-2">You are not signed in</h1>
          <p className="text-neutral-700 mb-6">Sign in to view your profile.</p>
          <SignInButton className="w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="max-w-lg w-full bg-white border border-brand-muted rounded-2xl p-6 shadow-elevation-3">
        <h1 className="text-2xl font-bold text-secondary-800 mb-4">Profile</h1>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-neutral-600">Email</span>
            <span className="font-medium text-neutral-900">{user.email || '—'}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-neutral-600">User ID</span>
            <span className="font-mono text-sm text-neutral-900">{user.id}</span>
          </div>
        </div>
        <div className="mt-6">
          <SignOutButton className="w-full" />
        </div>
      </div>
    </div>
  );
}

