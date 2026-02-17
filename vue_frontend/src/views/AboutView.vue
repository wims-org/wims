<template>
  <div class="col-12">
    <h1>This is an about page</h1>
    <h2>Config</h2>
    <pre>{{ clientStore().backend_config ? JSON.stringify(clientStore().backend_config, null, 2) : 'No config available' }}</pre>
    <h2>Selected barcode formats</h2>
    <CameraSettings />
  </div>
</template>

<script setup lang="ts">
import { clientStore } from '@/stores/clientStore'
</script>
<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>
