import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// ---------------------------------------------------------------------------
// AirVision AI — Vite configuration
// ---------------------------------------------------------------------------
// The dev server proxies every /api request to the Flask backend so the
// browser never talks to OpenWeather directly (the API key stays server-side).
// Set VITE_PROXY_TARGET to point at a deployed backend when needed.
// ---------------------------------------------------------------------------
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,          // required for the live preview / container
    port: 5173,
    // The sandbox preview proxies the app under a dynamic *.e2b.app host —
    // allow any host so the preview (and local dev on LAN) works.
    allowedHosts: true,
    proxy: {
      '/api': {
        target: process.env.VITE_PROXY_TARGET || 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    chunkSizeWarningLimit: 1300,
    rollupOptions: {
      output: {
        manualChunks: {
          react: ['react', 'react-dom', 'react-router-dom'],
          charts: ['recharts'],
          maps: ['leaflet', 'react-leaflet'],
          motion: ['framer-motion'],
          icons: ['@mui/icons-material'],
          export: ['jspdf', 'html2canvas'],
        },
      },
    },
  },
})
