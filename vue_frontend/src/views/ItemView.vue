<script setup lang="ts">
import LLMCompletion from '@/components/LLMCompletion.vue';
import ItemForm from '../components/ItemForm.vue';

import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const itemId = ref(route.params.tag_uuid);
const item = ref({});
const newItem = ref(false);

const fetchItem = async () => {
  try {
    const response = await axios.get(`/items/${itemId.value}`);
    item.value = response.data;
    newItem.value = false;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response && error.response.status === 404) {
      newItem.value = true;
      item.value = {tag_uuid: itemId.value};
      console.warn('Item not found, display empty item form');
    } else {
      console.error('Error fetching item:', error);
    }
  }
};

onMounted(fetchItem);

watch(() => route.params.tag_uuid, async (newId) => {
  itemId.value = newId;
  await fetchItem();
});

const handleFormSubmit = async (formData: Record<string, never>) => {
  try {
    if (newItem.value) {
      await axios.post('/items/', formData);
      alert('Item created successfully');
    } else {
      await axios.put(`/items/${itemId.value}`, formData);
      alert('Item updated successfully');
    }
    fetchItem();
  } catch (error) {
    console.error('Error submitting form:', error);
  }
};
</script>

<template>
  <main>
    <LLMCompletion/>
    <ItemForm :item="item" :newItem="newItem" @submit="handleFormSubmit" />
  </main>
</template>
