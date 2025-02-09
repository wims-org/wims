<template>
    <div>
        <input ref="searchInput" type="text" placeholder="Search..." v-model="searchQuery" />
        <div v-if="items.length === 0" class="list-group-item">
            <div class="spinner-border spinner-border-sm" role="status"></div>
            Start typing...
        </div>
        <ItemList v-else :items="items" @select="handleSelect" />
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, defineEmits } from 'vue'
import axios from 'axios'
import ItemList from './ItemList.vue'
import { useTemplateRef } from 'vue'

const searchQuery = ref('')
const items = ref([])
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
        items.value = response.data
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