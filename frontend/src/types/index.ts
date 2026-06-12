export interface Document {
  id: string
  filename: string
  file_type: string
  file_size: number
  status: 'uploading' | 'extracting' | 'chunking' | 'embedding' | 'ready' | 'failed'
  chunk_count: number | null
  error_message: string | null
  created_at: string
  updated_at: string
}

export interface Session {
  id: string
  title: string
  document_ids: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  content: string
  sources: string | null
  created_at: string
}

export interface Source {
  chunk_id: string
  document_id: string
  content: string
  score: number
  page_number: number | null
}
