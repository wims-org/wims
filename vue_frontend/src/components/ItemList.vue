<template>
  <div class="container">
    <BRow class="mb-3 justify-content-between align-items-center">
      <h3>{{ title }}</h3>
      <BInputGroup>
        <BButton :pressed="activeViewMode === 'text'" @click="setViewMode('text')"
          ><font-awesome-icon icon="grip-lines"
        /></BButton>
        <BButton
          :pressed="Boolean(activeViewMode === 'image-list')"
          @click="setViewMode('image-list')"
          ><font-awesome-icon icon="list"
        /></BButton>
        <BButton :pressed="activeViewMode === 'image'" @click="setViewMode('image')"
          ><font-awesome-icon icon="image"
        /></BButton>
        <BFormRating
          v-model="activeImageSize"
          :stars="5"
          inline
          class="size-selector"
          :class="{
            'show-size-selector': activeViewMode === 'image',
            'hide-size-selector': activeViewMode !== 'image',
          }"
        >
          <template #default="{ starIndex, isFilled }">
            <IFa7SolidImage
              v-if="isFilled"
              @click="activeImageSize = starIndex"
              :style="{ fontSize: '' + (0.5 + starIndex / 5) + 'rem' }"
            />
            <IFa7RegularImage
              v-else
              @click="activeImageSize = starIndex"
              :style="{ fontSize: '' + (0.5 + starIndex / 5) + 'rem' }"
            />
          </template>
        </BFormRating>
      </BInputGroup>
    </BRow>
    <div
      class="list-group"
      :class="{
        'list-group-items': activeViewMode === 'text' || activeViewMode === 'image-list',
        'list-group-panels': activeViewMode === 'image',
      }"
    >
      <div
        v-for="item in items"
        :key="item.tag_uuid"
        :class="{
          'list-group-item list-group-item-action':
            activeViewMode === 'text' || activeViewMode === 'image-list',
          'list-group-panel': activeViewMode === 'image',
        }"
        @click="selectItem(item)"
      >
        <template v-if="activeViewMode === 'text'">
          <h5 class="mb-1">{{ item.short_name }}</h5>
          <p class="mb-1">{{ item.description }}</p>
        </template>
        <template v-if="activeViewMode === 'image-list'">
          <BRow>
            <BCol class="col-1 thumbnail-container">
              <div
                class="img-wrapper"
                :data-img-id="item.tag_uuid"
                ref="el => observeImage(el, item.tag_uuid)"
              >
                <!-- placeholder shown while image not loaded -->
                <div
                  v-if="!loadedImages[item.tag_uuid] && !erroredImages[item.tag_uuid]"
                  class="img-placeholder"
                >
                  <img
                    src="@/assets/placeholder.png"
                    class="thumbnail placeholder-img"
                    alt="Image placeholder"
                  />
                </div>

                <!-- only create real <img> when loadRequested is true to avoid immediate heavy decoding -->
                <img
                  v-if="loadRequested[item.tag_uuid] && item.images?.length"
                  :src="item.images[0]"
                  class="thumbnail real-image"
                  :class="{
                    'img-visible': loadedImages[item.tag_uuid],
                    'img-hidden': erroredImages[item.tag_uuid],
                  }"
                  alt="Image Thumbnail"
                  loading="lazy"
                  decoding="async"
                  @load="onImageLoad(item.tag_uuid)"
                  @error="onImageError(item.tag_uuid)"
                />

                <img
                  v-else-if="!item.images?.length"
                  src="@/assets/placeholder.png"
                  class="thumbnail"
                  alt="Image Thumbnail"
                />
              </div>
            </BCol>
            <BCol col-11>
              <h5 class="mb-1">{{ item.short_name }}</h5>
              <p class="mb-1">{{ item.description }}</p>
            </BCol>
          </BRow>
        </template>

        <template v-if="activeViewMode === 'image'">
          <div
            class="d-flex flex-column align-items-center m-2 flex-column-reverse panel-sized"
            :class="`panel-size-${activeImageSize}`"
          >
            <div class="panel-title text-center">
              {{
                item.short_name.substring(0, 10 * activeImageSize) +
                (item.short_name.length > 10 * activeImageSize ? '...' : '')
              }}
            </div>

            <div class="thumbnail-container thumbnail-lg" v-if="activeViewMode === 'image'">
              <div v-if="item.images.length > 1" class="panel-controls">
                <BButton
                  class="panel-controls-prev"
                  @click.stop="
                    () => {
                      if (!imageIndices[item.tag_uuid]) {
                        imageIndices[item.tag_uuid] = 0
                      }
                      imageIndices[item.tag_uuid] =
                        (imageIndices[item.tag_uuid] + 1) % item.images.length
                    }
                  "
                >
                  <font-awesome-icon icon="arrow-left" />
                </BButton>
                <BButton
                  class="panel-controls-next"
                  @click.stop="
                    () => {
                      if (!imageIndices[item.tag_uuid]) {
                        imageIndices[item.tag_uuid] = 0
                      }
                      imageIndices[item.tag_uuid] =
                        (imageIndices[item.tag_uuid] - 1 + item.images.length) % item.images.length
                    }
                  "
                >
                  <font-awesome-icon icon="arrow-right" />
                </BButton>
              </div>
              <div
                class="img-wrapper"
                :data-img-id="item.tag_uuid"
                ref="el => observeImage(el, item.tag_uuid)"
              >
                <div
                  v-if="!loadedImages[item.tag_uuid] && !erroredImages[item.tag_uuid]"
                  class="img-placeholder"
                >
                  <img
                    src="@/assets/placeholder.png"
                    class="thumbnail placeholder-img"
                    alt="Image placeholder"
                  />
                </div>

                <img
                  v-if="loadRequested[item.tag_uuid] && item.images?.length"
                  :src="item.images[imageIndices[item.tag_uuid] || 0]"
                  class="thumbnail real-image"
                  :class="{
                    'img-visible': loadedImages[item.tag_uuid],
                    'img-hidden': erroredImages[item.tag_uuid],
                  }"
                  alt="Image Thumbnail"
                  loading="lazy"
                  decoding="async"
                  @load="onImageLoad(item.tag_uuid)"
                  @error="onImageError(item.tag_uuid)"
                />

                <img
                  v-else-if="!item.images?.length"
                  src="@/assets/placeholder.png"
                  class="thumbnail"
                  alt="Image Thumbnail"
                />
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineEmits, defineProps, ref, watch, nextTick, onUnmounted, onMounted } from 'vue'
import type { PropType } from 'vue'
import type { components } from '@/interfaces/api-types'

