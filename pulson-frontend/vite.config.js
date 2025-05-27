import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// ✅ Ustawienia dla Home Assistant path /pulson_alarm_panel
export default defineConfig({
  base: '/pulson_alarm_panel/',
  plugins: [react()],
  build: {
    outDir: 'dist',
  },
})
