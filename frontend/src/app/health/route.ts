// Minimal healthcheck endpoint with tiny plain-text response
// Ensures a dynamic response so cron jobs don't fetch the full app

export const dynamic = 'force-dynamic'

export function GET() {
  return new Response('health-true', {
    status: 200,
    headers: {
      'content-type': 'text/plain; charset=utf-8',
      // Avoid caching so it always hits the server/runtime
      'cache-control': 'no-store, no-cache, must-revalidate, max-age=0',
    },
  })
}

