import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import configureCompat from "@vue/compat"
import App from './App.vue'
import router from './router'
import axios from 'axios'
import { FontAwesomeIcon } from './font-awesome'
import { createBootstrap } from 'bootstrap-vue-next'

import * as Sentry from "@sentry/vue";

// Add the necessary CSS
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'

new configureCompat({
  ATTR_FALSE_VALUE: false,
  RENDER_FUNCTION: false,
  COMPONENT_ASYNC: false,
  WATCH_ARRAY: false,
})
const app = createApp(App)

if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    app,
    dsn: import.meta.env.VITE_SENTRY_DSN,
    sendDefaultPii: true,
    integrations: [
    ],
  })
}


app.use(createPinia())
app.use(router)
app.use(createBootstrap()) // Important
app.component('font-awesome-icon', FontAwesomeIcon)
app.mount('#app')

axios.defaults.baseURL = import.meta.env.VITE_API_URL
console.log(axios.defaults.baseURL)
