interface SidebarProps {
  active: 'chat' | 'settings'
  onNavigate: (tab: 'chat' | 'settings') => void
}

// 配色：深灰 #1e1e1e，侧边栏 #252525，蓝色 #5b8def
const BG = '#252525'
const ACTIVE = '#5b8def'
const INACTIVE = '#666666'

export default function Sidebar({ active, onNavigate }: SidebarProps) {
  return (
    <div
      style={{
        width: 52,
        background: BG,
        borderRight: '1px solid #333333',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        paddingTop: 12,
        gap: 6,
        flexShrink: 0,
      }}
    >
      <NavBtn active={active === 'chat'} onClick={() => onNavigate('chat')} label="Chat">
        <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      </NavBtn>
      <NavBtn active={active === 'settings'} onClick={() => onNavigate('settings')} label="Settings">
        <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.786.426 1.786 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.786-.426-1.786-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </NavBtn>
    </div>
  )
}

function NavBtn({
  active,
  onClick,
  label,
  children,
}: {
  active: boolean
  onClick: () => void
  label: string
  children: React.ReactNode
}) {
  return (
    <button
      title={label}
      onClick={onClick}
      style={{
        width: 38,
        height: 38,
        borderRadius: 10,
        border: 'none',
        background: active ? ACTIVE + '22' : 'transparent',
        color: active ? ACTIVE : INACTIVE,
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'all 0.15s',
      }}
    >
      {children}
    </button>
  )
}
