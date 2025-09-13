'use client';

import { useState } from 'react';
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
      // Create form data for the API request
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('format', format);
      formData.append('notes', notes);

      // Call the backend API
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-4">
            SketchFlow
          </h1>
          <p className="text-lg md:text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Transform your hand-drawn sketches into professional digital diagrams instantly
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {conversionState === 'idle' && (
            <SketchUpload onFileSelect={handleFileSelect} />
          )}

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
            <div className="w-full max-w-2xl mx-auto">
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-8 text-center">
                <div className="text-red-600 dark:text-red-400 mb-4">
                  <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
                  Conversion Failed
                </h3>
                <p className="text-red-600 dark:text-red-300 mb-6">
                  We encountered an error while processing your sketch. Please try again with a different image.
                </p>
                <button
                  onClick={handleReset}
                  className="inline-flex items-center px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
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
