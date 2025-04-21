<template>
  <main>
    <LLMCompletion />
    <ItemCompare
      v-if="isComparing"
      :item_org="item"
      :item_new="completion"
      :newItem="newItem"
      @submit="handleFormSubmit"
    />
    <ItemForm v-else :item="item" :newItem="newItem" @submit="handleFormSubmit" />
  </main>
</template>

<script setup lang="ts">
import LLMCompletion from '@/components/LLMCompletion.vue';
import ItemForm from '../components/ItemForm.vue';
import ItemCompare from '../components/ItemComparison.vue';
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import eventBus from '../stores/eventBus';
import { type Events } from '../stores/eventBus';

const route = useRoute();
const itemId = ref(route.params.tag_uuid);
const item = ref({});
const newItem = ref(false);
const isComparing = ref(false); // New state variable for edit mode
const completion = ref({}); // Variable to store the

eventBus.on('completion', (data: Events['completion']) => {
  if (data) {
    handleCompletion(data);
  }
});

const fetchItem = async () => {
  try {
    const response = await axios.get(`/items/${itemId.value}`);
    item.value = response.data;
    newItem.value = false;
    isComparing.value = false; // Reset edit mode when fetching item
  } catch (error) {
    if (axios.isAxiosError(error) && error.response && error.response.status === 404) {
      newItem.value = true;
      item.value = { tag_uuid: itemId.value };
      console.warn('Item not found, display empty item form');
    } else {
      console.error('Error fetching item:', error);
    }
  }
};

onMounted(fetchItem);

watch(() => route.params.tag_uuid,async (newId) => {
    if (itemId.value != newId) {
      itemId.value = newId;
      await fetchItem();
    }
  },
);

const handleFormSubmit = async (formData: Record<string, unknown>) => {
  try {
    isComparing.value = false;
    if (newItem.value) {
      await axios.post('/items', formData);
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

const handleCompletion = (result: { data: { response: object } }) => {
  if (result && result.data && result.data.response) {
    completion.value = result.data.response;
    isComparing.value = true;
  } else {
    isComparing.value = false;
  }
};
</script>
