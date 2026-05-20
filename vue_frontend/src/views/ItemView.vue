<template>
  <BContainer fluid data-testid="item-view">
    <router-link v-show="previousItemId"
      :to="`/items/${previousItemId}?query=${encodeURIComponent(JSON.stringify({ ...query, offset: offset - 1 }))}`"
      class="text-decoration-none arrow-button arrow-button-prev">
      <IFaArrowLeft />
    </router-link>
    <router-link v-show="nextItemId"
      :to="`/items/${nextItemId}?query=${encodeURIComponent(JSON.stringify({ ...query, offset: offset + 1 }))}`"
      class="text-decoration-none arrow-button arrow-button-next">
      <IFaArrowRight />
    </router-link>
    <BCol class="p-0">
      <div v-if="errorMessage" class="sticky-note sticky-note-error">{{ errorMessage }}</div>
      <div v-if="successMessage" class="sticky-note sticky-note-success">{{ successMessage }}</div>
      <template v-if="!itemNotFound">
        <h1>{{ item?.short_name }}</h1>
        <BTabs class="mt-3" content-class="mt-3" v-model="activeTab" data-testid="item-tabs">
          <BTab title="Container Tree" id="containerTree" data-testid="item-container-tree">
            <ContainerListComponent v-if="item?.id" :itemId="item?.id" @update:value="handleContainerSelect" />
            <button @click="() => (showModal = true)" class="btn btn-primary my-3" data-testid="add-content-button">
              Add content now
            </button>
            <ItemListContainer ref="containerContentListRef" v-if="item?.id" :settingsId="'item-view-container'"
              :query="{ filters: [{ field: 'container_id', value: item.id }] }" @select="handleItemSelect"
              :title="`Items in ${item?.short_name}`" />
          </BTab>
          <BTab title="Item Data" id="itemData" data-testid="item-data">
            <details closed class="mb-1" v-if="clientStore.backend_config?.llm_enabled">
              <summary>Identify this item</summary>
              <LLMIdentification class="mt-2 mb-2" :images="item?.images || []" :description="item?.short_name
                ? item?.short_name + (item?.description ? '; ' + item?.description : '')
                : ''
                " :key="item?.id" />
            </details>
            <button v-if="identification" @click="() => (isComparing = !isComparing)" class="btn btn-secondary mb-3">
              Toggle Comparison
            </button>
            <ItemCompare v-if="isComparing && identification && item" :item_org="item" :item_new="identification"
              :newItem="false" @submit="handleFormSubmit" :key="item?.id" />
            <ItemForm v-else :item="item" :isNewItem="false" @submit="handleFormSubmit" @delete="deleteItem" />
          </BTab>
        </BTabs>
      </template>
    </BCol>
    <SearchModal :show="showModal" @close="closeModal" @select="handleContentSelect" />
  </BContainer>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref, onMounted, onUnmounted, watch, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import eventBus from '@/stores/eventBus'
import { type Events } from '@/stores/eventBus'
import { EventAction } from '@/interfaces/EventAction'
import { clientStore as useClientStore } from '@/stores/clientStore'
import type { components } from '@/interfaces/api-types'
import type { Item } from '@/interfaces/items.interface'
import ApiService from '@/services/ApiService'

const LLMIdentification = defineAsyncComponent(() => import('@/components/LLMIdentification.vue'))
const ItemForm = defineAsyncComponent(() => import('../components/ItemForm.vue'))
const ItemCompare = defineAsyncComponent(() => import('../components/ItemComparison.vue'))
const ContainerListComponent = defineAsyncComponent(
  () => import('@/components/shared/ContainerListComponent.vue'),
)
const SearchModal = defineAsyncComponent(() => import('@/components/shared/SearchModal.vue'))

type SearchQuery = components['schemas']['Query']
type ItemPublic = components['schemas']['ItemPublic']


/*
Use Cases:
1. When navigating to /items/:id, the component should fetch and display the item data for the given id.
2. If the item is not found (404) the user should be forwarded to the /items/new view with the code and format pre-filled if they were provided as query parameters.

Component Lifecycle and Logic:

- The component listens to events from the event bus, particularly for identification results and redirects, to update the view accordingly.
- The component provides methods to handle form submission for creating/updating items, selecting items from the container tree, 
  and navigating to previous/next items based on search queries.
- The component uses watchers to react to changes in route parameters and query parameters to fetch data and update the view as needed.   
*/

