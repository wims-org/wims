<template>
  <div>
    <input ref="searchInput" type="text" placeholder="Search..." v-model="searchQuery" />
    <div v-if="items.length === 0 && !noResults" class="list-group-item">
      <div class="spinner-border spinner-border-sm" role="status"></div>
      Start typing...
    </div>
    <ItemList v-else :items="items" @select="handleSelect" />
    <div v-if="items.length === 0 && noResults" class="list-group-item">
      <div class="alert alert-warning" role="alert">No results found.</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, defineEmits } from 'vue'
import axios from 'axios'
import ItemList from '@/components/ItemList.vue'
import { useTemplateRef } from 'vue'

const searchQuery = ref('')
const items = ref([])
const noResults = ref(false)
let debounceTimeout: ReturnType<typeof setTimeout>

const searchInput = useTemplateRef('searchInput')

onMounted(() => {
  searchInput.value?.focus()
})

const fetchItems = async (query: string) => {
  try {
    const response = await axios.get(`/items`, {
      params: { query },
    })
    // Check if response is array
    if (Array.isArray(response.data) && response.data.length > 0) {
      items.value = response.data as never
      noResults.value = false
    } else {
      // nothing found
      items.value = []
      noResults.value = true
    }
  } catch (error) {
    console.error('Error fetching items:', error)
  }
}

watch(searchQuery, (newQuery: string) => {
  clearTimeout(debounceTimeout)
  if (newQuery) {
    debounceTimeout = setTimeout(() => {
      fetchItems(newQuery)
    }, 300) // Adjust the debounce delay as needed
  } else {
    items.value = []
  }
})

const emit = defineEmits(['select'])

const handleSelect = (item: Record<string, unknown>) => {
  emit('select', item.tag_uuid)
}
</script>
