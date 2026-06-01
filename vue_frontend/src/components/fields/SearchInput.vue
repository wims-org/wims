<template>
  <BContainer class="search-input">
    <div class="form-group d-flex align-items-center justify-content-between flex-wrap p-2" data-testid="text-field">
      <span v-if="!hideLabel && label" :for="name">{{ label }}</span>
      <div class="d-flex align-items-center gap-1 px-2  ms-auto">
        <BButton v-if="nfcSearch && clientStore().getNFCCapability" class=" primary p-1 me-2" variant="success"
          size="sm" @click="readNFC">
          <IMaterialSymbolsNfc v-if="!showNFCModal" class="nfc-icon" />
          <BSpinner v-else class="nfc-icon" animation="border" size="sm" />
        </BButton>
        <BButton v-if="qrSearch" class="primary p-1" variant="success" size="sm" @click="readQR">
          <IMaterialSymbolsQrCodeScanner v-if="!showQRModal" class="qr-icon" />
          <BSpinner v-else class="qr-icon" animation="border" size="sm" />
        </BButton>
      </div>
      <div class="dropdown">
        <input v-model="searchTerm" type="text" class="form-control" :placeholder="!disabled ? 'Search...' : 'No Value'"
          :disabled="disabled" :name="name" :required="required" autocomplete="off"
          :class="[{ 'is-invalid': required && !searchTerm }, { 'borderless-input': borderless }]"
          @focus="expanded = true" @blur="handleBlur" @input="handleInput" @keydown.enter.prevent="handleEnter"
          @keydown="handleKeyDown" @keydown.esc="clearSearch" />
        <ul v-if="!disabled && expanded && dropdownOptions.length" class="dropdown-menu dropdown-menu-end show">
          <li v-for="(option, index) in dropdownOptions" :key="option.id">
            <a class="dropdown-item" :class="{ 'selected-dropdown-item': selectedDropdownIndex === index }" href="#"
              @mousedown.prevent="selectOption(option)">
              {{ option.displayString }}
            </a>
          </li>
        </ul>
      </div>
    </div>

    <BModal v-model="showQRModal" title="Scan QR / Barcode" hide-footer centered>
      <QRReaderComp v-if="showQRModal" @scan="handleScan" />
    </BModal>

    <BModal v-model="showNFCModal" title="Scan NFC Tag" hide-footer centered>
      <NFCReaderComp v-if="showNFCModal" @scan="handleScan" />
    </BModal>
  </BContainer>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref, watch } from 'vue'
import axios from 'axios'
import { SearchType } from '@/interfaces/FormField.interface'
import type { ScanResult } from '@/interfaces/reader.interface'
import type { PropType } from 'vue'
import type { components } from '@/interfaces/api-types'
import { clientStore } from '@/stores/clientStore'
import { BModal } from 'bootstrap-vue-next'

// Lazy-loaded only when the respective modal is first opened
const QRReaderComp = defineAsyncComponent(() => import('@/components/QRReader.vue'))
const NFCReaderComp = defineAsyncComponent(() => import('@/components/NFCReader.vue'))

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
  qrSearch: {
    type: Boolean,
    default: false,
  },
  nfcSearch: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits<{
  (e: 'update:value', value: SearchResultType | null): void
  (e: 'search-term', value: string): void
}>()

const searchTerm = ref('')
const dropdownOptions = ref<SearchOption[]>([])
const expanded = ref(false)
const selectedDropdownIndex = ref<number | null>(null)
let debounceTimer: ReturnType<typeof setTimeout> | null = null
const showQRModal = ref(false)
const showNFCModal = ref(false)

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
    const { data } = await axios.post<SearchResultType[]>(config.value.search, { term })
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
  selectedDropdownIndex.value = null
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
  selectedDropdownIndex.value = null
  emit('update:value', option.item)
}

const handleBlur = (): void => {
  expanded.value = false
}

const updateSelectedDropdownItem = (key: string): void => {
  if (!expanded.value || dropdownOptions.value.length === 0) return

  if (key === 'ArrowDown') {
    if (selectedDropdownIndex.value === null) {
      selectedDropdownIndex.value = 0
      return
    }
    selectedDropdownIndex.value = (selectedDropdownIndex.value + 1) % dropdownOptions.value.length
  }

  if (key === 'ArrowUp') {
    if (selectedDropdownIndex.value === null) {
      selectedDropdownIndex.value = dropdownOptions.value.length - 1
      return
    }
    selectedDropdownIndex.value =
      (selectedDropdownIndex.value - 1 + dropdownOptions.value.length) % dropdownOptions.value.length
  }

  console.log('Selected index:', selectedDropdownIndex.value)
}

const handleKeyDown = (event: KeyboardEvent): void => {
  if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
    event.preventDefault()
  }
  updateSelectedDropdownItem(event.key)
}

const handleEnter = (): void => {
  if (selectedDropdownIndex.value === null) {
    emit('search-term', searchTerm.value)
    return
  }
  const selected = dropdownOptions.value[selectedDropdownIndex.value]
  if (selected) selectOption(selected)
}

const clearSearch = (): void => {
  searchTerm.value = ''
  dropdownOptions.value = []
  expanded.value = false
  selectedDropdownIndex.value = null
  emit('update:value', null)
}

const readQR = (): void => {
  showQRModal.value = true
}

const readNFC = (): void => {
  showNFCModal.value = true
}

const handleScan = async (result: ScanResult): Promise<void> => {
  showQRModal.value = false
  showNFCModal.value = false
  await axios.post<ItemPublic[]>('/items/search', {
    filters: [{ field: 'code', qualifier: 'eq', value: result.code_value }],
    limit: 1,
  }).then(({ data }) => {
    if (data.length > 0) {
      const scannedItem = data[0]
      selectOption({
        id: scannedItem.id,
        displayString: SEARCH_CONFIG[SearchType.ITEM].getDisplayString(scannedItem),
        item: scannedItem,
      })
    }
  }).catch((e) => {
    console.error('Scan result did not match any item', e)
  })
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

.qr-icon,
.nfc-icon {
  font-size: 1.2rem;
}

.selected-dropdown-item {
  background-color: var(--bs-primary) !important;
}
</style>
