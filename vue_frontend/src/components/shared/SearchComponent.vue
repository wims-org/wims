<template>
  <BContainer>
    <BRow align-v="center">
      <BCol>
        <BInputGroup class="borderless-input flex-nowrap">
          <BButton
            :disabled="!searchQuery.trim()"
            @click="fetchSearchTerm(searchQuery)"
            title="Add items"
          >
            <font-awesome-icon icon="fa-solid fa-magnifying-glass" />
          </BButton>
          <BInput
            v-if="!selectedSavedQuery"
            ref="searchInput"
            type="text"
            placeholder="Search..."
            v-model="searchQuery"
          />
          <BInput v-else disabled class="secondary" type="text" v-model="selectedSavedQuery.name" />
          <BButton v-if="selectedSavedQuery" @click="selectedSavedQuery = null" title="Add items">
            <font-awesome-icon icon="fa-solid fa-xmark" />
          </BButton>
          <BDropdown class="mt-2" end @show="fetchQueries()" v-b-color-mode="'dark'">
            <BDropdownItem v-for="query in queries" :key="query._id" @click="selectQuery(query)"
              >{{ query.name }}
            </BDropdownItem>
            <BDropdownDivider />
            <BDropdownItem @click="isEditing = !isEditing">
              <font-awesome-icon :icon="isEditing ? 'xmark' : 'pen-to-square'" />
              {{ isEditing ? 'Close' : 'Add / Edit Query' }}
            </BDropdownItem>
          </BDropdown>
        </BInputGroup>
      </BCol>
    </BRow>
    <BRow class="mt-2">
      <BCol>
        <QueryEditor
          v-if="isEditing"
          :existingQuery="selectedSavedQuery"
          @update:query="selectQuery($event)"
        />
      </BCol>
    </BRow>
    <BRow align-v="center">
      <BCol align-h="center" class="mt-3">
        <div
          v-if="items.length === 0 && !noResults"
          class="d-flex align-items-center justify-content-center"
        >
          <div class="spinner-border spinner-border-sm me-2" role="status"></div>
          Start typing...
        </div>
        <ItemList v-else :items="items" @select="handleSelect" />
        <div v-if="items.length === 0 && noResults" class="list-group-item">
          <div class="alert alert-warning" role="alert">No results found.</div>
        </div>
      </BCol>
    </BRow>
  </BContainer>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, defineEmits } from 'vue'
import axios from 'axios'
import ItemList from '@/components/ItemList.vue'
import { useTemplateRef } from 'vue'
import QueryEditor from '@/components/shared/QueryEditor.vue'
import type { Query } from '@/interfaces/queries'
import type { components } from '@/interfaces/api-types'
type Item = components['schemas']['Item'] & { [key: string]: unknown }
type SearchQuery = components['schemas']['SearchQuery'] & { [key: string]: unknown }

const searchQuery = ref('')
const searchedQuery = ref<Record<string, unknown>>({})
const items = ref<Item[]>([])
const noResults = ref(false)
const isEditing = ref(false)
let debounceTimeout: ReturnType<typeof setTimeout>
const selectedSavedQuery = ref<Query | null>(null)
const queries = ref<Query[]>([
  {
    _id: 'query3',
    name: 'Query 3',
    query: { tag_uuid: '123e4567-e89b-12d3-a456-426614174000' },
    description: null,
    created_at: null,
    updated_at: null,
  },
])

const searchInput = useTemplateRef('searchInput')

onMounted(() => {
  searchInput.value?.focus()
  fetchQueries()
})

const fetchSearchTerm = async (term: string) => {
  await axios.post('/items/search', { term }).then((response) => {
    items.value = response.data
    noResults.value = items.value.length === 0
  })
  searchedQuery.value = { term }
}

const fetchSearchQuery = async (query: SearchQuery) => {
  await axios.post('/items/search', { query }).then((response) => {
    items.value = response.data
    noResults.value = items.value.length === 0
  })
  searchedQuery.value = query
}


const fetchQueries = async () => {
  try {
    const response = await axios.get('/queries')
    queries.value = response.data as Query[]
  } catch (error) {
    console.error('Error fetching queries:', error)
  }
}

watch(searchQuery, (newQuery: string) => {
  clearTimeout(debounceTimeout)
  if (newQuery) {
    debounceTimeout = setTimeout(() => {
      if (!selectedSavedQuery.value) {
        fetchSearchTerm(newQuery)
      }
    }, 300)
  } else {
    items.value = []
  }
})

const emit = defineEmits(['select'])

const selectQuery = (query: Query) => {
  selectedSavedQuery.value = query
  fetchSearchQuery(query.query as SearchQuery)
}

const handleSelect = (item: Item) => {
  emit('select', item.tag_uuid, searchedQuery.value || null, items.value.indexOf(item))
}
</script>
