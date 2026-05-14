<template>
  <BContainer fluid data-testid="item-view">
    <BCol class="p-0">
      <div v-if="errorMessage" class="sticky-note sticky-note-error">{{ errorMessage }}</div>
      <div v-if="successMessage" class="sticky-note sticky-note-success">{{ successMessage }}</div>
      <div class="d-flex align-items-center gap-2">
        <h1>Create New Item</h1>
        <div v-if="foundItemId" class="mb-3 align-self-end ms-3">
          <BButton variant="warning" @click="router.push(`/items/${foundItemId}`)"
            >Item Found With That Code! Go To Item

            <FontAwesomeIcon icon="arrow-right" class="ms-2" />
          </BButton>
        </div>
      </div>
      <details closed  v-if="clientStore.backend_config?.llm_enabled">
        <summary class="">Identify this item</summary>
        <LLMIdentification
          class="mt-2"
          :images="item?.images || []"
          :description="
            item?.short_name || item?.description ? item?.short_name + '; ' + item?.description : ''
          "
          :key="item?.id"
        />
      </details>
      <div class="mt-2">
        <button
          v-if="identification"
          @click="() => (isComparing = !isComparing)"
          class="btn btn-secondary mb-3"
        >
          Toggle Comparison
        </button>
        <ItemCompare
          v-if="isComparing && identification && item"
          :item_org="item"
          :item_new="identification"
          :newItem="true"
          @submit="handleFormSubmit"
          :key="item?.id"
        />
        <ItemForm v-else :item="item" :isNewItem="true" @submit="handleFormSubmit" />
      </div>
    </BCol>
  </BContainer>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import eventBus from '../stores/eventBus'
import { type Events } from '../stores/eventBus'
import { EventAction } from '@/interfaces/EventAction'
import { clientStore as useClientStore } from '@/stores/clientStore'
import type { components } from '@/interfaces/api-types'
import type { Item } from '@/interfaces/items.interface'
import ApiService from '@/services/ApiService'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

const LLMIdentification = defineAsyncComponent(() => import('@/components/LLMIdentification.vue'))
const ItemForm = defineAsyncComponent(() => import('../components/ItemForm.vue'))
const ItemCompare = defineAsyncComponent(() => import('../components/ItemComparison.vue'))

type ItemUpdate = components['schemas']['ItemUpdate']

/*
Use Cases:
1. When navigating to /items/new, the component should display an empty form for creating a new item. 
   If query parameters for code_format and code_value are provided, they should pre-fill the corresponding fields in the form.
2. If there are parameters for code_format and code_value, it should search for an item with that id and suggest a forward

Component Lifecycle and Logic:

- The component listens to events from the event bus, particularly for identification results and redirects, to update the view accordingly.
- The component provides methods to handle form submission for creating/updating items, selecting items from the container tree, 
  and navigating to previous/next items based on search queries.
- The component uses watchers to react to changes in route parameters and query parameters to fetch data and update the view as needed.   
*/

// Reactive State
const route = useRoute()
const router = useRouter()
const item = ref<Item>({} as Item)
const isComparing = ref(false)
const identification = ref<Item>()
const errorMessage = ref('')
const successMessage = ref('')
const foundItemId = ref<number | null>(null)

// Stores
const clientStore = useClientStore()

const searchItemWithCode = async (code: string, format?: string) => {
  try {
    const response = await ApiService.searchItems({
      filters: [{ field: 'code', value: code }],
      limit: 1,
    })
    if (response.length > 0) {
      foundItemId.value = response[0].id
    } else {
      errorMessage.value = 'No item found with the provided code.'
    }
  } catch (error) {
    errorMessage.value = 'Error searching for item. Please try again.'
    console.error('Search error:', error)
  }
}

const handleFormSubmit = async (formData: ItemUpdate) => {
  errorMessage.value = ''
  try {
    isComparing.value = false
    const requestData = buildItemRequest(formData)
    await ApiService.createItem(requestData as Item).then((res) => router.push(`/items/${res.id}`))
    successMessage.value = 'Item created successfully'
    setTimeout(() => {
      successMessage.value = ''
    }, 5000)
  } catch (error) {
    errorMessage.value = 'Could not save changes. Please try again.'
    console.error('Error submitting form:', error)
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
}

// Lifecycle Hooks
onMounted(() => {})

eventBus.on(EventAction.IDENTIFICATION, (data: Events[EventAction.IDENTIFICATION]) => {
  if (data) {
    handleIdentification(data)
  }
})

const setCodeAndFormat = async (code: string, format?: string) => {
  item.value.code = code
  item.value.code_format = format
  await searchItemWithCode(code, format)
}

watch(
  () => [route.query.code, route.query.format],
  ([code, format]) => {
    if (typeof code === 'string') {
      setCodeAndFormat(code, typeof format === 'string' ? format : undefined)
    } else {
      foundItemId.value = null
    }
  },
  { immediate: true },
)
</script>

<style scoped></style>
