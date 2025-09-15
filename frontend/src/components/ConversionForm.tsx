'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { 
  ArrowLeftIcon, 
  PlayIcon, 
  DocumentTextIcon,
  Square3Stack3DIcon,
  EyeIcon,
  CpuChipIcon,
  CheckCircleIcon,
  PencilIcon
} from '@heroicons/react/24/outline';
import { 
  SparklesIcon as SparklesIconSolid,
  CheckCircleIcon as CheckCircleIconSolid 
} from '@heroicons/react/24/solid';
import type { ConversionState, DiagramFormat } from '@/app/page';

interface ConversionFormProps {
  file: File | null;
  notes: string;
  format: DiagramFormat;
  conversionState: ConversionState;
  onNotesChange: (notes: string) => void;
  onFormatChange: (format: DiagramFormat) => void;
  onConvert: () => void;
  onReset: () => void;
}

const ProcessingSteps = [
  { id: 'analyzing', label: 'Analyzing sketch', icon: EyeIcon, description: 'AI is examining your drawing' },
  { id: 'processing', label: 'Processing elements', icon: CpuChipIcon, description: 'Identifying shapes and connections' },
  { id: 'generating', label: 'Generating diagram', icon: SparklesIconSolid, description: 'Creating your digital diagram' },
];

