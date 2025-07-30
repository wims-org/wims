<template>
  <div class="greetings">
    <router-link to="/" style="text-decoration: none; color: inherit">
      <h1>{{ msg }}</h1>
    </router-link>
    <div data-testid="sse-connection-state">
      <span v-if="connection_state === 0" class="icon-connected">
        🟢 Connected to Reader with id {{ client_store.reader_id }}
      </span>
      <span v-else-if="connection_state === 1" class="icon-connecting">
        <div class="spinner-border spinner-border-sm" role="status"></div>
        Connecting to backend...
      </span>
      <span v-else-if="connection_state === 2" class="icon-disconnected">
        🔴 Not Connected to a reader, choose one at
        <router-link to="/readers">readers</router-link>
      </span>
      <span v-else class="icon-disconnected">
        🔴 Not Connected to a reader, choose one at
        <router-link to="/readers">readers</router-link>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { clientStore } from '@/stores/clientStore';
import { serverStream } from '@/stores/serverStream';

// State and Stores
const client_store = clientStore();
const server_stream = serverStream();
const msg = 'WIMS?!';

// Computed Properties
const connection_state = computed(() => {
  if (
    server_stream.alive &&
    client_store?.reader_id.length > 0 &&
    client_store?.reader_id === server_stream.reader_id
  ) {
    return 0; // Connected
  } else if (
    client_store?.reader_id.length > 0 &&
    client_store?.reader_id === server_stream.reader_id
  ) {
    return 1; // Connecting
  } else {
    return 2; // Disconnected
  }
});
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
