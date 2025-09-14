'use client';

import { useEffect, useRef, useState } from 'react';

type MermaidLib = import('mermaid').Mermaid;

interface MermaidPreviewProps {
  code: string;
}

export default function MermaidPreview({ code }: MermaidPreviewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [error, setError] = useState<string | null>(null);
  const initializedRef = useRef(false);

  useEffect(() => {
    let cancelled = false;
    setError(null);

    const render = async () => {
      try {
        // Dynamically import Mermaid on the client to avoid SSR issues
        const mod = await import('mermaid');
        const mermaid: MermaidLib = (mod as { default: MermaidLib }).default;

        const prefersDark = typeof window !== 'undefined' &&
          'matchMedia' in window && window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (!initializedRef.current) {
          mermaid.initialize({
            startOnLoad: false,
            securityLevel: 'strict',
            theme: prefersDark ? 'dark' : 'default',
          });
          initializedRef.current = true;
        }

        // Validate before rendering to provide clearer errors
        await mermaid.parse(code);

        const id = `mmd-${Math.random().toString(36).slice(2)}`;
        const { svg } = await mermaid.render(id, code);
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      } catch (e: unknown) {
        if (!cancelled) {
          const message = e instanceof Error ? e.message : 'Failed to render Mermaid diagram';
          setError(message);
          if (containerRef.current) containerRef.current.innerHTML = '';
        }
      }
    };

    render();

    return () => {
      cancelled = true;
    };
  }, [code]);

  return (
    <div className="w-full overflow-auto">
      {error ? (
        <div className="text-sm text-error-600 dark:text-error-400">
          {error}
        </div>
      ) : (
        <div ref={containerRef} />
      )}
    </div>
  );
}
