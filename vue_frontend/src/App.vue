<script lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { onMounted, watch } from 'vue'
import TitleComponent from './components/TitleComponent.vue'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'

import { serverStream } from './stores/serverStream'
import { clientStore } from './stores/clientStore'
// Import Bootstrap and BootstrapVue CSS files (order is important)
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import eventBus, { type Events } from './stores/eventBus'
import { EventAction } from './interfaces/EventAction'
import { setReaderId } from './utils'

export default {
  name: 'App',
  components: {
    TitleComponent,
  },
  setup() {
    const client_store = clientStore()
    const server_stream = serverStream()
    const router = useRouter()
    const route = useRoute()

    onMounted(async () => {
      await router.isReady()
      setReaderId(router)

      // Handle scan event from event bus
      eventBus.on(EventAction.REDIRECT, (data: Events[EventAction.REDIRECT]) => {
        router.push('/items/' + data.rfid)
      })
    })

    // Watch for route parameter changes
    watch(
      () => route.query.reader,
      (newReader) => {
        setReaderId(router)
      },
    )

    return {
      client_store,
      server_stream,
    }
  },
}
</script>

<template>
  <div class="col-12 h-100">
    <header>
      <div class="wrapper">
        <TitleComponent msg="WIMS?" />

        <nav>
          <RouterLink to="/">Home</RouterLink>
          <RouterLink to="/items">Items</RouterLink>
          <RouterLink to="/readers">Readers</RouterLink>
          <RouterLink to="/about">About</RouterLink>
        </nav>
      </div>
    </header>

    <RouterView />
  </div>
</template>

<style scoped>
.h-100 {
  height: 100vh !important;
}
</style>
