import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  root: 'static',
  build: {
    outDir: '../../dist',
    rollupOptions: {
      input: './static/js/main.js' // 修改入口点的路径
    }
  },
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:5000' // 可能更合适的代理配置，只代理以 /api 开头的请求
    }
  }
})
