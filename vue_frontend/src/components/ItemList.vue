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
      </BInputGroup>
    </BRow>
    <div class="list-group">
      <div
        v-for="item in items"
        :key="item.tag_uuid"
        class="list-group-item list-group-item-action"
        @click="selectItem(item)"
      >
        <template v-if="activeViewMode === 'text'">
          <h5 class="mb-1">{{ item.short_name }}</h5>
          <p class="mb-1">{{ item.description }}</p>
        </template>
        <template v-if="activeViewMode === 'image-list'">
          <BRow>
            <BCol class="col-1 thumbnail-container">
              <img
                v-if="item.images?.length"
                :src="item.images[0]"
                class="thumbnail"
                alt="Image Thumbnail"
              />
            </BCol>
            <BCol col-11>
              <h5 class="mb-1">{{ item.short_name }}</h5>
              <p class="mb-1">{{ item.description }}</p>
            </BCol>
          </BRow>
        </template>
        <template v-if="activeViewMode === 'image' && item.images?.length">
          <div class="thumbnail-container" v-if="activeViewMode === 'image' && item.images?.length">
            <img :src="item.images[0]" class="thumbnail" alt="Image Thumbnail" />
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineEmits, defineProps, ref, watch } from 'vue'
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
})

const activeViewMode = ref<'text' | 'image-list' | 'image'>(props.viewMode)

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
}>()

// Methods
const selectItem = (item: Item) => {
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

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>
