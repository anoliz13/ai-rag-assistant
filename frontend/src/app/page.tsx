'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { api } from '@/lib/api'
import type { Document, Session, Message, Source } from '@/types'
import ChatSidebar from '@/components/chat/ChatSidebar'
import ChatMessage from '@/components/chat/ChatMessage'
import ChatInput from '@/components/chat/ChatInput'
import DocumentPanel from '@/components/documents/DocumentPanel'
import DocumentUpload from '@/components/documents/DocumentUpload'

export default function Home() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [activeSession, setActiveSession] = useState<Session | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [documents, setDocuments] = useState<Document[]>([])
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [showDocs, setShowDocs] = useState(false)
  const [showUpload, setShowUpload] = useState(false)
  const [error, setError] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const loadSessions = useCallback(async () => {
    try {
      const data = await api.listSessions()
      setSessions(data.sessions || [])
    } catch { setError('Failed to load sessions') }
  }, [])

  const loadDocuments = useCallback(async () => {
    try {
      const data = await api.listDocuments()
      setDocuments(data.documents || [])
    } catch { setError('Failed to load documents') }
  }, [])

  useEffect(() => { loadSessions(); loadDocuments() }, [loadSessions, loadDocuments])

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const createSession = async () => {
    try {
      const session = await api.createSession('New Chat', selectedDocIds.length ? selectedDocIds : undefined)
      setSessions(prev => [session, ...prev])
      setActiveSession(session)
      setMessages([])
    } catch { setError('Failed to create session') }
  }

  const selectSession = async (session: Session) => {
    setActiveSession(session)
    try {
      const data = await api.getMessages(session.id)
      setMessages(data.messages || [])
    } catch { setMessages([]) }
  }

  const deleteSession = async (id: string) => {
    try {
      await api.deleteSession(id)
      setSessions(prev => prev.filter(s => s.id !== id))
      if (activeSession?.id === id) { setActiveSession(null); setMessages([]) }
    } catch { setError('Failed to delete session') }
  }

  const renameSession = async (id: string, title: string) => {
    try {
      const updated = await api.updateSession(id, title)
      setSessions(prev => prev.map(s => s.id === id ? updated : s))
      if (activeSession?.id === id) setActiveSession(updated)
    } catch { setError('Failed to rename session') }
  }

  const sendMessage = async (content: string) => {
    if (!activeSession || isStreaming) return
    setIsStreaming(true)
    setError('')

    const userMsg: Message = {
      id: `temp-${Date.now()}`, session_id: activeSession.id,
      role: 'user', content, sources: null, created_at: new Date().toISOString(),
    }
    setMessages(prev => [...prev, userMsg])

    try {
      const res = await fetch(api.chatStream(activeSession.id, content, selectedDocIds.length ? selectedDocIds : undefined), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: activeSession.id, message: content, document_ids: selectedDocIds.length ? selectedDocIds : undefined }),
      })

      if (!res.ok) throw new Error('Chat failed')

      const reader = res.body?.getReader()
      if (!reader) throw new Error('No stream')

      const decoder = new TextDecoder()
      let assistantContent = ''
      let sources: Source[] = []

      setMessages(prev => [...prev, {
        id: `temp-assistant-${Date.now()}`, session_id: activeSession.id,
        role: 'assistant', content: '', sources: null, created_at: new Date().toISOString(),
      }])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n\n').filter(l => l.startsWith('data: '))

        for (const line of lines) {
          try {
            const data = JSON.parse(line.replace('data: ', ''))
            if (data.type === 'chunk') {
              assistantContent += data.content
              setMessages(prev => {
                const copy = [...prev]
                const last = copy[copy.length - 1]
                if (last.role === 'assistant') last.content = assistantContent
                return copy
              })
            } else if (data.type === 'done') {
              sources = data.sources || []
              setMessages(prev => {
                const copy = [...prev]
                const last = copy[copy.length - 1]
                if (last.role === 'assistant') {
                  last.content = assistantContent
                  last.sources = JSON.stringify(sources)
                }
                return copy
              })
            }
          } catch { /* ignore parse errors */ }
        }
      }

      loadSessions()
    } catch (e: any) {
      setError(e.message || 'Chat failed')
    } finally {
      setIsStreaming(false)
    }
  }

  return (
    <div className="flex h-screen">
      <ChatSidebar
        sessions={sessions}
        activeSession={activeSession}
        onSelect={selectSession}
        onCreate={createSession}
        onDelete={deleteSession}
        onRename={renameSession}
      />

      <main className="flex-1 flex flex-col">
        <header className="h-14 border-b bg-white flex items-center px-4 gap-3 shrink-0">
          <h1 className="font-semibold text-lg">AI RAG Assistant</h1>
          <div className="flex gap-2 ml-auto">
            <button onClick={() => setShowDocs(!showDocs)} className="btn-secondary text-sm">
              {showDocs ? 'Chat' : 'Documents'}
            </button>
            <button onClick={() => setShowUpload(true)} className="btn-primary text-sm">
              Upload
            </button>
          </div>
        </header>

        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 px-4 py-2 text-sm">{error}</div>
        )}

        <div className="flex-1 flex overflow-hidden">
          <div className="flex-1 flex flex-col overflow-hidden">
            {!activeSession ? (
              <div className="flex-1 flex items-center justify-center text-gray-500">
                <div className="text-center space-y-2">
                  <p className="text-xl font-medium">Welcome to AI RAG Assistant</p>
                  <p className="text-sm">Upload documents and ask questions</p>
                  <button onClick={createSession} className="btn-primary mt-4">Start New Chat</button>
                </div>
              </div>
            ) : (
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map(m => (
                  <ChatMessage key={m.id} message={m} />
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}

            <ChatInput
              onSend={sendMessage}
              disabled={!activeSession}
              isStreaming={isStreaming}
              selectedDocIds={selectedDocIds}
              documents={documents}
            />
          </div>

          {showDocs && (
            <DocumentPanel
              documents={documents}
              selectedDocIds={selectedDocIds}
              onToggleDoc={(id) => setSelectedDocIds(prev =>
                prev.includes(id) ? prev.filter(d => d !== id) : [...prev, id]
              )}
              onDelete={async (id) => { await api.deleteDocument(id); loadDocuments() }}
              onRefresh={loadDocuments}
              previewUrl={api.getDocumentPreviewUrl}
            />
          )}
        </div>
      </main>

      {showUpload && (
        <DocumentUpload
          onClose={() => setShowUpload(false)}
          onUploaded={() => { loadDocuments(); setShowUpload(false) }}
        />
      )}
    </div>
  )
}
