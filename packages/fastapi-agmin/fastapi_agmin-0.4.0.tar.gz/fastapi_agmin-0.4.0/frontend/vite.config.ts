// @ts-ignore
import { defineConfig } from 'vite'
// @ts-ignore
import vue from '@vitejs/plugin-vue'
// @ts-ignore
import { resolve, dirname } from 'path'
// @ts-ignore
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))

export default defineConfig(({ command }) => ({
  plugins: [vue()],
  build: {
    outDir: resolve(__dirname, '../src/fastapi_agmin/static'),
    emptyOutDir: true,
  },
  server: command === 'serve' ? {
    proxy: {
      '/agmin/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  } : undefined
}))
