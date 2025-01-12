import './assets/main.css'

import { createApp, watch } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import axios from 'axios'
import { serverStream } from './stores/serverStream'
const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

const server_stream = serverStream()
axios.defaults.baseURL = "http://localhost:5005"

watch(server_stream.messages, (newMessages) => {
    for (let i = 0; i < newMessages.length; i++) {
        const data = JSON.parse(newMessages[i].replace(/'/g, '"'));
        router.push('/item/' + data.rfid)
    }
})