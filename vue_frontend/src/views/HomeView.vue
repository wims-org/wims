<template>
  <main>
    <h1>Home</h1>
    <ul class="list-group block-item-list">
      <li class="list-group-item" @click="$router.push('/items')">Items</li>
      <li class="list-group-item" @click="$router.push('/readers')">Readers</li>
      <li class="list-group-item" @click="$router.push('/import')">Import</li>
      <li class="list-group-item" @click="$router.push('/users')">Users</li>
    </ul>
    <BContainer class="my-4">
      <hr />
      <h3>Recent Items</h3>
      <ItemList v-if="items.length" :items="items" @select="handleSelect" />
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

type Item = components['schemas']['Item'] & { [key: string]: unknown }
const items = ref<Item[]>([])
onMounted(() => {
  fetchRecentItems()
})

const fetchRecentItems = async () => {
  try {
    const response = await axios.get('/api/items/recent')
    items.value = response.data
  } catch (error) {
    console.error('Error fetching recent items:', error)
  }
}

const handleSelect = (item: { tag_uuid: string }, query?: Record<string, unknown> | null, offset?: number | null) => {
  const tag = item.tag_uuid
  console.log('Selected tag:', tag)
  router.push(
    `/items/${tag}` +
      (query ? `?query=${encodeURIComponent(JSON.stringify(query))}` : '') +
      (offset !== null && offset !== undefined ? `&offset=${offset}` : ''),
  )
}
</script>
