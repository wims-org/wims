<template>
  <BContainer class="search-input">
    <div
      class="form-group d-flex align-items-center justify-content-between flex-wrap p-2"
      data-testid="text-field" >
      <span v-if="!hideLabel || !label" :for="name">{{ label }}</span>
      <div>
        <input
          v-model="searchTerm"
          type="text"
          class="form-control"
          :placeholder="!disabled ? 'Search...' : 'No Value'"
          :disabled="disabled"
          :name="name"
          :required="required"
          :class="[{ 'is-invalid': required && !searchTerm }, { 'borderless-input': borderless }]"
          @focus="expanded = true"
          @blur="closeDropdown()"
        />
        <ul v-if="!disabled && expanded && dropdownOptions.length" class="dropdown-menu show">
          <li v-for="option in dropdownOptions" :key="option.id">
            <a class="dropdown-item" href="#" @click="selectOption(option)">
              {{ option.display_string }}
            </a>
          </li>
        </ul>
      </div>
    </div>
  </BContainer>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import axios from 'axios'
import { SearchType, SearchTypeEndpoint } from '@/interfaces/FormField.interface'

import type { components } from '@/interfaces/api-types'
type User = components['schemas']['User'] & { [key: string]: unknown }
type Item = components['schemas']['Item'] & { [key: string]: unknown }
type Query = components['schemas']['Query'] & { [key: string]: unknown }

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
  type: {
    type: String,
    default: 'text',
  },
  value: {
    type: String,
    default: '',
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
const searchTerm = ref('')
const dropdownOptions = ref<searchResult[]>([])
const expanded = ref(false)
const emit = defineEmits<{
  (e: 'update:value', value: User | Item | Query | string): void
}>()
const debounceTimeout = ref<NodeJS.Timeout | null>(null)
const minLength = 3 // Minimum length for search term
const selection = ref(false)

const fetchSearchResults = async (term: string) => {
  try {
    const response = await axios.get(SearchTypeEndpoint[props.searchType], {
      params: { term },
    })
    dropdownOptions.value = getOptionsAndSelectorsFromSearchTypeQueryResult(response.data) || []
  } catch (error) {
    console.error('Error fetching search results:', error)
    dropdownOptions.value = []
  }
}
watch(
  () => props.value,
  (newValue) => {
    if (!newValue) {
      searchTerm.value = ''
      return
    }
    getSearchTermFromValue(newValue).then((result) => {
      selection.value = true
      searchTerm.value = result
      setTimeout(() => {
        selection.value = false
      }, 300)
    })
  },
)

watch(searchTerm, (newTerm) => {
  if (debounceTimeout.value) {
    clearTimeout(debounceTimeout.value)
  }
  if (!props.disabled && newTerm.length >= minLength && !selection.value) {
    debounceTimeout.value = setTimeout(() => {
      fetchSearchResults(newTerm).then(() => {
        expanded.value = dropdownOptions.value.length > 0
      })
    }, 300)
  } else {
    dropdownOptions.value = []
  }
})

const selectOption = (option: searchResult) => {
  selection.value = true
  console.log('Selected option:', option)
  searchTerm.value = option.display_string
  expanded.value = false
  emit('update:value', option.select)
  setTimeout(() => {
    selection.value = false
  }, 300)
}

interface searchResult {
  id: string
  display_string: string
  select: User | Item | Query | string
}

const closeDropdown = () => {
  // defer @blur to register the click before the dropdown closes... this is fucked up, i know
  setTimeout(() => {
    expanded.value = false
  }, 300)
}

const getOptionsAndSelectorsFromSearchTypeQueryResult = (result: unknown): searchResult[] => {
  const options: searchResult[] = []
  if (props.searchType === SearchType.USER) {
    options.push(
      ...(result as User[]).map((user) => ({
        id: user._id,
        display_string: user.username + (user.email ? ` <${user.email}>` : ''),
        select: user._id,
      })),
    )
  } else if (props.searchType === SearchType.ITEM) {
    return (result as Item[]).map(
      (item) => ({ id: item.tag_uuid, display_string: item.name, select: item }) as searchResult,
    )
  } else if (props.searchType === SearchType.QUERY) {
    return (result as Query[]).map(
      (query) => ({ id: query.name, display_string: query.name, select: query }) as searchResult,
    )
  }

  return options
}

const getSearchTermFromValue = (value: string) => {
  return new Promise<string>((resolve) => {
    switch (props.searchType) {
      case SearchType.USER:
        return axios.get(`/users/${value}`).then((response) => {
          resolve(response.data.username)
        })
        break
      case SearchType.ITEM:
        return axios.get(`/items/${value}`).then((response) => {
          resolve(response.data.name)
        })
        break
      case SearchType.QUERY:
        return axios.get(`/queries/${value}`).then((response) => {
          resolve(response.data.name)
        })
        break
      default:
        resolve('')
    }
  })
}
</script>
