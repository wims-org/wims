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
      <ItemList title="Recent Items" v-if="items.length" :items="items" @select="handleSelect" />
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

const handleSelect = (item: { tag_uuid: string }) => {
  const tag = item.tag_uuid
  console.log('Selected tag:', tag)
  router.push(
    `/items/${tag}` + (query.value ? `?query=${encodeURIComponent(JSON.stringify(query.value))}` : ''),
  )
}
</script>
