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

import * as Sentry from "@sentry/vue";

import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'

const app = createApp(App)
const pinia = createPinia()

if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    app,
    dsn: import.meta.env.VITE_SENTRY_DSN,
    sendDefaultPii: true,
    integrations: [
    ],
  })
}


app.use(pinia)
useThemeStore().applyTheme()
app.use(router)
app.use(createBootstrap()) // Important
app.component('font-awesome-icon', FontAwesomeIcon)
app.mount('#app')

axios.defaults.baseURL = import.meta.env.VITE_API_URL
console.log(axios.defaults.baseURL)
