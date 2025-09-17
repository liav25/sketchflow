'use client';

import { useEffect, useMemo, useState } from 'react';

interface LucidchartPreviewProps {
  initialUrl?: string;
  // Optional: Draw.io XML we generated that users can import into Lucidchart
  fallbackXml?: string;
}

function extractSrcFromIframe(html: string): string | null {
  try {
    const match = html.match(/src\s*=\s*"([^"]+)"/i) || html.match(/src\s*=\s*'([^']+)'/i);
    return match ? match[1] : null;
  } catch {
    return null;
  }
}

function isAllowedLucidUrl(url: string): boolean {
  try {
    const u = new URL(url);
    const host = u.hostname.toLowerCase();
    return (
      host === 'lucid.app' ||
      host === 'www.lucidchart.com' ||
      host === 'app.lucidchart.com'
    );
  } catch {
    return false;
  }
}

export default function LucidchartPreview({ initialUrl, fallbackXml }: LucidchartPreviewProps) {
  const [embedUrl, setEmbedUrl] = useState<string>('');
  const [input, setInput] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!initialUrl) return;
    // If initial value looks like a valid URL and points to Lucid, use it.
    if (/^https?:\/\//i.test(initialUrl) && isAllowedLucidUrl(initialUrl)) {
      setEmbedUrl(initialUrl);
      setInput(initialUrl);
    } else if (/^<iframe/i.test(initialUrl)) {
      const src = extractSrcFromIframe(initialUrl);
      if (src && isAllowedLucidUrl(src)) {
        setEmbedUrl(src);
        setInput(src);
      }
    }
  }, [initialUrl]);

  const handleApply = () => {
    setError(null);
    const trimmed = input.trim();
    if (!trimmed) {
      setEmbedUrl('');
      return;
    }
    const candidate = /^<iframe/i.test(trimmed) ? (extractSrcFromIframe(trimmed) || '') : trimmed;
    if (!candidate) {
      setError('Could not find an iframe src in the provided snippet');
      return;
    }
    if (!isAllowedLucidUrl(candidate)) {
      setError('Invalid URL. Please paste a Lucidchart embed URL');
      return;
    }
    setEmbedUrl(candidate);
  };

  const importLink = useMemo(() => {
    // Lucidchart landing; users sign in and import Draw.io via File → Import
    return 'https://lucid.app/';
  }, []);

  return (
    <div className="w-full space-y-4">
      {/* Input for embed URL */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300">
          Lucidchart embed URL or iframe snippet
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="https://lucid.app/documents/embeddedchart/…"
            className="flex-1 px-3 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100"
          />
          <button
            onClick={handleApply}
            className="btn-secondary px-4"
          >
            Apply
          </button>
        </div>
        {error && (
          <p className="text-sm text-warning-700 dark:text-warning-400">{error}</p>
        )}
        <p className="text-xs text-neutral-500 dark:text-neutral-400">
          In Lucidchart: Share → Publish → Embed → copy the URL or iframe snippet and paste it here
        </p>
      </div>

      {/* Preview area */}
      <div className="w-full rounded-xl overflow-hidden bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700">
        {embedUrl ? (
          <iframe
            src={embedUrl}
            title="Lucidchart Preview"
            className="w-full"
            style={{ height: 420, border: 'none', borderRadius: 8 }}
          />
        ) : (
          <div className="p-6 space-y-4">
            <div className="text-neutral-700 dark:text-neutral-300">
              <p className="font-medium mb-1">No embed URL provided</p>
              <p className="text-sm">
                To preview a Lucidchart diagram here, publish your diagram in Lucidchart and paste the embed URL above.
              </p>
            </div>
            <div className="text-sm text-neutral-700 dark:text-neutral-300">
              <p className="font-medium mb-1">Tip: Start from your generated XML</p>
              <ol className="list-decimal ml-5 space-y-1">
                <li>Download the XML file from above</li>
                <li>Open Lucidchart → File → Import → Draw.io and select the XML</li>
                <li>Once ready, Share → Publish → Embed and copy the link</li>
                <li>Paste the link into the field above to preview it</li>
              </ol>
            </div>
            <div>
              <a
                href={importLink}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-ghost"
              >
                Open Lucidchart
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

