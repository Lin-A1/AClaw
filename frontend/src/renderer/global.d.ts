export interface LLMConfig {
  name: string
  url: string
  apikey: string
  params: Record<string, unknown>
}

export interface ClawConfig {
  name: string
  role: string
  description: string
  version: string
  port: number
  server: {
    llm: LLMConfig
  }
  paths: {
    memory: string
    skills: string
    mcp: string
  }
}

export interface ClawAPI {
  sendMessage: (message: string, sessionId?: string) => Promise<{ response: string; sessionId: string }>
  getBackendUrl: () => Promise<string>
  readConfig: () => Promise<ClawConfig | null>
  writeConfig: (config: ClawConfig) => Promise<boolean>
}

declare global {
  interface Window {
    clawAPI: ClawAPI
  }
}
