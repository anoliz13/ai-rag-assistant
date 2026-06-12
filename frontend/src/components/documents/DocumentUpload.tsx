'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { api } from '@/lib/api'

interface Props {
  onClose: () => void
  onUploaded: () => void
}

export default function DocumentUpload({ onClose, onUploaded }: Props) {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState('')

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true)
    for (const file of acceptedFiles) {
      setProgress(`Uploading ${file.name}...`)
      try {
        await api.uploadDocument(file)
      } catch (e: any) {
        setProgress(`Failed: ${file.name} - ${e.message}`)
        return
      }
    }
    setProgress('Done!')
    onUploaded()
  }, [onUploaded])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'text/csv': ['.csv'],
      'text/markdown': ['.md'],
    },
    maxSize: 50 * 1024 * 1024,
  })

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-white rounded-xl p-6 w-full max-w-md mx-4"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Upload Document</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
        </div>

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
            isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          {uploading ? (
            <div className="space-y-2">
              <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-sm text-gray-500">{progress}</p>
            </div>
          ) : (
            <div>
              <p className="text-3xl mb-2">📄</p>
              <p className="text-sm text-gray-600">
                {isDragActive ? 'Drop files here' : 'Drag & drop files or click to browse'}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                PDF, DOCX, TXT, CSV, Markdown (max 50MB)
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
