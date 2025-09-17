This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

## Ads (Google AdSense)

This app includes optional Google AdSense integration.

- Set the following variables in your `.env.local`:
  - `NEXT_PUBLIC_ADSENSE_CLIENT` (e.g., `ca-pub-1234567890123456`)
  - `NEXT_PUBLIC_ADSENSE_ENABLED=true|false`
  - `NEXT_PUBLIC_ADSENSE_SLOT_HOMEPAGE_MID` (numeric slot id)
  - `NEXT_PUBLIC_ADSENSE_SLOT_HOMEPAGE_BOTTOM` (numeric slot id)
- In development, if slots are unset or ads are disabled, a subtle placeholder renders.
- The AdSense script is injected in `src/app/layout.tsx` only when a client id is present and ads are enabled.
- Ad slots are rendered via `src/components/ads/AdSlot.tsx` and placed in `src/app/page.tsx`.
- Add an `ads.txt` record in `public/ads.txt` when live (see file for example).
- Content Security Policy: when ads are enabled, `next.config.ts` automatically adds required Google ad domains to CSP (`script-src`, `img-src`, `frame-src`, `connect-src`).
