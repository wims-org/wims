import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

import { readFileSync } from 'fs'
const packageJson = JSON.parse(readFileSync(new URL('./package.json', import.meta.url), 'utf-8'))
process.env.VUE_APP_VERSION = packageJson.version

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vueDevTools(),
    vue({
      template: {
        compilerOptions: {
          compatConfig: {
            MODE: 2
          },
        },
      },
    }),
  ],
  resolve: {
    alias: {
      vue: '@vue/compat',
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
