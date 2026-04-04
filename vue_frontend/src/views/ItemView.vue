<template>
  <BContainer fluid class="d-flex row" data-testid="item-view">
    <BCol class="col-1 p-0 text-end">
      <router-link v-show="previousItemId"
        :to="`/items/${previousItemId}?query=${encodeURIComponent(query_param)}&offset=${offset - 1}`"
        class="text-decoration-none arrow-button">
        <IFaArrowLeft />
      </router-link>
    </BCol>
    <BCol>
      <div v-if="saveError" class="sticky-note sticky-note-error">Error saving changes</div>
      <div v-if="saveSuccess" class="sticky-note sticky-note-success">{{ saveSuccess }}</div>
      <h1 class="m-4">{{ item?.short_name }}</h1>
      <BTabs class="mt-3" content-class="mt-3" v-model="activeTab" data-testid="item-tabs">
        <BTab title="Container Tree" id="containerTree" data-testid="item-container-tree">
          <ContainerListComponent v-if="item?.id" :itemId="typeof item?.id === 'string' ? item?.id : ''"
            @update:value="handleContainerSelect" />
          <button @click="() => (showModal = true)" class="btn btn-primary my-3" data-testid="add-content-button">
            Add content now
          </button>
          <ItemListContainer :settingsId="'item-view-container'" :query="{
            query: { container_id: itemId },
          }" @select="handleItemSelect" :title="`Items in ${item?.short_name}`" />
        </BTab>
        <BTab title="Item Data" id="itemData" data-testid="item-data">
          <button v-if="completion" @click="() => (isComparing = !isComparing)" class="btn btn-secondary mb-3">
            Toggle Comparison
          </button>
          <ItemCompare v-if="isComparing && completion && item" :item_org="item" :item_new="completion"
            :newItem="newItem" @submit="handleFormSubmit" :key="item?.id" />
          <ItemForm v-else :item="item" :isNewItem="newItem" @submit="handleFormSubmit" />
        </BTab>
        <BTab v-if="clientStore.backend_config?.llm_enabled" title="Object Identification" id="objectIdentification"
          data-testid="object-identification">
          <LLMCompletion :images="item?.images || []" :key="item?.id" />
        </BTab>
      </BTabs>
    </BCol>
    <BCol class="col-1 p-0">
      <router-link v-show="nextItemId"
        :to="`/items/${nextItemId}?query=${encodeURIComponent(query_param)}&offset=${offset + 1}`"
        class="text-decoration-none arrow-button">
        <IFaArrowRight />
      </router-link>
    </BCol>
    <SearchModal :show="showModal" @close="closeModal" @select="handleContentSelect" />
  </BContainer>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import eventBus from '../stores/eventBus'
import { type Events } from '../stores/eventBus'
import { EventAction } from '@/interfaces/EventAction'
import { clientStore as useClientStore } from '@/stores/clientStore'
import type { components } from '@/interfaces/api-types'
import LLMCompletion from '@/components/LLMCompletion.vue'
import ItemForm from '../components/ItemForm.vue'
import ItemCompare from '../components/ItemComparison.vue'
import ContainerListComponent from '@/components/shared/ContainerListComponent.vue'
import SearchModal from '@/components/shared/SearchModal.vue'
import ApiService from '@/services/ApiService'

type SearchQuery = components['schemas']['SearchQuery'] & { [key: string]: unknown }
type Item = components['schemas']['ItemPublic'] & { [key: string]: unknown }
type ItemUpdate = components['schemas']['ItemUpdate'] & { [key: string]: unknown }


// Reactive State
const route = useRoute()
const router = useRouter()
const itemId = ref<number | undefined>(typeof route.params.id === 'string' ? +route.params.id : undefined)
const item = ref<Item>({} as Item)
const newItem = ref(false)
const isComparing = ref(false)
const completion = ref<Item>()
const saveError = ref('')
const saveSuccess = ref('')
const items = ref<Item[]>([])
const showModal = ref(false)
const query_param = ref<string>(decodeURIComponent((route.query.query as string) || '')) // contains query object
const previousItemId = ref<number | undefined>(undefined)
const nextItemId = ref<number | undefined>(undefined)
const offset = ref<number>(0)
const activeTab = ref<string>('itemData')
const tabCheck = ref(0)

// Stores
const clientStore = useClientStore()

// Methods
const fetchItem = async () => {
  try {
    const data = await ApiService.getItem(itemId.value as number)
    console.log('Fetched item:', data)
    item.value = data
    newItem.value = false
    isComparing.value = false
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      newItem.value = true
      item.value = {} as Item
      console.warn('Item not found, display empty item form')
    } else {
      item.value = { id: itemId.value } as Item
      console.error('Error fetching item:', error)
    }
  }
  // for testing comparison view
  // completion.value = item.value
  // isComparing.value = true
  tabCheck.value++
}

