import { useState, useEffect, useRef, useCallback } from 'react'
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
  // 跟踪当前 session
  const [sessionId, setSessionId] = useState<string>('')
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    window.clawAPI.getBackendUrl().then((url) => {
      setBackendBase(url.replace(/\/$/, ''))
    })
  }, [])

  if (!backendBase) return null

  // 解析 <think>...</think> 标签，提取 thinking 内容
  const parseThinking = (content: string): { thinking: string; clean: string } => {
    const parts: string[] = []
    let rest = content
    const thinkRe = /<think>([\s\S]*?)</think>/
    let match = rest.match(thinkRe)
    while (match) {
      parts.push(match[1].trim())
      rest = rest.slice(0, match.index!) + rest.slice(match.index! + match[0].length)
      match = rest.match(thinkRe)
    }
    return { thinking: parts.join('\n'), clean: rest }
  }

  const handleSend = useCallback(async (text: string) => {
    if (loading) return
    if (abortRef.current) abortRef.current.abort()
    const controller = new AbortController()
    abortRef.current = controller

    const userMsg: Message = { id: crypto.randomUUID(), role: 'user', content: text }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)
    setError(null)

    const assistantId = crypto.randomUUID()
    const placeholder: Message = { id: assistantId, role: 'assistant', content: '', thinking: '' }
    setMessages((prev) => [...prev, placeholder])

    let fullText = ''
    let fullThinking = ''

    try {
      // 发送当前 session_id（首次为空，后端会生成）
      const res = await fetch(`${backendBase}/api/claw/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: sessionId }),
        signal: controller.signal,
      })

      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      // 从 header 提取并保存 session_id
      const newSessionId = res.headers.get('X-Session-Id')
      if (newSessionId && newSessionId !== sessionId) {
        setSessionId(newSessionId)
      }

      const reader = res.body!.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        for (const line of chunk.split('\n')) {
          if (!line.startsWith('data: ')) continue
          const raw = line.slice(6).trim()
          if (raw === '[DONE]' || !raw) continue

          try {
            const data = JSON.parse(raw)
            if (data.type === 'thinking') {
              fullThinking += data.content
              setMessages((prev) =>
                prev.map((m) => m.id === assistantId ? { ...m, thinking: fullThinking } : m)
              )
            } else if (data.type === 'text') {
              fullText += data.content
              const { thinking, clean } = parseThinking(fullText)
              fullThinking = thinking
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, content: clean, thinking: thinking } : m
                )
              )
            } else if (data.type === 'tool_call') {
              fullText += `[${data.tool_name}]\n`
              setMessages((prev) =>
                prev.map((m) => m.id === assistantId ? { ...m, content: fullText } : m)
              )
            } else if (data.type === 'tool_result') {
              fullText += `${data.content}\n`
              setMessages((prev) =>
                prev.map((m) => m.id === assistantId ? { ...m, content: fullText } : m)
              )
            }
          } catch {
            // skip malformed
          }
        }
      }
    } catch (err) {
      if ((err as Error).name === 'AbortError') return
      const msg = err instanceof Error ? err.message : String(err)
      setError(msg)
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId ? { ...m, content: `请求失败: ${msg}` } : m
        )
      )
    } finally {
      setLoading(false)
      abortRef.current = null
    }
  }, [loading, backendBase, sessionId])

  return (
    <div style={{
      display: 'flex', height: '100vh', background: '#1a1a1a', color: '#e5e5e5',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontSize: 14,
    }}>
      <Sidebar active={tab} onNavigate={setTab} />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {error && (
          <div style={{
            padding: '8px 16px', background: '#3d1a1a', color: '#ff8080',
            fontSize: 12, borderBottom: '1px solid #5a2020', flexShrink: 0,
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
