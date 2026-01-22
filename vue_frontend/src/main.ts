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

import * as Sentry from '@sentry/vue'

import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'
import { clientStore } from './stores/clientStore'
import { createSentryPiniaPlugin } from '@sentry/vue'

const app = createApp(App)
const pinia = createPinia()
pinia.use(createSentryPiniaPlugin())

app.use(pinia)
useThemeStore().applyTheme()
app.use(router)
app.use(createBootstrap()) // Important
app.component('font-awesome-icon', FontAwesomeIcon)

axios.defaults.baseURL = import.meta.env.VITE_API_URL

// Enable Sentry if tracking is enabled
clientStore().fetchBackendConfig().then(() => {
  const enableAnalytics = localStorage.getItem('enable_analytics') === 'true'
  if (enableAnalytics && clientStore().backend_config?.sentry_dsn?.length) {
    Sentry.init({
      app,
      dsn: clientStore().backend_config.sentry_dsn,
      integrations: [Sentry.browserTracingIntegration({ router })],
      environment: 'dev',
      release: '0.1.0',
      tracesSampleRate: 0.01,
    })
  }
})

app.mount('#app')
console.log(axios.defaults.baseURL)
