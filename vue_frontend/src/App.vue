<script lang="ts">
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'
import HelloWorld from './components/HelloWorld.vue'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'

import { serverStream } from './stores/serverStream'
import { clientStore } from './stores/clientStore'
// Import Bootstrap and BootstrapVue CSS files (order is important)
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import eventBus, { type Events } from './stores/eventBus'
import { EventAction } from './interfaces/EventAction'

export default {
  name: 'App',
  components: {
    HelloWorld,
  },
  setup() {
    const client_store = clientStore()
    const server_stream = serverStream()
    const router = useRouter()
    onMounted(async () => {
      await router.isReady()
      if (client_store.reader_id === '') {
        client_store.reader_id = Array.isArray(router.currentRoute.value.query.reader)
          ? router.currentRoute.value.query.reader[0] || ''
          : router.currentRoute.value.query.reader || ''
        server_stream.connect(client_store.client_id, 'client_id')
      }
      if (client_store.reader_id) {
        server_stream.connect(client_store.reader_id, 'reader_id')
      }

      // Handle scan event from event bus
      eventBus.on('scan', (data: Events['scan']) => {
        console.log('Scan event:', data)
        if (client_store.expected_event_action === EventAction.REDIRECT) {
          router.push('/items/' + data.rfid);
        }
      });
    })
    return {
      client_store,
      server_stream,
    }
  },
}
</script>

<template>
  <div class="col-12">
    <header>
      <div class="wrapper">
        <HelloWorld msg="WIMS?" />

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

<style scoped></style>
