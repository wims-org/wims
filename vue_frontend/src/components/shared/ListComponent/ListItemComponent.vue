<template>
  <BRow>
    <BCol class="col-1 thumbnail-container">
      <div class="img-wrapper">
        <!-- placeholder shown while image not loaded -->
        <img
          v-if="!images?.length || imageErrored || !loadRequested"
          src="@/assets/placeholder.png"
          class="thumbnail"
          alt="Image Thumbnail"
        />
        <img
          v-else
          :src="images[0]"
          class="thumbnail real-image"
          alt="Image Thumbnail"
          loading="lazy"
          decoding="async"
          @error="imageErrored = true"
        />
      </div>
    </BCol>
    <BCol col-11>
      <h5 class="mb-1">{{ title }}</h5>
      <p class="mb-1">{{ description }}</p>
    </BCol>
  </BRow>
</template>
<script setup lang="ts">
import { ref } from 'vue'
defineProps<{
  images: string[]
  title: string
  description?: string | null
  imageSize?: number
  loadRequested?: boolean
}>()
const imageErrored = ref<boolean>(false)
</script>
<style scoped>
.thumbnail-container {
  position: relative;
  width: 4rem;
  height: 4rem;
  cursor: pointer;
}
.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.img-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}
</style>
