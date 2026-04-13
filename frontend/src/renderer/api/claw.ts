// 通过 preload 暴露的 clawAPI 访问后端配置
import type { ClawConfig } from '../global.d'

export async function getBackendUrl(): Promise<string> {
  return window.clawAPI.getBackendUrl()
}

export async function readConfig(): Promise<ClawConfig | null> {
  return window.clawAPI.readConfig()
}

export async function writeConfig(config: ClawConfig): Promise<boolean> {
  return window.clawAPI.writeConfig(config)
}
