<template>
  <div
    class="d-flex flex-column align-items-center m-2 flex-column-reverse panel-sized"
    :class="`panel-size-${imageSize || defaultImageSize}`"
  >
    <div class="panel-title text-center">
      {{
        title.substring(0, 10 * (imageSize || defaultImageSize)) +
        (title.length > 10 * (imageSize || defaultImageSize) ? '...' : '')
      }}
    </div>

    <div class="thumbnail-container thumbnail-lg">
      <div v-if="images.length > 1" class="panel-controls">
        <BButton class="panel-controls-prev" @click.stop="selectPrevImage()">
          <font-awesome-icon icon="arrow-left" />
        </BButton>
        <BButton class="panel-controls-next" @click.stop="selectNextImage()">
          <font-awesome-icon icon="arrow-right" />
        </BButton>
      </div>
      <div
        class="img-wrapper"
        :data-img-id="imageIndex"
        ref="el => observeImage(el, item.tag_uuid)"
      >
        <div
          v-if="erroredImages[imageIndex] || !images[imageIndex] || !loadRequested"
          class="img-placeholder"
        >
          <img
            src="@/assets/placeholder.png"
            class="thumbnail placeholder-img"
            alt="Image placeholder"
          />
        </div>

        <img
          v-else
          :src="images[imageIndex]"
          class="thumbnail real-image"
          :class="{
            'img-hidden': erroredImages[imageIndex],
          }"
          alt="Image Thumbnail"
          loading="lazy"
          decoding="async"
          @error="onImageError()"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
// Item component for displaying a single item in a list with a picture slider and title.
// Props definition containing pictures array and title string. Emit event on item click.
import { ref } from 'vue'
const props = defineProps<{
  images: string[]
  title: string
  imageSize?: number
  loadRequested?: boolean
}>()

const imageIndex = ref<number>(0)
const defaultImageSize = ref<number>(2)
const erroredImages = ref<Record<string, boolean>>({})

const onImageError = () => {
  erroredImages.value[imageIndex.value] = true
}

defineEmits<{
  (e: 'item-clicked'): void
}>()

const selectNextImage = () => {
  if (!imageIndex.value) {
    imageIndex.value = 0
  }
  imageIndex.value = (imageIndex.value + 1) % props.images.length
}
const selectPrevImage = () => {
  if (!imageIndex.value) {
    imageIndex.value = 0
  }
  imageIndex.value = (imageIndex.value - 1 + props.images.length) % props.images.length
}
</script>

<style scoped>
.img-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}
.img-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-light);
  overflow: hidden;
}
.placeholder-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.thumbnail-container {
  position: relative;
  width: 4rem;
  height: 4rem;
  cursor: pointer;
}
.thumbnail-lg {
  width: 8rem;
  height: 8rem;
}

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.panel-title {
  width: 100%;
  padding-top: 0.3rem;
  transform: translateY(-0.3rem);
  background-color: var(--color-bg-light);
  border-radius: 4px;
  border: 1px solid var(--border-color);
}
.panel-controls {
  padding: 0 0.2rem;
  position: absolute;
  display: flex;
  justify-content: space-between;
  width: 100%;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
}
.panel-controls-next,
.panel-controls-prev {
  background-color: var(--color-bg-light);
  border: 1px solid var(--border-color);
  color: var(--color-text);
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  z-index: 10;
  opacity: 0.3;
  pointer-events: all;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  &:hover {
    opacity: 1;
    transition: opacity 0.2s;
  }
}
.img-hidden {
  display: none;
}

.panel-sized {
  min-width: calc(max(var(--panel-size), 50px) + 2rem);
  min-height: calc(max(var(--panel-size), 50px) + 2rem);
  > .thumbnail-lg {
    width: calc(max(var(--panel-size), 50px) + 2rem);
    height: calc(max(var(--panel-size), 50px) + 2rem);
  }
}
.panel-size-1 {
  --panel-size: 4vw;
}
.panel-size-2 {
  --panel-size: 10vw;
}
.panel-size-3 {
  --panel-size: 16vw;
}
.panel-size-4 {
  --panel-size: 23vw;
}
.panel-size-5 {
  --panel-size: 50vw;
}
</style>
