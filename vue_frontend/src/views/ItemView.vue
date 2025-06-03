<template>
  <main>
      <div v-if="saveError" class="sticky-note">Error saving changes</div>

    <LLMCompletion />
    <ItemCompare
      v-if="isComparing"
      :item_org="item"
      :item_new="completion"
      :newItem="newItem"
      @submit="handleFormSubmit"
    />
    <ItemForm v-else :item="item" :newItem="newItem" @submit="handleFormSubmit" />
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

const route = useRoute()
const itemId = ref<string>(
  typeof route.params.tag_uuid === 'string'
    ? route.params.tag_uuid
    : Array.isArray(route.params.tag_uuid)
      ? route.params.tag_uuid[0]
      : '',
)
const item = ref({})
const newItem = ref(false)
const isComparing = ref(false)
const completion = ref({})
const saveError = ref('')

eventBus.on('completion', (data: Events['completion']) => {
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
      item.value = { tag_uuid: itemId.value }
      console.warn('Item not found, display empty item form')
    } else {
      item.value = { tag_uuid: itemId.value }
      console.error('Error fetching item:', error)
    }
  }
}

onMounted(fetchItem)

watch(
  () => route.params.tag_uuid,
  async (newId) => {
    if (itemId.value !== newId) {
      itemId.value = typeof newId === 'string' ? newId : ''
      await fetchItem()
    }
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
}

const handleCompletion = (result: { data: { response: object } }) => {
  if (result && result.data && result.data.response) {
    completion.value = result.data.response
    isComparing.value = true
  } else {
    isComparing.value = false
  }
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
