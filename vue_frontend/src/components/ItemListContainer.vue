<template>
  <BCol class="my-4" v-infinite-scroll="[onLoadMore, { distance: 10, canLoadMore: () => canLoadMore }]">
    <div v-if="!items.length && canLoadMore" class="d-flex justify-content-center">
      <BSpinner />
    </div>
    <ItemList :title="title" v-if="items.length" :items="items" @select="handleSelect"
      @update:view-mode="updateViewMode" @update:imageSize="updateImageSize" :view-mode="activeViewMode"
      :image-size="activeImageSize" />
    <div v-if="!canLoadMore" class="text-center mt-2">No more items to load</div>
  </BCol>
</template>

<script setup lang="ts">
import { onMounted, ref, type PropType } from 'vue'
import { vInfiniteScroll } from '@vueuse/components'
import axios from 'axios'
import ItemList from '@/components/ItemList.vue'
import type { components } from '@/interfaces/api-types'
import { useRouter } from 'vue-router'
import { watch } from 'vue'
const router = useRouter()

type SearchQuery = components['schemas']['SearchQuery'] & { [key: string]: unknown }
type Item = components['schemas']['Item'] & { [key: string]: unknown }

// Props
const props = defineProps({
  title: {
    type: String,
    default: 'Item List',
  },
  settingsId: {
    type: String,
  },
  viewMode: {
    type: String as PropType<'text' | 'image-list' | 'image'>,
    default: 'image-list',
  },
  imageSize: {
    type: Number,
    default: 3,
  },
  query: {
    type: Object as PropType<SearchQuery>,
    default: null,
  },
})

const items = ref<Item[]>([])
const searchQuery = ref<SearchQuery | null>(props.query)
const currentRoute = ref<string>(router.currentRoute.value.fullPath as string)

const loading = ref(false)
const batchSize = 10
const offset = ref(0)
const canLoadMore = ref(true)

onMounted(async () => {
  activeViewMode.value =
    (localStorage.getItem('home.itemListViewMode') as
      | 'text'
      | 'image-list'
      | 'image'
      | undefined) || 'image-list'
  activeImageSize.value = parseInt(
    localStorage.getItem(`${props.settingsId}.itemListImageSize`) || '3',
  )
})

const fetchBatch = async (offset: number) => {
  try {
    console.debug('Fetching items with query:', searchQuery.value, 'offset:', offset)
    searchQuery.value = {
      states: ['latest'],
      ...props.query,
      limit: batchSize,
      offset: offset,
    }
    const response = await axios.post('/items/search', searchQuery.value)
    console.log('Fetched items batch with names:', response.data.map((item: Item) => item.short_name))
    const data = Array.isArray(response.data) ? response.data : []
    items.value = items.value.concat(data)
    canLoadMore.value = data.length === batchSize
    return true
  } catch (err) {
    console.error('Error fetching items batch', err)
    canLoadMore.value = false
    return false
  }
}

const onLoadMore = async () => {
  if (!canLoadMore.value) return
  loading.value = true
  await fetchBatch(offset.value).then(() => {
    offset.value += batchSize
  }).finally(() => {
    loading.value = false
  })
}

const activeViewMode = ref<'text' | 'image-list' | 'image' | undefined>('text')
const updateViewMode = (newMode: string) => {
  localStorage.setItem('home.itemListViewMode', newMode)
}

const activeImageSize = ref<number>(3)
const updateImageSize = (newSize: number) => {
  localStorage.setItem('home.itemListImageSize', newSize.toString())
}

// Watchers
watch(
  () => router.currentRoute.value,
  async (newRoute) => {
    if (newRoute.fullPath !== currentRoute.value) {
      currentRoute.value = newRoute.name as string
      items.value = []
      canLoadMore.value = true
    }
  },
)

const handleSelect = (item: { tag_uuid: string }) => {
  const tag = item.tag_uuid
  const offset = items.value.findIndex((i) => i.tag_uuid === tag)
  console.log('Selected tag:', tag)
  router.push(
    `/items/${tag}` +
    (searchQuery.value
      ? `?query=${encodeURIComponent(JSON.stringify(searchQuery.value))}&offset=${offset}`
      : ''),
  )
}
</script>
