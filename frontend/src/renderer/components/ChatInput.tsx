import { useState } from 'react'

interface ChatInputProps {
  onSend: (text: string) => void
  loading: boolean
}

export default function ChatInput({ onSend, loading }: ChatInputProps) {
  const [text, setText] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!text.trim() || loading) return
    onSend(text.trim())
    setText('')
  }

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        padding: '12px 16px',
        borderTop: '1px solid #333',
        background: '#16213e',
        display: 'flex',
        gap: '8px',
      }}
    >
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="输入消息..."
        disabled={loading}
        style={{
          flex: 1,
          padding: '10px 14px',
          borderRadius: '8px',
          border: '1px solid #333',
          background: '#1a1a2e',
          color: '#e0e0e0',
          outline: 'none',
          fontSize: '14px',
        }}
      />
      <button
        type="submit"
        disabled={!text.trim() || loading}
        style={{
          padding: '10px 20px',
          borderRadius: '8px',
          border: 'none',
          background: '#4f46e5',
          color: '#fff',
          cursor: loading ? 'not-allowed' : 'pointer',
          fontSize: '14px',
          opacity: loading ? 0.6 : 1,
        }}
      >
        {loading ? '...' : '发送'}
      </button>
    </form>
  )
}
