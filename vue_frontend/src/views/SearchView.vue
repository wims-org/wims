<template>
  <main>
    <h1>Search</h1>
    <SearchComponent @select="handleSelect" />
  </main>
</template>

<script setup lang="ts">
import SearchComponent from '../components/shared/SearchComponent.vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const handleSelect = (tag: string, query: Record<string, unknown> | null, offset: number | null) => {
  console.log('Selected tag:', tag)
  router.push(`/items/${tag}` + (query ? `?query=${encodeURIComponent(JSON.stringify(query))}` : '') + (offset !== null ? `&offset=${offset}` : ''))
}
</script>