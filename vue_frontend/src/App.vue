<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { onMounted } from 'vue'
import HelloWorld from './components/HelloWorld.vue'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'

import { serverStream } from './stores/serverStream'
import { clientStore } from './stores/clientStore'
// Import Bootstrap and BootstrapVue CSS files (order is important)
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

const client_store = clientStore()
const server_stream = serverStream()
const router = useRouter()

onMounted(async () => {
  await router.isReady()
  client_store.reader_id = Array.isArray(router.currentRoute.value.query.reader)
    ? router.currentRoute.value.query.reader[0] || ''
    : router.currentRoute.value.query.reader || ''
  server_stream.connect(client_store.client_id, 'client_id')
  if (client_store.reader_id) {
    server_stream.connect(client_store.reader_id, 'reader_id')
  }
})
</script>

<template>
  <header>
    <div class="wrapper">
      <HelloWorld msg="WIMS?" />

      <nav>
        onMounted
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/about">About</RouterLink>
      </nav>
    </div>
  </header>

  <RouterView />
</template>

<style scoped></style>
