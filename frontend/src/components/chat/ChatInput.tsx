'use client'

import { useState, useRef, useEffect } from 'react'
import type { Document } from '@/types'

interface Props {
  onSend: (message: string) => void
  disabled: boolean
  isStreaming: boolean
  selectedDocIds: string[]
  documents: Document[]
}

export default function ChatInput({ onSend, disabled, isStreaming, selectedDocIds, documents }: Props) {
  const [input, setInput] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [input])

  const handleSubmit = () => {
    if (!input.trim() || disabled || isStreaming) return
    onSend(input.trim())
    setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="border-t bg-white p-4">
      {selectedDocIds.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {selectedDocIds.map(id => {
            const doc = documents.find(d => d.id === id)
            return (
              <span key={id} className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full">
                {doc?.filename || id.slice(0, 8)}
              </span>
            )
          })}
        </div>
      )}
      <div className="flex gap-2 items-end">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your documents..."
          className="input-field resize-none min-h-[44px] max-h-[200px]"
          rows={1}
          disabled={disabled}
        />
        <button
          onClick={handleSubmit}
          disabled={!input.trim() || disabled || isStreaming}
          className="btn-primary h-[44px] px-6 shrink-0"
        >
          {isStreaming ? (
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 bg-white rounded-full animate-bounce" />
              <span className="text-xs">Generating...</span>
            </span>
          ) : (
            'Send'
          )}
        </button>
      </div>
    </div>
  )
}
