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
  description: "Transform your hand-drawn sketches into professional digital diagrams (Mermaid & Draw.io) with AI",
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
      </head>
      <body className={`${inter.variable} ${jetbrainsMono.variable} antialiased`}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
