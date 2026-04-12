import { useState, useEffect } from 'react'
import type { ClawConfig } from '../global.d'

const BG = '#1a1a1a'
const CARD = '#252525'
const BORDER = '#333333'
const TEXT = '#e0e0e0'
const LABEL = '#888888'
const BLUE = '#5b8def'
const GREEN = '#4ade80'
const RED = '#e5534b'

// ── Settings ──────────────────────────────────────────────────────────────────

export default function Settings() {
  const [config, setConfig] = useState<ClawConfig | null>(null)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [err, setErr] = useState('')
  const [rawInput, setRawInput] = useState('')
  const [rawValid, setRawValid] = useState(true)

  useEffect(() => {
    window.clawAPI.readConfig().then((cfg) => {
      if (cfg) {
        setConfig(cfg as ClawConfig)
        setRawInput(JSON.stringify(cfg, null, 2))
      }
    })
  }, [])

  const save = async () => {
    if (!config) return
    setSaving(true)
    setSaved(false)
    setErr('')
    const ok = await window.clawAPI.writeConfig(config)
    setSaving(false)
    if (ok) { setSaved(true); setTimeout(() => setSaved(false), 2000) }
    else setErr('保存失败')
  }

  if (!config) return <div style={{ color: LABEL, padding: 24 }}>加载中...</div>

  return (
    <div style={{ flex: 1, overflowY: 'auto', position: 'relative' }}>
      <div style={{
        maxWidth: 720,
        margin: '0 auto',
        padding: 'clamp(16px, 4vw, 32px)' as unknown as string,
      }}>
        <h2 style={{ color: TEXT, fontSize: 16, fontWeight: 600, marginBottom: 20 }}>设置</h2>

        {/* 基本信息 */}
        <Block title="基本信息">
          <FieldRow label="名称"    value={config.name}        onChange={(v) => setConfig({ ...config, name: v })} />
          <FieldRow label="角色"    value={config.role}        onChange={(v) => setConfig({ ...config, role: v })} />
          <FieldRow label="描述"    value={config.description} onChange={(v) => setConfig({ ...config, description: v })} multiline />
          <FieldRow label="版本"    value={config.version}     onChange={(v) => setConfig({ ...config, version: v })} />
        </Block>

        {/* 路径 */}
        <Block title="路径">
          <FieldRow label="Memory" value={config.paths.memory} onChange={(v) => setConfig({ ...config, paths: { ...config.paths, memory: v } })} />
          <FieldRow label="Skills" value={config.paths.skills} onChange={(v) => setConfig({ ...config, paths: { ...config.paths, skills: v } })} />
          <FieldRow label="MCP"   value={config.paths.mcp}    onChange={(v) => setConfig({ ...config, paths: { ...config.paths, mcp: v } })} />
        </Block>

        {/* 服务 */}
        <Block title="服务">
          <FieldRow label="端口"    value={String(config.port)} onChange={(v) => setConfig({ ...config, port: Number(v) })} type="number" />
        </Block>

        {/* LLM */}
        <Block title="LLM 大语言模型">
          <FieldRow label="模型"  value={config.server.llm.name}   onChange={(v) => setConfig({ ...config, server: { ...config.server, llm: { ...config.server.llm, name: v } } })} />
          <FieldRow label="URL"   value={config.server.llm.url}    onChange={(v) => setConfig({ ...config, server: { ...config.server, llm: { ...config.server.llm, url: v } } })} />
          <FieldRow label="Key"   value={config.server.llm.apikey} onChange={(v) => setConfig({ ...config, server: { ...config.server, llm: { ...config.server.llm, apikey: v } } })} password />
          <Divider />
          <div style={{ padding: '0 16px 16px' }}>
            <p style={{ color: LABEL, fontSize: 11, fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase' as const, marginBottom: 8 }}>模型参数</p>
            <ParamsEditor params={config.server.llm.params ?? {}} onChange={(params) => setConfig({ ...config, server: { ...config.server, llm: { ...config.server.llm, params } } })} />
          </div>
        </Block>

        {/* 其他参数 */}
        <Block title="其他参数">
          <div style={{ padding: '0 16px 16px' }}>
            <RawEditor
              value={rawInput}
              valid={rawValid}
              onChange={(raw) => {
                setRawInput(raw)
                try {
                  JSON.parse(raw)
                  setRawValid(true)
                  setConfig(JSON.parse(raw))
                } catch {
                  setRawValid(false)
                }
              }}
            />
          </div>
        </Block>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 24, paddingBottom: 16 }}>
          <button type="button" onClick={save} disabled={saving || !rawValid} style={btnStyle(saving || !rawValid)}>
            {saving ? '保存中...' : '保存'}
          </button>
          {saved && <span style={{ color: GREEN, fontSize: 13 }}>已保存</span>}
          {err && <span style={{ color: RED, fontSize: 13 }}>{err}</span>}
        </div>
      </div>
    </div>
  )
}

