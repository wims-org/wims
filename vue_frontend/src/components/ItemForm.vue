<template>
  <div class="container mt-5" ref="itemForm">
    <button @click="toggleDetails" class="btn btn-secondary mb-3">
      {{ showDetails ? 'Hide Details' : 'Show Details' }}
    </button>
    <h1 class="mb-4">Item Details</h1>
    <form v-if="item" @submit.prevent="handleSubmit">
      <div class="form-group" v-for="(field, key) in formFields" :key="key"
        v-show="!field.hidden && (!field.details || (showDetails && field.details))">
        <label :for="String(key)">{{ field.label || key }}</label>
        <input v-if="field.type !== 'textarea' && field.type !== 'object'" :type="field.type || 'text'"
          :name="String(key)" :disabled="field.disabled ?? undefined" :value="getFieldModel(String(key), field.type)"
          :required="field.required" @input="updateFieldModel($event, String(key), field.type)"
          @click="handleInputClick(key)" class="form-control" :class="{ 'is-invalid': field.required && !item[key] }" />
        <div v-else-if="field.type === 'object'" class="card p-3">
          <div v-for="(subValue, subKey) in item[key]" :key="subKey" class="form-group"
            v-show="subValue !== null && subValue !== undefined">
            <label :for="`${key}-${subKey}`">{{ subKey }}</label>
            <input :type="typeof subValue === 'number' ? 'number' : 'text'" :name="`${key}-${subKey}`" :value="subValue"
              :disabled="field.disabled ?? undefined"
              @input="updateFieldModel($event, `${key}.${subKey}`, typeof subValue)" class="form-control" />
          </div>
        </div>
        <textarea v-else :name="String(key)" :disabled="field.disabled ?? undefined" :v-model="item[key]"
          class="form-control" :class="{ 'is-invalid': field.required && !item[key] }"></textarea>
      </div>
      <button type="submit" class="btn btn-primary mt-3">Submit</button>
    </form>
    <div v-else>
      <p>Error loading item details. Please try again later.</p>
    </div>
    <SearchModal :show="showModal" @close="closeModal" @select="handleSelect" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';
import type FormField from '@/interfaces/FormField.interface';
import SearchModal from './SearchModal.vue';
import { EventAction } from '@/interfaces/EventAction';
import { clientStore as useClientStore } from '@/stores/clientStore';

const formFields: Record<string, FormField> = {
  tag_uuid: { label: 'Container Tag UUID', type: 'text', disabled: true, hidden: false, details: false, required: true },
  short_name: { label: 'Short Name', type: 'text', disabled: false, hidden: false, details: false, required: true },
  description: { label: 'Description', type: 'textarea', disabled: false, hidden: false, details: true, required: false },
  amount: { label: 'Amount', type: 'number', disabled: false, hidden: false, details: false, required: true },
  item_type: { label: 'Item Type', type: 'text', disabled: false, hidden: false, details: false, required: true },
  consumable: { label: 'Consumable', type: 'checkbox', disabled: false, hidden: false, details: false, required: false },
  created_at: { label: 'Created At', type: 'epoch', disabled: true, hidden: false, details: false, required: false },
  created_by: { label: 'Created By', type: 'text', disabled: true, hidden: false, details: false, required: false },
  changes: { label: 'Changes', type: 'array', disabled: true, hidden: true, details: false, required: false },
  ai_generated: { label: 'AI Generated', type: 'array', disabled: true, hidden: true, details: false, required: false },
  min_amount: { label: 'Minimum Amount', type: 'number', disabled: false, hidden: false, details: false, required: false },
  tags: { label: 'Tags', type: 'array', disabled: false, hidden: false, details: false, required: true },
  images: { label: 'Images', type: 'array', disabled: false, hidden: false, details: true, required: false },
  cost_new: { label: 'Cost New', type: 'number', disabled: false, hidden: false, details: false, required: false },
  acquisition_date: { label: 'Acquisition Date', type: 'epoch', disabled: false, hidden: false, details: false, required: false },
  cost_used: { label: 'Cost Used', type: 'number', disabled: false, hidden: false, details: false, required: false },
  manufacturer: { label: 'Manufacturer', type: 'text', disabled: false, hidden: false, details: false, required: false },
  model_number: { label: 'Model Number', type: 'text', disabled: false, hidden: false, details: false, required: false },
  manufacturing_date: { label: 'Manufacturing Date', type: 'epoch', disabled: false, hidden: false, details: false, required: false },
  upc: { label: 'UPC', type: 'text', disabled: false, hidden: false, details: false, required: false },
  asin: { label: 'ASIN', type: 'text', disabled: false, hidden: false, details: false, required: false },
  serial_number: { label: 'Serial Number', type: 'text', disabled: false, hidden: false, details: false, required: false },
  vendors: { label: 'Vendors', type: 'array', disabled: false, hidden: false, details: true, required: false },
  shop_url: { label: 'Shop URL', type: 'array', disabled: false, hidden: false, details: true, required: false },
  size: { label: 'Size', type: 'object', disabled: false, hidden: false, details: false, required: false },
  documentation: { label: 'Documentation', type: 'array', disabled: false, hidden: false, details: true, required: false },
  related_items: { label: 'Related Items', type: 'array', disabled: false, hidden: false, details: true, required: false },
  container_tag_uuid: { label: 'Container Tag UUID', type: 'text', disabled: false, hidden: false, details: false, required: false },
  container: { label: 'Container', type: 'object', disabled: true, hidden: false, details: false, required: false },
  current_location: { label: 'Current Location', type: 'text', disabled: false, hidden: false, details: false, required: false },
  borrowed_by: { label: 'Borrowed By', type: 'text', disabled: false, hidden: false, details: false, required: false },
  borrowed_at: { label: 'Borrowed At', type: 'epoch', disabled: false, hidden: false, details: false, required: false },
  borrowed_until: { label: 'Borrowed Until', type: 'epoch', disabled: false, hidden: false, details: false, required: false },
  owner: { label: 'Owner', type: 'text', disabled: false, hidden: false, details: false, required: false },
}

