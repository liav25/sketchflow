import { createBrowserClient } from "@supabase/ssr";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseKey);

// Minimal no-op auth implementation to avoid crashes when env vars are missing
type BrowserSupabase = ReturnType<typeof createBrowserClient>;

function createNoopSupabase(): BrowserSupabase {
  const noop = () => {};
  const client = {
    auth: {
      async getSession() {
        return { data: { session: null }, error: null } as const;
      },
      onAuthStateChange() {
        return { data: { subscription: { unsubscribe: noop } }, error: null } as const;
      },
      async signInWithOAuth() {
        console.warn('[Supabase] signInWithOAuth called but Supabase is not configured');
        return { data: { url: null }, error: null } as const;
      },
      async signOut() {
        console.warn('[Supabase] signOut called but Supabase is not configured');
        return { error: null } as const;
      },
      async exchangeCodeForSession() {
        console.warn('[Supabase] exchangeCodeForSession called but Supabase is not configured');
        return { data: { session: null, user: null }, error: null } as const;
      },
      async getUser() {
        return { data: { user: null }, error: null } as const;
      },
    },
  } as unknown as BrowserSupabase;
  return client;
}

export const createClient = () => {
  if (!isSupabaseConfigured) {
    console.warn('[Supabase] Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY. Falling back to no-op client.');
    return createNoopSupabase();
  }
  return createBrowserClient(supabaseUrl!, supabaseKey!);
};
