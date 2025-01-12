<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { onMounted } from 'vue'
import HelloWorld from './components/HelloWorld.vue'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'

import { serverStream } from './stores/serverStream'
import { clientStore } from './stores/clientStore'
import { computed } from 'vue'
// Import Bootstrap and BootstrapVue CSS files (order is important)
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

const client_store = clientStore()
const server_stream = serverStream()
const router = useRouter()

onMounted(async () => {
  await router.isReady();
  console.log('mounted', computed(()=> router.currentRoute.value.query.reader).value)
  client_store.reader_id = router.currentRoute.value.query.reader
  server_stream.connect(String(client_store.reader_id))
})
</script>

<template>
  <header>
    <div class="wrapper">
      <HelloWorld msg="WIMS?" />

      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/about">About</RouterLink>
      </nav>
    </div>
  </header>

  <RouterView />
</template>

<style scoped></style>
