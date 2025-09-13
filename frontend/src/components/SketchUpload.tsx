'use client';

import { useRef, useState } from 'react';
import { PhotoIcon, CameraIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline';

interface SketchUploadProps {
  onFileSelect: (file: File) => void;
}

export default function SketchUpload({ onFileSelect }: SketchUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && isValidImageFile(file)) {
      onFileSelect(file);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
    
    const files = event.dataTransfer.files;
    if (files.length > 0 && isValidImageFile(files[0])) {
      onFileSelect(files[0]);
    }
  };

  const isValidImageFile = (file: File): boolean => {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    return validTypes.includes(file.type) && file.size <= maxSize;
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const openCamera = () => {
    cameraInputRef.current?.click();
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Main Upload Area */}
      <div
        className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
          isDragOver
            ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <PhotoIcon className="mx-auto h-16 w-16 text-gray-400 mb-4" />
        
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          Upload your sketch
        </h3>
        
        <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-md mx-auto">
          Drag and drop your hand-drawn sketch or diagram here, or use one of the options below
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          {/* Desktop/File Upload */}
          <button
            onClick={openFileDialog}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
          >
            <ArrowUpTrayIcon className="h-5 w-5" />
            Choose File
          </button>

          {/* Mobile Camera */}
          <button
            onClick={openCamera}
            className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors sm:hidden"
          >
            <CameraIcon className="h-5 w-5" />
            Take Photo
          </button>

          {/* Desktop Camera (if supported) */}
          <button
            onClick={openCamera}
            className="hidden sm:flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
          >
            <CameraIcon className="h-5 w-5" />
            Use Camera
          </button>
        </div>

        {/* File Type Info */}
        <p className="text-xs text-gray-400 mt-4">
          Supports JPG, PNG, WebP files up to 10MB
        </p>

        {/* Hidden File Inputs */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
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
      </div>

      {/* Instructions */}
      <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
        <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
          Tips for best results:
        </h4>
        <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-0.5">•</span>
            Use clear, well-lit photos with good contrast
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-0.5">•</span>
            Ensure text and shapes are clearly visible
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-0.5">•</span>
            Avoid shadows and reflections when possible
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-0.5">•</span>
            Include any additional context in the notes section
          </li>
        </ul>
      </div>
    </div>
  );
}