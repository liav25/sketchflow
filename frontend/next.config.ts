import type { NextConfig } from 'next'

function originFrom(url?: string) {
  try {
    if (!url) return ''
    const u = new URL(url)
    return u.origin
  } catch {
    return ''
  }
}

const apiOrigin = originFrom(process.env.NEXT_PUBLIC_API_URL)

const securityHeaders = [
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
  { key: 'Strict-Transport-Security', value: 'max-age=15552000' }, // 180 days
]

const csp = [
  "default-src 'self'",
  "base-uri 'self'",
  "img-src 'self' data: blob:",
  // Mermaid and our UI may use inline styles for rendering
  "style-src 'self' 'unsafe-inline'",
  // Allow calling our API and Supabase
  `connect-src 'self' ${apiOrigin} https://*.supabase.co`,
  "font-src 'self' data:",
  "frame-ancestors 'none'",
].join('; ')

const nextConfig: NextConfig = {
  async headers() {
    // Disable CSP in development to avoid Turbopack issues
    if (process.env.NODE_ENV === 'development') {
      return []
    }
    
    return [
      {
        source: '/(.*)',
        headers: [
          ...securityHeaders,
          { key: 'Content-Security-Policy', value: csp },
        ],
      },
    ]
  },
}

export default nextConfig
