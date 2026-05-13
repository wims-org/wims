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
import ItemList from '@/components/ItemList.vue'
import type { components } from '@/interfaces/api-types'
import { useRouter } from 'vue-router'
import { watch } from 'vue'
import ApiService from '@/services/ApiService'
import { preloadItemView } from '@/router'
const router = useRouter()

type Query = components['schemas']['Query'] 
type Item = components['schemas']['ItemPublic']

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
    type: Object as PropType<Query>,
    default: null,
  },
  batchSize: {
    type: Number,
    default: 10,
  },
  offset: {
    type: Number,
    default: 0,
  },
})

const items = ref<Item[]>([])
const searchQuery = ref<Query | null>(props.query)
const currentRoute = ref<string>(router.currentRoute.value.fullPath as string)

const loading = ref(false)
const batchSize = ref(props.batchSize)
const offset = ref(props.offset)
const canLoadMore = ref(true)

watch(router.currentRoute, async () => {
  items.value = []
  offset.value = props.offset || 0
  canLoadMore.value = true
})

onMounted(async () => {
  if (typeof window !== 'undefined') {
    // Warm up the ItemView route chunk so the first item click is fast.
    window.setTimeout(() => {
      preloadItemView().catch((err) => {
        console.debug('ItemView prefetch skipped:', err)
      })
    }, 0)
  }

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
      ...props.query,
      limit: batchSize.value,
      offset: offset,
    }

    const data = await ApiService.searchItems(searchQuery.value)
    items.value.push(...data)
    canLoadMore.value = data.length === batchSize.value
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
    offset.value += batchSize.value
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

const handleSelect = (item: { id: number }) => {
  const time_start = performance.now()
  const id = item.id
  const offset = items.value.findIndex((i) => i.id === id)
  console.log('Selected tag:', id)
  router.push(
    `/items/${id}` +
    (searchQuery.value
      ? `?query=${encodeURIComponent(JSON.stringify({ ...searchQuery.value, offset }))}`
      : ''),
  ).then(() => {
    const time_end = performance.now()
    console.log('Navigation successful, time taken:', time_end - time_start, 'ms')
  }).catch((err) => {
    console.error('Navigation error:', err)
  })
}
</script>