// Reactive State
const route = useRoute()
const router = useRouter()
const itemId = ref<number | undefined>(
  typeof route.params.id === 'string' ? +route.params.id : undefined,
)
const item = ref<Item>({} as Item)
const isComparing = ref(false)
const identification = ref<Item>()
const errorMessage = ref('')
const successMessage = ref('')
const items = ref<Item[]>([])
const showModal = ref(false)
const query = ref<SearchQuery | undefined>(undefined)
const previousItemId = ref<number | undefined>(undefined)
const nextItemId = ref<number | undefined>(undefined)
const offset = ref<number>(0)
const activeTab = ref<string>('itemData')
const tabCheck = ref(0)
const itemNotFound = ref(false)
const containerContentListRef = useTemplateRef('containerContentListRef')
// Stores
const clientStore = useClientStore()

const fetchItem = async () => {
  try {
    if (!itemId.value || isNaN(itemId.value)) {
      throw new Error('Invalid item ID')
    }
    const data = await ApiService.getItem(itemId.value as number)
    item.value = data
    isComparing.value = false
    itemNotFound.value = false
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      router.push(
        `/items/new?${route.query ? new URLSearchParams(route.query as Record<string, string>).toString() : ''}`,
      )
    } else {
      item.value = { id: itemId.value } as Item
      console.error('Error fetching item:', error)
    }
  }
  // for testing comparison view
  // identification.value = item.value
  // isComparing.value = true
}

const fetchPrevNextItems = async () => {
  previousItemId.value = undefined
  nextItemId.value = undefined
  if (!query.value) return
  const prevRequest =
    offset.value > 0
      ? axios
        .post('/items/search', {
          ...query.value,
          offset: offset.value - 1,
          limit: 1,
        })
        .catch(() => null)
      : Promise.resolve(null)

  const nextRequest = axios
    .post('/items/search', {
      ...query.value,
      offset: offset.value + 1,
      limit: 1,
    })
    .catch(() => null)

  const [prevItem, nextItem] = await Promise.all([prevRequest, nextRequest])

  if (prevItem?.data?.length) {
    previousItemId.value = (prevItem.data.pop() as Item).id
  }
  if (nextItem?.data?.length) {
    nextItemId.value = (nextItem.data.pop() as Item).id
  }
}

const handleFormSubmit = async (formData: Item) => {
  errorMessage.value = ''
  try {
    isComparing.value = false
    await ApiService.updateItem(itemId.value as number, formData).then(fetchItem)
    successMessage.value = 'Item updated successfully'
    setTimeout(() => {
      successMessage.value = ''
    }, 5000)
  } catch (error) {
    errorMessage.value = 'Could not save changes. Please try again.'
    console.error('Error submitting form:', error)
  }
  tabCheck.value++
}

const deleteItem = async (id: number) => {
  errorMessage.value = ''
  try {
    await ApiService.deleteItem(id)
    successMessage.value = 'Item deleted successfully'
    setTimeout(() => {
      successMessage.value = ''
    }, 5000)
    router.push('/items/new')
  } catch (error) {
    errorMessage.value = 'Could not delete item. Please try again.'
    console.error('Error deleting item:', error)
  }
}

const handleIdentification = (result: { data: { response: object } }) => {
  if (result?.data?.response) {
    identification.value = ApiService.itemPublicToItem(result.data.response as ItemPublic)
    isComparing.value = true
  } else {
    isComparing.value = false
  }
  tabCheck.value++
}

const handleItemSelect = (item: Item) => {
  const id = item.id
  console.log('Selected item with id:', id)
  const offset = items.value.findIndex((i) => i.id === item.id)
  const query = {
    filters: {
      container_id: itemId.value,
    },
  }
  router.push(
    `/items/${id}` +
    (query ? `?query=${encodeURIComponent(JSON.stringify({ ...query, offset }))}` : ''),
  )
}

const handleContentSelect = async (id: number | undefined) => {
  if (!id) {
    return
  }
  try {
    const selectedItem = await ApiService.getItem(id)
    selectedItem.container_id = itemId.value
    selectedItem.container_name = item.value?.short_name
    await ApiService.updateItem(id, selectedItem)
  } catch (error) {
    errorMessage.value = 'Could not save changes. Please try again.'
    console.error(error)
  }
}

const handleContainerSelect = (tag: number) => {
  if (!item.value) return
  item.value.container_id = tag
}

