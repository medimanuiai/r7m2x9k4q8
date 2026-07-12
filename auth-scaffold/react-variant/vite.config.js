import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy /api/v1 calls to the Express server (EJS variant runs on 3000)
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
      '/login': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
      '/register': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
      '/logout': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
      '/forgot-password': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
      // Ensure dashboard route is proxied so client redirects work during dev
      '/dashboard': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
    },
  },
});
