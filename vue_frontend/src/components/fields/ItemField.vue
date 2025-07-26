<template>
  <container>
    <div class="d-flex justify-content align-items-center p-2">
      <span :for="name">{{ label }}</span>
      <a
        :href="`/items/${formData['tag_uuid']}`"
        target="_blank"
        v-if="formData['short_name']"
      >
        <span :for="name" class="mr-2">{{ formData['short_name'] }} </span>
        <font-awesome-icon icon="external-link-alt" aria-label="Open item in new tab" />
      </a>

      <div @click="toggleIsCollapsed()" class="col-1 text-center cursor-pointer ml-auto">
        <font-awesome-icon
          :icon="isCollapsed ? 'chevron-up' : 'chevron-down'"
          aria-label="Toggle collapse"
        />
      </div>
    </div>
    <div class="card" data-testid="item-field" v-if="Object.keys(formData).length > 0">
      <div v-if="!isCollapsed">
        <component
          v-for="(field, key, fieldIndex) in filteredFormFields"
          :is="fieldTypeToComponent(field.type)"
          :key="key"
          :name="String(key)"
          :label="field.label || key"
          :value="formData[key]"
          :disabled="disabled"
          :required="field.required"
          :hide-label="hideLabelDeep"
          :borderless="borderless"
          :class="fieldIndex % 2 === 0 ? 'bg-light' : ''"
          @update:value="updateField($event, key)"
          v-show="!field.hidden && !field.details"
          :v-if="
            formData[key] !== undefined &&
            formData[key] !== null &&
            formData[key] !== '' &&
            (Array.isArray(formData[key]) && formData[key].length > 0)
          "
        />
      </div>
      <span v-else class="p-2">contents hidden...</span>
    </div>
    <div v-else class="card p-3 mb-3">
      <span>No fields available</span>
    </div>
  </container>
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
      default: '',
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
    hideLabel: {
      type: Boolean,
      default: false,
    },
    hideLabelDeep: {
      type: Boolean,
      default: false,
    },
    borderless: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['update:value'],
  setup(props, { emit }) {
    const formData = ref<Record<string, unknown>>({})
    const filteredFormFields = ref<Record<string, (typeof formFields)[keyof typeof formFields]>>({})
    const isCollapsed = ref(true)

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
