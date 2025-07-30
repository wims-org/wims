<template>
  <BContainer fluid class="d-flex row">
    <BCol class="align-content-center col-1 p-0 width-1 text-end">
      <router-link
        v-show="previousItemId"
        :to="`/items/${previousItemId}?offset=${+offset - 1 || 0}&query=${encodeURIComponent(query)}`"
        class="text-decoration-none"
      >
        <font-awesome-icon icon="arrow-left" />
      </router-link>
    </BCol>
    <BCol>
      <div v-if="saveError" class="sticky-note">Error saving changes</div>
      <h1 class="m-4">{{ item?.short_name }}</h1>
      <BTabs class="mt-3" content-class="mt-3" v-model="activeTab">
        <BTab title="Container Tree" id="containerTree">
          <ContainerListComponent
            v-if="item?.tag_uuid"
            :itemId="typeof item?.tag_uuid === 'string' ? item?.tag_uuid : ''"
            @update:value="handleContainerSelect"
          />
          <ItemList
            :items="items"
            @select="handleItemSelect"
            :title="`Items in ${item?.short_name}`"
          />
          <div class="d-flex justify-content-center mt-3">
            <button
              @click="() => (showModal = true)"
              class="btn btn-primary mb-3"
              data-testid="add-content-button"
            >
              Add content now
            </button>
          </div>
        </BTab>
        <BTab title="Item Data" id="itemData">
          <button
            v-if="completion"
            @click="() => (isComparing = !isComparing)"
            class="btn btn-secondary mb-3"
          >
            Toggle Comparison
          </button>
          <ItemCompare
            v-if="isComparing && completion && item"
            :item_org="item"
            :item_new="completion"
            :newItem="newItem"
            @submit="handleFormSubmit"
          />
          <ItemForm
            v-else
            :item="item"
            :isNewItem="newItem"
            @submit="handleFormSubmit"
          />
        </BTab>
        <BTab title="Object Identification" id="objectIdentification">
          <LLMCompletion />
        </BTab>
      </BTabs>
    </BCol>
    <BCol class="align-content-center col-1 p-0">
      <router-link
        v-show="nextItemId"
        :to="`/items/${nextItemId}?offset=${+offset + 1}&query=${encodeURIComponent(query)}`"
        class="text-decoration-none"
      >
        <font-awesome-icon icon="arrow-right" />
      </router-link>
    </BCol>
    <SearchModal :show="showModal" @close="closeModal" @select="handleContentSelect" />
  </BContainer>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import eventBus from '../stores/eventBus'
import { type Events } from '../stores/eventBus'
import { EventAction } from '@/interfaces/EventAction'
import { clientStore as useClientStore } from '@/stores/clientStore'
import type { components } from '@/interfaces/api-types'
import LLMCompletion from '@/components/LLMCompletion.vue'
import ItemForm from '../components/ItemForm.vue'
import ItemCompare from '../components/ItemComparison.vue'
import ItemList from '@/components/ItemList.vue'
import ContainerListComponent from '@/components/shared/ContainerListComponent.vue'
import SearchModal from '@/components/shared/SearchModal.vue'

type Item = components['schemas']['Item'] & { [key: string]: unknown }

// Reactive State
const route = useRoute()
const itemId = ref<string>(
  typeof route.params.tag_uuid === 'string'
    ? route.params.tag_uuid
    : Array.isArray(route.params.tag_uuid)
      ? route.params.tag_uuid[0]
      : '',
)
const item = ref<Item>()
const newItem = ref(false)
const isComparing = ref(false)
const completion = ref<Item>()
const saveError = ref('')
const items = ref<Item[]>([])
const noContent = ref(false)
const showModal = ref(false)
const query = ref<string>(decodeURIComponent((route.query.query as string) || ''))
const previousItemId = ref<string>('')
const nextItemId = ref<string>('')
const offset = ref<number>(0)
const activeTab = ref<string>('itemData')
const tabCheck = ref(0)

// Stores
const clientStore = useClientStore()

// Methods
const fetchItem = async () => {
  try {
    const response = await axios.get(`/items/${itemId.value}`)
    item.value = response.data
    newItem.value = false
    isComparing.value = false
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      newItem.value = true
      item.value = { tag_uuid: itemId.value } as Item
      console.warn('Item not found, display empty item form')
    } else {
      item.value = { tag_uuid: itemId.value } as Item
      console.error('Error fetching item:', error)
    }
  }
  // for testing comparison view
  // completion.value = item.value
  // isComparing.value = true
  tabCheck.value++
}

