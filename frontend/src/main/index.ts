import { app, BrowserWindow, ipcMain } from 'electron'
import { join } from 'path'
import { readFile, writeFile } from 'fs/promises'
import { getBackendUrl } from './backend'

let mainWindow: BrowserWindow | null = null

async function createWindow() {
  const backendUrl = await getBackendUrl()
  console.log('[Main] Backend URL:', backendUrl)

  ipcMain.handle('claw:backend-url', () => backendUrl)

  const configPath = app.isPackaged
    ? join(process.resourcesPath, '.claw/config.json')
    : join(__dirname, '../../../.claw/config.json')

  ipcMain.handle('config:read', async () => {
    try {
      const content = await readFile(configPath, 'utf-8')
      const cfg = JSON.parse(content)
      return cfg
    } catch {
      return null
    }
  })

  ipcMain.handle('config:write', async (_event, config: object) => {
    try {
      await writeFile(configPath, JSON.stringify(config, null, 2), 'utf-8')
      return true
    } catch {
      return false
    }
  })

  mainWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    title: 'MultClaw',
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  if (process.env.ELECTRON_RENDERER_URL) {
    mainWindow.loadURL(process.env.ELECTRON_RENDERER_URL)
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }

  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools()
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  app.quit()
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})
