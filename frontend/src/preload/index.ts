import { contextBridge, ipcRenderer } from 'electron'

export interface ClawAPI {
  getBackendUrl: () => Promise<string>
  readConfig: () => Promise<object | null>
  writeConfig: (config: object) => Promise<boolean>
}

contextBridge.exposeInMainWorld('clawAPI', {
  getBackendUrl: () => ipcRenderer.invoke('claw:backend-url'),
  readConfig: () => ipcRenderer.invoke('config:read'),
  writeConfig: (config: object) => ipcRenderer.invoke('config:write', config),
} as ClawAPI)
