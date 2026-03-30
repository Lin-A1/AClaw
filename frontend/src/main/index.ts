import { app, BrowserWindow } from 'electron'
import { join } from 'path'
import { startBackend, stopBackend, getBackendUrl } from './backend'

let mainWindow: BrowserWindow | null = null

async function createWindow() {
  // 启动后端服务
  const backendUrl = await startBackend()
  console.log('[Main] Backend started at', backendUrl)

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

  // 加载后端页面
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL(backendUrl)
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  stopBackend()
  app.quit()
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})
