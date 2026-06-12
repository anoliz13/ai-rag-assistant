import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI RAG Assistant',
  description: 'Upload documents and ask questions with AI-powered answers',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
