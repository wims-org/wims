<template>
  <div class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <img :src="image" class="modal-image" alt="Full Image" />
      <button class="btn btn-secondary mt-3" @click="close">Close</button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  image: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

function close() {
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8); /* Slightly darker background */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  max-width: 90%;
  max-height: 90%;
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.modal-image {
  max-width: 100%;
  max-height: 80vh;
  border-radius: 8px;
  object-fit: contain; /* Ensures the image scales properly */
}
</style>