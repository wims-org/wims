import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import configureCompat from "@vue/compat"
import App from './App.vue'
import router from './router'
import axios from 'axios'
import { FontAwesomeIcon } from './font-awesome'
new configureCompat({
  ATTR_FALSE_VALUE: false,
  RENDER_FUNCTION: false,
})
const app = createApp(App)

app.use(createPinia())
app.use(router)

app.component('font-awesome-icon', FontAwesomeIcon)
app.mount('#app')

axios.defaults.baseURL = import.meta.env.VITE_API_URL
console.log(axios.defaults.baseURL)
