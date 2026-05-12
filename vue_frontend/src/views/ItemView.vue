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
            <ContainerListComponent v-if="item?.id" :itemId="'' + item?.id" @update:value="handleContainerSelect" />
            <button @click="() => (showModal = true)" class="btn btn-primary my-3" data-testid="add-content-button">
              Add content now
            </button>
            <ItemListContainer v-if="item?.id" :settingsId="'item-view-container'"
              :query="{ filters: [{ field: 'container_id', value: item.id }] }" @select="handleItemSelect"
              :title="`Items in ${item?.short_name}`" />
          </BTab>
          <BTab title="Item Data" id="itemData" data-testid="item-data">
            <button v-if="identification" @click="() => (isComparing = !isComparing)" class="btn btn-secondary mb-3">
              Toggle Comparison
            </button>
            <ItemCompare v-if="isComparing && identification && item" :item_org="item" :item_new="identification"
              :newItem="newItem" @submit="handleFormSubmit" :key="item?.id" />
            <ItemForm v-else :item="item" :isNewItem="newItem" @submit="handleFormSubmit" @delete="deleteItem" />
          </BTab>
          <BTab v-if="clientStore.backend_config?.llm_enabled" title="Object Identification" id="objectIdentification"
            data-testid="object-identification">
            <LLMIdentification :images="item?.images || []"
              :description="item?.short_name || item?.description ? (item?.short_name + '; ' + item?.description) : ''"
              :key="item?.id" />
          </BTab>
        </BTabs>
      </template>
      <ItemError v-else />
    </BCol>
    <SearchModal v-if="showModal" :show="showModal" @close="closeModal" @select="handleContentSelect" />
  </BContainer>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import eventBus from '../stores/eventBus'
import { type Events } from '../stores/eventBus'
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
const ItemError = defineAsyncComponent(() => import('@/components/ItemError.vue'))

type SearchQuery = components['schemas']['Query']
type ItemUpdate = components['schemas']['ItemUpdate']


/*
Use Cases:
1. When navigating to /items/new, the component should display an empty form for creating a new item. 
   If query parameters for code_format and code_value are provided, they should pre-fill the corresponding fields in the form.
2. When navigating to /items/:id, the component should fetch and display the item data for the given id.
3. If the item is not found (404) and there are parameters for code_format and code_value, it should display an empty form with a message indicating that the item was not found, allowing the user to create a new item like 2.
4. If the item is not found (404) and there are no parameters for code_format and code_value, it should display a new component "ItemError" with a button to navigate to items/new

Component Lifecycle and Logic:

- On mount, the component checks if the route parameter 'id' is 'new' to determine if it's creating a new item or editing an existing one.
  It then fetches the item data if it's an existing item, and sets up the query parameters for navigation.
- The component listens to events from the event bus, particularly for identification results and redirects, to update the view accordingly.
- The component provides methods to handle form submission for creating/updating items, selecting items from the container tree, 
  and navigating to previous/next items based on search queries.
- The component uses watchers to react to changes in route parameters and query parameters to fetch data and update the view as needed.   
*/


// Reactive State
const route = useRoute()
const router = useRouter()
const itemId = ref<number | undefined>(typeof route.params.id === 'string' ? +route.params.id : undefined)
const item = ref<Item>({} as Item)
const newItem = ref(false)
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

// Stores
const clientStore = useClientStore()

// Methods
const applyQueryParamsToItem = () => {
  const code = route.query.code as string | undefined
  if (code && item.value) {
    item.value.code = code
  }
}

const fetchItem = async () => {
  const hasCodeParams = !!(route.query.code)
  try {
    if (!itemId.value || isNaN(itemId.value)) {
      throw new Error('Invalid item ID')
    }
    const data = await ApiService.getItem(itemId.value as number)
    item.value = data
    newItem.value = false
    isComparing.value = false
    itemNotFound.value = false
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      if (hasCodeParams) {
        // Case 3: item not found but code params present → pre-filled new item form
        newItem.value = true
        item.value = {} as Item
        applyQueryParamsToItem()
        errorMessage.value = 'Item not found. You can create a new item below.'
        isComparing.value = false
      } else {
        // Case 4: item not found, no code params → show error component
        itemNotFound.value = true
      }
    } else {
      item.value = { id: itemId.value } as Item
      console.error('Error fetching item:', error)
    }
  }
  // for testing comparison view
  // identification.value = item.value
  // isComparing.value = true
  tabCheck.value++
}

const fetchPrevNextItems = async () => {
  previousItemId.value = undefined
  nextItemId.value = undefined
  if (!query.value) return
  const prevRequest = offset.value > 0 ? axios
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

const handleFormSubmit = async (formData: ItemUpdate) => {
  errorMessage.value = ''
  try {
    isComparing.value = false
    const requestData = buildItemRequest(formData)
    console.log('Request data:', requestData)
    if (newItem.value) {
      await ApiService.createItem(requestData as Item).then(res =>
        router.push(`/items/${res.id}`)
      )
      successMessage.value = 'Item created successfully'
      setTimeout(() => {
        successMessage.value = ''
      }, 5000)
    } else {
      await ApiService.updateItem(itemId.value as number, requestData as ItemUpdate)
      successMessage.value = 'Item updated successfully'
      setTimeout(() => {
        successMessage.value = ''
      }, 5000)
    }
    fetchItem()
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

const buildItemRequest = (formData: ItemUpdate): Item | ItemUpdate => {
  // Transform the formData into the format expected by the API
  return {
    ...formData,
  }
}

const handleIdentification = (result: { data: { response: object } }) => {
  if (result?.data?.response) {
    identification.value = result.data.response as Item
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
    return;
  }
  try {
    const selectedItem = await ApiService.getItem(id)
    selectedItem.container_id = itemId.value
    selectedItem.container_name = item.value?.short_name

    await ApiService.updateItem(id, selectedItem as ItemUpdate)
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
  query.value = route.query.query ? JSON.parse(decodeURIComponent((route.query.query as string) || '')) : undefined
  offset.value = query.value?.offset || 0
  console.log('Mounted with query:', query.value, 'and offset:', offset.value, route.params)
  if (route.params.id === 'new' || Number.isNaN(Number(route.params.id))) {
    // Case 1: new item form, optionally pre-filled from query params
    newItem.value = true
    applyQueryParamsToItem()
  } else {
    // Cases 2, 3, 4: fetch existing item (handles 404 scenarios internally)
    fetchItem()
  }

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
    if (_newId === 'new' || (typeof _newId === 'string' && Number.isNaN(Number(_newId)))) {
      newItem.value = true
      itemId.value = undefined
      item.value = {} as Item
      identification.value = undefined
      isComparing.value = false
      applyQueryParamsToItem()
      return
    }
    if (!Number.isNaN(_newId) && itemId.value !== Number(_newId)) {
      itemId.value = Number(_newId)
      item.value = {} as Item
      identification.value = undefined
      newItem.value = false
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
  () => tabCheck.value,
  () => {
    if (isComparing.value) {
      activeTab.value = 'itemData'
    } else if (newItem.value && clientStore.backend_config.llm_enabled) {
      activeTab.value = 'objectIdentification'
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