const fetchContainerContent = async () => {
  try {
    const response = await axios.get(`/items/${itemId.value}/content`)
    if (Array.isArray(response.data) && response.data.length > 0) {
      items.value = response.data as Item[]
      noContent.value = false
    } else {
      items.value = []
      noContent.value = true
    }
  } catch {
    noContent.value = true
    items.value = []
  }
  tabCheck.value++
}

const fetchPrevNextItems = async () => {
  previousItemId.value = ''
  nextItemId.value = ''
  const parsedQuery = JSON.parse(query.value.trim().toLowerCase())
  try {
    if (offset.value > 0) {
      const prevItem = await axios.post('/items/search', {
        query: parsedQuery,
        offset: offset.value - 1,
        limit: 1,
      })
      if (prevItem.data.length > 0) {
        previousItemId.value = (prevItem.data.pop() as Item).tag_uuid
      }
    }
    const nextItem = await axios.post('/items/search', {
      query: parsedQuery,
      offset: offset.value + 1,
      limit: 1,
    })
    if (nextItem.data.length > 0) {
      nextItemId.value = (nextItem.data.pop() as Item).tag_uuid
    }
  } catch (error) {
    console.error('Error fetching previous/next items:', error)
  }
}

const handleFormSubmit = async (formData: Record<string, unknown>) => {
  saveError.value = ''
  try {
    isComparing.value = false
    if (newItem.value) {
      await axios.post('/items', formData)
      alert('Item created successfully')
    } else {
      await axios.put(`/items/${itemId.value}`, formData)
      alert('Item updated successfully')
    }
    fetchItem()
  } catch (error) {
    saveError.value = 'Could not save changes. Please try again.'
    console.error('Error submitting form:', error)
  }
  tabCheck.value++
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
  clientStore.expected_event_action = EventAction.REDIRECT
  eventBus.emit(EventAction.REDIRECT, { rfid: item.tag_uuid } as Events[EventAction.REDIRECT])
}

const handleContentSelect = async (tag: string) => {
  try {
    const selectedItem = await axios.get(`/items/${tag}`)
    selectedItem.data['container_tag_uuid'] = itemId.value
    selectedItem.data['container_name'] = item.value?.short_name

    await axios.put(`/items/${tag}`, selectedItem.data)
  } catch (error) {
    saveError.value = 'Could not save changes. Please try again.'
    console.error(error)
  } finally {
    fetchContainerContent()
  }
}

const handleContainerSelect = (tag: string) => {
  if (!item.value) return
  item.value.container_tag_uuid = tag
}

const closeModal = () => {
  showModal.value = false
  clientStore.expected_event_action = EventAction.REDIRECT
}

// Lifecycle Hooks
onMounted(fetchItem)
onMounted(fetchContainerContent)
onMounted(() => {
  query.value = decodeURIComponent((route.query.query as string) || '')
  offset.value = parseInt(route.query.offset as string, 10) || 0
  if (query.value) {
    fetchPrevNextItems()
  } else {
    previousItemId.value = ''
    nextItemId.value = ''
  }
})

eventBus.on(EventAction.COMPLETION, (data: Events[EventAction.COMPLETION]) => {
  if (data) {
    handleCompletion(data)
  }
})

// Watchers
watch(
  () => route.params.tag_uuid,
  async (newId) => {
    if (itemId.value !== newId) {
      itemId.value = typeof newId === 'string' ? newId : ''
      await fetchItem()
      await fetchContainerContent()
      await fetchPrevNextItems()
    }
  },
)

watch(
  () => [route.query.query, route.query.offset],
  async ([newQuery, newOffset]) => {
    if (newQuery && typeof newQuery === 'string') {
      query.value = decodeURIComponent(newQuery || '')
      offset.value = parseInt(newOffset as string, 10) || 0
      await fetchPrevNextItems()
    } else {
      query.value = ''
      previousItemId.value = ''
      nextItemId.value = ''
    }
  },
)

watch(
  () => tabCheck.value,
  () => {
    if (isComparing.value) {
      activeTab.value = 'itemData'
    } else if (newItem.value) {
      activeTab.value = 'objectIdentification'
    } else if (items.value.length > 0) {
      activeTab.value = 'containerTree'
    } else {
      activeTab.value = 'itemData'
    }
  },
)
</script>

<style scoped>
.sticky-note {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  background-color: red;
  color: white;
  padding: 0 20px;
  border-radius: 8px;
  font-weight: bold;
  z-index: 1000;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);
}
</style>
