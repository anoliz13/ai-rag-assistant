'use client'

import ReactMarkdown from 'react-markdown'
import type { Message, Source } from '@/types'
import { format } from 'date-fns'
import { clsx } from 'clsx'
import { useState } from 'react'

interface Props {
  message: Message
}

export default function ChatMessage({ message }: Props) {
  const [showSources, setShowSources] = useState(false)
  const isUser = message.role === 'user'
  const sources: Source[] = message.sources ? JSON.parse(message.sources) : []

  return (
    <div className={clsx('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div className={clsx('max-w-3xl w-full', isUser ? 'ml-auto' : 'mr-auto')}>
        <div className={clsx(
          'rounded-xl px-4 py-3',
          isUser ? 'bg-primary-600 text-white' : 'bg-white border border-gray-200'
        )}>
          {isUser ? (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-700">
              {message.content ? (
                <ReactMarkdown>{message.content}</ReactMarkdown>
              ) : (
                <span className="text-gray-400 animate-pulse">▊</span>
              )}
            </div>
          )}
        </div>

        {!isUser && sources.length > 0 && (
          <div className="mt-1">
            <button
              onClick={() => setShowSources(!showSources)}
              className="text-xs text-primary-600 hover:text-primary-700 font-medium"
            >
              {showSources ? 'Hide' : 'Show'} sources ({sources.length})
            </button>
            {showSources && (
              <div className="mt-1 space-y-1">
                {sources.map((s, i) => (
                  <div key={i} className="text-xs bg-gray-100 rounded px-2 py-1 text-gray-600">
                    <span className="font-medium">Document {s.document_id.slice(0, 8)}</span>
                    {s.page_number && <span> · Page {s.page_number}</span>}
                    <span className="text-gray-400"> · Score: {(s.score * 100).toFixed(0)}%</span>
                    <p className="mt-0.5 text-gray-500 line-clamp-2">{s.content.slice(0, 200)}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <p className="text-xs text-gray-400 mt-1 px-1">
          {format(new Date(message.created_at), 'HH:mm')}
        </p>
      </div>
    </div>
  )
}
