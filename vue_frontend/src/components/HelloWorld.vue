<template>
  <div class="greetings">
    <h1>{{ msg }}</h1>
    <h3></h3>
    <div>
      <span v-if="isConnected" class="icon-connected">🟢</span>
      <span v-else class="icon-disconnected">🔴</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { serverStream } from '@/stores/serverStream'
const server_stream = serverStream()

defineProps<{
  msg: string
}>()

import { computed } from 'vue'

const isConnected = computed(() => server_stream.alive)
</script>

<style scoped>
.icon-connected {
  color: green;
}

.icon-disconnected {
  color: red;
}
</style>
