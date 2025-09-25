import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    host: true,
    open: false, // Não abrir automaticamente o navegador
    strictPort: true, // Falhar se a porta estiver ocupada
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // Não reescrever o path - manter /api
      },
    },
  },
  resolve: {
    alias: {
      '@': '/src',
      components: '/src/components',
      contexts: '/src/contexts',
      hooks: '/src/hooks',
      services: '/src/services',
      features: '/src/features',
      pages: '/src/pages',
      styles: '/src/styles',
    },
  },
})
