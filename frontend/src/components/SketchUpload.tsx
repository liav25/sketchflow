'use client';

import { useEffect, useRef, useState } from 'react';
import { 
  PhotoIcon, 
  CameraIcon, 
  ArrowUpTrayIcon, 
  LightBulbIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';
import { 
  SparklesIcon as SparklesIconSolid 
} from '@heroicons/react/24/solid';

interface SketchUploadProps {
  onFileSelect: (file: File) => void;
}

export default function SketchUpload({ onFileSelect }: SketchUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [validationError, setValidationError] = useState<string>('');
  const [isMobile, setIsMobile] = useState(false);
  const [hasCamera, setHasCamera] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const validation = validateImageFile(file);
      if (validation.isValid) {
        setValidationError('');
        onFileSelect(file);
      } else {
        setValidationError(validation.error);
      }
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(true);
    setValidationError('');
  };

  const handleDragLeave = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      const validation = validateImageFile(files[0]);
      if (validation.isValid) {
        setValidationError('');
        onFileSelect(files[0]);
      } else {
        setValidationError(validation.error);
      }
    }
  };

  const validateImageFile = (file: File): { isValid: boolean; error: string } => {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    if (!validTypes.includes(file.type)) {
      return { 
        isValid: false, 
        error: 'Please upload a JPG, PNG, or WebP image file.' 
      };
    }
    
    if (file.size > maxSize) {
      return { 
        isValid: false, 
        error: 'File size must be less than 10MB.' 
      };
    }
    
    return { isValid: true, error: '' };
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const openCamera = () => {
    cameraInputRef.current?.click();
  };

  // Detect environment and enable paste-to-upload
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        setIsMobile(window.matchMedia('(pointer: coarse)').matches);
      } catch {}

      // Basic camera capability check without using `any`
      setHasCamera(
        typeof navigator !== 'undefined' &&
          typeof navigator.mediaDevices?.getUserMedia === 'function'
      );

      const onPaste = (e: ClipboardEvent) => {
        const items = e.clipboardData?.items || [];
        for (let i = 0; i < items.length; i++) {
          const item = items[i];
          if (item.kind === 'file') {
            const file = item.getAsFile();
            if (file) {
              const validation = validateImageFile(file);
              if (validation.isValid) {
                setValidationError('');
                onFileSelect(file);
                return;
              } else {
                setValidationError(validation.error);
              }
            }
          }
        }
      };

      window.addEventListener('paste', onPaste);
      return () => window.removeEventListener('paste', onPaste);
    }
  }, [onFileSelect]);

  return (
    <div className="w-full max-w-3xl mx-auto animate-slide-up">
      {/* Main Upload Area */}
      <div
        className={`relative border-2 border-dashed rounded-2xl p-8 md:p-10 text-center transition-all duration-400 group ${
          isDragOver
            ? 'border-primary-400 bg-primary-50/50 ring-4 ring-primary-200 shadow-elevation-4'
            : validationError
            ? 'border-error-300 bg-error-50/30'
            : 'border-brand-muted hover:border-primary-400 bg-white'
        } backdrop-blur-sm shadow-elevation-1 hover:shadow-elevation-2`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {/* Upload Icon with Animation */}
        <div className={`relative mb-6 transition-all duration-300 ${
          isDragOver ? 'scale-110' : 'group-hover:scale-105'
        }`}>
          {isDragOver ? (
            <div className="relative">
              <SparklesIconSolid className="mx-auto h-20 w-20 text-primary-500 animate-pulse" />
              <div className="absolute inset-0 bg-primary-400/20 rounded-full blur-xl animate-pulse"></div>
            </div>
          ) : validationError ? (
            <ExclamationTriangleIcon className="mx-auto h-20 w-20 text-error-500" />
          ) : (
            <div className="relative">
              <PhotoIcon className="mx-auto h-20 w-20 text-neutral-400 transition-colors group-hover:text-primary-500" />
              <div className="absolute inset-0 bg-primary-400/0 rounded-full blur-xl transition-all group-hover:bg-primary-400/10"></div>
            </div>
          )}
        </div>
        
        {/* Main Text */}
        <h3 className="text-2xl md:text-3xl font-bold text-slate-800 mb-3">
          {isDragOver ? 'Drop your sketch here!' : 'Upload Your Sketch'}
        </h3>
        
        <p className="text-lg text-neutral-700 mb-8 max-w-md mx-auto leading-relaxed">
          {isDragOver 
            ? 'Release to upload your hand-drawn diagram'
            : 'Drag and drop your sketch, or choose from the options below'
          }
        </p>

        {/* Error Message */}
        {validationError && (
          <div className="mb-6 p-4 bg-error-50 border border-error-200 rounded-xl">
            <p className="text-error-600 font-medium">{validationError}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center items-center mb-6">
          {/* File Upload Button */}
          <button
            onClick={openFileDialog}
            className={`${isMobile && hasCamera ? 'btn-secondary' : 'btn-primary'} text-lg px-7 py-4 group shadow-elevation-2 hover:shadow-elevation-4`}
            disabled={isDragOver}
          >
            <ArrowUpTrayIcon className="h-6 w-6 mr-2 transition-transform group-hover:-translate-y-0.5" />
            Choose File
          </button>

          {/* Camera Button */}
          {(hasCamera || isMobile) && (
            <button
              onClick={openCamera}
              className={`${isMobile && hasCamera ? 'btn-primary' : 'btn-ghost'} text-lg px-7 py-4 group shadow-elevation-1 hover:shadow-elevation-2`}
              disabled={isDragOver}
            >
              <CameraIcon className="h-6 w-6 mr-2 transition-transform group-hover:scale-110" />
              <span className="sm:hidden">Take Photo</span>
              <span className="hidden sm:inline">Use Camera</span>
            </button>
          )}
        </div>

        {/* Paste helper */}
        <div className="mb-6 text-sm text-neutral-600">
          Tip: you can also paste an image here (⌘V / Ctrl+V)
        </div>

        {/* File Type Info */}
        <div className="flex items-center justify-center gap-2 text-sm text-neutral-600">
          <CheckCircleIcon className="h-4 w-4" />
          <span>Supports JPG, PNG, WebP • Up to 10MB</span>
        </div>

        {/* Hidden File Inputs */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/jpg,image/png,image/webp"
          onChange={handleFileChange}
          className="hidden"
        />
        
        <input
          ref={cameraInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Subtle hover overlay */}
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary-50/20 via-transparent to-secondary-50/20 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      </div>

      {/* Tips Section */}
      <div className="mt-4 bg-brand-surface backdrop-blur-sm rounded-2xl p-6 shadow-elevation-1 border border-brand-muted">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-primary-50 rounded-xl flex items-center justify-center">
            <LightBulbIcon className="w-5 h-5 text-primary-600" />
          </div>
          <h4 className="text-lg font-bold text-slate-800">
            Tips for Best Results
          </h4>
        </div>
        
        <div className="grid sm:grid-cols-2 gap-4">
          <ul className="space-y-3">
            <li className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-primary-50 flex items-center justify-center mt-0.5">
                <div className="w-2 h-2 rounded-full bg-primary-600"></div>
              </div>
              <span className="text-sm text-neutral-700">
                Use clear, well-lit photos with good contrast
              </span>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-primary-50 flex items-center justify-center mt-0.5">
                <div className="w-2 h-2 rounded-full bg-primary-600"></div>
              </div>
              <span className="text-sm text-neutral-700">
                Ensure all text and shapes are clearly visible
              </span>
            </li>
          </ul>
          <ul className="space-y-3">
            <li className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-primary-50 flex items-center justify-center mt-0.5">
                <div className="w-2 h-2 rounded-full bg-primary-600"></div>
              </div>
              <span className="text-sm text-neutral-700">
                Avoid shadows and reflections when possible
              </span>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-primary-50 flex items-center justify-center mt-0.5">
                <div className="w-2 h-2 rounded-full bg-primary-600"></div>
              </div>
              <span className="text-sm text-neutral-700">
                Add context notes to improve AI accuracy
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
