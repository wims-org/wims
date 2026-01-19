<template>
  <BContainer>
    <BFormGroup
      class="d-flex p-2 justify-content-between align-items-center"
      data-testid="text-field"
    >
      <label v-if="!hideLabel || !label" :for="name">{{ label }}</label>
      <BFormInput
        :id="name"
        :type="(type || 'text') as any"
        :name="name"
        :disabled="disabled ?? undefined"
        :modelValue="value as any"
        :required="required"
        @update:modelValue="onModelUpdate"
        :placeholder="hideLabel ? '' : label"
        :class="[{ 'borderless-input': borderless }]"
      />
    </BFormGroup>
  </BContainer>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import { BFormInput, BFormGroup } from 'bootstrap-vue-next'
defineProps({
  name: {
    type: String,
    required: true,
  },
  label: {
    type: String,
    default: '',
  },
  type: {
    type: String,
    default: 'text',
    validator: (value: string) => {
      return [
        'text',
        'number',
        'email',
        'password',
        'search',
        'url',
        'tel',
        'date',
        'time',
        'range',
        'color',
        'datetime-local',
        'month',
        'week',
      ].includes(value)
    },
  },
  value: {
    type: [String, Number, Boolean],
    default: '',
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
  borderless: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits<{ (e: 'update:value', value: string | number | null): void }>()

function onModelUpdate(v: string | number | null) {
  emit('update:value', v)
}
</script>

<style scoped>

.borderless span {
  display: none !important;
}

.borderless-input {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 0.1rem 0.2rem !important;
  min-width: 0;
}
</style>
