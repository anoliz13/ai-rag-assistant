'use client'

import { useState } from 'react'
import type { Session } from '@/types'

interface Props {
  sessions: Session[]
  activeSession: Session | null
  onSelect: (s: Session) => void
  onCreate: () => void
  onDelete: (id: string) => void
  onRename: (id: string, title: string) => void
}

export default function ChatSidebar({ sessions, activeSession, onSelect, onCreate, onDelete, onRename }: Props) {
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState('')

  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col shrink-0">
      <div className="p-3 border-b border-gray-700">
        <button onClick={onCreate} className="w-full btn-primary text-sm">
          + New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {sessions.map(s => (
          <div
            key={s.id}
            className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer text-sm transition-colors ${
              activeSession?.id === s.id ? 'bg-primary-600' : 'hover:bg-gray-800'
            }`}
            onClick={() => onSelect(s)}
          >
            {editingId === s.id ? (
              <input
                autoFocus
                className="flex-1 bg-gray-700 text-white px-2 py-1 rounded text-sm outline-none"
                value={editTitle}
                onChange={e => setEditTitle(e.target.value)}
                onBlur={() => { onRename(s.id, editTitle); setEditingId(null) }}
                onKeyDown={e => {
                  if (e.key === 'Enter') { onRename(s.id, editTitle); setEditingId(null) }
                  if (e.key === 'Escape') setEditingId(null)
                }}
              />
            ) : (
              <span
                className="flex-1 truncate"
                onDoubleClick={() => { setEditingId(s.id); setEditTitle(s.title) }}
              >
                {s.title}
              </span>
            )}
            <button
              className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 text-xs"
              onClick={e => { e.stopPropagation(); onDelete(s.id) }}
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </aside>
  )
}
