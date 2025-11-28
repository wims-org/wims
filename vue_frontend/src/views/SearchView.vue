<template>
  <main>
    <h1>Search</h1>
    <SearchComponent @select="handleSelect" />
  </main>
</template>

<script setup lang="ts">
import SearchComponent from '../components/shared/SearchComponent.vue'
import { useRouter } from 'vue-router'
import type { components } from '@/interfaces/api-types'
type SearchQuery = components['schemas']['SearchQuery'] & { [key: string]: unknown }
const router = useRouter()

const handleSelect = (tag: string, query: SearchQuery | null, offset: number | null) => {
  console.log('Selected tag:', tag)
  router.push(`/items/${tag}` + (query ? `?query=${encodeURIComponent(JSON.stringify(query))}&offset=${offset}` : ''))
}
</script>