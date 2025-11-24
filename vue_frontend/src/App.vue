<template>
  <div class="h-100">
    <TitleComponent />
    <BContainer class="content">
      <RouterView />
    </BContainer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import TitleComponent from './components/TitleComponent.vue'
import eventBus, { type Events } from './stores/eventBus'
import { EventAction } from './interfaces/EventAction'
import { setReaderId, setUserFromSessionStorage } from './utils'
import { clientStore } from '@/stores/clientStore'

// Router and Route
const router = useRouter()
const route = useRoute()

// Lifecycle Hooks
onMounted(async () => {
  await router.isReady()
  setReaderId(router)
  setUserFromSessionStorage()

  // Handle scan event from event bus
  eventBus.on(EventAction.REDIRECT, (data: Events[EventAction.REDIRECT]) => {
    router.push('/items/' + data.rfid)
  })

  clientStore().fetchBackendConfig()
})

// Watchers
watch(
  () => route.query.reader,
  () => {
    setReaderId(router)
  },
)
</script>

<style scoped>
.h-100 {
  min-height: 100vh !important;
}

.content {
  flex-grow: 1;
  margin: 1.5rem auto;
  padding: 0 0;
  max-width: var(--content-max-width) !important;
}

@media (max-width: var(--content-max-width)) {
  .content {
    max-width: var(--content-max-width-small) !important;
    margin: 0 0 !important;
  }
}
</style>
