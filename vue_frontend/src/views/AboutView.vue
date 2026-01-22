<template>
  <div class="col-12">
    <h1>This is an about page</h1>
    <h2>Config</h2>
    <pre>{{
      clientStore().backend_config
        ? JSON.stringify(clientStore().backend_config, null, 2)
        : 'No config available'
    }}</pre>

    <BFormCheckbox
      v-model="enableAnalytics"
      class="align-items-center d-flex"
    >
      I want to support the development by sharing anonymous usage data.
    </BFormCheckbox>
  </div>
</template>

<script setup lang="ts">
import { clientStore } from '@/stores/clientStore'
import { watch, ref } from 'vue'

const enableAnalytics = ref<boolean>(localStorage.getItem('enable_analytics') === 'true')
watch(
  () => enableAnalytics.value,
  (newValue) => {
    console.log('Enable Analytics changed to:', newValue)
    localStorage.setItem('enable_analytics', newValue ? 'true' : 'false')
    location.reload()
  },
)
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
