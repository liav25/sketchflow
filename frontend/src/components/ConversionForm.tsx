'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import { 
  ArrowLeftIcon, 
  PlayIcon, 
  DocumentTextIcon,
  Square3Stack3DIcon
} from '@heroicons/react/24/outline';
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

  // Create image preview when file changes
  React.useEffect(() => {
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  }, [file]);

  const isProcessing = conversionState === 'processing';

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={onReset}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                disabled={isProcessing}
              >
                <ArrowLeftIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
              </button>
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Convert Sketch
                </h2>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Add details and choose your output format
                </p>
              </div>
            </div>
            
            {isProcessing && (
              <div className="flex items-center gap-2 text-blue-600">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
                <span className="text-sm font-medium">Converting...</span>
              </div>
            )}
          </div>
        </div>

        <div className="p-6">
          <div className="grid md:grid-cols-2 gap-8">
            {/* Image Preview */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Your Sketch
              </h3>
              
              {imagePreview && (
                <div className="relative aspect-square bg-gray-50 dark:bg-gray-700 rounded-lg overflow-hidden">
                  <Image
                    src={imagePreview}
                    alt="Uploaded sketch preview"
                    fill
                    className="object-contain"
                  />
                </div>
              )}

              {file && (
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  <p><strong>File:</strong> {file.name}</p>
                  <p><strong>Size:</strong> {(file.size / 1024 / 1024).toFixed(2)} MB</p>
                  <p><strong>Type:</strong> {file.type}</p>
                </div>
              )}
            </div>

            {/* Form */}
            <div className="space-y-6">
              {/* Notes Section */}
              <div>
                <label 
                  htmlFor="notes" 
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                >
                  Additional Notes (Optional)
                </label>
                <textarea
                  id="notes"
                  value={notes}
                  onChange={(e) => onNotesChange(e.target.value)}
                  placeholder="Add any context, labels, or specific instructions for the AI..."
                  disabled={isProcessing}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed resize-none"
                  rows={4}
                />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  Help the AI understand your diagram by describing connections, labels, or purpose
                </p>
              </div>

              {/* Format Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Output Format
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {/* Mermaid Option */}
                  <button
                    type="button"
                    onClick={() => onFormatChange('mermaid')}
                    disabled={isProcessing}
                    className={`p-4 rounded-lg border-2 transition-all text-left disabled:opacity-50 disabled:cursor-not-allowed ${
                      format === 'mermaid'
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <DocumentTextIcon className="h-6 w-6 text-blue-600 mt-1 flex-shrink-0" />
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white">
                          Mermaid
                        </h4>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          Text-based diagrams perfect for documentation
                        </p>
                      </div>
                    </div>
                  </button>

                  {/* Draw.io Option */}
                  <button
                    type="button"
                    onClick={() => onFormatChange('drawio')}
                    disabled={isProcessing}
                    className={`p-4 rounded-lg border-2 transition-all text-left disabled:opacity-50 disabled:cursor-not-allowed ${
                      format === 'drawio'
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <Square3Stack3DIcon className="h-6 w-6 text-green-600 mt-1 flex-shrink-0" />
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white">
                          Draw.io
                        </h4>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          XML format for detailed visual editing
                        </p>
                      </div>
                    </div>
                  </button>
                </div>
              </div>

              {/* Convert Button */}
              <button
                onClick={onConvert}
                disabled={!file || isProcessing}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors disabled:cursor-not-allowed"
              >
                {isProcessing ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    <PlayIcon className="h-5 w-5" />
                    Convert to {format === 'mermaid' ? 'Mermaid' : 'Draw.io'}
                  </>
                )}
              </button>

              {/* Processing Status */}
              {isProcessing && (
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <div className="flex items-center gap-3">
                    <div className="animate-pulse flex space-x-1">
                      <div className="h-2 w-2 bg-blue-600 rounded-full animate-bounce"></div>
                      <div className="h-2 w-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="h-2 w-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-blue-800 dark:text-blue-200">
                        AI is analyzing your sketch...
                      </p>
                      <p className="text-xs text-blue-600 dark:text-blue-300">
                        This usually takes 10-30 seconds
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}