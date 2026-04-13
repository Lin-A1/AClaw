import { useState } from 'react'
import { Marked } from 'marked'
import type { Message } from '../App'

const BUBBLE_USER_BG = '#5b8def'
const BUBBLE_AI_BG = '#2e2e2e'
const EMPTY_COLOR = '#555555'
const THINK_COLOR = '#7a7a7a'
const THINK_BG = '#252525'

const marked = new Marked({ breaks: true, gfm: true })

function renderMarkdown(text: string): string {
  return marked.parse(text) as string
}

function ThinkingBlock({ text }: { text: string }) {
  const [open, setOpen] = useState(false)
  if (!text.trim()) return null
  return (
    <div style={{ marginBottom: 6, fontSize: 12 }}>
      <button
        onClick={() => setOpen((v) => !v)}
        style={{
          background: 'none',
          border: 'none',
          color: THINK_COLOR,
          cursor: 'pointer',
          fontSize: 12,
          padding: '2px 0',
          display: 'flex',
          alignItems: 'center',
          gap: 4,
          marginBottom: open ? 4 : 0,
        }}
      >
        <svg
          width="10" height="10" viewBox="0 0 10 10"
          style={{ transition: 'transform 0.15s', transform: open ? 'rotate(90deg)' : 'rotate(0deg)' }}
          fill="none" stroke={THINK_COLOR} strokeWidth="1.5"
        >
          <path d="M3 2l4 3-4 3" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <span>思考过程</span>
      </button>
      {open && (
        <div style={{
          background: THINK_BG,
          border: '1px solid #333',
          borderRadius: 8,
          padding: '6px 10px',
          color: THINK_COLOR,
          whiteSpace: 'pre-wrap',
          lineHeight: 1.6,
          maxHeight: 200,
          overflowY: 'auto',
        }}>
          {text}
        </div>
      )}
    </div>
  )
}

export default function Chat({ messages }: { messages: Message[] }) {
  return (
    <div
      style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px 20px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {messages.length === 0 && (
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            color: EMPTY_COLOR,
            gap: 10,
          }}
        >
          <svg width="36" height="36" fill="none" stroke={EMPTY_COLOR} strokeWidth="1.5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <span style={{ fontSize: 13 }}>发送消息开始对话</span>
        </div>
      )}
      {messages.map((msg) => {
        const isUser = msg.role === 'user'
        return (
          <div
            key={msg.id}
            style={{
              display: 'flex',
              justifyContent: isUser ? 'flex-end' : 'flex-start',
              marginBottom: 10,
            }}
          >
            <div style={{ maxWidth: '75%' }}>
              {!isUser && msg.thinking !== undefined && (
                <ThinkingBlock text={msg.thinking} />
              )}
              <div
                style={{
                  padding: '9px 13px',
                  borderRadius: isUser ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
                  background: isUser ? BUBBLE_USER_BG : BUBBLE_AI_BG,
                  color: '#e5e5e5',
                  fontSize: 14,
                  lineHeight: 1.55,
                  wordBreak: 'break-word',
                }}
                dangerouslySetInnerHTML={{ __html: isUser ? renderMarkdown(msg.content) : renderMarkdown(msg.content) }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