export default defineComponent({
  name: 'ItemForm',
  components: {
    SearchModal,
  },
  props: {
    item: {
      type: Object as () => Record<string, any>,
      required: true,
    },
    newItem: {
      type: Boolean,
      required: true,
    },
  },
  setup(props, { emit }) {
    const formData = ref({ ...props.item });
    const showModal = ref(false);
    const clientStore = useClientStore();

    watch(
      () => props.item,
      (newItem) => {
        formData.value = { ...newItem };
      },
      { immediate: true }
    );

    const showDetails = ref(false);

    const toggleDetails = () => {
      showDetails.value = !showDetails.value;
    };

    const handleSubmit = () => {
      emit('submit', formData.value);
    };

    const formatDate = (timestamp: number): string => {
      if (!timestamp) return '';
      const date = new Date(timestamp * 1000);
      return isNaN(date.getTime()) ? '' : date.toISOString().split('T')[0];
    };

    const getFieldModel = (key: string, type: string) => {
      if (type === 'checkbox') {
        return formData.value[key] ? 'checked' : '';
      } else if (type === 'epoch') {
        return formatDate(formData.value[key] as number);
      }
      return formData.value[key];
    };

    const updateFieldModel = (event: Event, key: string, type: string) => {
      const target = event.target as HTMLInputElement;
      if (type === 'checkbox') {
        formData.value[key] = target.checked;
      } else if (type === 'epoch') {
        formData.value[key] = new Date(target.value).getTime() / 1000;
      } else if (type === 'number') {
        formData.value[key] = Number(target.value);
      } else if (type === 'array') {
        formData.value[key] = target.value.split(',|;').map(item => item.trim());
      } else {
        formData.value[key] = target.value;
      }
    };

    const handleInputClick = (key: string) => {
      if (key === 'container_tag_uuid') {
        showModal.value = true;
      }
    };

    const handleSelect = (tag: string) => {
      formData.value.container_tag_uuid = tag;
    };

    const closeModal = () => {
      showModal.value = false;
      clientStore.expected_event_action = EventAction.REDIRECT
    };

    return {
      formData,
      formFields,
      showDetails,
      toggleDetails,
      handleSubmit,
      getFieldModel,
      updateFieldModel,
      showModal,
      handleInputClick,
      handleSelect,
      closeModal,
    };
  },
});
</script>

<style scoped>
.sub-fields {
  margin-left: 20px;
}
</style>
