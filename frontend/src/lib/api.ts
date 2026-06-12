const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function fetchAPI(path: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'API Error')
  }
  return res.json()
}

export const api = {
  // Documents
  async uploadDocument(file: File) {
    const form = new FormData()
    form.append('file', file)
    const res = await fetch(`${API_BASE}/api/documents/upload`, { method: 'POST', body: form })
    if (!res.ok) throw new Error((await res.json()).detail)
    return res.json()
  },

  async listDocuments() {
    return fetchAPI('/api/documents')
  },

  async getDocument(id: string) {
    return fetchAPI(`/api/documents/${id}`)
  },

  async deleteDocument(id: string) {
    return fetchAPI(`/api/documents/${id}`, { method: 'DELETE' })
  },

  getDocumentPreviewUrl(id: string) {
    return `${API_BASE}/api/documents/${id}/preview`
  },

  // Sessions
  async listSessions() {
    return fetchAPI('/api/sessions')
  },

  async createSession(title: string, documentIds?: string[]) {
    return fetchAPI('/api/sessions', {
      method: 'POST',
      body: JSON.stringify({ title, document_ids: documentIds }),
    })
  },

  async getSession(id: string) {
    return fetchAPI(`/api/sessions/${id}`)
  },

  async updateSession(id: string, title: string) {
    return fetchAPI(`/api/sessions/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ title }),
    })
  },

  async deleteSession(id: string) {
    return fetchAPI(`/api/sessions/${id}`, { method: 'DELETE' })
  },

  async getMessages(sessionId: string) {
    return fetchAPI(`/api/sessions/${sessionId}/messages`)
  },

  getSessionExportUrl(sessionId: string) {
    return `${API_BASE}/api/sessions/${sessionId}/export`
  },

  // Chat
  chatStream(sessionId: string, message: string, documentIds?: string[]) {
    return `${API_BASE}/api/chat`
  },
}
