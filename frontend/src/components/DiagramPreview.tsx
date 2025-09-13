'use client';

import { useState } from 'react';
import { 
  ArrowLeftIcon,
  ClipboardDocumentIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  CheckIcon
} from '@heroicons/react/24/outline';
import type { DiagramFormat } from '@/app/page';

interface DiagramPreviewProps {
  format: DiagramFormat;
  diagramCode: string;
  onReset: () => void;
}

export default function DiagramPreview({
  format,
  diagramCode,
  onReset,
}: DiagramPreviewProps) {
  const [copied, setCopied] = useState(false);

  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(diagramCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([diagramCode], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `diagram.${format === 'mermaid' ? 'mmd' : 'xml'}`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'SketchFlow Diagram',
          text: `Check out this ${format} diagram created with SketchFlow!`,
          files: [new File([diagramCode], `diagram.${format === 'mermaid' ? 'mmd' : 'xml'}`, {
            type: 'text/plain'
          })]
        });
      } catch (err) {
        console.error('Error sharing:', err);
        handleCopyCode(); // Fallback to copy
      }
    } else {
      handleCopyCode(); // Fallback to copy
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={onReset}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <ArrowLeftIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
              </button>
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Your {format === 'mermaid' ? 'Mermaid' : 'Draw.io'} Diagram
                </h2>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Conversion completed successfully!
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100">
                <CheckIcon className="h-3 w-3 mr-1" />
                Complete
              </span>
            </div>
          </div>
        </div>

        <div className="p-6">
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Preview Area */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Diagram Preview
              </h3>
              
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-8 text-center min-h-[300px] flex items-center justify-center">
                {format === 'mermaid' ? (
                  <div className="space-y-4">
                    <div className="text-blue-600 dark:text-blue-400">
                      <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <p className="text-gray-600 dark:text-gray-300">
                      Mermaid diagram ready!
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Use the code below in any Mermaid-compatible tool
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="text-green-600 dark:text-green-400">
                      <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                      </svg>
                    </div>
                    <p className="text-gray-600 dark:text-gray-300">
                      Draw.io XML ready!
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Import this XML into Draw.io to edit your diagram
                    </p>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={handleCopyCode}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
                >
                  {copied ? (
                    <>
                      <CheckIcon className="h-4 w-4" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <ClipboardDocumentIcon className="h-4 w-4" />
                      Copy Code
                    </>
                  )}
                </button>
                
                <button
                  onClick={handleDownload}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
                >
                  <ArrowDownTrayIcon className="h-4 w-4" />
                  Download
                </button>
                
                <button
                  onClick={handleShare}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors"
                >
                  <ShareIcon className="h-4 w-4" />
                  Share
                </button>
              </div>
            </div>

            {/* Code Display */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Generated Code
                </h3>
                <span className="text-xs font-mono text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                  {format === 'mermaid' ? '.mmd' : '.xml'}
                </span>
              </div>
              
              <div className="bg-gray-900 rounded-lg overflow-hidden">
                <div className="bg-gray-800 px-4 py-2 text-xs text-gray-400 border-b border-gray-700">
                  {format === 'mermaid' ? 'Mermaid Syntax' : 'Draw.io XML'}
                </div>
                <pre className="p-4 text-sm text-gray-100 overflow-x-auto max-h-96 overflow-y-auto">
                  <code>{diagramCode}</code>
                </pre>
              </div>

              <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
                <p>• Lines: {diagramCode.split('\n').length}</p>
                <p>• Characters: {diagramCode.length}</p>
                <p>• Format: {format === 'mermaid' ? 'Mermaid' : 'Draw.io XML'}</p>
              </div>
            </div>
          </div>

          {/* Usage Instructions */}
          <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
              How to use your diagram:
            </h4>
            <div className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
              {format === 'mermaid' ? (
                <>
                  <p>• Paste the code into any Mermaid Live Editor</p>
                  <p>• Use in GitHub/GitLab markdown files</p>
                  <p>• Integrate with documentation tools like Notion, Confluence</p>
                  <p>• Render with mermaid CLI or online tools</p>
                </>
              ) : (
                <>
                  <p>• Import the XML file directly into Draw.io</p>
                  <p>• Open Draw.io and use File → Import from → Device</p>
                  <p>• Edit shapes, colors, and layout as needed</p>
                  <p>• Export to various formats (PNG, SVG, PDF)</p>
                </>
              )}
            </div>
          </div>

          {/* Try Another */}
          <div className="mt-6 text-center">
            <button
              onClick={onReset}
              className="inline-flex items-center px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 font-medium transition-colors"
            >
              Convert Another Sketch
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}