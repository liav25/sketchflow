'use client';

import { useEffect, useRef, useState } from 'react';

interface DrawioPreviewProps {
  xml: string;
}

declare global {
  interface Window {
    GraphViewer?: {
      createViewerForElement: (el: Element, cb?: (viewer: unknown) => void) => void;
      processElements: (cls?: string) => void;
    };
    onDrawioViewerLoad?: () => void;
  }
}

// Load the official viewer script once
function loadDrawioViewer(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (typeof window === 'undefined') return resolve();
    if (window.GraphViewer) return resolve();

    const existing = document.getElementById('drawio-viewer-script') as HTMLScriptElement | null;
    if (existing && window.GraphViewer) return resolve();

    const script = existing ?? document.createElement('script');
    if (!existing) {
      script.id = 'drawio-viewer-script';
      script.src = 'https://viewer.diagrams.net/js/viewer-static.min.js';
      script.async = true;
      document.head.appendChild(script);
    }

    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load Draw.io viewer'));
  });
}

// Helper: convert Uint8Array to base64 without stack overflow on large arrays
const uint8ToBase64 = (uint8: Uint8Array): string => {
  const CHUNK_SIZE = 0x8000;
  const chunks: string[] = [];
  for (let i = 0; i < uint8.length; i += CHUNK_SIZE) {
    const chunk = uint8.subarray(i, i + CHUNK_SIZE);
    const chunkArr: number[] = Array.from(chunk);
    chunks.push(String.fromCharCode(...chunkArr));
  }
  return btoa(chunks.join(''));
};

export default function DrawioPreview({ xml }: DrawioPreviewProps) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [fallbackUrl, setFallbackUrl] = useState<string | null>(null);

  // Prepare fallback Open-in-Draw.io URL
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        if (!xml) return setFallbackUrl(null);
        const { deflateRaw } = await import('pako');
        const deflated = deflateRaw(new TextEncoder().encode(xml));
        const b64 = uint8ToBase64(deflated);
        const openUrl = `https://app.diagrams.net/#R${b64}`;
        if (!cancelled) setFallbackUrl(openUrl);
      } catch {
        if (!cancelled) setFallbackUrl(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [xml]);

  // Initialize the viewer with data-mxgraph per jgraph/drawio-integration
  useEffect(() => {
    let cancelled = false;
    setError(null);
    setLoading(true);

    const render = async () => {
      try {
        if (!hostRef.current) return;
        // Clear previous content
        hostRef.current.innerHTML = '';

        if (!xml || xml.trim().length === 0) {
          if (!cancelled) setLoading(false);
          return;
        }

        await loadDrawioViewer();

        // Create the mxgraph container and attach config
        const el = document.createElement('div');
        el.className = 'mxgraph';
        el.style.width = '100%';
        el.style.minHeight = '420px';
        el.style.borderRadius = '8px';
        el.style.overflow = 'hidden';

        const config = {
          // Enable simple navigation controls
          nav: 1,
          resize: 1,
          toolbar: 0,
          lightbox: 0,
          'auto-fit': 1,
          // Provide raw XML; the viewer parses it internally
          xml,
        } as const;

        el.setAttribute('data-mxgraph', JSON.stringify(config));
        hostRef.current.appendChild(el);

        if (!window.GraphViewer) throw new Error('Draw.io viewer not available');

        // Render only this element
        window.GraphViewer.createViewerForElement(el, () => {
          if (!cancelled) setLoading(false);
        });
      } catch (e) {
        if (!cancelled) {
          const message = e instanceof Error ? e.message : 'Failed to render diagram';
          setError(message);
          setLoading(false);
        }
      }
    };

    render();
    return () => {
      cancelled = true;
    };
  }, [xml]);

  if (error) {
    return (
      <div className="w-full h-64 flex items-center justify-center bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div className="text-center space-y-4">
          <div className="text-primary-600 dark:text-primary-400">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-900 dark:text-white">Preview unavailable</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">{error}</p>
          </div>
          <div className="space-y-2">
            {fallbackUrl && (
              <a
                href={fallbackUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-3 py-2 text-xs font-medium text-primary-600 dark:text-primary-400 border border-primary-300 dark:border-primary-500 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
              >
                <svg className="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                Open in Draw.io
              </a>
            )}
            <p className="text-xs text-gray-400">View and edit your diagram</p>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="w-full h-64 flex items-center justify-center bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto"></div>
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Loading diagram preview...</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">This may take a few seconds</p>
          </div>
          <div className="w-32 h-1 bg-gray-200 dark:bg-gray-600 rounded-full mx-auto overflow-hidden">
            <div className="h-full bg-blue-600 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!xml || xml.trim().length === 0) {
    return (
      <div className="w-full h-64 flex items-center justify-center text-sm text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 rounded-lg">
        No diagram to preview
      </div>
    );
  }

  return (
    <div className="w-full overflow-hidden rounded-lg bg-white dark:bg-gray-800">
      <div ref={hostRef} className="w-full" />
    </div>
  );
}
