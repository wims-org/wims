<script setup lang="ts">
import LLMCompletion from '@/components/LLMCompletion.vue';
import ItemForm from '../components/ItemForm.vue';

import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

const item = ref<Record<string, never>>({});
const newItem = ref(false);

const route = useRoute();
const itemId = route.params.tag_uuid; // Assuming the URL parameter is named 'id'

onMounted(async () => {
  try {
    const response = await axios.get(`/item/${itemId}`);
    item.value = response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response && error.response.status === 404) {
      newItem.value = true;
      item.value = {};
      console.warn('Item not found, display empty item form');
    } else {
      console.error('Error fetching item:', error);
    }
  }
});

const handleFormSubmit = async (formData: Record<string, never>) => {
  try {
    if (newItem.value) {
      await axios.post('/item', formData);
      alert('Item created successfully');
    } else {
      await axios.put(`/item/${itemId}`, formData);
      alert('Item updated successfully');
    }
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
