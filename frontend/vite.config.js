import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/chat': 'http://backend:8000',
      '/restaurants': 'http://backend:8000',
      '/categories': 'http://backend:8000'
    }
  }
})
