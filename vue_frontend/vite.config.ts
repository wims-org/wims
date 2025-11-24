import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

import Components from 'unplugin-vue-components/vite'
import { BootstrapVueNextResolver } from 'bootstrap-vue-next'
import Icons from 'unplugin-icons/vite'
import IconsResolve from 'unplugin-icons/resolver'

import { readFileSync } from 'fs'
const packageJson = JSON.parse(readFileSync(new URL('./package.json', import.meta.url), 'utf-8'))
process.env.VUE_APP_VERSION = packageJson.version

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vueDevTools(),
    vue({
      template: {

      },
    }),
    Components({
      resolvers: [BootstrapVueNextResolver(), IconsResolve()],
      dts: true
    }),
    Icons({
      compiler: 'vue3',
      autoInstall: true,
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
