<script setup lang="ts">
import { ref, watch } from 'vue';
import axios from 'axios';
import ItemList from '../components/ItemList.vue';

const searchQuery = ref('');
const items = ref([]);
let debounceTimeout: ReturnType<typeof setTimeout>;

const fetchItems = async (query: string) => {
    try {
        const response = await axios.get(`/items`, {
            params: { query }
        });
        items.value = response.data;
    } catch (error) {
        console.error('Error fetching items:', error);
    }
};

watch(searchQuery, (newQuery) => {
    clearTimeout(debounceTimeout);
    if (newQuery) {
        debounceTimeout = setTimeout(() => {
            fetchItems(newQuery);
        }, 300); // Adjust the debounce delay as needed
    } else {
        items.value = [];
    }
});
</script>

<template>
    <main>
        <h1>Search</h1>
        <input type="text" placeholder="Search..." v-model="searchQuery" />
        <ItemList :items="items" />
    </main>
</template>