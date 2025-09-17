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

// Include Google AdSense domains when ads are enabled
// Auto ads are injected via a global script in <head>, so we only
// depend on the enabled flag here (not a client env var).
const adsEnabled = process.env.NEXT_PUBLIC_ADSENSE_ENABLED !== 'false'

const scriptSrc = [
  "script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: data:",
  // AdSense loader
  ...(adsEnabled ? [
    'https://pagead2.googlesyndication.com',
  ] : []),
]

const imgSrc = [
  "img-src 'self' data: blob:",
  ...(adsEnabled ? [
    'https://*.googlesyndication.com',
    'https://*.doubleclick.net',
    'https://googleads.g.doubleclick.net',
    'https://tpc.googlesyndication.com',
    'https://www.gstatic.com',
  ] : []),
]

const frameSrc = [
  // Draw.io embed/viewer
  'https://embed.diagrams.net',
  'https://app.diagrams.net',
  'https://viewer.diagrams.net',
  // Lucidchart embed
  'https://lucid.app',
  'https://www.lucidchart.com',
  'https://app.lucidchart.com',
  // AdSense iframes
  ...(adsEnabled ? [
    'https://*.googlesyndication.com',
    'https://*.doubleclick.net',
    'https://googleads.g.doubleclick.net',
  ] : []),
]

const connectSrc = [
  `connect-src 'self' ${apiOrigin} https://*.supabase.co wss://*.supabase.co https://*.onrender.com`,
  ...(adsEnabled ? [
    'https://pagead2.googlesyndication.com',
    'https://googleads.g.doubleclick.net',
    'https://*.googlesyndication.com',
  ] : []),
]

const csp = [
  "default-src 'self'",
  "base-uri 'self'",
  imgSrc.join(' '),
  scriptSrc.join(' '),
  // Mermaid and our UI may use inline styles for rendering
  "style-src 'self' 'unsafe-inline'",
  // Allow calling our API/Supabase and (optionally) AdSense endpoints
  connectSrc.join(' '),
  // Allow embeds for Draw.io and (optionally) AdSense
  `frame-src ${frameSrc.join(' ')}`,
  "font-src 'self' data:",
  // Allow web workers if needed
  "worker-src 'self' blob:",
  "frame-ancestors 'none'",
].join('; ')

const nextConfig: NextConfig = {
  // External packages for server components
  serverExternalPackages: ['mermaid'],
  
  // Experimental features to fix streaming issues
  experimental: {},
  
  // Disable React strict mode in production to prevent double-hydration issues
  reactStrictMode: process.env.NODE_ENV !== 'production',
  
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
