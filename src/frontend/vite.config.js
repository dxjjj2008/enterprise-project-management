import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    open: true
  },
  build: {
    // 构建优化
    rollupOptions: {
      output: {
        manualChunks: {
          // 将 Element Plus 单独打包
          'element-plus': ['element-plus'],
          // 将图标单独打包
          'icons': ['@element-plus/icons-vue'],
          // 将路由相关的库单独打包
          'vue-router': ['vue-router'],
          // 将状态管理单独打包
          'pinia': ['pinia']
        }
      }
    },
    // 启用 gzip 压缩大小报告
    reportCompressedSize: true,
    // chunk 大小警告限制
    chunkSizeWarningLimit: 500
  },
  test: {
    globals: true,
    environment: 'happy-dom',
    include: ['**/*.test.{js,ts,jsx,tsx}'],
    setupFiles: ['./vitest.setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        '.eslintrc.js',
        'vite.config.js',
        'src/main.js'
      ]
    }
  }
})
