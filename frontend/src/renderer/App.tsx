import { useState, useEffect, useRef } from 'react'
import Chat from './components/Chat'
import ChatInput from './components/ChatInput'
import Sidebar from './components/Sidebar'
import Settings from './components/Settings'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  thinking?: string
}

export default function App() {
  const [tab, setTab] = useState<'chat' | 'settings'>('chat')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [backendBase, setBackendBase] = useState<string>('')

  // current assistant message being streamed (for in-place update)
  const streamingId = useRef<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    window.clawAPI.getBackendUrl().then((url) => {
      setBackendBase(url.replace(/\/$/, ''))
    })
  }, [])

  if (!backendBase) return null

  const handleSend = async (text: string) => {
    if (loading) return
    // abort any in-progress stream
    if (abortRef.current) abortRef.current.abort()
    const controller = new AbortController()
    abortRef.current = controller

    const userMsg: Message = { id: crypto.randomUUID(), role: 'user', content: text }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)
    setError(null)

    // placeholders for the streaming assistant message
    const assistantId = crypto.randomUUID()
    const placeholder: Message = { id: assistantId, role: 'assistant', content: '', thinking: '' }
    setMessages((prev) => [...prev, placeholder])
    streamingId.current = assistantId

    let fullText = ''
    let fullThinking = ''

    try {
      const res = await fetch(`${backendBase}/api/claw/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
        signal: controller.signal,
      })

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`)
      }

      const reader = res.body!.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value, { stream: true })
        for (const line of text.split('\n')) {
          if (!line.startsWith('data: ')) continue
          const raw = line.slice(6).trim()
          if (raw === '[DONE]' || !raw) continue

          try {
            const chunk = JSON.parse(raw)
            if (chunk.type === 'thinking') {
              fullThinking += chunk.content
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, thinking: fullThinking } : m
                )
              )
            } else if (chunk.type === 'text') {
              fullText += chunk.content
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, content: fullText } : m
                )
              )
            } else if (chunk.type === 'tool_call') {
              fullText += `[调用工具: ${chunk.tool_name}]\n`
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, content: fullText } : m
                )
              )
            }
          } catch {
            // skip malformed lines
          }
        }
      }
    } catch (err) {
      if ((err as Error).name === 'AbortError') return
      const msg = err instanceof Error ? err.message : String(err)
      setError(msg)
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: `请求失败: ${msg}` }
            : m
        )
      )
    } finally {
      setLoading(false)
      streamingId.current = null
      abortRef.current = null
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
        {error && (
          <div style={{
            padding: '8px 16px',
            background: '#3d1a1a',
            color: '#ff8080',
            fontSize: 12,
            borderBottom: '1px solid #5a2020',
            flexShrink: 0,
          }}>
            {error}
          </div>
        )}
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
