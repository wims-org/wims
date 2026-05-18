<template>
  <BContainer class="pb-5" ref="itemForm">
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
        v-if="clientStore().user && props.item?.borrower?.id === clientStore().user?.id"
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
    <BForm v-if="item && formData" @submit.prevent="handleSubmit" @keydown="preventEnterKey">
      <component
        v-for="(field, key, fieldIndex) in visibleFields"
        :is="getFieldComponent(field.type)"
        :key="key"
        :name="String(key)"
        :label="field.label || key"
        :value="formData[key]"
        :disabled="field.disabled ?? undefined"
        :required="field.required"
        class="rounded"
        :class="fieldIndex % 2 === 0 ? 'striped-bg' : ''"
        :searchType="field.search_type"
        :qrSearch="field.qrSearch"
        :nfcSearch="field.nfcSearch"
        :resolves="field.resolves"
        :data-testid="`form-field-${String(key)}`"
        @update:value="updateFieldModel($event, String(key), field.type, field.resolves)"
        v-show="!field.hidden && (!field.details || showDetails)"
        >{{ fieldIndex }}
      </component>
      <div class="d-flex">
        <BButton type="submit" variant="primary" class="mt-3">Submit</BButton>
        <BButton
          v-if="!props.isNewItem"
          type="button"
          variant="danger"
          class="mt-3 ms-2 ms-auto"
          @click="$emit('delete', props.item.id)"
        >
          Delete Item
        </BButton>
      </div>
    </BForm>
    <div v-else>
      <p>Error loading item details. Please try again later.</p>
    </div>
    <div v-if="Array.isArray(errors) && errors.length" class="alert alert-danger mt-3">
      <p>There were errors in the data model from the database:</p>
      <ul>
        <li v-for="(error, index) in errors" :key="index">{{ error }}</li>
      </ul>
    </div>
  </BContainer>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { BForm, BButton } from 'bootstrap-vue-next'
import { formFields } from '@/interfaces/FormField.interface'
import { fieldTypeToComponent } from '@/utils/form.helper'
import axios from 'axios'
import type { components } from '@/interfaces/api-types'
import { clientStore } from '@/stores/clientStore'

type Item = components['schemas']['ItemPublic']

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

// Computed Properties
const visibleFields = computed(() => {
  return Object.fromEntries(
    Object.entries(formFields).filter(
      ([, field]) => !field.hidden || (field.details && showDetails.value),
    ),
  )
})

// Emits
const emit = defineEmits(['submit', 'delete'])

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

const updateFieldModel = (value: unknown, key: string, type: string, resolves?: string) => {
  console.log(`Updating field '${key}' with value:`, value) // Debug log
  if (value === formData.value[key]) return // No change, do nothing
  if (type === 'checkbox') {
    formData.value[key] = Boolean(value)
  } else if (type === 'epoch') {
    formData.value[key] = value === null ? null : Math.floor(new Date(value as number).getTime() / 1000)
  } else if (type === 'number') {
    formData.value[key] = Number(value)
  } else if (type === 'array') {
    formData.value[key] = value
  } else if (key === 'container_id') {
    if (value && !Number.isNaN(value)) {
      axios
        .get<Item>(`/items/${value}`)
        .then((response) => (formData.value['container'] = response.data))
        .catch(() => {
          console.warn(`Container with ID ${value} not found, creating new container entry`)
          formData.value['container'] = { id: +value } as Item
        })
    } else {
      formData.value['container'] = null // Clear the field if no value
    }
    formData.value[key] = value as string
  } else if (type === 'item' || type === 'category' || type === 'user') {
    // value is an object from SearchInput; sync the _id FK field
    const itemId = value && typeof value === 'object' ? (value as { id: number }).id : (value as number | null)
    const idField = resolves ?? `${key}_id` // Use resolves if provided, otherwise default to key_id
    if (idField in formData.value) {
      formData.value[idField] = itemId ?? null
    }
    formData.value[key] = value ?? null
  } else {
    formData.value[key] = value
  }
  unsavedChanges.value = true // Mark changes as unsaved
}

const borrow_able = () => {
  return !props.item?.borrower && !props.item?.borrowed_until && clientStore().user?.id
}

const borrow = () => {
  if (clientStore().user) {
    updateFieldModel(clientStore().user?.id, 'borrower', 'user')
    updateFieldModel(Date.now() + 604800000, 'borrowed_until', 'epoch') // 7 days from now
    handleSubmit()
  }
}

const returnItem = () => {
  updateFieldModel(null, 'borrower', 'user')
  updateFieldModel(null, 'borrowed_until', 'epoch')
  handleSubmit()
}
</script>

<style scoped>
:deep(.form-control, .input-group) {
  width: var(--form-input-width);
  min-width: 0;
}

.sub-fields {
  margin-left: 20px;
}

.striped-bg {
  background-color: var(--color-bg-light);
  transition:
    color 0.3s,
    background-color 0.3s;
}
</style>
