import { readFile } from 'fs/promises'
import { join } from 'path'

async function getConfiguredPort(): Promise<number> {
  try {
    const configPath = join(__dirname, '../../../.claw/config.json')
    const content = await readFile(configPath, 'utf-8')
    const config = JSON.parse(content)
    return config.port || 18000
  } catch {
    return 18000
  }
}

let backendUrl: string | null = null

export async function getBackendUrl(): Promise<string> {
  if (backendUrl) return backendUrl
  const port = await getConfiguredPort()
  backendUrl = `http://localhost:${port}`
  return backendUrl
}
