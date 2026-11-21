import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // U razvoju (npm run dev) stranica radi na :5173, a sve /api zahteve
    // prosledjujemo FastAPI serveru (python app.py) na :8000.
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
