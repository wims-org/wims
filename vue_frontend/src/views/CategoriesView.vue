<template>
  <div>
    <h1>Categories</h1>

    <CategoryTreeView :categories="categories" :selectable="true" @add-child="fetchCategories" />
  </div>
</template>

<script setup lang="ts">
import axios from 'axios'
import { onMounted, ref } from 'vue'
import type { components } from '@/interfaces/api-types'

type Categories = components['schemas']['CategoryReqRes'][]

const categories = ref<Categories>([])

const fetchCategories = async () => {
  axios
    .get('/categories/tree')
    .then((response) => {
      console.log('Categories fetched:', response.data)
      categories.value = response.data
    })
    .catch((error) => {
      console.error('Error fetching categories:', error)
    })
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped></style>
