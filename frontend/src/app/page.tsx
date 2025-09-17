'use client';

import { useEffect, useState } from 'react';
import { ArrowRightIcon, SparklesIcon, ClockIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import SketchUpload from '@/components/SketchUpload';
import ConversionForm from '@/components/ConversionForm';
import DiagramPreview from '@/components/DiagramPreview';
import { useAuth } from '@/components/AuthProvider';
import UserMenu from '@/components/UserMenu';
import ExamplesSwitcher from '@/components/ExamplesSwitcher';
import AdSlot from '@/components/ads/AdSlot';

export type ConversionState = 'idle' | 'uploading' | 'processing' | 'completed' | 'error';
export type DiagramFormat = 'mermaid' | 'drawio';

export default function Home() {
  const [conversionState, setConversionState] = useState<ConversionState>('idle');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [notes, setNotes] = useState('');
  const [format, setFormat] = useState<DiagramFormat>('mermaid');
  const [generatedDiagram, setGeneratedDiagram] = useState<string>('');
  const [jobId, setJobId] = useState<string>('');
  const { user, getAccessToken } = useAuth();

  console.log('[HomePage] Page loaded, user state:', { hasUser: !!user });

  // Restore preview state after auth redirect
  useEffect(() => {
    try {
      const raw = typeof window !== 'undefined' ? sessionStorage.getItem('sf.previewState') : null;
      if (!raw) return;
      const saved = JSON.parse(raw) as Partial<{ format: DiagramFormat; diagramCode: string; jobId: string; conversionState: string }>;
      if (saved && saved.diagramCode && saved.format) {
        setFormat(saved.format);
        setGeneratedDiagram(saved.diagramCode);
        setJobId(saved.jobId || '');
        setConversionState('completed');
      }
    } catch (e) {
      console.warn('Failed to restore preview state after login:', e);
    } finally {
      try { sessionStorage.removeItem('sf.previewState'); } catch {}
    }
  }, []);

  // Before navigating away (e.g., OAuth redirect), stash preview state
  useEffect(() => {
    const onBeforeUnload = () => {
      try {
        // Only persist if we actually have a completed preview and an auth redirect is queued
        const hasRedirect = typeof window !== 'undefined' && !!sessionStorage.getItem('sf.redirect');
        if (!hasRedirect) return;
        if (conversionState === 'completed' && generatedDiagram) {
          const state = { format, diagramCode: generatedDiagram, jobId, conversionState: 'completed' as const };
          sessionStorage.setItem('sf.previewState', JSON.stringify(state));
        }
      } catch {}
    };
    window.addEventListener('beforeunload', onBeforeUnload);
    return () => window.removeEventListener('beforeunload', onBeforeUnload);
  }, [conversionState, generatedDiagram, format, jobId]);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setConversionState('uploading');
  };

  const handleConvert = async () => {
    if (!selectedFile) return;
    
    setConversionState('processing');
    
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('format', format);
      formData.append('notes', notes);

      const headers: Record<string, string> = {};
      
      // Wrap token retrieval in try-catch to prevent streaming issues
      try {
        const token = await getAccessToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;
      } catch (tokenError) {
        console.warn('Failed to get access token:', tokenError);
        // Continue without token for anonymous access
      }

      const controller = new AbortController();
      // Increase timeout to 300 seconds to accommodate longer conversions
      const timeoutId = setTimeout(() => controller.abort(), 300000); // 300s timeout

      const response = await fetch(`${apiBase}/api/convert`, {
        method: 'POST',
        body: formData,
        headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.status === 'completed' && result.result) {
        setGeneratedDiagram(result.result.code);
        setJobId(result.result.job_id || result.job_id || '');
        setConversionState('completed');
      } else if (result.status === 'failed') {
        console.error('Conversion failed:', result.error);
        setConversionState('error');
      }
    } catch (error) {
      console.error('Error during conversion:', error);
      setConversionState('error');
    }
  };

  const handleReset = () => {
    setConversionState('idle');
    setSelectedFile(null);
    setNotes('');
    setGeneratedDiagram('');
  };

  const handleGetStarted = () => {
    document.getElementById('upload-section')?.scrollIntoView({ 
      behavior: 'smooth',
      block: 'center'
    });
  };

  const handleViewExamples = () => {
    document.getElementById('examples')?.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    });
  };

  if (conversionState !== 'idle') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-white via-white to-brand-surface">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-5xl mx-auto">
            {(conversionState === 'uploading' || conversionState === 'processing') && (
              <ConversionForm
                file={selectedFile}
                notes={notes}
                format={format}
                conversionState={conversionState}
                onNotesChange={setNotes}
                onFormatChange={setFormat}
                onConvert={handleConvert}
                onReset={handleReset}
              />
            )}

            {conversionState === 'completed' && (
              <DiagramPreview
                format={format}
                diagramCode={generatedDiagram}
                jobId={jobId}
                onReset={handleReset}
              />
            )}

            {conversionState === 'error' && (
              <div className="w-full max-w-2xl mx-auto animate-slide-up">
                <div className="bg-brand-surface border border-error-200 rounded-3xl p-8 text-center shadow-elevation-4">
                  <div className="text-error-500 mb-6">
                    <svg className="mx-auto h-20 w-20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                    </svg>
                  </div>
                  <h3 className="text-2xl font-bold text-secondary-800 mb-3">
                    Conversion Failed
                  </h3>
                  <p className="text-neutral-700 mb-8 text-lg">
                    We encountered an error while processing your sketch. Please try again with a different image or check your connection.
                  </p>
                  <button
                    onClick={handleReset}
                    className="btn-primary text-lg px-8 py-4"
                  >
                    Try Again
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-white to-brand-surface animate-gradient">
      {/* Navigation */}
      <nav className="relative z-50 bg-white/80 backdrop-blur-md border-b border-brand-muted">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-tr from-primary-600 to-secondary-500 rounded-xl flex items-center justify-center">
                <SparklesIcon className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-slate-800">SketchFlow</span>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-neutral-600 hover:text-secondary-700 font-medium transition-colors">
                Features
              </a>
              <a href="#how-it-works" className="text-neutral-600 hover:text-secondary-700 font-medium transition-colors">
                How It Works
              </a>
              <UserMenu />
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-20 pb-8 lg:pt-24 lg:pb-12 overflow-hidden">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center px-4 py-2 bg-secondary-100 text-secondary-700 rounded-full text-sm font-medium mb-8 animate-fade-in">
              <SparklesIcon className="w-4 h-4 mr-2" />
              AI-Powered Diagram Generation
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-secondary-800 mb-4 animate-slide-up text-balance">
              Turn Hand‑Drawn <span className="text-[#ef7722]">Sketches</span> into Polished Diagrams
            </h1>

            {/* Subtitle */}
            <p className="text-lg md:text-xl text-neutral-700 mb-8 max-w-3xl mx-auto leading-relaxed animate-slide-up text-balance">
              Upload a photo of your sketch and watch our AI convert it into clean, professional Mermaid or Draw.io diagrams in seconds. No design skills required.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-10 animate-scale-in">
              <button 
                onClick={handleGetStarted}
                className="btn-primary text-lg px-6 py-3 sm:px-8 sm:py-4 group"
              >
                Get Started Free
                <ArrowRightIcon className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </button>
              <button onClick={handleViewExamples} className="btn-secondary text-lg px-6 py-3 sm:px-8 sm:py-4">
                View Examples
              </button>
            </div>

            {/* Trust Indicators */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto animate-fade-in">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600 mb-1">60s</div>
                <div className="text-sm text-neutral-600">Average Conversion Time</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-secondary-600 mb-1">99%</div>
                <div className="text-sm text-neutral-600">Accuracy Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600 mb-1">Free</div>
                <div className="text-sm text-neutral-600">And will remain free</div>
              </div>
            </div>
          </div>
        </div>

        {/* Background Elements */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-primary-400/15 to-secondary-400/15 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-secondary-400/15 to-primary-400/10 rounded-full blur-3xl"></div>
        </div>
      </section>

      {/* Examples Section */}
      <ExamplesSwitcher />

      {/* Ad: Homepage mid (below examples) */}
      <section className="py-6">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <AdSlot
            slot={process.env.NEXT_PUBLIC_ADSENSE_SLOT_HOMEPAGE_MID}
            className="mx-auto"
            style={{ minHeight: 90 }}
          />
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-12 bg-brand-surface backdrop-blur-sm">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h2 className="text-4xl font-bold text-secondary-800 mb-4">
              Why Choose SketchFlow?
            </h2>
            <p className="text-xl text-neutral-700 max-w-2xl mx-auto">
              Designed for professionals who need quick, accurate diagram conversion without the complexity.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="text-center p-5 rounded-2xl bg-white border border-neutral-200 shadow-elevation-1">
              <div className="w-12 h-12 bg-primary-50 rounded-xl flex items-center justify-center mx-auto mb-4">
                <ClockIcon className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold text-secondary-800 mb-2">Lightning Fast</h3>
              <p className="text-neutral-700">Convert sketches to diagrams in under 30 seconds with our advanced AI processing.</p>
            </div>

            <div className="text-center p-5 rounded-2xl bg-white border border-neutral-200 shadow-elevation-1">
              <div className="w-12 h-12 bg-secondary-50 rounded-xl flex items-center justify-center mx-auto mb-4">
                <CheckCircleIcon className="w-6 h-6 text-secondary-600" />
              </div>
              <h3 className="text-xl font-bold text-secondary-800 mb-2">High Accuracy</h3>
              <p className="text-neutral-700">Our AI understands complex diagrams with 99% accuracy, even from rough sketches.</p>
            </div>

            <div className="text-center p-5 rounded-2xl bg-white border border-neutral-200 shadow-elevation-1">
              <div className="w-12 h-12 bg-primary-50 rounded-xl flex items-center justify-center mx-auto mb-4">
                <SparklesIcon className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold text-secondary-800 mb-2">Multiple Formats</h3>
              <p className="text-neutral-700">Export as Mermaid or Draw.io format, ready to use in your favorite tools.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Ad: Homepage bottom (above upload section) */}
      <section className="py-6">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <AdSlot
            slot={process.env.NEXT_PUBLIC_ADSENSE_SLOT_HOMEPAGE_BOTTOM}
            className="mx-auto"
            style={{ minHeight: 90 }}
          />
        </div>
      </section>

      {/* Upload Section */}
      <section id="upload-section" className="py-16">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-secondary-800 mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-xl text-neutral-700">
              Upload your sketch and see the magic happen
            </p>
          </div>

          <SketchUpload onFileSelect={handleFileSelect} />
        </div>
      </section>
    </div>
  );
}
