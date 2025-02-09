<template>
  <div class="container mt-5">
    <button @click="toggleDetails" class="btn btn-secondary mb-3">
      {{ showDetails ? 'Hide Details' : 'Show Details' }}
    </button>
    <h1 class="mb-4">Item Details</h1>
    <form v-if="item" @submit.prevent="handleSubmit">
      <div class="form-group" v-for="(field, key) in formFields" :key="key"
        v-show="!field.hidden && (!field.details || (showDetails && field.details))">
        <label :for="String(key)">{{ field.label }}</label>
        <input v-if="field.type !== 'textarea' && field.type !== 'object'" :type="field.type" :name="String(key)"
          :disabled="field.disabled ?? undefined" :value="getFieldModel(String(key), field.type)"
          :required="field.required" @input="updateFieldModel($event, String(key), field.type)" class="form-control"
          :class="{ 'is-invalid': field.required && !item[key] }" />
        <div v-else-if="field.type === 'object'" class="card p-3">
          <div v-for="(subField, subKey) in item[key]" :key="subKey" class="form-group"
            v-show="subField !== null && subField !== undefined">
            <label :for="`${key}-${subKey}`">{{ subKey }}</label>
            <input :type="typeof subField === 'number' ? 'number' : 'text'" :name="`${key}-${subKey}`" :value="subField"
              :disabled="field.disabled ?? undefined"
              @input="updateFieldModel($event, `${key}.${subKey}`, typeof subField)" class="form-control" />
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
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';


import type FormField from '@/interfaces/FormField.interface'
const formFields: Record<string, FormField> = {
  tag_uuid: { label: 'Container Tag UUID', type: 'text', disabled: true, hidden: false, details: false, required: true },
  short_name: { label: 'Short Name', type: 'text', disabled: false, hidden: false, details: false, required: true },
  description: { label: 'Description', type: 'textarea', disabled: false, hidden: false, details: true, required: false },
  amount: { label: 'Amount', type: 'number', disabled: false, hidden: false, details: false, required: true },
  item_type: { label: 'Item Type', type: 'text', disabled: false, hidden: false, details: false, required: true },
  consumable: { label: 'Consumable', type: 'checkbox', disabled: false, hidden: false, details: false, required: true },
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
  props: {
    item: {
      type: Object as () => { [key: string]: string | number | readonly string[] | boolean | null | undefined },
      required: true,
    },
    newItem: {
      type: Boolean,
      required: true,
    },
  },
  setup(props, { emit }) {
    const formData = ref<{ [key: string]: string | number | boolean | readonly string[] | null | undefined }>({});

    watch(
      () => props.item,
      (newFields) => {
        formData.value = { ...newFields };
      },
      { immediate: true }
    );

    const showSubFields = ref<{ [key: string]: boolean }>({});

    const toggleSubFields = (key: string) => {
      showSubFields.value[key] = !showSubFields.value[key];
    };

    const handleSubmit = () => {
      emit('submit', formData.value);
    };

    return {
      formData,
      showSubFields,
      toggleSubFields,
      handleSubmit,
    };
  },
  data() {
    return {
      rfid: this.$route.params.rfid,
      formFields: {} as Record<string, FormField>,
      showDetails: false,
    }
  }, 
  created() {
    this.formFields = formFields
  },

  methods: {
    formatDate(timestamp: number): string {
      if (!timestamp) return ''
      const date = new Date(timestamp * 1000)
      return isNaN(date.getTime()) ? '' : date.toISOString().split('T')[0]
    },
    getFieldModel(key: string, type: string) {
      if (type === 'checkbox') {
        return this.item[key] ? 'checked' : ''
      } else if (type === 'epoch') {
        return this.formatDate(this.item[key] as number)
      }
      return this.item[key]
    },
    updateFieldModel(event: Event, key: string, type: string) {
      const target = event.target as HTMLInputElement
      const fieldType = this.formFields[key].type
      if (type === 'checkbox') {
        this.formData[key] = target.checked
      } else if (type === 'epoch') {
        this.formData[key] = new Date(target.value).getTime() / 1000
      } else if (fieldType === 'number') {
        this.formData[key] = Number(target.value)
      } else if (fieldType === 'array') {
        this.formData[key] = target.value.split(',').map(item => item.trim())
      } else {
        this.formData[key] = target.value
      }
    },
    toggleDetails() {
      this.showDetails = !this.showDetails
    },
  },
})
</script>

<style scoped>
.sub-fields {
  margin-left: 20px;
}
</style>
