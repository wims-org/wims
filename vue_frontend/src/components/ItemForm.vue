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
        <textarea v-else :name="String(key)" :disabled="field.disabled ?? undefined" v-model="item[key]"
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
import { defineComponent } from 'vue'
import axios from 'axios'

import type { ValidationArgs } from '@vuelidate/core'
import type { PropType } from 'vue'

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
  props: {
    schema: {
      type: Object as PropType<ValidationArgs>,
      required: true,
    },
  },
  data() {
    return {
      rfid: this.$route.params.rfid,
      item: {} as Record<string, string | number | readonly string[] | boolean | null | undefined>,
      showDetails: false,
      formFields: {} as Record<string, FormField>,
      newItem: false,
    }
  },
  created() {
    this.fetchItem()
    this.formFields = formFields
  },
  methods: {
    async fetchItem() {
      try {
        const response = await axios.get(`/item/${this.rfid}`)
        this.item = response.data
        console.log('Item:', this.item)
      } catch {
        this.newItem = true
        this.item = Object.keys(this.formFields).reduce((acc, key) => {
          acc[key] = null
          return acc
        }, {} as Record<string, string | number | readonly string[] | boolean | null | undefined>)
        this.item['tag_uuid'] = this.rfid
        console.warn('Item not found, display empty item form')
      }
    },
    async handleSubmit() {
      try {
        if (this.newItem) {
          await axios.post(`/item`, Object(this.item))
        } else {
          await axios.put(`/item`, Object(this.item))
        }
        alert('Item updated successfully')
      } catch (error) {
        console.error('Error updating item:', error)
      }
    },

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
        this.item[key] = target.checked
      } else if (type === 'epoch') {
        this.item[key] = new Date(target.value).getTime() / 1000
      } else if (fieldType === 'number') {
        this.item[key] = Number(target.value)
      } else if (fieldType === 'array') {
        this.item[key] = target.value.split(',').map(item => item.trim())
      } else {
        this.item[key] = target.value
      }
    },
    toggleDetails() {
      this.showDetails = !this.showDetails
    },
  },
})
</script>

<style scoped>
/* Add your styles here */
</style>