function btnStyle(disabled: boolean): React.CSSProperties {
  return {
    padding: '8px 24px',
    borderRadius: 6,
    border: 'none',
    background: BLUE,
    color: '#fff',
    cursor: disabled ? 'not-allowed' : 'pointer',
    fontSize: 14,
    opacity: disabled ? 0.65 : 1,
    transition: 'opacity 0.15s',
  }
}

// ── Block ─────────────────────────────────────────────────────────────────────

function Block({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <p style={{ color: LABEL, fontSize: 11, fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase' as const, marginBottom: 8, marginLeft: 2 }}>{title}</p>
      <div style={{ background: CARD, border: `1px solid ${BORDER}`, borderRadius: 8, overflow: 'hidden' }}>
        {children}
      </div>
    </div>
  )
}

function Divider() {
  return <div style={{ height: 1, background: BORDER, margin: '0 16px' }} />
}

// ── Params Editor ──────────────────────────────────────────────────────────────

function ParamsEditor({ params, onChange }: { params: Record<string, unknown>; onChange: (p: Record<string, unknown>) => void }) {
  const [raw, setRaw] = useState(() => JSON.stringify(params, null, 2))
  const [valid, setValid] = useState(true)

  const apply = (text: string) => {
    setRaw(text)
    try {
      const parsed = JSON.parse(text)
      setValid(true)
      onChange(parsed)
    } catch {
      setValid(false)
    }
  }

  return (
    <textarea
      value={raw}
      onChange={(e) => apply(e.target.value)}
      rows={5}
      spellCheck={false}
      style={{
        width: '100%',
        boxSizing: 'border-box',
        background: valid ? BG : '#1f0f0f',
        border: `1px solid ${valid ? BORDER : RED}`,
        borderRadius: 6,
        color: TEXT,
        fontSize: 12,
        fontFamily: '"Fira Code", "Cascadia Code", "JetBrains Mono", "Consolas", monospace',
        padding: '8px 10px',
        resize: 'vertical',
        outline: 'none',
        lineHeight: 1.75,
        tabSize: 2,
        transition: 'border-color 0.15s, background 0.15s',
      }}
    />
  )
}

// ── Raw JSON Editor ────────────────────────────────────────────────────────────

function RawEditor({
  value,
  valid,
  onChange,
}: {
  value: string
  valid: boolean
  onChange: (raw: string) => void
}) {
  return (
    <>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={10}
        spellCheck={false}
        style={{
          width: '100%',
          boxSizing: 'border-box',
          background: valid ? '#111' : '#1f0f0f',
          border: `1px solid ${valid ? BORDER : RED}`,
          borderRadius: 8,
          color: valid ? TEXT : RED,
          fontSize: 12.5,
          fontFamily: '"Fira Code", "Cascadia Code", "JetBrains Mono", "Consolas", monospace',
          padding: '12px 14px',
          resize: 'vertical',
          outline: 'none',
          lineHeight: 1.75,
          transition: 'border-color 0.15s, background 0.15s',
        }}
      />
      {!valid && (
        <p style={{ color: RED, fontSize: 11, marginTop: 6 }}>JSON 格式错误</p>
      )}
    </>
  )
}

// ── Field Row ──────────────────────────────────────────────────────────────────

function FieldRow({
  label, value, onChange, type = 'text', multiline = false, password = false,
}: {
  label: string
  value: string
  onChange: (v: string) => void
  type?: string
  multiline?: boolean
  password?: boolean
}) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', padding: '10px 16px', gap: 12, borderBottom: `1px solid ${BORDER}` }}>
      <span style={{ width: 36, color: LABEL, fontSize: 12, flexShrink: 0, paddingTop: 6 }}>{label}</span>
      <TextInput value={value} onChange={onChange} type={type} multiline={multiline} password={password} label={label} />
    </div>
  )
}

function TextInput({
  value, onChange, type = 'text', multiline = false, password = false, label = '',
}: {
  value: string; onChange: (v: string) => void; type?: string; multiline?: boolean; password?: boolean; label?: string
}) {
  const [focused, setFocused] = useState(false)
  const base: React.CSSProperties = {
    flex: 1,
    background: BG,
    border: `1px solid ${focused ? BLUE : BORDER}`,
    borderRadius: 6,
    color: TEXT,
    fontSize: 13,
    fontFamily: 'inherit',
    padding: '6px 10px',
    outline: 'none',
    boxSizing: 'border-box',
    transition: 'border-color 0.15s',
  }
  if (multiline) {
    return (
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={2}
        aria-label={label}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        style={{ ...base, resize: 'vertical', lineHeight: 1.5 }}
      />
    )
  }
  return (
    <input
      type={password ? 'password' : type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      aria-label={label}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={base}
    />
  )
}
