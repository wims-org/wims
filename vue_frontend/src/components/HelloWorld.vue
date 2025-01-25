<template>
  <div class="greetings">
    <a href="/" style="text-decoration: none; color: inherit;"><h1>{{ msg }}</h1></a>
    <div>
      <span v-if="isConnected" class="icon-connected"
        >🟢 Connected to Reader with id {{ client_store.reader_id }}</span
      >
      <span v-else class="icon-disconnected">🔴 Not Connected to a reader, choose one at <a href="/readers"></a></span>
    </div>
  </div>
</template>

<script lang="ts">
import { clientStore } from '@/stores/clientStore';
import { serverStream } from '@/stores/serverStream';
import { defineComponent } from 'vue'

export default defineComponent({
  setup() {
    const client_store = clientStore()
    const server_stream = serverStream()
    const msg = 'WIMS?!'

    return {
      client_store,
      isConnected: server_stream.alive && client_store?.reader_id.length > 0,
      msg,
    }
  },
})
</script>

<style scoped>
.icon-connected {
  color: green;
}

.icon-disconnected {
  color: red;
}
</style>
