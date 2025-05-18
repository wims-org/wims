<template>
  <div class="greetings">
    <router-link to="/" style="text-decoration: none; color: inherit;">
      <h1>{{ msg }}</h1>
    </router-link>
    <div data-testid="sse-connection-state">
      <span v-if="connection_state === 0" class="icon-connected">🟢 Connected to Reader with id {{
        client_store.reader_id }}</span>
      <span v-else-if="connection_state == 1" class="icon-connecting">
        <div class="spinner-border spinner-border-sm" role="status"> </div>
        Connecting to backend...
      </span>
      <span v-else-if="connection_state == 2" class="icon-disconnected">🔴 Not Connected to a reader, choose one at
        <router-link to="/readers">readers</router-link></span>
      <span v-else class="icon-disconnected">🔴 Not Connected to a reader, choose one at <router-link
          to="/readers">readers</router-link></span>
    </div>
  </div>
</template>

<script lang="ts">
import { clientStore } from '@/stores/clientStore';
import { serverStream } from '@/stores/serverStream';
import { defineComponent } from 'vue'
import { computed } from 'vue'

export default defineComponent({
  name: 'TitleComponent',
  setup() {
    const client_store = clientStore()
    const server_stream = serverStream()
    const msg = 'WIMS?!'

    return {
      client_store,
      reader_id_len: computed(() => (client_store?.reader_id.length)),
      reader_id: computed(() => (client_store?.reader_id)),
      server_stream_reader_id: computed(() => (server_stream.reader_id)),
      alive: computed(() => (server_stream.alive)),
      connection_state: computed(() => (
        server_stream.alive && client_store?.reader_id.length > 0 && client_store?.reader_id === server_stream.reader_id)
        ? 0
        : (client_store?.reader_id.length> 0 && client_store?.reader_id === server_stream.reader_id)
          ? 1
          : 2),
      msg,
    }
  },
})
</script>

<style scoped>
.icon-connected {
  color: green;
}

.icon-connecting {
  color: gray;
}
.icon-disconnected {
  color: red;
}
</style>
