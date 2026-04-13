// 通过 preload 暴露的 clawAPI 访问后端配置
export async function getBackendUrl(): Promise<string> {
  return window.clawAPI.getBackendUrl()
}

export async function readConfig(): Promise<object | null> {
  return window.clawAPI.readConfig()
}

export async function writeConfig(config: object): Promise<boolean> {
  return window.clawAPI.writeConfig(config)
}