const fetchPrevNextItems = async () => {
  previousItemId.value = undefined
  nextItemId.value = undefined
  if (!query_param.value) return
  const parsedQuery: SearchQuery = JSON.parse(query_param.value.trim().toLowerCase())
  try {
    if (offset.value > 0) {
      const prevItem = await axios.post('/items/search', {
        ...parsedQuery,
        offset: offset.value - 1,
        limit: 1,
      })
      if (prevItem.data.length > 0) {
        previousItemId.value = (prevItem.data.pop() as Item).id
      }
    }
  } catch (error) {
    console.error('Error fetching previous items:', error)
  }
  try {
    const nextItem = await axios.post('/items/search', {
      ...parsedQuery,
      offset: offset.value + 1,
      limit: 1,
    })
    if (nextItem.data.length > 0) {
      nextItemId.value = (nextItem.data.pop() as Item).id
    }
  } catch {
    nextItemId.value = undefined
  }
}

const handleFormSubmit = async (formData: Record<string, unknown>) => {
  saveError.value = ''
  try {
    isComparing.value = false
    const requestData = buildItemRequest(formData)
    console.log('Request data:', requestData)
    if (newItem.value) {
      await ApiService.createItem(requestData as Item).then(res =>
        router.push(`/items/${res.data.id}`)
      )
      saveSuccess.value = 'Item created successfully'
      setTimeout(() => {
        saveSuccess.value = ''
      }, 5000)
    } else {
      await ApiService.updateItem(itemId.value as number, requestData as ItemUpdate)
      saveSuccess.value = 'Item updated successfully'
      setTimeout(() => {
        saveSuccess.value = ''
      }, 5000)
    }
    fetchItem()
  } catch (error) {
    saveError.value = 'Could not save changes. Please try again.'
    console.error('Error submitting form:', error)
  }
  tabCheck.value++
}

const buildItemRequest = (formData: Record<string, unknown>): Record<string, unknown> => {
  // Transform the formData into the format expected by the API
  return {
    ...formData,
  }
}

const handleCompletion = (result: { data: { response: object } }) => {
  if (result?.data?.response) {
    completion.value = result.data.response as Item
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
    query: {
      container_id: itemId.value,
    },
  }
  router.push(
    `/items/${id}` +
    (query ? `?query=${encodeURIComponent(JSON.stringify(query))}&offset=${offset}` : ''),
  )
}

const handleContentSelect = async (id: number | undefined) => {
  if (!id) {
    return;
  }
  try {
    const selectedItem = await ApiService.getItem(id)
    selectedItem['container_id'] = itemId.value
    selectedItem['container_name'] = item.value?.short_name

    await ApiService.updateItem(id, selectedItem)
  } catch (error) {
    saveError.value = 'Could not save changes. Please try again.'
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
      `/items/${previousItemId.value}?query=${encodeURIComponent(query_param.value)}&offset=${offset.value - 1}`,
    )
  }
}

const handle_item_next = () => {
  if (nextItemId.value) {
    router.push(
      `/items/${nextItemId.value}?query=${encodeURIComponent(query_param.value)}&offset=${offset.value + 1}`,
    )
  }
}

// Lifecycle Hooks
onMounted(() => {
  if (route.params.id !== "new") {
    fetchItem()
  } else {
    newItem.value = true;
  }
  query_param.value = decodeURIComponent((route.query.query as string) || '')
  offset.value = parseInt(route.query.offset as string, 10) || 0
  item.value.tag_uuid = route.query.rawValue as string || null


  if (query_param.value) {
    fetchPrevNextItems()
  } else {
    previousItemId.value = undefined
    nextItemId.value = undefined
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

eventBus.on(EventAction.COMPLETION, (data: Events[EventAction.COMPLETION]) => {
  if (data) {
    handleCompletion(data)
  }
})

// Watchers
watch(
  () => route.params.id,
  async (_newId) => {
    if (_newId === 'new') {
      newItem.value = true
      itemId.value = undefined
    }
    if (!Number.isNaN(_newId) && itemId.value !== Number(_newId)) {
      const newId = Number(_newId)
      itemId.value = newId
      items.value = []
      item.value = {} as Item
      completion.value = undefined
      newItem.value = false
      isComparing.value = false
      await fetchItem()
      await fetchPrevNextItems()
    }
    items.value = []
  },
)

watch(
  () => [route.query.query, route.query.offset],
  async ([newQuery, newOffset]) => {
    if (newQuery && typeof newQuery === 'string') {
      query_param.value = decodeURIComponent(newQuery || '')
      offset.value = parseInt(newOffset as string, 10) || 0
      await fetchPrevNextItems()
    } else {
      query_param.value = ''
      previousItemId.value = undefined
      nextItemId.value = undefined
    }
  },
)

watch(
  () => [route.query.rawValue, route.query.format],
  async ([newRawValue, newFormat]) => {
    console.log('new values ', newRawValue)
    if (item.value !== undefined && newRawValue && (typeof newRawValue === 'string' || typeof newRawValue === 'number')) {
      item.value.tag_uuid = newRawValue
    } else {
      query_param.value = ''
      previousItemId.value = undefined
      nextItemId.value = undefined
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
  position: fixed;
  top: 45vh;
  font-size: 1.2rem;
  transform: translateX(-50%);

  &:hover {
    background-color: unset;
  }
}
</style>
