import type { Message } from '../App'

const BUBBLE_USER_BG = '#5b8def'
const BUBBLE_AI_BG = '#2e2e2e'
const EMPTY_COLOR = '#555555'

interface ChatProps {
  messages: Message[]
}

export default function Chat({ messages }: ChatProps) {
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
            <div
              style={{
                maxWidth: '70%',
                padding: '9px 13px',
                borderRadius: isUser ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
                background: isUser ? BUBBLE_USER_BG : BUBBLE_AI_BG,
                color: '#e5e5e5',
                fontSize: 14,
                lineHeight: 1.55,
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}
            >
              {msg.content}
            </div>
          </div>
        )
      })}
    </div>
  )
}
