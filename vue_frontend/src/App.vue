<template>
  <div class="h-100">
    <TitleComponent />
    <div class="title-liner"></div>
    <BContainer class="content">
      <RouterView />
    </BContainer>
    <FooterComponent class="footer" />
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
.title-liner {
  box-shadow: 0 40px 230px 30px color-mix(in srgb, var(--color-primary) 35%, transparent);
  -webkit-box-shadow: 0 40px 230px 30px color-mix(in srgb, var(--color-primary) 35%, transparent);
  -moz-box-shadow: 0 40px 230px 30px color-mix(in srgb, var(--color-primary) 35%, transparent);
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
