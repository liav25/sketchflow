'use client'

import { useState } from 'react'

export default function FeedbackPage() {
  const [feedback, setFeedback] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<'success' | 'error' | null>(null)
  const [errorMessage, setErrorMessage] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!feedback.trim()) {
      setSubmitStatus('error')
      setErrorMessage('Please enter your feedback before submitting.')
      return
    }

    setIsSubmitting(true)
    setSubmitStatus(null)
    setErrorMessage('')

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          feedback_text: feedback.trim()
        })
      })

      if (response.ok) {
        setSubmitStatus('success')
        setFeedback('')
      } else {
        const errorData = await response.json()
        setSubmitStatus('error')
        setErrorMessage(errorData.detail || 'Failed to submit feedback. Please try again.')
      }
    } catch (error) {
      setSubmitStatus('error')
      setErrorMessage('Network error. Please check your connection and try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const resetForm = () => {
    setFeedback('')
    setSubmitStatus(null)
    setErrorMessage('')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-2xl mx-auto pt-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-center mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Send us your feedback
            </h1>
            <p className="text-gray-600">
              Help us improve SketchFlow! Share your thoughts, suggestions, or report any issues.
            </p>
          </div>
          
          <div className="space-y-6">
            {submitStatus === 'success' && (
              <div className="border border-green-200 bg-green-50 rounded-md p-4">
                <div className="flex items-center">
                  <div className="h-4 w-4 text-green-600 mr-2">✓</div>
                  <div className="text-green-800">
                    Thank you for your feedback! We appreciate your input and will review it carefully.
                  </div>
                </div>
              </div>
            )}

            {submitStatus === 'error' && (
              <div className="border border-red-200 bg-red-50 rounded-md p-4">
                <div className="flex items-center">
                  <div className="h-4 w-4 text-red-600 mr-2">✕</div>
                  <div className="text-red-800">
                    {errorMessage}
                  </div>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="feedback" className="block text-sm font-medium text-gray-700 mb-2">
                  Your feedback
                </label>
                <textarea
                  id="feedback"
                  placeholder="Tell us what you think about SketchFlow. What works well? What could be improved? Any bugs you've encountered?"
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  className="w-full min-h-[120px] p-3 border border-gray-300 rounded-md resize-y focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  disabled={isSubmitting}
                  maxLength={2000}
                />
                <div className="mt-1 text-xs text-gray-500">
                  {feedback.length}/2000 characters
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button 
                  type="submit" 
                  disabled={isSubmitting || !feedback.trim()}
                  className="btn-primary flex-1 flex items-center justify-center"
                >
                  {isSubmitting ? (
                    <>
                      <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                      Submitting...
                    </>
                  ) : (
                    'Submit feedback'
                  )}
                </button>
                
                {(feedback || submitStatus) && (
                  <button 
                    type="button" 
                    className="btn-secondary"
                    onClick={resetForm}
                    disabled={isSubmitting}
                  >
                    Clear
                  </button>
                )}
              </div>
            </form>
            
            <div className="pt-4 border-t text-sm text-gray-500">
              <p className="mb-2">
                <strong>Privacy note:</strong> Your feedback helps us improve the service. 
                We may collect your IP address for spam prevention.
              </p>
              <p>
                For urgent issues or detailed support, please contact us directly.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}