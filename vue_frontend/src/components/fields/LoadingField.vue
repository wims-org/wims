<template>
  <div class="card p-2" data-testid="loading-field">
    <div class="d-flex flex-column justify-content-center align-items-center" style="height: 100px;">
      <div class="m-2 spinner-border text-primary" role="status"></div>
      <span>Container will be fetched after saving...</span>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'LoadingField',
});
</script>