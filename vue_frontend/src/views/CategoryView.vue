<template>
  <div>
    <div v-if="category">
      <h1 class="text-capitalize">{{ category.title }}</h1>
      <p>{{ category.description }}</p>
    </div>
    <div v-else>
      <p>Loading category...</p>
    </div>
    <ItemList
      :items="containers"
      :title="`Containers containing ${category?.title}`"
      @select="handleSelect($event.tag_uuid, containers_query, $event.offset)"
    />
    <ItemList
      :items="items"
      :title="`Items in ${category?.title}`"
      @select="handleSelect($event.tag_uuid, items_query, $event.offset)"
    />
  </div>
</template>

<script setup lang="ts">
import axios from 'axios'
import { onMounted, ref } from 'vue'
import type { components } from '@/interfaces/api-types'
import router from '@/router'
type SearchQuery = components['schemas']['SearchQuery'] & { [key: string]: unknown }

type Category = components['schemas']['CategoryReqRes']

const category = ref<Category | null>(null)
const items = ref<components['schemas']['Item'][]>([])
const containers = ref<components['schemas']['Item'][]>([])
const containers_query = ref<SearchQuery>({})
const items_query = ref<SearchQuery>({})

const fetchCategory = async (id: string): Promise<void> => {
  return axios
    .get('/categories/' + id)
    .then((response) => {
      console.log('Category fetched:', response.data)
      category.value = response.data
    })
    .catch((error) => {
      console.error('Error fetching category:', error)
    })
}

const fetchItemsByCategory = async (categoryTitle: string): Promise<void> => {
  items_query.value = { query: { item_type: { $regex: categoryTitle, $options: 'i' } } }
  return axios
    .post('/items/search', items_query.value)
    .then((response) => {
      console.log('Items fetched for category:', response.data)
      items.value = response.data
    })
    .catch((error) => {
      console.error('Error fetching items for category:', error)
    })
}

const fetchContainersForItems = async (container_tag_uuids: string[]): Promise<void> => {
  containers_query.value = { query: { tag_uuid: { $in: container_tag_uuids } } }
  return axios
    .post('/items/search', containers_query.value)
    .then((response) => {
      console.log('Containers fetched for items:', response.data)
      containers.value = response.data
    })
    .catch((error) => {
      console.error('Error fetching containers for items:', error)
    })
}

onMounted(() => {
  fetchCategory(router.currentRoute.value.params.categoryId as string).then(() => {
    fetchItemsByCategory(category.value?.title || '').then(() => {
      fetchContainersForItems(
        items.value.map((item) => item.container_tag_uuid).filter((id) => id) as string[],
      ).then(() => {
        console.log('Containers fetched for items:', containers.value)
      })
    })
  })
})

const handleSelect = (tag: string, query: SearchQuery | null, offset: number | null) => {
  console.log('Selected tag:', tag)
  router.push(
    `/items/${tag}` +
      (query ? `?query=${encodeURIComponent(JSON.stringify(query))}&offset=${offset}` : ''),
  )
}
</script>

<style scoped></style>
