import { spawn } from 'child_process'
import { readFile } from 'fs/promises'
import { join } from 'path'

let backendProcess: ReturnType<typeof spawn> | null = null
const PORT_FILE = '/tmp/multclaw-port.txt'

function parsePort(stdout: string): string | null {
  const match = stdout.match(/Uvicorn running on http://[^:]+:(\d+)/)
  return match ? `http://localhost:${match[1]}` : null
}

export async function startBackend(): Promise<string> {
  return new Promise((resolve, reject) => {
    const backendDir = join(__dirname, '../../backend')
    backendProcess = spawn('uvicorn', ['app.main:app', '--reload'], {
      cwd: backendDir,
      stdio: ['pipe', 'pipe', 'pipe'],
      shell: true,
    })

    let resolved = false

    backendProcess.stdout?.on('data', (data: Buffer) => {
      const output = data.toString()
      console.log('[Backend]', output)
      if (!resolved) {
        const url = parsePort(output)
        if (url) {
          resolved = true
          resolve(url)
        }
      }
    })

    backendProcess.stderr?.on('data', (data: Buffer) => {
      console.error('[Backend Error]', data.toString())
    })

    backendProcess.on('error', (err) => {
      if (!resolved) reject(err)
    })
  })
}

export function stopBackend() {
  if (backendProcess) {
    backendProcess.kill()
    backendProcess = null
  }
}
