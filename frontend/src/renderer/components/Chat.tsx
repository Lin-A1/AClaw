import type { Message } from '../App'

interface ChatProps {
  messages: Message[]
}

export default function Chat({ messages }: ChatProps) {
  return (
    <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
      {messages.length === 0 && (
        <div style={{ color: '#666', textAlign: 'center', marginTop: 40 }}>
          发送消息开始对话
        </div>
      )}
      {messages.map((msg) => (
        <div
          key={msg.id}
          style={{
            display: 'flex',
            justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            marginBottom: '12px',
          }}
        >
          <div
            style={{
              maxWidth: '70%',
              padding: '10px 14px',
              borderRadius: '12px',
              background: msg.role === 'user' ? '#4f46e5' : '#2d2d44',
              color: '#fff',
              whiteSpace: 'pre-wrap',
            }}
          >
            {msg.content}
          </div>
        </div>
      ))}
    </div>
  )
}