type Item = components['schemas']['Item']

// Props
const props = defineProps({
  items: {
    type: Array as PropType<Item[]>,
    required: true,
  },
  title: {
    type: String,
    default: 'Item List',
  },
  viewMode: {
    type: String as PropType<'text' | 'image-list' | 'image'>,
    default: 'image-list',
  },
  imageSize: {
    type: Number,
    default: 3,
  },
})

const activeViewMode = ref<'text' | 'image-list' | 'image'>(props.viewMode)
const activeImageSize = ref<number>(props.imageSize)
const imageIndices = ref<{ [key: string]: number }>({})
const loadedImages = ref<Record<string, boolean>>({})
const erroredImages = ref<Record<string, boolean>>({})
const loadRequested = ref<Record<string, boolean>>({})

// Minimal deferred-loading: scan visible wrappers and request load for those in viewport.
// Other images are excluded from the DOM with v-if.
const scanVisibleImages = (margin = 200) => {
  document.querySelectorAll('.img-wrapper').forEach((el) => {
    const id = (el as HTMLElement).dataset.imgId
    if (!id || loadRequested.value[id]) return
    const rect = (el as HTMLElement).getBoundingClientRect()
    if (rect.top < window.innerHeight + margin && rect.bottom > -margin) {
      loadRequested.value[id] = true
    }
  })
}

const onScrollOrResize = () => scanVisibleImages()

