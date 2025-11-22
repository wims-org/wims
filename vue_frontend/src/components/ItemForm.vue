<template>
  <div class="container pb-5" ref="itemForm">
    <!-- Sticky Note -->
    <div v-if="unsavedChanges" class="sticky-note">Unsaved Changes</div>

    <div class="d-flex mb-3">
      <button
        @click="toggleDetails"
        type="button"
        class="btn btn-secondary p-2"
        data-testid="toggle-details-button"
      >
        {{ showDetails ? 'Hide Details' : 'Show Details' }}
      </button>
      <button
        v-if="borrow_able()"
        type="button"
        class="btn btn-warning p-2 ms-2"
        data-testid="borrow-item-button"
        @click="borrow()"
      >
        Borrow Item
      </button>
      <button
        v-if="props.item?.borrowed_by && props.item?.borrowed_by === clientStore().user?._id"
        type="button"
        class="btn btn-danger p-2 ms-2"
        data-testid="return-item-button"
        @click="returnItem()"
      >
        Return Item
      </button>
      <button @click="handleSubmit" type="button" class="btn btn-primary p-2 ms-auto">
        Submit
      </button>
    </div>
    <h1 class="mb-4">{{ item?.short_name }}</h1>
    <form v-if="item && formData" @submit.prevent="handleSubmit" @keydown="preventEnterKey">
      <component
        v-for="(field, key, fieldIndex) in formFields"
        :is="getFieldComponent(field.type)"
        :key="key"
        :name="String(key)"
        :label="field.label || key"
        :value="formData[key]"
        :disabled="field.disabled ?? undefined"
        :required="field.required"
        :class="fieldIndex % 2 === 0 ? 'striped-bg' : ''"
        :searchType="field.search_type"
        @update:value="updateFieldModel($event, String(key), field.type)"
        v-show="!field.hidden && (!field.details || showDetails)"
      />
      <button type="button" class="btn btn-primary mt-3" @click="handleSubmit">Submit</button>
    </form>
    <div v-else>
      <p>Error loading item details. Please try again later.</p>
    </div>
    <div v-if="Array.isArray(errors) && errors.length" class="alert alert-danger mt-3">
      <p>There were errors in the data model from the database:</p>
      <ul>
        <li v-for="(error, index) in errors" :key="index">{{ error }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { formFields } from '@/interfaces/FormField.interface'
import { fieldTypeToComponent } from '@/utils/form.helper'
import axios from 'axios'
import type { components } from '@/interfaces/api-types'
import { clientStore } from '@/stores/clientStore'

type Item = components['schemas']['Item'] & { [key: string]: unknown }

// Props
const props = defineProps({
  item: {
    type: Object as () => Item,
    default: () => ({}) as Item,
    required: true,
  },
  isNewItem: {
    type: Boolean,
    required: true,
  },
  errors: {
    type: Array as () => string[],
    default: () => [],
  },
})

// Emits
const emit = defineEmits(['submit'])

// Reactive State
const formData = ref<Record<string, unknown | null>>({})
const unsavedChanges = ref(false)
const showDetails = ref(false)

// Watchers
watch(
  () => props.item,
  (newItem) => {
    formData.value = { ...newItem }
    unsavedChanges.value = false // Reset unsaved changes when item prop changes
  },
  { immediate: true, deep: true },
)

// Methods
const toggleDetails = () => {
  showDetails.value = !showDetails.value
}

const handleSubmit = async () => {
  emit('submit', formData.value)
  unsavedChanges.value = false
}

const preventEnterKey = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    event.preventDefault()
  }
}

const getFieldComponent = (type: string) => {
  return fieldTypeToComponent(type)
}

const updateFieldModel = (value: unknown, key: string, type: string) => {
  if (value === formData.value[key]) return // No change, do nothing
  if (type === 'checkbox') {
    formData.value[key] = Boolean(value)
  } else if (type === 'epoch') {
    formData.value[key] = Math.floor(new Date(value as number).getTime() / 1000)
  } else if (type === 'number') {
    formData.value[key] = Number(value)
  } else if (type === 'array') {
    formData.value[key] = value
  } else if (key === 'container_tag_uuid') {
    if (typeof value === 'string' && value.trim() !== '') {
      axios
        .get<Item>(`/items/${value}`)
        .then((response) => (formData.value['container'] = response.data))
        .catch(() => {
          console.warn(`Container with UUID ${value} not found, creating new container entry`)
          formData.value['container'] = { tag_uuid: value } as Item
        })
    } else {
      formData.value['container'] = null // Clear the field if no value
    }
    formData.value[key] = value as string
  } else if (type === 'user') {
    formData.value[key] = value
  } else {
    formData.value[key] = value
  }
  unsavedChanges.value = true // Mark changes as unsaved
}

const borrow_able = () => {
  return !props.item?.borrowed_by && !props.item?.borrowed_until && clientStore().user?._id
}

const borrow = () => {
  if (clientStore().user) {
    updateFieldModel(clientStore().user?._id, 'borrowed_by', 'user')
    updateFieldModel(Date.now() + 604800000, 'borrowed_until', 'epoch') // 7 days from now
    handleSubmit()
  }
}

const returnItem = () => {
  updateFieldModel(null, 'borrowed_by', 'user')
  updateFieldModel(null, 'borrowed_until', 'epoch')
  handleSubmit()
}
</script>

<style scoped>
:deep(.form-control) {
  width: unset;
  min-width: 0;
}

.sub-fields {
  margin-left: 20px;
}

.striped-bg {
  background-color: var(--color-bg-light);
}

.sticky-note {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--color-danger);
  color: var(--color-primary-contrast);
  padding: 0 20px;
  border-radius: 8px;
  font-weight: bold;
  z-index: 1200;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);
}
</style>
