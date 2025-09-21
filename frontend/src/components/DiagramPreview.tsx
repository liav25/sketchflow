'use client';

import { useState, useEffect, Component } from 'react';
import { 
  ArrowLeftIcon,
  ClipboardDocumentIcon,
  CheckIcon,
  SparklesIcon,
  CodeBracketIcon,
  EyeIcon,
  CloudArrowDownIcon,
  LinkIcon
} from '@heroicons/react/24/outline';
import { 
  CheckCircleIcon as CheckCircleIconSolid,
  SparklesIcon as SparklesIconSolid 
} from '@heroicons/react/24/solid';
import type { DiagramFormat } from '@/app/page';
import dynamic from 'next/dynamic';
import { createClient } from '@/utils/supabase/client';

// Error boundary for Mermaid rendering
interface MermaidErrorBoundaryProps {
  children: React.ReactNode;
  fallback: React.ComponentType;
}

interface MermaidErrorBoundaryState {
  hasError: boolean;
}

class MermaidErrorBoundary extends Component<MermaidErrorBoundaryProps, MermaidErrorBoundaryState> {
  constructor(props: MermaidErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Mermaid rendering error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      const Fallback = this.props.fallback;
      return <Fallback />;
    }
    return this.props.children;
  }
}

// Fallback component for Mermaid errors
const MermaidFallback = () => (
  <div className="text-center space-y-4 p-8">
    <div className="w-16 h-16 bg-warning-100 dark:bg-warning-900/30 rounded-xl flex items-center justify-center mx-auto">
      <CodeBracketIcon className="w-8 h-8 text-warning-600 dark:text-warning-400" />
    </div>
    <div>
      <h4 className="text-lg font-bold text-neutral-900 dark:text-white mb-2">
        Diagram Preview Unavailable
      </h4>
      <p className="text-neutral-600 dark:text-neutral-300">
        The diagram code is ready, but preview rendering failed.<br />
        You can still copy and use the code below.
      </p>
    </div>
  </div>
);

// Dynamically load the Mermaid preview to avoid SSR issues with proper error handling
const MermaidPreview = dynamic(() => import('./MermaidPreview'), { 
  ssr: false,
  loading: () => (
    <div className="text-center p-8">
      <div className="animate-pulse text-neutral-600">Loading diagram preview...</div>
    </div>
  ),
});

// Dynamically load the Draw.io preview to avoid SSR issues
const DrawioPreview = dynamic(() => import('./DrawioPreview'), {
  ssr: false,
  loading: () => (
    <div className="text-center p-8">
      <div className="animate-pulse text-neutral-600">Loading diagram preview...</div>
    </div>
  ),
});

// Dynamically load the PlantUML preview to avoid SSR issues
const PlantUMLPreview = dynamic(() => import('./PlantUMLPreview'), {
  ssr: false,
  loading: () => (
    <div className="text-center p-8">
      <div className="animate-pulse text-neutral-600">Loading UML preview...</div>
    </div>
  ),
});

interface DiagramPreviewProps {
  format: DiagramFormat;
  diagramCode: string;
  jobId?: string;
  onReset: () => void;
  embedUrl?: string;
}

