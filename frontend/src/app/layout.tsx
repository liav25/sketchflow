import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from '@/components/AuthProvider';

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "SketchFlow - AI-Powered Sketch to Diagram Converter",
  description: "Transform your hand-drawn sketches into professional digital diagrams (Mermaid, Draw.io & UML/PlantUML) with AI",
};

export const viewport: Viewport = {
  themeColor: '#ffffff',
  colorScheme: 'light',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* Google AdSense: injected in <head> on every page */}
        {process.env.NEXT_PUBLIC_ADSENSE_ENABLED !== 'false' ? (
          <script
            async
            src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9317202877406769"
            crossOrigin="anonymous"
          />
        ) : null}
        {/* Optional: helps Google associate your site with your AdSense account */}
        <meta name="google-adsense-account" content="ca-pub-9317202877406769" />
        {/* Perf hints for Auto ads */}
        <link rel="preconnect" href="https://pagead2.googlesyndication.com" crossOrigin="anonymous" />
        <link rel="dns-prefetch" href="https://pagead2.googlesyndication.com" />
        <link rel="preconnect" href="https://googleads.g.doubleclick.net" crossOrigin="anonymous" />
        <link rel="dns-prefetch" href="https://googleads.g.doubleclick.net" />
      </head>
      <body className={`${inter.variable} ${jetbrainsMono.variable} antialiased`}>
        <AuthProvider>
          {children}
          {/* Site-wide footer */}
          <footer className="py-10">
            <div className="container mx-auto px-4 text-center">
              <a
                href="https://www.buymeacoffee.com/liav25"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Buy me a coffee"
                className="inline-block"
              >
                <img
                  src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png"
                  alt="Buy Me A Coffee"
                  style={{ height: 60, width: 217 }}
                />
              </a>
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
