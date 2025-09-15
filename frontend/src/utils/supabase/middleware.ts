import { createServerClient } from "@supabase/ssr";
import { type NextRequest, NextResponse } from "next/server";
type ServerSupabase = ReturnType<typeof createServerClient>;

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

export const createClient = (request: NextRequest) => {
  // Create an unmodified response
  let supabaseResponse = NextResponse.next({
    request: {
      headers: request.headers,
    },
  });

  // If env vars are missing, return a no-op auth client to avoid crashes
  if (!supabaseUrl || !supabaseKey) {
    const supabase = {
      auth: {
        async getUser() {
          return { data: { user: null }, error: null } as const;
        },
      },
    } as unknown as ServerSupabase;
    return { supabase, response: supabaseResponse };
  }

  const supabase = createServerClient(
    supabaseUrl,
    supabaseKey,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
          supabaseResponse = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          );
        },
      },
    },
  );

  return { supabase, response: supabaseResponse };
};