export default function DiagramPreview({
  format,
  diagramCode,
  jobId,
  onReset,
  embedUrl,
}: DiagramPreviewProps) {
  const [copied, setCopied] = useState(false);
  const [downloaded, setDownloaded] = useState(false);
  const [shared, setShared] = useState(false);
  const [activeView, setActiveView] = useState<'preview' | 'code'>('preview');
  const supabase = createClient();

  // Celebration effect on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      // Trigger success animations
    }, 300);
    return () => clearTimeout(timer);
  }, []);

  const handleCopyCode = async () => {
    try {
      let code = diagramCode;
      const apiBase = process.env.NEXT_PUBLIC_API_URL;
      if (apiBase && jobId) {
        // Try fetching authoritative code from backend (auth-protected)
        const tok = (await supabase.auth.getSession()).data.session?.access_token
        const tokenResp = await fetch(apiBase + `/api/conversions/${jobId}/code`, {
          headers: tok ? { 'Authorization': `Bearer ${tok}` } : {},
        });
        if (tokenResp.ok) {
          const data = await tokenResp.json();
          code = data.code || code;
        }
      }
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handleDownload = async () => {
    let code = diagramCode;
    const apiBase = process.env.NEXT_PUBLIC_API_URL;
    if (apiBase && jobId) {
      try {
        const tok = (await supabase.auth.getSession()).data.session?.access_token
        const tokenResp = await fetch(apiBase + `/api/conversions/${jobId}/code`, {
          headers: tok ? { 'Authorization': `Bearer ${tok}` } : {},
        });
        if (tokenResp.ok) {
          const data = await tokenResp.json();
          code = data.code || code;
        }
      } catch {}
    }
    const element = document.createElement('a');
    const file = new Blob([code], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `sketchflow-diagram.${format === 'mermaid' ? 'mmd' : format === 'drawio' ? 'xml' : 'puml'}`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    
    setDownloaded(true);
    setTimeout(() => setDownloaded(false), 2000);
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'SketchFlow - AI Generated Diagram',
          text: `Check out this ${format} diagram created with SketchFlow AI!`,
          files: [new File([diagramCode], `sketchflow-diagram.${format === 'mermaid' ? 'mmd' : format === 'drawio' ? 'xml' : 'puml'}`, {
            type: 'text/plain'
          })]
        });
        setShared(true);
        setTimeout(() => setShared(false), 2000);
      } catch (err) {
        console.error('Error sharing:', err);
        handleCopyCode(); // Fallback to copy
      }
    } else {
      handleCopyCode(); // Fallback to copy
    }
  };

  const codeTrimmed = (diagramCode || '').trim();
  const stats = {
    lines: codeTrimmed ? codeTrimmed.split('\n').length : 0,
    characters: diagramCode.length,
    words: codeTrimmed ? codeTrimmed.split(/\s+/).filter(Boolean).length : 0,
  };

  return (
    <div className="w-full max-w-7xl mx-auto animate-slide-up">
      {/* Success Header with Celebration */}
      <div className="mb-8">
        <div className="text-center">
          <div className="relative inline-flex items-center justify-center w-20 h-20 bg-gradient-to-tr from-success-500 to-success-600 rounded-3xl mb-4 shadow-elevation-4">
            <CheckCircleIconSolid className="w-12 h-12 text-white animate-scale-in" />
            <div className="absolute inset-0 bg-success-400/30 rounded-3xl blur-xl animate-pulse"></div>
          </div>
          <h1 className="text-4xl font-bold text-neutral-900 dark:text-white mb-2">
            Conversion Complete!
          </h1>
          <p className="text-xl text-neutral-600 dark:text-neutral-300">
            Your {format === 'mermaid' ? 'Mermaid' : format === 'drawio' ? 'Draw.io' : 'UML'} diagram is ready
          </p>
        </div>
      </div>

      {/* Main Content Card */}
      <div className="bg-white/80 dark:bg-neutral-800/80 backdrop-blur-sm rounded-3xl shadow-elevation-8 overflow-hidden border border-neutral-200 dark:border-neutral-700">
        {/* Navigation Header */}
        <div className="border-b border-neutral-200 dark:border-neutral-700 bg-white/50 dark:bg-neutral-800/50">
          <div className="flex items-center justify-between p-6">
            <button
              onClick={onReset}
              className="btn-ghost group"
            >
              <ArrowLeftIcon className="h-5 w-5 mr-2 transition-transform group-hover:-translate-x-1" />
              New Conversion
            </button>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-neutral-600 dark:text-neutral-400">
                <SparklesIconSolid className="w-4 h-4 text-primary-500" />
                AI Generated
              </div>
              <div className="flex items-center px-3 py-1.5 bg-success-100 dark:bg-success-900/30 text-success-800 dark:text-success-200 rounded-full text-sm font-medium">
                <CheckCircleIconSolid className="w-4 h-4 mr-1" />
                Success
              </div>
            </div>
          </div>
        </div>

        {/* View Toggle */}
        <div className="px-6 pt-6">
          <div className="flex items-center gap-2 p-1 bg-neutral-100 dark:bg-neutral-700 rounded-xl">
            <button
              onClick={() => setActiveView('preview')}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${
                activeView === 'preview'
                  ? 'bg-white dark:bg-neutral-600 text-primary-600 dark:text-primary-400 shadow-elevation-1'
                  : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-800 dark:hover:text-neutral-200'
              }`}
            >
              <EyeIcon className="w-5 h-5" />
              Preview
            </button>
            <button
              onClick={() => setActiveView('code')}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${
                activeView === 'code'
                  ? 'bg-white dark:bg-neutral-600 text-primary-600 dark:text-primary-400 shadow-elevation-1'
                  : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-800 dark:hover:text-neutral-200'
              }`}
            >
              <CodeBracketIcon className="w-5 h-5" />
              Code
            </button>
          </div>
        </div>

        <div className="p-6">
          {activeView === 'preview' ? (
            <div className="space-y-6">
              {/* Diagram Preview */}
              <div className="bg-neutral-50 dark:bg-neutral-900 rounded-2xl p-8 border border-neutral-200 dark:border-neutral-700">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-2xl font-bold text-neutral-900 dark:text-white">
                    {format === 'mermaid' ? 'Mermaid' : format === 'drawio' ? 'Draw.io' : 'UML'} Diagram
                  </h3>
                  <span className="px-3 py-1 bg-info-100 dark:bg-info-900/30 text-info-800 dark:text-info-200 rounded-full text-sm font-mono">
                    .{format === 'mermaid' ? 'mmd' : format === 'drawio' ? 'xml' : 'puml'}
                  </span>
                </div>
                
                <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 min-h-[400px] shadow-elevation-2">
                  {format === 'mermaid' ? (
                    <div className="w-full max-h-[600px] overflow-auto">
                      <MermaidErrorBoundary fallback={MermaidFallback}>
                        <MermaidPreview code={diagramCode} />
                      </MermaidErrorBoundary>
                    </div>
                  ) : format === 'drawio' ? (
                    <div className="w-full">
                      <DrawioPreview xml={diagramCode} />
                    </div>
                  ) : (
                    <div className="w-full max-h-[600px] overflow-auto flex items-start justify-center">
                      <PlantUMLPreview code={diagramCode} />
                    </div>
                  )}
                </div>
              </div>

              {/* Stats Cards */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 rounded-xl p-4 text-center">
                  <div className="text-2xl font-bold text-primary-600 dark:text-primary-400 mb-1">
                    {stats.lines}
                  </div>
                  <div className="text-sm text-primary-600/80 dark:text-primary-400/80">
                    Lines
                  </div>
                </div>
                <div className="bg-gradient-to-br from-success-50 to-success-100 dark:from-success-900/20 dark:to-success-800/20 rounded-xl p-4 text-center">
                  <div className="text-2xl font-bold text-success-600 dark:text-success-400 mb-1">
                    {stats.words}
                  </div>
                  <div className="text-sm text-success-600/80 dark:text-success-400/80">
                    Elements
                  </div>
                </div>
                <div className="bg-gradient-to-br from-info-50 to-info-100 dark:from-info-900/20 dark:to-info-800/20 rounded-xl p-4 text-center">
                  <div className="text-2xl font-bold text-info-600 dark:text-info-400 mb-1">
                    {Math.round(stats.characters / 1000)}K
                  </div>
                  <div className="text-sm text-info-600/80 dark:text-info-400/80">
                    Characters
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Code Editor Style Display */}
              <div className="bg-neutral-900 rounded-2xl overflow-hidden shadow-elevation-4 relative">
                <div className="bg-neutral-800 px-6 py-4 border-b border-neutral-700 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-error-500 rounded-full"></div>
                      <div className="w-3 h-3 bg-warning-500 rounded-full"></div>
                      <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                    </div>
                    <span className="text-neutral-400 text-sm font-mono">
                      sketchflow-diagram.{format === 'mermaid' ? 'mmd' : 'xml'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-neutral-400">
                    <span>{format === 'mermaid' ? 'Mermaid' : 'Draw.io XML'}</span>
                  </div>
                </div>
                <div className="p-6 max-h-[500px] overflow-auto">
                  <pre className="text-sm text-neutral-100 font-mono leading-relaxed">
                    <code>{diagramCode}</code>
                  </pre>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 mt-8">
            <button
              onClick={handleCopyCode}
              className={`flex-1 flex items-center justify-center gap-3 px-6 py-4 rounded-xl font-medium text-lg transition-all shadow-elevation-2 hover:shadow-elevation-4 ${
                copied 
                  ? 'bg-success-600 text-white' 
                  : 'btn-primary'
              }`}
            >
              {copied ? (
                <>
                  <CheckIcon className="h-5 w-5" />
                  Copied to Clipboard!
                </>
              ) : (
                <>
                  <ClipboardDocumentIcon className="h-5 w-5" />
                  Copy Code
                </>
              )}
            </button>
            
            <button
              onClick={handleDownload}
              className={`flex-1 flex items-center justify-center gap-3 px-6 py-4 rounded-xl font-medium text-lg transition-all shadow-elevation-1 hover:shadow-elevation-2 ${
                downloaded
                  ? 'bg-success-600 text-white'
                  : 'btn-secondary'
              }`}
            >
              {downloaded ? (
                <>
                  <CheckIcon className="h-5 w-5" />
                  Downloaded!
                </>
              ) : (
                <>
                  <CloudArrowDownIcon className="h-5 w-5" />
                  Download File
                </>
              )}
            </button>
            
            <button
              onClick={handleShare}
              className={`flex-1 flex items-center justify-center gap-3 px-6 py-4 rounded-xl font-medium text-lg transition-all border-2 border-neutral-300 dark:border-neutral-600 ${
                shared
                  ? 'bg-success-600 text-white border-success-600'
                  : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700'
              }`}
            >
              {shared ? (
                <>
                  <CheckIcon className="h-5 w-5" />
                  Shared!
                </>
              ) : (
                <>
                  <LinkIcon className="h-5 w-5" />
                  Share
                </>
              )}
            </button>
          </div>

          {/* Usage Instructions */}
          <div className="mt-8 p-6 bg-gradient-to-br from-info-50 to-primary-50 dark:from-info-900/20 dark:to-primary-900/20 rounded-2xl border border-info-200 dark:border-info-800">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-info-100 dark:bg-info-900/30 rounded-xl flex items-center justify-center">
                <SparklesIcon className="w-5 h-5 text-info-600 dark:text-info-400" />
              </div>
              <h4 className="text-lg font-bold text-info-900 dark:text-info-100">
                How to use your {format === 'mermaid' ? 'Mermaid' : format === 'drawio' ? 'Draw.io' : 'UML'} diagram
              </h4>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4 text-sm text-info-800 dark:text-info-200">
              {format === 'mermaid' ? (
                <>
                  <div className="space-y-2">
                    <p className="flex items-start gap-2">
                      <CheckCircleIconSolid className="w-4 h-4 mt-0.5 text-success-600" />
                      Paste into Mermaid Live Editor for instant preview
                    </p>
                    <p className="flex items-start gap-2">
                      <CheckCircleIconSolid className="w-4 h-4 mt-0.5 text-success-600" />
                      Use directly in GitHub/GitLab markdown files
                    </p>
                  </div>
                  <div className="space-y-2">
                    <p className="flex items-start gap-2">
                      <CheckCircleIconSolid className="w-4 h-4 mt-0.5 text-success-600" />
                      Integrate with Notion, Confluence, and docs
                    </p>
                    <p className="flex items-start gap-2">
                      <CheckCircleIconSolid className="w-4 h-4 mt-0.5 text-success-600" />
                      Render with mermaid CLI or online tools
                    </p>
                  </div>
                </>
              ) : format === 'drawio' ? (
                <>
                  <div className="space-y-2">
                    <p className="flex items-start gap-2">
                      <CheckCircleIconSolid className="w-4 h-4 mt-0.5 text-success-600" />
                      Import XML file directly into Draw.io
                    </p>
                    <p className="flex items-start gap-2">
                      <CheckCircleIconSolid className="w-4 h-4 mt-0.5 text-success-600" />
                      Use File → Import from → Device in Draw.io
                    </p>
                  </div>
                  <div className="space-y-2">
                    <p className="flex items-start gap-2">
                      <CheckCircleIconSolid className="w-4 h-4 mt-0.5 text-success-600" />
                      Edit shapes, colors, and layout as needed
                    </p>
                    <p className="flex items-start gap-2">
                      <CheckCircleIconSolid className="w-4 h-4 mt-0.5 text-success-600" />
                      Export to PNG, SVG, PDF, and more formats
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <div className="space-y-2">
                    <p className="flex items-start gap-2">
                      <CheckCircleIconSolid className="w-4 h-4 mt-0.5 text-success-600" />
                      Use any PlantUML renderer (local or online) to preview
                    </p>
                    <p className="flex items-start gap-2">
                      <CheckCircleIconSolid className="w-4 h-4 mt-0.5 text-success-600" />
                      Supported by many tools (IntelliJ, VS Code, Confluence plugins)
                    </p>
                  </div>
                  <div className="space-y-2">
                    <p className="flex items-start gap-2">
                      <CheckCircleIconSolid className="w-4 h-4 mt-0.5 text-success-600" />
                      Save as .puml and version control alongside code
                    </p>
                    <p className="flex items-start gap-2">
                      <CheckCircleIconSolid className="w-4 h-4 mt-0.5 text-success-600" />
                      Convert to images via PlantUML CLI/server when needed
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="text-center mt-12">
        <button
          onClick={onReset}
          className="btn-secondary text-lg px-8 py-4 shadow-elevation-2 hover:shadow-elevation-4"
        >
          Convert Another Sketch
        </button>
      </div>
    </div>
  );
}
