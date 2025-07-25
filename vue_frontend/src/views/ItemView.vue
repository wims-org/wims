<template>
  <main>
    <div v-if="saveError" class="sticky-note">Error saving changes</div>
    <h1 class="m-4">{{ item?.short_name }}</h1>
    <b-tabs class="mt-3" content-class="mt-3" @activate-tab="(e) => console.log(e)">
      <b-tab title="Container Tree" :active="activeTab == 'containerTree'">
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
      </b-tab>
      <b-tab title="Item Data" :active="activeTab == 'itemData'">
        <button v-if="completion"
          @click="() => (isComparing = !isComparing)"
          class="btn btn-secondary mb-3"
        >
          Toggle Comparison
        </button>
        <ItemCompare
          v-if="isComparing"
          :item_org="item"
          :item_new="completion"
          :newItem="newItem"
          @submit="handleFormSubmit"
        />
        <ItemForm v-else :item="item" :isNewItem="newItem" @submit="handleFormSubmit" />
      </b-tab>
      <b-tab title="Object detection" :active="activeTab == 'objectDetection'">
        <LLMCompletion />
      </b-tab>
    </b-tabs>

    <SearchModal :show="showModal" @close="closeModal" @select="handleContentSelect" />
  </main>
</template>

<script setup lang="ts">
import LLMCompletion from '@/components/LLMCompletion.vue'
import ItemForm from '../components/ItemForm.vue'
import ItemCompare from '../components/ItemComparison.vue'
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import eventBus from '../stores/eventBus'
import { type Events } from '../stores/eventBus'
import { EventAction } from '@/interfaces/EventAction'
import { clientStore as useClientStore } from '@/stores/clientStore'
import ItemList from '@/components/ItemList.vue'
import type { components } from '@/interfaces/api-types'
type Item = components['schemas']['Item'] & { [key: string]: unknown }
import ContainerListComponent from '@/components/shared/ContainerListComponent.vue'
import SearchModal from '@/components/shared/SearchModal.vue'

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

const clientStore = useClientStore()
const activeTab = ref<string>('itemData')
const tabCheck = ref(0)

eventBus.on(EventAction.COMPLETION, (data: Events[EventAction.COMPLETION]) => {
  if (data) {
    handleCompletion(data)
  }
})

const fetchItem = async () => {
  try {
    const response = await axios.get(`/items/${itemId.value}`)
    item.value = response.data
    newItem.value = false
    isComparing.value = false
  } catch (error) {
    if (axios.isAxiosError(error) && error.response && error.response.status === 404) {
      newItem.value = true
      item.value = { tag_uuid: itemId.value } as Item
      console.warn('Item not found, display empty item form')
    } else {
      item.value = { tag_uuid: itemId.value } as Item
      console.error('Error fetching item:', error)
    }
  }
  tabCheck.value++
}

const fetchContainerContent = async () => {
  try {
    const response = await axios.get(`/items/${itemId.value}/content`)
    // Check if response is array
    if (Array.isArray(response.data) && response.data.length > 0) {
      items.value = response.data as Item[]
      noContent.value = false
    } else {
      // nothing found
      items.value = []
      noContent.value = true
    }
  } catch {
    noContent.value = true
    items.value = []
  }
  tabCheck.value++
}

onMounted(fetchItem)
onMounted(fetchContainerContent)

watch(
  () => route.params.tag_uuid,
  async (newId) => {
    if (itemId.value !== newId) {
      itemId.value = typeof newId === 'string' ? newId : ''
      await fetchItem()
      await fetchContainerContent()
    }
  },
)

watch(
  () => tabCheck.value,
  () => {
    if (isComparing.value) {
      activeTab.value = 'itemData'
    } else if (newItem.value) {
      activeTab.value = 'objectDetection'
    } else if (items.value?.length > 0) {
      activeTab.value = 'containerTree'
    } else {
      activeTab.value = 'itemData'
    }

    console.log(
      'Active tab changed to:',
      activeTab.value,
      'isComparing:',
      isComparing.value,
      'newItem:',
      newItem.value,
      'items length:',
      items.value.length,
    )
  },
)

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
  if (result && result.data && result.data.response) {
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
