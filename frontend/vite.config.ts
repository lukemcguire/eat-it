import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/',
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  server: {
    proxy: {
      '/recipes': 'http://localhost:8000',
      '/shopping-lists': 'http://localhost:8000',
    },
  },
});
