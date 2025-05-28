<template>
  <div>
    <div class="row">
      <label :for="name">{{ label }}</label>
      <div @click="toggleIsCollapsed()" class="col-1 text-center">
        <font-awesome-icon
          :icon="isCollapsed ? 'chevron-up' : 'chevron-down'"
          aria-label="Toggle collapse"
        />
      </div>
    </div>
    <div class="card p-3" data-testid="item-field" v-if="Object.keys(formData).length > 0">
      <div v-if="!isCollapsed">
        <component
          v-for="(field, key) in filteredFormFields"
          :is="fieldTypeToComponent(field.type)"
          :key="key"
          :name="String(key)"
          :label="field.label || key"
          :value="formData[key]"
          :disabled="disabled"
          :required="field.required"
          :hide-label="true"
          :borderless="true"
          @update:value="updateField($event, key)"
          v-show="!field.hidden && !field.details"
        />
      </div>
      <span v-else>contents hidden...</span>
    </div>
    <div v-else class="card p-3">
      <span>No fields available</span>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, type PropType } from 'vue'
import { fieldTypeToComponent } from '@/utils/form.helper'
import { formFields } from '@/interfaces/FormField.interface'

export default defineComponent({
  name: 'ItemField',
  components: {
    TextField: () => import('@/components/fields/TextField.vue'),
    TextAreaField: () => import('@/components/fields/TextAreaField.vue'),
    ObjectField: () => import('@/components/fields/ObjectField.vue'),
    LoadingField: () => import('@/components/fields/LoadingField.vue'),
    CheckboxField: () => import('@/components/fields/CheckboxField.vue'),
    ArrayField: () => import('@/components/fields/ArrayField.vue'),
    ModalField: () => import('@/components/fields/ModalField.vue'),
    NumberField: () => import('@/components/fields/NumberField.vue'),
    ItemField: () => import('@/components/fields/ItemField.vue'),
    ImageThumbnailField: () => import('@/components/fields/ImageThumbnailField.vue'),
  },
  props: {
    name: {
      type: String,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
    value: {
      type: Object as PropType<Record<string, unknown>>,
      default: () => ({}),
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    required: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['update:value'],
  setup(props, { emit }) {
    const formData = ref<Record<string, unknown>>({})
    const filteredFormFields = ref<Record<string, (typeof formFields)[keyof typeof formFields]>>({})
    const isCollapsed = ref(false)

    const toggleIsCollapsed = () => {
      isCollapsed.value = !isCollapsed.value
    }

    // Watch for changes in the value prop and update formData and filteredFormFields
    watch(
      () => props.value,
      (newValue) => {
        if (newValue) {
          Object.entries(newValue).forEach(([key, value]) => {
            if (value && formFields[key]?.type !== 'item') {
              formData.value[key] = value
            }
          })
          // Update filteredFormFields
          filteredFormFields.value = Object.fromEntries(
            Object.entries(formFields)
              .filter(
                ([key, field]) =>
                  field.type !== 'item' && newValue[key] !== undefined && newValue[key] !== null,
              )
              .map(([key, field]) => [
                key,
                { ...field, value: newValue[key] as string | number | boolean | undefined },
              ]),
          )
        }
      },
      { immediate: true, deep: true },
    )

    const updateField = (newValue: unknown, key: string) => {
      formData.value[key] = newValue
      emit('update:value', { ...formData.value })
    }

    return {
      formData,
      formFields,
      fieldTypeToComponent,
      filteredFormFields,
      updateField,
      isCollapsed,
      toggleIsCollapsed,
    }
  },
})
</script>
