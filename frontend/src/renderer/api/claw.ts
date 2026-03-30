// API 调用封装层 - 后续可统一管理后端地址和请求逻辑
export async function sendChat(message: string, sessionId?: string) {
  const res = await fetch('http://localhost:8000/api/claw/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId }),
  })
  return res.json()
}
