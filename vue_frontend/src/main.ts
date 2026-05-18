import './assets/main.css'
import './assets/_bootstrap-variables.scss'
import 'bootstrap/scss/bootstrap.scss'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import { FontAwesomeIcon } from './font-awesome'
import { createBootstrap } from 'bootstrap-vue-next'
import { useThemeStore } from './stores/themeStore'
import type { components } from '@/interfaces/api-types'
type ConfigResponseModel = components['schemas']['ConfigResponseModel']
import * as Sentry from "@sentry/vue";

import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'

const app = createApp(App)
const pinia = createPinia()
axios.get('/config/').then((response) => {
  const backend_config: ConfigResponseModel = response.data

  if (backend_config.send_telemetry && (backend_config.sentry_dsn_frontend || import.meta.env.VITE_SENTRY_DSN)) {
    Sentry.init({
      app,
      dsn: backend_config.sentry_dsn_frontend || import.meta.env.VITE_SENTRY_DSN,
      sendDefaultPii: true,
      integrations: [
        Sentry.browserTracingIntegration({ router }),
      ],
      environment: import.meta.env.MODE
    })
  }
}).catch(() => ({}))


app.use(pinia)
useThemeStore().applyTheme()
app.use(router)
app.use(createBootstrap()) // Important
app.component('font-awesome-icon', FontAwesomeIcon)
app.mount('#app')

axios.defaults.baseURL = import.meta.env.VITE_API_URL
console.log(axios.defaults.baseURL)