watch(
  () => activeViewMode.value,
  (newMode) => {
    if (newMode !== props.viewMode) {
      unloadAllImages()
      emit('update:viewMode', newMode)
    }

    if (newMode === 'image' || newMode === 'image-list') {
      nextTick(() => {
        scanVisibleImages()
        window.addEventListener('scroll', onScrollOrResize, { passive: true })
        window.addEventListener('resize', onScrollOrResize)
      })
    } else {
      window.removeEventListener('scroll', onScrollOrResize)
      window.removeEventListener('resize', onScrollOrResize)
      unloadAllImages()
    }
  },
)

watch(
  () => activeImageSize.value,
  (newImageSize) => {
    emit('update:imageSize', newImageSize)
  },
)

const onImageLoad = (id?: string) => {
  if (!id) return
  loadedImages.value[id] = true
  erroredImages.value[id] = false
}

const onImageError = (id?: string) => {
  if (!id) return
  erroredImages.value[id] = true
  loadedImages.value[id] = false
}

onMounted(() => {
  if (activeViewMode.value === 'image' || activeViewMode.value === 'image-list') {
    scanVisibleImages()
    window.addEventListener('scroll', onScrollOrResize, { passive: true })
    window.addEventListener('resize', onScrollOrResize)
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScrollOrResize)
  window.removeEventListener('resize', onScrollOrResize)
  unloadAllImages()
})

// Unload helpers: remove requested/loaded/error flags so the real <img> is removed
const unloadAllImages = () => {
  Object.keys(loadRequested.value).forEach((k) => delete loadRequested.value[k])
  Object.keys(loadedImages.value).forEach((k) => delete loadedImages.value[k])
  Object.keys(erroredImages.value).forEach((k) => delete erroredImages.value[k])
}

// Watchers
watch(
  () => props.viewMode,
  (newMode) => {
    activeViewMode.value = newMode
  },
)

// Emits
const emit = defineEmits<{
  (event: 'select', item: Item): void
  (event: 'update:viewMode', mode: 'text' | 'image-list' | 'image'): void
  (event: 'update:imageSize', size: number): void
}>()

// Methods
const selectItem = (item: Item) => {
  unloadAllImages()
  emit('select', item)
}

const setViewMode = (mode: 'text' | 'image-list' | 'image') => {
  activeViewMode.value = mode
  emit('update:viewMode', mode)
  console.log(`View mode set to: ${mode}`)
}
</script>

<style scoped>
.container {
  margin-top: 20px;
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

.list-group-items {
  display: flex;
  flex-direction: column;
}
.list-group-panels {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: center;
}
.list-group-panel {
  &:hover {
    cursor: pointer;
    .thumbnail {
      transform: scale(1.05);
      transition: transform 0.2s;
    }
    .panel-title {
      background-color: var(--color-bg-hover);
      transform: translateY(-0.1rem);
      transition:
        transform 0.2s,
        background-color 0.2s;
    }
  }
}

.panel-title {
  width: 100%;
  padding-top: 0.3rem;
  transform: translateY(-0.3rem);
  background-color: var(--color-bg-light);
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.size-selector {
  cursor: pointer;
  margin: 0;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: unset;
  transform: scaleX(0);
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
  --panel-size: 5vw;
}
.panel-size-2 {
  --panel-size: 12vw;
}
.panel-size-3 {
  --panel-size: 20vw;
}
.panel-size-4 {
  --panel-size: 23vw;
}
.panel-size-5 {
  --panel-size: 50vw;
}

.show-size-selector {
  transform-origin: left;
  transform: scaleX(1);
  transition: transform 0.1s ease-in-out;
}
.hide-size-selector {
  transform-origin: left;
  transform: scaleX(0);
  transition: transform 0.1s ease-in-out;
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
  filter: blur(3px);
}
.real-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 180ms ease-in-out;
  opacity: 0;
}
.real-image.img-visible {
  opacity: 1;
}
.real-image.img-hidden {
  display: none;
}
</style>
