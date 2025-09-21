import type { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'SketchFlow',
    short_name: 'SketchFlow',
    description: 'Transform hand-drawn sketches into professional diagrams with AI',
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#1687A7',
    icons: [
      // Using SVG app icon; PNGs can be added later for broader PWA support
      { src: '/icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' },
    ],
  };
}

