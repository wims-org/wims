<template>
  <BContainer class="search-input">
    <div class="form-group d-flex align-items-center justify-content-between flex-wrap p-2" data-testid="text-field">
      <span v-if="!hideLabel && label" :for="name">{{ label }}</span>
      <div class="dropdown">
        <input
          v-model="searchTerm"
          type="text"
          class="form-control"
          :placeholder="!disabled ? 'Search...' : 'No Value'"
          :disabled="disabled"
          :name="name"
          :required="required"
          autocomplete="off"
          :class="[{ 'is-invalid': required && !searchTerm }, { 'borderless-input': borderless }]"
          @focus="expanded = true"
          @blur="handleBlur"
          @input="handleInput"
          @keydown.enter.prevent="handleEnter"
          @keydown.esc="clearSearch"
        />
        <ul v-if="!disabled && expanded && dropdownOptions.length" class="dropdown-menu dropdown-menu-end show">
          <li v-for="option in dropdownOptions" :key="option.id">
            <a class="dropdown-item" href="#" @mousedown.prevent="selectOption(option)">
              {{ option.displayString }}
            </a>
          </li>
        </ul>
      </div>
    </div>
  </BContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import axios from 'axios'
import { SearchType } from '@/interfaces/FormField.interface'
import type { PropType } from 'vue'
import type { components } from '@/interfaces/api-types'

type UserPublic = components['schemas']['UserPublic']
type ItemPublic = components['schemas']['ItemPublic']
type CategoryPublic = components['schemas']['CategoryPublic']
type SearchResultType = UserPublic | ItemPublic | CategoryPublic

interface SearchOption {
  id: number
  displayString: string
  item: SearchResultType
}

interface SearchTypeConfig {
  fetchById: (id: number) => string
  search: string
  getDisplayString: (item: SearchResultType) => string
}

const SEARCH_CONFIG: Record<SearchType, SearchTypeConfig> = {
  [SearchType.USER]: {
    fetchById: (id) => `/users/${id}`,
    search: '/users/search',
    getDisplayString: (item) => (item as UserPublic).username,
  },
  [SearchType.ITEM]: {
    fetchById: (id) => `/items/${id}`,
    search: '/items/search',
    getDisplayString: (item) => (item as ItemPublic).short_name,
  },
  [SearchType.CATEGORY]: {
    fetchById: (id) => `/categories/${id}`,
    search: '/categories/search',
    getDisplayString: (item) => (item as CategoryPublic).title,
  },
  [SearchType.QUERY]: {
    fetchById: (id) => `/items/${id}`,
    search: '/items/search',
    getDisplayString: (item) => (item as ItemPublic).short_name,
  },
}

const DEBOUNCE_MS = 300
const MIN_LENGTH = 3

const props = defineProps({
  searchType: {
    type: String as () => SearchType,
    default: SearchType.ITEM,
  },
  name: {
    type: String,
    required: true,
  },
  label: {
    type: String,
    default: '',
  },
  value: {
    type: [Number, Object] as PropType<number | SearchResultType | null>,
    default: null,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  required: {
    type: Boolean,
    default: false,
  },
  hideLabel: {
    type: Boolean,
    default: false,
  },
  borderless: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits<{
  (e: 'update:value', value: SearchResultType | null): void
}>()

const searchTerm = ref('')
const dropdownOptions = ref<SearchOption[]>([])
const expanded = ref(false)
let debounceTimer: ReturnType<typeof setTimeout> | null = null

const config = computed(() => SEARCH_CONFIG[props.searchType])

const resolveDisplayString = async (value: number | SearchResultType): Promise<string> => {
  if (typeof value === 'object') {
    return config.value.getDisplayString(value)
  }
  const { data } = await axios.get<SearchResultType>(config.value.fetchById(value))
  return config.value.getDisplayString(data)
}

const fetchSearchResults = async (term: string): Promise<void> => {
  try {
    const { data } = await axios.get<SearchResultType[]>(config.value.search, { params: { term } })
    dropdownOptions.value = data.map((item) => ({
      id: (item as { id: number }).id,
      displayString: config.value.getDisplayString(item),
      item,
    }))
  } catch {
    dropdownOptions.value = []
  }
}

watch(
  () => props.value,
  async (newValue) => {
    if (!newValue) {
      searchTerm.value = ''
      return
    }
    try {
      searchTerm.value = await resolveDisplayString(newValue)
    } catch {
      searchTerm.value = ''
    }
  },
)

onMounted(async () => {
  if (props.value) {
    try {
      searchTerm.value = await resolveDisplayString(props.value)
    } catch {
      searchTerm.value = ''
    }
  }
})

const handleInput = (): void => {
  if (debounceTimer) clearTimeout(debounceTimer)
  if (searchTerm.value.length < MIN_LENGTH) {
    dropdownOptions.value = []
    expanded.value = false
    return
  }
  debounceTimer = setTimeout(async () => {
    await fetchSearchResults(searchTerm.value)
    expanded.value = dropdownOptions.value.length > 0
  }, DEBOUNCE_MS)
}

const selectOption = (option: SearchOption): void => {
  searchTerm.value = option.displayString
  expanded.value = false
  dropdownOptions.value = []
  emit('update:value', option.item)
}

const handleBlur = (): void => {
  expanded.value = false
}

const handleEnter = (): void => {
  if (dropdownOptions.value.length > 0) {
    selectOption(dropdownOptions.value[0])
  } else {
    clearSearch()
  }
}

const clearSearch = (): void => {
  searchTerm.value = ''
  dropdownOptions.value = []
  expanded.value = false
  emit('update:value', null)
}
</script>

<style scoped>
.is-invalid {
  padding-right: 0.75rem;
}

.search-input .dropdown-menu {
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  scrollbar-width: thin;
  scrollbar-color: var(--bs-primary) var(--card-bg);
}
</style>
