'use client';

import { createBrowserClient } from '@supabase/ssr';

export const supabase = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
    // No `realtime.enabled` option in supabase-js v2; omit to avoid TS error
    global: {
      headers: {
        'X-Client-Info': 'sketchflow-web',
      },
    },
  }
);

