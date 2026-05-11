<template>
  <div>
    <div v-if="category">
      <h1 class="text-capitalize">{{ category.title }}</h1>
      <p>{{ category.description }}</p>
    </div>
    <div v-else>
      <p>Loading category...</p>
    </div>
    <CategoryTreeView :categories="category ? [category] : []" :selectable="true" :expand-all="true" />
    <ItemList :items="containers" :title="`Containers containing ${category?.title}`"
      @select="handleSelect($event.id, containers_query)" />
    <ItemList :items="items" :title="`Items in ${category?.title}`" @select="handleSelect($event.id, items_query)" />
  </div>
</template>

<script setup lang="ts">
import axios from 'axios'
import { onMounted, ref, watch } from 'vue'
import type { components } from '@/interfaces/api-types'
import router from '@/router'
import CategoryTreeView from '@/components/shared/CategoryTreeView.vue'
type SearchQuery = components['schemas']['Query'] & { [key: string]: unknown }

type Category = components['schemas']['CategoryPublic']

const category = ref<Category>()
const items = ref<components['schemas']['ItemPublic'][]>([])
const containers = ref<components['schemas']['ItemPublic'][]>([])
const containers_query = ref<SearchQuery>({})
const items_query = ref<SearchQuery>({})



watch(
  () => router.currentRoute.value.params.categoryId,
  async (newId) => {
    if (newId != null) {
      containers.value = []
      items.value = []
      category.value = undefined
      await fetchCategory(+newId as number).then(async (fetchedCategory) => {
        category.value = fetchedCategory
        await fetchItemsByCategory(fetchedCategory)
        await fetchContainersForItems(
          items.value.map((item) => item.container_id).filter((id) => id) as number[],
        )
      })
    }
  },
)

const fetchCategory = async (id: number): Promise<Category> => {
  return axios
    .get(`/categories/${id}`)
    .then((response) => {
      return response.data
    })
    .catch((error) => {
      console.error('Error fetching category:', error)
    })
}

const fetchItemsByCategory = async (category: Category): Promise<void> => {
  items_query.value = { filters: [{ field: 'category_id', qualifier: 'eq', value: category.id }] }
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

const fetchContainersForItems = async (container_ids: number[]): Promise<void> => {
  containers_query.value = { filters: [{ field: 'id', qualifier: 'in', value: container_ids }] }
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
  fetchCategory(+router.currentRoute.value.params.categoryId).then(async () => {
    await fetchItemsByCategory(category.value as Category)
    await fetchContainersForItems(
      items.value.map((item) => item.container_id).filter((id) => id) as number[]
    )
  }).catch((error) => {
    console.error('Error fetching category on mount:', error)
  })
})

const handleSelect = (id: number, query: SearchQuery | null) => {
  console.log('Selected id:', id)
  router.push(
    `/items/${id}` +
    (query ? `?query=${encodeURIComponent(JSON.stringify(query))}` : ''),
  )
}
</script>

<style scoped></style>
