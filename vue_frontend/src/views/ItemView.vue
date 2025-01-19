<script setup lang="ts">
import LLMCompletion from '@/components/LLMCompletion.vue';
import Item from '../components/ItemForm.vue'
import type FormField from '@/interfaces/FormField.interface';

import { ref } from 'vue';

const formFields = ref<{ [key: string]: FormField }>({});
const schema = ref({});
</script>

<template>
  <main>
    <LLMCompletion/>
    <Item :formFields="formFields" :schema="schema" />
  </main>
</template>
