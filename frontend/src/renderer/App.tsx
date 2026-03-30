import { useState } from 'react'
import Chat from './components/Chat'
import ChatInput from './components/ChatInput'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)

  const handleSend = async (text: string) => {
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
    }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)

    try {
      const res = await fetch('http://localhost:8000/api/claw/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })
      const data = await res.json()
      const aiMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response,
      }
      setMessages((prev) => [...prev, aiMsg])
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <header style={{ padding: '12px 16px', borderBottom: '1px solid #333', background: '#16213e' }}>
        <h1 style={{ fontSize: '16px', fontWeight: 600 }}>MultClaw</h1>
      </header>
      <Chat messages={messages} />
      <ChatInput onSend={handleSend} loading={loading} />
    </div>
  )
}
