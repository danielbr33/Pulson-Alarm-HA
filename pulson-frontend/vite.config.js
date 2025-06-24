import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '/pulson-alarm-panel/',
  plugins: [react()],
  build: {
    sourcemap: true,
    emptyOutDir: true,
    outDir: '../custom_components/pulson_alarm/www/panel/',
    rollupOptions: {
      input: 'src/main.jsx',  // <- <-- NAJWAŻNIEJSZE
      output: {
        entryFileNames: 'assets/index-[hash].js',
        assetFileNames: 'assets/[name].[ext]',
      },
    },
  },
})
