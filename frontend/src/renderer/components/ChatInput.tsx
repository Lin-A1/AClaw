import { useState } from 'react'

const BLUE = '#5b8def'
const BG = '#2e2e2e'
const BORDER = '#3a3a3a'
const TEXT = '#e0e0e0'

interface ChatInputProps {
  onSend: (text: string) => void
  loading: boolean
}

export default function ChatInput({ onSend, loading }: ChatInputProps) {
  const [text, setText] = useState('')

  const submit = () => {
    if (!text.trim() || loading) return
    onSend(text.trim())
    setText('')
  }

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div
      style={{
        padding: '10px 16px 14px',
        borderTop: `1px solid ${BORDER}`,
        background: '#1a1a1a',
        display: 'flex',
        gap: 8,
        alignItems: 'flex-end',
        flexShrink: 0,
      }}
    >
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKey}
        placeholder="输入消息..."
        disabled={loading}
        rows={1}
        style={{
          flex: 1,
          padding: '9px 13px',
          borderRadius: 8,
          border: `1px solid ${BORDER}`,
          background: BG,
          color: TEXT,
          fontSize: 14,
          outline: 'none',
          resize: 'none',
          lineHeight: 1.5,
          maxHeight: 120,
          overflowY: 'auto',
          fontFamily: 'inherit',
        }}
      />
      <button
        type="button"
        onClick={submit}
        disabled={!text.trim() || loading}
        style={{
          width: 36,
          height: 36,
          borderRadius: 8,
          border: 'none',
          background: text.trim() && !loading ? BLUE : BG,
          color: text.trim() && !loading ? '#fff' : '#555',
          cursor: text.trim() && !loading ? 'pointer' : 'not-allowed',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          transition: 'background 0.15s',
        }}
      >
        {loading ? (
          <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"
            style={{ animation: 'spin 0.7s linear infinite' }}>
            <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
            <path strokeLinecap="round" d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
          </svg>
        ) : (
          <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        )}
      </button>
    </div>
  )
}
