import { contextBridge, ipcRenderer } from 'electron'

export interface ClawAPI {
  sendMessage: (message: string, sessionId?: string) => Promise<{ response: string; sessionId: string }>
}

contextBridge.exposeInMainWorld('clawAPI', {
  sendMessage: (message: string, sessionId?: string) =>
    ipcRenderer.invoke('claw:send', message, sessionId),
} as ClawAPI)
