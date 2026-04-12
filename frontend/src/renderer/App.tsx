import { useState, useEffect } from 'react'
import Chat from './components/Chat'
import ChatInput from './components/ChatInput'
import Sidebar from './components/Sidebar'
import Settings from './components/Settings'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

export default function App() {
  const [tab, setTab] = useState<'chat' | 'settings'>('chat')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [backendBase, setBackendBase] = useState<string>('')

  useEffect(() => {
    window.clawAPI.getBackendUrl().then((url) => {
      setBackendBase(url.replace(/\/.*/, ''))
    })
  }, [])

  if (!backendBase) return null

  const handleSend = async (text: string) => {
    const userMsg: Message = { id: crypto.randomUUID(), role: 'user', content: text }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)

    try {
      const res = await fetch(`${backendBase}/api/claw/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })
      const data = await res.json()
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: 'assistant', content: data.response },
      ])
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        height: '100vh',
        background: '#1a1a1a',
        color: '#e5e5e5',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        fontSize: 14,
      }}
    >
      <Sidebar active={tab} onNavigate={setTab} />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {tab === 'chat' ? (
          <>
            <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
              <Chat messages={messages} />
              <ChatInput onSend={handleSend} loading={loading} />
            </div>
          </>
        ) : (
          <Settings />
        )}
      </div>
    </div>
  )
}
