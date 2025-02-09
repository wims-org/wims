<template>
  <main>
    <h1>Search</h1>
    <SearchComponent @select="handleSelect" />
  </main>
</template>

<script setup lang="ts">
import SearchComponent from '../components/SearchComponent.vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const handleSelect = (tag: string) => {
  console.log('Selected tag:', tag)
  

  router.push(`/item/${tag}`)
  // Add your logic to handle the selected tag
}
</script>