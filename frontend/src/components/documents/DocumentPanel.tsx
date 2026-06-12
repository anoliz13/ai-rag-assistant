'use client'

import type { Document } from '@/types'
import { format } from 'date-fns'
import { clsx } from 'clsx'

interface Props {
  documents: Document[]
  selectedDocIds: string[]
  onToggleDoc: (id: string) => void
  onDelete: (id: string) => void
  onRefresh: () => void
  previewUrl: (id: string) => string
}

const STATUS_COLORS: Record<string, string> = {
  ready: 'text-green-600 bg-green-100',
  failed: 'text-red-600 bg-red-100',
  uploading: 'text-yellow-600 bg-yellow-100',
  extracting: 'text-blue-600 bg-blue-100',
  chunking: 'text-purple-600 bg-purple-100',
  embedding: 'text-indigo-600 bg-indigo-100',
}

export default function DocumentPanel({ documents, selectedDocIds, onToggleDoc, onDelete, onRefresh, previewUrl }: Props) {
  return (
    <aside className="w-80 border-l bg-white overflow-y-auto shrink-0">
      <div className="p-3 border-b flex items-center justify-between">
        <h2 className="font-semibold text-sm">Documents</h2>
        <button onClick={onRefresh} className="text-xs text-primary-600 hover:text-primary-700">Refresh</button>
      </div>

      <div className="p-2 space-y-2">
        {documents.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-8">No documents uploaded</p>
        ) : (
          documents.map(doc => (
            <div
              key={doc.id}
              className={clsx(
                'card text-sm cursor-pointer transition-colors',
                selectedDocIds.includes(doc.id) && 'ring-2 ring-primary-500'
              )}
              onClick={() => onToggleDoc(doc.id)}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{doc.filename}</p>
                  <p className="text-xs text-gray-400">
                    {(doc.file_size / 1024).toFixed(1)} KB · {format(new Date(doc.created_at), 'MMM d, HH:mm')}
                  </p>
                </div>
                <span className={clsx('text-xs px-2 py-0.5 rounded-full font-medium shrink-0', STATUS_COLORS[doc.status] || 'text-gray-600 bg-gray-100')}>
                  {doc.status}
                </span>
              </div>

              {doc.chunk_count !== null && (
                <p className="text-xs text-gray-400 mt-1">{doc.chunk_count} chunks</p>
              )}

              {doc.status === 'failed' && doc.error_message && (
                <p className="text-xs text-red-500 mt-1">{doc.error_message}</p>
              )}

              {(doc.status === 'uploading' || doc.status === 'extracting' || doc.status === 'chunking' || doc.status === 'embedding') && (
                <div className="mt-2 h-1 bg-gray-200 rounded overflow-hidden">
                  <div className="h-full bg-primary-500 rounded animate-pulse" style={{ width: '60%' }} />
                </div>
              )}

              <div className="flex gap-2 mt-2">
                {doc.file_type === 'application/pdf' && doc.status === 'ready' && (
                  <a
                    href={previewUrl(doc.id)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-primary-600 hover:text-primary-700"
                    onClick={e => e.stopPropagation()}
                  >
                    Preview
                  </a>
                )}
                <button
                  onClick={e => { e.stopPropagation(); onDelete(doc.id) }}
                  className="text-xs text-red-500 hover:text-red-600 ml-auto"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  )
}
