'use client';

import { createBrowserClient } from '@supabase/ssr';
type BrowserSupabase = ReturnType<typeof createBrowserClient>;

const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

function createNoopSupabase(): BrowserSupabase {
  const noop = () => {};
  const client = {
    auth: {
      async getSession() { return { data: { session: null }, error: null } as const },
      onAuthStateChange() { return { data: { subscription: { unsubscribe: noop } }, error: null } as const },
      async signInWithOAuth() { return { data: { url: null }, error: null } as const },
      async signOut() { return { error: null } as const },
      async exchangeCodeForSession() { return { data: { session: null, user: null }, error: null } as const },
      async getUser() { return { data: { user: null }, error: null } as const },
    },
  } as unknown as BrowserSupabase;
  return client;
}

export const supabase = (url && anon)
  ? createBrowserClient(url, anon, {
      auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true },
      global: { headers: { 'X-Client-Info': 'sketchflow-web' } },
    })
  : createNoopSupabase();
