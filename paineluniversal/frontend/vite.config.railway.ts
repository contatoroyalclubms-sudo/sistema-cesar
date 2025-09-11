import { defineConfig } from 'vite'

// Configuração específica para Railway
export default defineConfig({
  preview: {
    port: process.env.PORT ? parseInt(process.env.PORT) : 4173,
    host: '0.0.0.0'
  }
})
