import { contextBridge, ipcRenderer } from 'electron'

export interface ClawAPI {
  sendMessage: (message: string, sessionId?: string) => Promise<{ response: string; sessionId: string }>
  getBackendUrl: () => Promise<string>
  readConfig: () => Promise<object | null>
  writeConfig: (config: object) => Promise<boolean>
}

contextBridge.exposeInMainWorld('clawAPI', {
  sendMessage: (message: string, sessionId?: string) =>
    ipcRenderer.invoke('claw:send', message, sessionId),
  getBackendUrl: () => ipcRenderer.invoke('claw:backend-url'),
  readConfig: () => ipcRenderer.invoke('config:read'),
  writeConfig: (config: object) => ipcRenderer.invoke('config:write', config),
} as ClawAPI)