export default function ConversionForm({
  file,
  notes,
  format,
  conversionState,
  onNotesChange,
  onFormatChange,
  onConvert,
  onReset,
}: ConversionFormProps) {
  const [imagePreview, setImagePreview] = useState<string>('');
  const [currentStep, setCurrentStep] = useState(0);

  // Create image preview when file changes
  useEffect(() => {
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  }, [file]);

  // Simulate processing steps progression
  useEffect(() => {
    if (conversionState === 'processing') {
      const progressTimer = setInterval(() => {
        setCurrentStep(prev => {
          if (prev < ProcessingSteps.length - 1) {
            return prev + 1;
          }
          return prev;
        });
      }, 3000); // Change step every 3 seconds

      return () => clearInterval(progressTimer);
    } else {
      setCurrentStep(0);
    }
  }, [conversionState]);

  const isProcessing = conversionState === 'processing';

  return (
    <div className="w-full max-w-6xl mx-auto animate-slide-up">
      {/* Progress Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={onReset}
            className="btn-ghost group"
            disabled={isProcessing}
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2 transition-transform group-hover:-translate-x-1" />
            Back to Upload
          </button>
          
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 text-sm text-neutral-600 dark:text-neutral-400">
              <div className="w-2 h-2 bg-success-500 rounded-full"></div>
              <span>Step 2 of 3</span>
            </div>
          </div>
        </div>

        <div className="text-center">
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-white mb-2">
            {isProcessing ? 'Converting Your Sketch' : 'Customize Your Conversion'}
          </h1>
          <p className="text-lg text-neutral-600 dark:text-neutral-300">
            {isProcessing ? 'AI is working its magic...' : 'Add context and choose your output format'}
          </p>
        </div>
      </div>

      {/* Main Conversion Card */}
      <div className="bg-white/80 dark:bg-neutral-800/80 backdrop-blur-sm rounded-3xl shadow-elevation-8 overflow-hidden border border-neutral-200 dark:border-neutral-700">
        <div className="p-8">
          <div className="grid lg:grid-cols-2 gap-12">
            {/* Sketch Preview */}
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center">
                  <EyeIcon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                </div>
                <h3 className="text-2xl font-bold text-neutral-900 dark:text-white">
                  Your Sketch
                </h3>
              </div>
              
              {imagePreview && (
                <div className="relative aspect-square bg-neutral-50 dark:bg-neutral-900 rounded-2xl overflow-hidden border-2 border-dashed border-neutral-300 dark:border-neutral-600 group">
                  <Image
                    src={imagePreview}
                    alt="Uploaded sketch preview"
                    fill
                    className={`object-contain transition-all duration-500 ${
                      isProcessing ? 'filter brightness-75 blur-[1px]' : 'group-hover:scale-105'
                    }`}
                  />
                  
                  {/* Processing Overlay */}
                  {isProcessing && (
                    <div className="absolute inset-0 bg-gradient-to-t from-primary-600/20 to-transparent flex items-center justify-center">
                      <div className="bg-white/90 dark:bg-neutral-800/90 backdrop-blur-sm rounded-2xl p-6 text-center">
                        <div className="relative w-16 h-16 mx-auto mb-4">
                          <SparklesIconSolid className="w-16 h-16 text-primary-500 animate-pulse" />
                          <div className="absolute inset-0 bg-primary-400/30 rounded-full blur-xl animate-pulse"></div>
                        </div>
                        <p className="text-sm font-medium text-neutral-900 dark:text-white">
                          AI Analyzing...
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* File Info */}
              {file && (
                <div className="bg-neutral-100 dark:bg-neutral-700 rounded-xl p-4">
                  <div className="grid grid-cols-1 gap-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-neutral-600 dark:text-neutral-400">Filename:</span>
                      <span className="font-medium text-neutral-900 dark:text-white">{file.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-600 dark:text-neutral-400">Size:</span>
                      <span className="font-medium text-neutral-900 dark:text-white">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-600 dark:text-neutral-400">Type:</span>
                      <span className="font-medium text-neutral-900 dark:text-white uppercase">
                        {file.type.split('/')[1]}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Configuration Form */}
            <div className="space-y-8">
              {/* Notes Section */}
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-warning-100 dark:bg-warning-900/30 rounded-xl flex items-center justify-center">
                    <PencilIcon className="w-5 h-5 text-warning-600 dark:text-warning-400" />
                  </div>
                  <h3 className="text-xl font-bold text-neutral-900 dark:text-white">
                    Add Context (Optional)
                  </h3>
                </div>
                
                <textarea
                  id="notes"
                  value={notes}
                  onChange={(e) => onNotesChange(e.target.value)}
                  placeholder="Help AI understand your sketch better...
• Describe the diagram purpose
• Label unclear elements  
• Specify relationships between parts
• Add any specific requirements"
                  disabled={isProcessing}
                  className="w-full px-4 py-4 border-2 border-neutral-200 dark:border-neutral-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-neutral-800 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed resize-none text-base transition-all"
                  rows={5}
                />
                <p className="mt-2 text-sm text-neutral-500 dark:text-neutral-400">
                  More context leads to more accurate diagram generation
                </p>
              </div>

              {/* Format Selection */}
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-info-100 dark:bg-info-900/30 rounded-xl flex items-center justify-center">
                    <Square3Stack3DIcon className="w-5 h-5 text-info-600 dark:text-info-400" />
                  </div>
                  <h3 className="text-xl font-bold text-neutral-900 dark:text-white">
                    Choose Output Format
                  </h3>
                </div>
                
                <div className="grid gap-4">
                  {/* Mermaid Option */}
                  <button
                    type="button"
                    onClick={() => onFormatChange('mermaid')}
                    disabled={isProcessing}
                    className={`p-6 rounded-2xl border-2 transition-all text-left disabled:opacity-50 disabled:cursor-not-allowed group ${
                      format === 'mermaid'
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 shadow-elevation-4'
                        : 'border-neutral-200 dark:border-neutral-600 hover:border-primary-300 dark:hover:border-primary-500 hover:shadow-elevation-2'
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors ${
                        format === 'mermaid' 
                          ? 'bg-primary-100 dark:bg-primary-900/50' 
                          : 'bg-neutral-100 dark:bg-neutral-700 group-hover:bg-primary-100 dark:group-hover:bg-primary-900/30'
                      }`}>
                        <DocumentTextIcon className={`h-7 w-7 ${
                          format === 'mermaid' 
                            ? 'text-primary-600 dark:text-primary-400' 
                            : 'text-neutral-500 dark:text-neutral-400 group-hover:text-primary-600 dark:group-hover:text-primary-400'
                        }`} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="text-lg font-bold text-neutral-900 dark:text-white">
                            Mermaid Diagram
                          </h4>
                          {format === 'mermaid' && (
                            <CheckCircleIconSolid className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                          )}
                        </div>
                        <p className="text-neutral-600 dark:text-neutral-300 mb-2">
                          Text-based diagrams perfect for documentation and version control
                        </p>
                        <div className="flex flex-wrap gap-2">
                          <span className="px-2 py-1 bg-success-100 dark:bg-success-900/30 text-success-800 dark:text-success-200 rounded-md text-xs font-medium">
                            GitHub Ready
                          </span>
                          <span className="px-2 py-1 bg-info-100 dark:bg-info-900/30 text-info-800 dark:text-info-200 rounded-md text-xs font-medium">
                            Live Preview
                          </span>
                        </div>
                      </div>
                    </div>
                  </button>

                  {/* Draw.io Option */}
                  <button
                    type="button"
                    onClick={() => onFormatChange('drawio')}
                    disabled={isProcessing}
                    className={`p-6 rounded-2xl border-2 transition-all text-left disabled:opacity-50 disabled:cursor-not-allowed group ${
                      format === 'drawio'
                        ? 'border-success-500 bg-success-50 dark:bg-success-900/20 shadow-elevation-4'
                        : 'border-neutral-200 dark:border-neutral-600 hover:border-success-300 dark:hover:border-success-500 hover:shadow-elevation-2'
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors ${
                        format === 'drawio' 
                          ? 'bg-success-100 dark:bg-success-900/50' 
                          : 'bg-neutral-100 dark:bg-neutral-700 group-hover:bg-success-100 dark:group-hover:bg-success-900/30'
                      }`}>
                        <Square3Stack3DIcon className={`h-7 w-7 ${
                          format === 'drawio' 
                            ? 'text-success-600 dark:text-success-400' 
                            : 'text-neutral-500 dark:text-neutral-400 group-hover:text-success-600 dark:group-hover:text-success-400'
                        }`} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="text-lg font-bold text-neutral-900 dark:text-white">
                            Draw.io XML
                          </h4>
                          {format === 'drawio' && (
                            <CheckCircleIconSolid className="w-5 h-5 text-success-600 dark:text-success-400" />
                          )}
                        </div>
                        <p className="text-neutral-600 dark:text-neutral-300 mb-2">
                          XML format for detailed visual editing and professional diagrams
                        </p>
                        <div className="flex flex-wrap gap-2">
                          <span className="px-2 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-800 dark:text-primary-200 rounded-md text-xs font-medium">
                            Visual Editor
                          </span>
                          <span className="px-2 py-1 bg-warning-100 dark:bg-warning-900/30 text-warning-800 dark:text-warning-200 rounded-md text-xs font-medium">
                            Export Options
                          </span>
                        </div>
                      </div>
                    </div>
                  </button>
                </div>
              </div>

              {/* Convert Button */}
              <button
                onClick={onConvert}
                disabled={!file || isProcessing}
                className="w-full btn-primary text-xl px-8 py-6 shadow-elevation-4 hover:shadow-elevation-8"
              >
                {isProcessing ? (
                  <div className="flex items-center justify-center gap-3">
                    <div className="animate-spin rounded-full h-6 w-6 border-2 border-white border-t-transparent"></div>
                    <span>Converting...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-3 group">
                    <SparklesIconSolid className="h-6 w-6 transition-transform group-hover:scale-110" />
                    <span>Convert to {format === 'mermaid' ? 'Mermaid' : 'Draw.io'}</span>
                    <PlayIcon className="h-6 w-6 transition-transform group-hover:translate-x-1" />
                  </div>
                )}
              </button>
            </div>
          </div>

          {/* Processing Status */}
          {isProcessing && (
            <div className="mt-12 bg-gradient-to-r from-primary-50 via-info-50 to-primary-50 dark:from-primary-900/20 dark:via-info-900/20 dark:to-primary-900/20 rounded-2xl p-8 border border-primary-200 dark:border-primary-800">
              <div className="text-center mb-8">
                <h4 className="text-2xl font-bold text-primary-900 dark:text-primary-100 mb-2">
                  AI Converting Your Sketch
                </h4>
                <p className="text-primary-700 dark:text-primary-300 text-lg">
                  This process typically takes 15-30 seconds
                </p>
              </div>

              {/* Processing Steps */}
              <div className="grid md:grid-cols-3 gap-6">
                {ProcessingSteps.map((step, index) => {
                  const Icon = step.icon;
                  const isActive = index === currentStep;
                  const isCompleted = index < currentStep;
                  
                  return (
                    <div key={step.id} className={`relative p-6 rounded-xl transition-all duration-500 ${
                      isActive 
                        ? 'bg-white dark:bg-neutral-800 shadow-elevation-4 scale-105' 
                        : isCompleted 
                        ? 'bg-white/70 dark:bg-neutral-800/70' 
                        : 'bg-white/30 dark:bg-neutral-800/30'
                    }`}>
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 mx-auto transition-all ${
                        isActive 
                          ? 'bg-primary-100 dark:bg-primary-900/50' 
                          : isCompleted 
                          ? 'bg-success-100 dark:bg-success-900/50' 
                          : 'bg-neutral-100 dark:bg-neutral-700'
                      }`}>
                        {isCompleted ? (
                          <CheckCircleIcon className="w-7 h-7 text-success-600 dark:text-success-400" />
                        ) : (
                          <Icon className={`w-7 h-7 ${
                            isActive 
                              ? 'text-primary-600 dark:text-primary-400' 
                              : 'text-neutral-500 dark:text-neutral-400'
                          } ${isActive ? 'animate-pulse' : ''}`} />
                        )}
                      </div>
                      
                      <h5 className={`font-bold text-center mb-2 ${
                        isActive 
                          ? 'text-primary-900 dark:text-primary-100' 
                          : isCompleted 
                          ? 'text-success-900 dark:text-success-100' 
                          : 'text-neutral-600 dark:text-neutral-400'
                      }`}>
                        {step.label}
                      </h5>
                      
                      <p className={`text-sm text-center ${
                        isActive 
                          ? 'text-primary-700 dark:text-primary-300' 
                          : isCompleted 
                          ? 'text-success-700 dark:text-success-300' 
                          : 'text-neutral-500 dark:text-neutral-500'
                      }`}>
                        {step.description}
                      </p>

                      {/* Progress dot */}
                      <div className={`absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-2 h-2 rounded-full transition-all ${
                        isActive 
                          ? 'bg-primary-500 animate-pulse' 
                          : isCompleted 
                          ? 'bg-success-500' 
                          : 'bg-neutral-300 dark:bg-neutral-600'
                      }`}></div>
                    </div>
                  );
                })}
              </div>

              {/* Progress Bar */}
              <div className="mt-8 bg-neutral-200 dark:bg-neutral-700 rounded-full h-2 overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-primary-500 to-info-500 h-full transition-all duration-1000 ease-out"
                  style={{ 
                    width: `${((currentStep + 1) / ProcessingSteps.length) * 100}%` 
                  }}
                ></div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}