const closeModal = () => {
  showModal.value = false
  clientStore.expected_event_action = EventAction.REDIRECT
}

const handle_item_prev = () => {
  if (previousItemId.value) {
    router.push(
      `/items/${previousItemId.value}?query=${encodeURIComponent(JSON.stringify({ ...query.value, offset: offset.value - 1 }))}`,
    )
  }
}

const handle_item_next = () => {
  if (nextItemId.value) {
    router.push(
      `/items/${nextItemId.value}?query=${encodeURIComponent(JSON.stringify({ ...query.value, offset: offset.value + 1 }))}`,
    )
  }
}

// Lifecycle Hooks
onMounted(() => {
  query.value = route.query.query
    ? JSON.parse(decodeURIComponent((route.query.query as string) || ''))
    : undefined
  offset.value = query.value?.offset || 0
  console.log('Mounted with query:', query.value, 'and offset:', offset.value, route.params)
  eventBus.on(EventAction.ELEMENT_UPDATE_ITEM, (data) => data.id === itemId.value && fetchItem())
  eventBus.on(
    EventAction.ELEMENT_UPDATE_CONTAINER,
    (data) => data.id === item.value?.id && containerContentListRef.value?.reloadResults(),
  )
  fetchItem().then(() => {
    tabCheck.value++
  })

  if (query.value) {
    fetchPrevNextItems()
  }
  // Keyboard navigation: left/right arrows navigate prev/next item.
  const onKeyDown = (e: KeyboardEvent) => {
    // Ignore inputs
    const target = e.target as HTMLElement | null
    if (target) {
      const tag = target.tagName
      if (
        tag === 'INPUT' ||
        tag === 'TEXTAREA' ||
        (target.isContentEditable && target.isContentEditable === true)
      ) {
        return
      }
    }
    if (e.key === 'ArrowLeft') {
      e.preventDefault()
      handle_item_prev()
    } else if (e.key === 'ArrowRight') {
      e.preventDefault()
      handle_item_next()
    }
  }

  window.addEventListener('keydown', onKeyDown)

  onUnmounted(() => {
    window.removeEventListener('keydown', onKeyDown)
  })
})

onUnmounted(() => {
  eventBus.off(EventAction.ELEMENT_UPDATE_CONTAINER, fetchItem)
})
eventBus.on(EventAction.IDENTIFICATION, (data: Events[EventAction.IDENTIFICATION]) => {
  if (data) {
    handleIdentification(data)
  }
})

// Watchers
watch(
  () => route.params.id,
  async (_newId) => {
    itemNotFound.value = false
    errorMessage.value = ''

    items.value = []

    if (!Number.isNaN(_newId) && itemId.value !== Number(_newId)) {
      itemId.value = Number(_newId)
      item.value = {} as Item
      identification.value = undefined
      isComparing.value = false
      await fetchItem()
      await fetchPrevNextItems()
    }
  },
)

watch(
  () => [route.query.query],
  async ([newQuery]) => {
    console.log('Updated query:', query.value, newQuery)
    if (newQuery && typeof newQuery === 'string') {
      query.value = JSON.parse(decodeURIComponent(newQuery || ''))
      offset.value = query.value?.offset || 0
      await fetchPrevNextItems()
    } else {
      query.value = {} as SearchQuery
      previousItemId.value = undefined
      nextItemId.value = undefined
    }
  },
)

watch(
  () => [route.query.code, route.query.format],
  async ([code, newFormat]) => {
    console.log('new values ', code, newFormat)
    if (item.value !== undefined && (typeof code === 'string' || typeof code === 'number')) {
      item.value.code = code
      // item.value.code_format = typeof newFormat === 'string' ? newFormat : undefined // ToDo define formats and codes
    } else {
      item.value.code = null
    }
  },
)

watch(

  // TODO FIX DEFAULT TAB

  () => tabCheck.value,
  () => {
    if (isComparing.value) {
      activeTab.value = 'itemData'
    } else if (item.value?.is_container) {
      activeTab.value = 'containerTree'
    } else {
      activeTab.value = 'itemData'
    }
  },
)
</script>

<style scoped>
.arrow-button {
  font-size: 1.5rem;
  position: fixed;
  bottom: 1.5rem;
  z-index: 50;
  padding: 0.5rem;

  &:hover {
    background-color: unset;
  }
}

.arrow-button-prev {
  left: calc(50% - 2.5rem);
}

.arrow-button-next {
  left: calc(50% + 0.5rem);
}
</style>
