<template>
  <div class="h-100">
    <header>
      <div class="wrapper">
        <TitleComponent msg="WIMS?" />

        <nav>
          <RouterLink to="/">Home</RouterLink>
          <RouterLink to="/items">Items</RouterLink>
          <RouterLink to="/readers">Readers</RouterLink>
          <RouterLink to="/users">Users</RouterLink>
          <RouterLink to="/about">About</RouterLink>
        </nav>
      </div>
    </header>

    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import TitleComponent from './components/TitleComponent.vue';
import eventBus, { type Events } from './stores/eventBus';
import { EventAction } from './interfaces/EventAction';
import { setReaderId , setUserFromSessionStorage } from './utils'
import { clientStore } from '@/stores/clientStore';


// Router and Route
const router = useRouter();
const route = useRoute();

// Lifecycle Hooks
onMounted(async () => {
  await router.isReady();
  setReaderId(router);
  setUserFromSessionStorage();

  // Handle scan event from event bus
  eventBus.on(EventAction.REDIRECT, (data: Events[EventAction.REDIRECT]) => {
    router.push('/items/' + data.rfid);
  });

  clientStore().fetchBackendConfig();
});

// Watchers
watch(
  () => route.query.reader,
  () => {
    setReaderId(router);
  }
);
</script>

<style scoped>
.h-100 {
  height: 100vh !important;
}
</style>
