<template>
  <main>
    <h1>Home</h1>
    <ul class="list-group block-item-list" data-testid="home-nav-list">
      <li class="list-group-item" @click="$router.push('/items')">Items</li>
      <li class="list-group-item" @click="$router.push('/readers')">Readers</li>
      <li class="list-group-item" @click="$router.push('/import')">Import</li>
      <li class="list-group-item" @click="$router.push('/users')">Users</li>
    </ul>
    <BContainer class="my-4">
      <div v-if="!items.length" class="d-flex justify-content-center">
        <BSpinner />
      </div>
      <ItemList
        title="Recent Items"
        v-if="items.length"
        :items="items"
        @select="handleSelect"
        @update:view-mode="updateViewMode"
        @update:imageSize="updateImageSize"
        :view-mode="activeViewMode"
        :image-size="activeImageSize"
      />
    </BContainer>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import axios from 'axios'
import ItemList from '@/components/ItemList.vue'
import type { components } from '@/interfaces/api-types'
import { useRouter } from 'vue-router'
const router = useRouter()

type SearchQuery = components['schemas']['SearchQuery'] & { [key: string]: unknown }
type Item = components['schemas']['Item'] & { [key: string]: unknown }
const items = ref<Item[]>([])
const query = ref<SearchQuery | null>(null)

onMounted(() => {
  activeViewMode.value = localStorage.getItem('home.itemListViewMode') as "text" | "image-list" | "image" | undefined || 'image-list'
  activeImageSize.value = parseInt(localStorage.getItem('home.itemListImageSize') || '3')
  fetchRecentItems()
})

const fetchRecentItems = async () => {
  try {
    query.value = {
      states: ['latest'],
    }
    const response = await axios.post('/items/search', query.value)
    items.value = response.data
  } catch (error) {
    console.error('Error fetching latest items:', error)
  }
}

const activeViewMode = ref<"text" | "image-list" | "image" | undefined>('text')
const updateViewMode = (newMode: string) => {
  localStorage.setItem('home.itemListViewMode', newMode)
}

const activeImageSize = ref<number>(3)
const updateImageSize = (newSize: number) => {
  localStorage.setItem('home.itemListImageSize', newSize.toString())
}

const handleSelect = (item: { tag_uuid: string }) => {
  const tag = item.tag_uuid
  const offset = items.value.findIndex((i) => i.tag_uuid === tag)
  console.log('Selected tag:', tag)
  router.push(
    `/items/${tag}` +
      (query.value
        ? `?query=${encodeURIComponent(JSON.stringify(query.value))}&offset=${offset}`
        : ''),
  )
}
</script>
