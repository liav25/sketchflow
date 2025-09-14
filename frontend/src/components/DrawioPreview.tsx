'use client';

import { useEffect, useRef, useState } from 'react';

interface DrawioPreviewProps {
  xml: string;
}

export default function DrawioPreview({ xml }: DrawioPreviewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
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

  // Build a proper #R URL (deflateRaw + base64, then used as-is after #R)
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        if (!xml) {
          if (!cancelled) setFallbackUrl(null);
          return;
        }
        const { deflateRaw } = await import('pako');
        const deflated = deflateRaw(new TextEncoder().encode(xml));
        const b64 = uint8ToBase64(deflated);
        if (!cancelled) setFallbackUrl(`https://app.diagrams.net/#R${b64}`);
      } catch {
        if (!cancelled) setFallbackUrl(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [xml]);

  useEffect(() => {
    let cancelled = false;
    let timeoutId: NodeJS.Timeout | null = null;
    
    setError(null);
    setLoading(true);

    const render = async () => {
      try {
        if (!containerRef.current || !xml) return;
        
        // Clean the container
        containerRef.current.innerHTML = '';
        
        // Create iframe with official postMessage API - this is the most reliable approach
        const iframe = document.createElement('iframe');
        iframe.style.width = '100%';
        iframe.style.height = '400px';
        iframe.style.border = 'none';
        iframe.style.borderRadius = '8px';
        // Use official Draw.io embed URL as per documentation
        iframe.src = 'https://embed.diagrams.net/?embed=1&proto=json&spin=1';
        
        let messageReceived = false;
        
        // PostMessage listener for Draw.io ready event (following official docs)
        const messageListener = (event: MessageEvent) => {
          if (cancelled || !iframe.contentWindow || messageReceived) return;
          
          try {
            // Parse JSON message as per Draw.io documentation
            const msg = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
            
            // Handle init event as per official Draw.io documentation
            if (msg.event === 'init') {
              messageReceived = true;
              
              // Send load action with XML as specified in Draw.io docs
              iframe.contentWindow.postMessage(JSON.stringify({
                action: 'load',
                xml: xml
              }), '*');
              
              if (!cancelled) {
                setLoading(false);
                setError(null);
                if (timeoutId) clearTimeout(timeoutId);
              }
            }
            
          } catch {
            // Handle non-JSON messages (like simple 'ready' string)
            if (event.data === 'ready' && !messageReceived) {
              messageReceived = true;
              
              try {
                iframe.contentWindow.postMessage({
                  action: 'load',
                  xml: xml
                }, '*');
                
                if (!cancelled) {
                  setLoading(false);
                  setError(null);
                  if (timeoutId) clearTimeout(timeoutId);
                }
              } catch {
                if (!cancelled) {
                  setError('Failed to load diagram content');
                  setLoading(false);
                }
              }
            }
          }
        };

        window.addEventListener('message', messageListener);
        
        iframe.onerror = () => {
          if (!cancelled) {
            setError('Failed to load diagram viewer');
            setLoading(false);
          }
          window.removeEventListener('message', messageListener);
        };

        containerRef.current.appendChild(iframe);
        
        // Set timeout
        timeoutId = setTimeout(() => {
          if (!cancelled) {
            setError('Diagram preview timed out');
            setLoading(false);
            window.removeEventListener('message', messageListener);
          }
        }, 10000);
        
        // Cleanup function for the message listener
        return () => {
          window.removeEventListener('message', messageListener);
        };

      } catch (e) {
        const message = e instanceof Error ? e.message : 'Failed to render Draw.io diagram';
        if (!cancelled) {
          setError(message);
          setLoading(false);
          if (containerRef.current) containerRef.current.innerHTML = '';
        }
      }
    };

    render();

    return () => {
      cancelled = true;
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [xml]);

  if (error) {
    return (
      <div className="w-full h-64 flex items-center justify-center bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div className="text-center space-y-4">
          <div className="text-orange-600 dark:text-orange-400">
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
                className="inline-flex items-center px-3 py-2 text-xs font-medium text-blue-600 dark:text-blue-400 border border-blue-300 dark:border-blue-500 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
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
      <div ref={containerRef} className="w-full" />
    </div>
  );
}
