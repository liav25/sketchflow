'use client';

import { useEffect, useRef, useState } from 'react';

interface DrawioPreviewProps {
  xml: string;
}

export default function DrawioPreview({ xml }: DrawioPreviewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewerUrl, setViewerUrl] = useState<string | null>(null);
  const [fallbackUrl, setFallbackUrl] = useState<string | null>(null);

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

  // Build viewer and fallback URLs (#R deflateRaw+base64 payload)
  useEffect(() => {
    let cancelled = false;
    setError(null);
    setLoading(true);

    (async () => {
      try {
        if (!xml) {
          if (!cancelled) {
            setViewerUrl(null);
            setFallbackUrl(null);
            setLoading(false);
          }
          return;
        }
        const { deflateRaw } = await import('pako');
        const deflated = deflateRaw(new TextEncoder().encode(xml));
        const b64 = uint8ToBase64(deflated);

        // Read-only viewer (no postMessage needed)
        const url = `https://viewer.diagrams.net/?embed=1&spin=1&proto=json&nav=1#R${b64}`;
        const openUrl = `https://app.diagrams.net/#R${b64}`;

        if (!cancelled) {
          setViewerUrl(url);
          setFallbackUrl(openUrl);
        }
      } catch (e) {
        if (!cancelled) {
          const message = e instanceof Error ? e.message : 'Failed to prepare diagram preview';
          setError(message);
          setViewerUrl(null);
          setFallbackUrl(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

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
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              Preview unavailable
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {error.includes('timed out') 
                ? 'The diagram preview took too long to load'
                : 'Unable to load the diagram preview'
              }
            </p>
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
            <p className="text-xs text-gray-400">
              View and edit your diagram
            </p>
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
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Loading diagram preview...
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              This may take a few seconds
            </p>
          </div>
          <div className="w-32 h-1 bg-gray-200 dark:bg-gray-600 rounded-full mx-auto overflow-hidden">
            <div className="h-full bg-blue-600 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full overflow-hidden rounded-lg bg-white dark:bg-gray-800">
      <div ref={containerRef} className="w-full">
        {viewerUrl ? (
          <iframe
            src={viewerUrl}
            title="Draw.io Preview"
            className="w-full"
            style={{ height: 420, border: 'none', borderRadius: 8 }}
            onLoad={() => setLoading(false)}
            onError={() => setError('Failed to load diagram viewer')}
          />
        ) : (
          <div className="w-full h-64 flex items-center justify-center text-sm text-gray-500 dark:text-gray-400">
            No diagram to preview
          </div>
        )}
      </div>
    </div>
  );
}
