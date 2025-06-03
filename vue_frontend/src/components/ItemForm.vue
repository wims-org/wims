<template>
  <div class="container pb-5" ref="itemForm">
    <!-- Sticky Note -->
    <div v-if="unsavedChanges" class="sticky-note">Unsaved Changes</div>

    <ContainerListComponent
      v-if="item && item.tag_uuid"
      :itemId="typeof item.tag_uuid === 'string' ? item.tag_uuid : ''"
      @update:value="updateFieldModel($event, 'container_tag_uuid', 'modal')"
    />
    <div class="row mb-3">
      <button
        @click="toggleDetails"
        type="button"
        class="btn btn-secondary mt-3 mr-auto"
        data-testid="toggle-details-button"
      >
        {{ showDetails ? 'Hide Details' : 'Show Details' }}
      </button>
      <button @click="handleSubmit" type="submit" class="btn btn-primary mt-3">Submit</button>
    </div>
    <h1 class="mb-4">{{ item.short_name }}</h1>
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
        :class="fieldIndex % 2 === 0 ? 'bg-light' : ''"
        @update:value="updateFieldModel($event, String(key), field.type)"
        v-show="!field.hidden && (!field.details || (showDetails && field.details))"
      />
      <button type="submit" class="btn btn-primary mt-3">Submit</button>
    </form>
    <div v-else>
      <p>Error loading item details. Please try again later.</p>
    </div>
    <div v-if="Array.isArray(item.errors) && item.errors.length" class="alert alert-danger mt-3">
      <p>There were errors in the data model from the database:</p>
      <ul>
        <li v-for="(error, index) in item.errors" :key="index">{{ error }}</li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue'
import { formFields } from '@/interfaces/FormField.interface'
import TextField from '@/components/fields/TextField.vue'
import TextAreaField from '@/components/fields/TextAreaField.vue'
import ObjectField from '@/components/fields/ObjectField.vue'
import LoadingField from '@/components/fields/LoadingField.vue'
import CheckboxField from '@/components/fields/CheckboxField.vue'
import ArrayField from '@/components/fields/ArrayField.vue'
import ModalField from '@/components/fields/ModalField.vue'
import NumberField from '@/components/fields/NumberField.vue'
import ImageThumbnailField from '@/components/fields/ImageThumbnailField.vue'
import ItemField from '@/components/fields/ItemField.vue'
import { fieldTypeToComponent } from '@/utils/form.helper'
import ContainerListComponent from '@/components/shared/ContainerListComponent.vue'
import axios from 'axios'
import type { components } from '@/interfaces/api-types'
type Item = components['schemas']['Item'] & { [key: string]: unknown }

export default defineComponent({
  name: 'ItemForm',
  components: {
    TextField,
    TextAreaField,
    ObjectField,
    LoadingField,
    CheckboxField,
    ArrayField,
    ModalField,
    NumberField,
    ItemField,
    ImageThumbnailField,
    ContainerListComponent,
  },
  props: {
    item: {
      type: Object as () => Record<string, unknown>,
      required: true,
    },
    newItem: {
      type: Boolean,
      required: true,
    },
  },
  setup(props, { emit }) {
    const formData = ref<{ [x: string]: unknown | undefined }>({ ...props.item }) // form data is the live data in the form
    const unsavedChanges = ref(false)
    const saveError = ref('')

    watch(
      () => props.item,
      (newItem) => {
        formData.value = { ...newItem }
        unsavedChanges.value = false // Reset unsaved changes when item prop changes
      },
      { immediate: true, deep: true },
    )

    const showDetails = ref(false)

    const toggleDetails = () => {
      showDetails.value = !showDetails.value
    }

    const handleSubmit = async () => {
      await emit('submit', formData.value)
      unsavedChanges.value = false
    }

    const preventEnterKey = (event: KeyboardEvent) => {
      if (event.key === 'Enter') {
        event.preventDefault()
      }
    }

    const formatDate = (timestamp: number): string => {
      if (!timestamp) return ''
      const date = new Date(timestamp * 1000)
      return isNaN(date.getTime()) ? '' : date.toISOString().split('T')[0]
    }

    const getFieldModel = (key: string, type: string) => {
      if (type === 'checkbox') {
        return formData.value[key] ? 'checked' : ''
      } else if (type === 'epoch') {
        return formatDate(formData.value[key] as number)
      }
      return formData.value[key]
    }

    const getFieldComponent = (type: string) => {
      return fieldTypeToComponent(type)
    }

    const updateFieldModel = (value: unknown, key: string, type: string) => {
      console.log(`Updating field ${key} with value:`, value)
      if (type === 'checkbox') {
        formData.value[key] = Boolean(value)
      } else if (type === 'epoch') {
        formData.value[key] = new Date(value as string).getTime() / 1000
      } else if (type === 'number') {
        formData.value[key] = Number(value)
      } else if (type === 'array') {
        formData.value[key] = value
      } else if (key === 'container_tag_uuid') {
        if (value) {
          axios
            .get<Item>(`/items/${value}`)
            .then((response) => (formData.value['container'] = response.data))
        } else {
          formData.value['container'] = undefined // Clear the field if no value
        }
      } else {
        formData.value[key] = value
      }
      unsavedChanges.value = true // Mark changes as unsaved
    }

    const removeImage = (index: number) => {
      if (!Array.isArray(formData.value.imageUrls)) return
      formData.value.imageUrls.splice(index, 1)
    }

    return {
      formData,
      formFields,
      showDetails,
      toggleDetails,
      handleSubmit,
      preventEnterKey,
      getFieldComponent,
      getFieldModel,
      updateFieldModel,
      removeImage,
      unsavedChanges,
      saveError,
    }
  },
})  
</script>

<style scoped>
:deep(.form-control) {
  width: unset;
  min-width: 0;
}
.sub-fields {
  margin-left: 20px;
}

.sticky-note {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  background-color: red;
  color: white;
  padding: 0 20px;
  border-radius: 8px;
  font-weight: bold;
  z-index: 1000;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);
}
</style>
