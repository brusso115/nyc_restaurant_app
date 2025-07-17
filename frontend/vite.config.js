import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/query': 'http://query-api:8000',
      '/restaurants': 'http://query-api:8000',
      '/categories': 'http://query-api:8000'
    }
  }
})
