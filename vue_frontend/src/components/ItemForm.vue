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
          @input="updateFieldModel($event, String(key), field.type)" class="form-control" />
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
          class="form-control"></textarea>
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
  container_tag_id: { label: 'Container Tag UUID', type: 'text', disabled: true, hidden: false, details: false },
  short_name: { label: 'Short Name', type: 'text', disabled: false, hidden: false, details: true },
  amount: { label: 'Amount', type: 'number', disabled: false, hidden: false, details: false },
  item_type: { label: 'Item Type', type: 'text', disabled: false, hidden: false, details: false },
  consumable: {
    label: 'Consumable',
    type: 'checkbox',
    disabled: false,
    hidden: false,
    details: false,
  },
  created_at: { label: 'Created At', type: 'epoch', disabled: true, hidden: false, details: false },
  created_by: { label: 'Created By', type: 'text', disabled: true, hidden: false, details: false },
  changes: { label: 'Changes', type: 'array', disabled: true, hidden: true, details: false },
  ai_generated: {
    label: 'AI Generated',
    type: 'array',
    disabled: true,
    hidden: true,
    details: false,
  },
  description: {
    label: 'Description',
    type: 'textarea',
    disabled: false,
    hidden: false,
    details: true,
  },
  min_amount: {
    label: 'Minimum Amount',
    type: 'number',
    disabled: false,
    hidden: false,
    details: false,
  },
  tags: { label: 'Tags', type: 'array', disabled: false, hidden: false, details: false },
  images: { label: 'Images', type: 'array', disabled: false, hidden: false, details: true },
  cost_new: { label: 'Cost New', type: 'number', disabled: false, hidden: false, details: false },
  acquisition_date: {
    label: 'Acquisition Date',
    type: 'epoch',
    disabled: false,
    hidden: false,
    details: false,
  },
  cost_used: { label: 'Cost Used', type: 'number', disabled: false, hidden: false, details: false },
  manufacturer: {
    label: 'Manufacturer',
    type: 'text',
    disabled: false,
    hidden: false,
    details: false,
  },
  model_number: {
    label: 'Model Number',
    type: 'text',
    disabled: false,
    hidden: false,
    details: false,
  },
  manufacturing_date: {
    label: 'Manufacturing Date',
    type: 'epoch',
    disabled: false,
    hidden: false,
    details: false,
  },
  upc: { label: 'UPC', type: 'text', disabled: false, hidden: false, details: false },
  asin: { label: 'ASIN', type: 'text', disabled: false, hidden: false, details: false },
  serial_number: {
    label: 'Serial Number',
    type: 'text',
    disabled: false,
    hidden: false,
    details: false,
  },
  vendors: { label: 'Vendors', type: 'array', disabled: false, hidden: false, details: true },
  shop_url: { label: 'Shop URL', type: 'array', disabled: false, hidden: false, details: true },
  size: { label: 'Size', type: 'object', disabled: false, hidden: false, details: false },
  documentation: {
    label: 'Documentation',
    type: 'array',
    disabled: false,
    hidden: false,
    details: true,
  },
  related_items: {
    label: 'Related Items',
    type: 'array',
    disabled: false,
    hidden: false,
    details: true,
  },
  container_tag_uuid: {
    label: 'Container Tag UUID',
    type: 'text',
    disabled: false,
    hidden: false,
    details: false,
  },
  container: {
    label: 'Container',
    type: 'object',
    disabled: true,
    hidden: false,
    details: false,
  },
  current_location: {
    label: 'Current Location',
    type: 'text',
    disabled: false,
    hidden: false,
    details: false,
  },
  borrowed_by: {
    label: 'Borrowed By',
    type: 'text',
    disabled: false,
    hidden: false,
    details: false,
  },
  borrowed_at: {
    label: 'Borrowed At',
    type: 'epoch',
    disabled: false,
    hidden: false,
    details: false,
  },
  borrowed_until: {
    label: 'Borrowed Until',
    type: 'epoch',
    disabled: false,
    hidden: false,
    details: false,
  },
  owner: { label: 'Owner', type: 'text', disabled: false, hidden: false, details: false },
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
      item: {} as Record<string, string | number | readonly string[] | null | undefined>,
      showDetails: false,
      formFields: {} as Record<string, FormField>,
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
        this.item = Object.keys(this.formFields).reduce((acc, key) => {
          acc[key] = null
          return acc
        }, {} as Record<string, string | number | readonly string[] | null | undefined>)
        this.item['container_tag_id'] = this.rfid
        console.warn('Item not found, display empty item form')
      }
    },
    async handleSubmit() {
      try {
        await axios.post(`/item`, this.item)
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
      if (type === 'checkbox') {
        this.item[key] = '' + target.checked
      }
      if (type === 'epoch') {
        this.item[key] = new Date(target.value).getTime() / 1000
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
