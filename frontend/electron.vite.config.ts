import { defineConfig, externalizeDepsPlugin } from 'electron-vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react(), externalizeDepsPlugin()],
  root: '.',
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/main/index.ts'),
        preload: resolve(__dirname, 'src/preload/index.ts'),
        renderer: resolve(__dirname, 'src/renderer/index.html'),
      },
    },
  },
})
