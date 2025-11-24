<template>
  <div class="mt-3">
    <div v-if="loading" class="pill">
      <font-awesome-icon icon="spinner" spin />
      Loading...
    </div>
    <div v-else>
      <div class="flex-row">
        <template v-if="containerChain.length > 0">
          <template v-for="(item, index) in containerChain" :key="item.tag_uuid">
            <router-link :to="`/items/${item.tag_uuid}`" class="pill mr-2">
              {{ item.short_name }}
            </router-link>
            <font-awesome-icon
              v-if="index < containerChain.length - 1"
              icon="chevron-right"
              class="mr-2"
            />
          </template>
        </template>
        <template v-else>
          <span
            class="pill pill-placeholder"
            @click="showSearchModal = true"
            data-testid="container-placeholder"
          >
            No container assigned (click to select)
          </span>
        </template>
      </div>
      <div v-if="error" class="error mt-2">
        {{ error }}
      </div>
    </div>
    <SearchModal
      :show="showSearchModal"
      @close="showSearchModal = false"
      @select="handleContainerSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import type { ItemContainers } from '@/interfaces/items.interface'
import SearchModal from '@/components/shared/SearchModal.vue'

interface ContainerItem {
  tag_uuid: string
  short_name: string
}

const props = defineProps<{
  itemId: string | null
}>()

const emit = defineEmits<{
  (e: 'update:value', value: string): void
}>()

const loading = ref(true)
const containerChain = ref<ContainerItem[]>([])
const error = ref<string | null>(null)
const showSearchModal = ref(false)

const fetchContainerChain = async () => {
  loading.value = true
  error.value = null
  containerChain.value = []
  if (!props.itemId || typeof props.itemId !== 'string') {
    containerChain.value = []
    return
  }
  try {
    const { data } = await axios.get<ItemContainers>(`/items/${props.itemId}/containers`)
    const flattenContainers = (item: ItemContainers | null): ContainerItem[] => {
      const result: ContainerItem[] = []
      while (item && item.container) {
        item = item.container
        if (item) {
          result.unshift({
            tag_uuid: item.tag_uuid,
            short_name: item.short_name,
          })
        }
      }
      return result
    }
    if (!data || !data.container) {
      containerChain.value = []
    } else {
      containerChain.value = flattenContainers(data)
    }
  } catch (err) {
    console.error('Error fetching container chain:', err)
    error.value = 'Failed to load container chain.'
  } finally {
    loading.value = false
  }
}

const handleContainerSelect = async (tag: string) => {
  showSearchModal.value = false
  if (tag && tag !== '') {
    emit('update:value', tag)
    loading.value = true
  }
}

onMounted(fetchContainerChain)
watch(() => props.itemId, fetchContainerChain)
</script>

<style scoped>
.pill {
  display: inline-block;
  background: var(--hover-bg);
  color: var(--primary-text-color);
  border-radius: 14px;
  padding: 0.4em 1em;
  text-decoration: none;
  font-weight: 500;
  transition: background 0.2s;
}
.pill:hover {
  background: var(--color-muted);
  cursor: pointer;
}
.pill-placeholder {
  background: var(--color-secondary);
  color: var(--color-secondary-contrast);
}
.error {
  color: var(--color-danger);
}
</style>
