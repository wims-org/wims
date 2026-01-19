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
              @click="setImageSize(starIndex)"
              :style="{ fontSize: '' + (0.5 + starIndex / 5) + 'rem' }"
            />
            <IFa7RegularImage
              v-else
              @click="setImageSize(starIndex)"
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
        v-for="(item, i) in items"
        :key="item.tag_uuid"
        :class="{
          'list-group-item list-group-item-action':
            activeViewMode === 'text' || activeViewMode === 'image-list',
          'list-group-panel': activeViewMode === 'image',
        }"
        @click="selectItem(item, i)"
      >
        <template v-if="activeViewMode === 'text'">
          <h5 class="mb-1">{{ item.short_name }}</h5>
          <p class="mb-1">{{ item.description }}</p>
        </template>
        <template v-if="activeViewMode === 'image-list'">
          <ListItemComponent
            class="image-component"
            :data-img-id="item.tag_uuid"
            :title="item.short_name"
            :description="item.description"
            :images="item.images"
            :image-size="activeImageSize"
            :load-requested="loadRequested[item.tag_uuid]"
          />
        </template>

        <template v-if="activeViewMode === 'image'">
          <ListCardComponent
            class="image-component"
            :data-img-id="item.tag_uuid"
            :title="item.short_name"
            :images="item.images"
            :image-size="activeImageSize"
            :load-requested="loadRequested[item.tag_uuid]"
          />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onUnmounted, onMounted } from 'vue'
import type { PropType } from 'vue'
import type { components } from '@/interfaces/api-types'
import ListCardComponent from '@/components/shared/ListComponent/ListCardComponent.vue'
import ListItemComponent from '@/components/shared/ListComponent/ListItemComponent.vue'

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
const loadRequested = ref<Record<string, boolean>>({})

// Minimal deferred-loading: scan visible wrappers and request load for those in viewport.
// Other images are excluded from the DOM with v-if.
const scanVisibleImages = (margin = 200) => {
  document.querySelectorAll('.image-component').forEach((el) => {
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

    if (['image', 'image-list'].includes(newMode)) {
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

watch(
  () => props.items,
  () => {
    nextTick(() => {
      if (['image', 'image-list'].includes(activeViewMode.value)) {
        scanVisibleImages()
      }
    })
  },
)

onMounted(() => {
  if (['image', 'image-list'].includes(activeViewMode.value)) {
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
  (event: 'select', item: Item, offset: number): void
  (event: 'update:viewMode', mode: 'text' | 'image-list' | 'image'): void
  (event: 'update:imageSize', size: number): void
}>()

// Methods
const selectItem = (item: Item, index: number) => {
  emit('select', item, index)
}

const setViewMode = (mode: 'text' | 'image-list' | 'image') => {
  activeViewMode.value = mode
  emit('update:viewMode', mode)
  console.log(`View mode set to: ${mode}`)
}

const setImageSize = (size: number) => {
  activeImageSize.value = size
  setTimeout(() => {
    scanVisibleImages()
  }, 50)
  emit('update:imageSize', size)
}
</script>

<style scoped>
.container {
  margin-top: 20px;
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

.size-selector {
  cursor: pointer;
  margin: 0;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: unset;
  transform: scaleX(0);
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
