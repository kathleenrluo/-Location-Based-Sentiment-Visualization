import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  base: '/-Location-Based-Sentiment-Visualization/',
  build: {
    outDir: 'dist'
  }
})

