'use client';

import { useState } from 'react';
import { ArrowRightIcon, SparklesIcon, ClockIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import SketchUpload from '@/components/SketchUpload';
import ConversionForm from '@/components/ConversionForm';
import DiagramPreview from '@/components/DiagramPreview';

export type ConversionState = 'idle' | 'uploading' | 'processing' | 'completed' | 'error';
export type DiagramFormat = 'mermaid' | 'drawio';

export default function Home() {
  const [conversionState, setConversionState] = useState<ConversionState>('idle');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [notes, setNotes] = useState('');
  const [format, setFormat] = useState<DiagramFormat>('mermaid');
  const [generatedDiagram, setGeneratedDiagram] = useState<string>('');

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setConversionState('uploading');
  };

  const handleConvert = async () => {
    if (!selectedFile) return;
    
    setConversionState('processing');
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('format', format);
      formData.append('notes', notes);

      const response = await fetch('http://localhost:8000/api/convert', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.status === 'completed' && result.result) {
        setGeneratedDiagram(result.result.code);
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

  if (conversionState !== 'idle') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50">
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
                onReset={handleReset}
              />
            )}

            {conversionState === 'error' && (
              <div className="w-full max-w-2xl mx-auto animate-slide-up">
                <div className="bg-amber-50 border border-red-200 rounded-3xl p-8 text-center shadow-elevation-4">
                  <div className="text-red-500 mb-6">
                    <svg className="mx-auto h-20 w-20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                    </svg>
                  </div>
                  <h3 className="text-2xl font-bold text-slate-800 mb-3">
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
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50 animate-gradient">
      {/* Navigation */}
      <nav className="relative z-50 bg-amber-50/80 backdrop-blur-md border-b border-neutral-200">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-tr from-slate-800 to-orange-600 rounded-xl flex items-center justify-center">
                <SparklesIcon className="w-5 h-5 text-amber-50" />
              </div>
              <span className="text-xl font-bold text-slate-800">SketchFlow</span>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-neutral-600 hover:text-slate-700 font-medium transition-colors">
                Features
              </a>
              <a href="#how-it-works" className="text-neutral-600 hover:text-slate-700 font-medium transition-colors">
                How It Works
              </a>
              <button className="btn-secondary">
                Sign In
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-20 pb-32 lg:pt-32 lg:pb-40 overflow-hidden">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center px-4 py-2 bg-yellow-100 text-slate-800 rounded-full text-sm font-medium mb-8 animate-fade-in">
              <SparklesIcon className="w-4 h-4 mr-2" />
              AI-Powered Diagram Generation
            </div>

            {/* Main Headline */}
            <h1 className="text-display md:text-6xl lg:text-7xl font-bold text-slate-800 mb-6 animate-slide-up text-balance">
              Transform Hand-Drawn
              <span className="bg-gradient-to-r from-orange-600 to-red-500 bg-clip-text text-transparent"> Sketches </span>
              into Professional Diagrams
            </h1>

            {/* Subtitle */}
            <p className="text-lg md:text-xl text-neutral-700 mb-12 max-w-3xl mx-auto leading-relaxed animate-slide-up text-balance">
              Upload a photo of your sketch and watch our AI convert it into clean, professional Mermaid or Draw.io diagrams in seconds. No design skills required.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16 animate-scale-in">
              <button 
                onClick={handleGetStarted}
                className="btn-primary text-lg px-8 py-4 group"
              >
                Get Started Free
                <ArrowRightIcon className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </button>
              <button className="btn-secondary text-lg px-8 py-4">
                View Examples
              </button>
            </div>

            {/* Trust Indicators */}
            <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto animate-fade-in">
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600 mb-1">30s</div>
                <div className="text-sm text-neutral-600">Average Conversion Time</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600 mb-1">99%</div>
                <div className="text-sm text-neutral-600">Accuracy Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-500 mb-1">Free</div>
                <div className="text-sm text-neutral-600">First Conversion</div>
              </div>
            </div>
          </div>
        </div>

        {/* Background Elements */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-yellow-400/20 to-orange-400/20 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-amber-400/30 to-red-400/20 rounded-full blur-3xl"></div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-amber-50/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-800 mb-4">
              Why Choose SketchFlow?
            </h2>
            <p className="text-xl text-neutral-700 max-w-2xl mx-auto">
              Designed for professionals who need quick, accurate diagram conversion without the complexity.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6 rounded-2xl bg-amber-50/80 backdrop-blur-sm border border-neutral-200 shadow-elevation-2">
              <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                <ClockIcon className="w-6 h-6 text-orange-600" />
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-2">Lightning Fast</h3>
              <p className="text-neutral-700">Convert sketches to diagrams in under 30 seconds with our advanced AI processing.</p>
            </div>

            <div className="text-center p-6 rounded-2xl bg-amber-50/80 backdrop-blur-sm border border-neutral-200 shadow-elevation-2">
              <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                <CheckCircleIcon className="w-6 h-6 text-yellow-600" />
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-2">High Accuracy</h3>
              <p className="text-neutral-700">Our AI understands complex diagrams with 99% accuracy, even from rough sketches.</p>
            </div>

            <div className="text-center p-6 rounded-2xl bg-amber-50/80 backdrop-blur-sm border border-neutral-200 shadow-elevation-2">
              <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                <SparklesIcon className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-2">Multiple Formats</h3>
              <p className="text-neutral-700">Export as Mermaid or Draw.io format, ready to use in your favorite tools.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Upload Section */}
      <section id="upload-section" className="py-24">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-slate-800 mb-4">
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
