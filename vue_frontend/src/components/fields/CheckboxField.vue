<template>
  <BContainer>
    <BFormGroup class="d-flex p-2 justify-content-between" data-testid="checkbox-field">
      <span v-if="!hideLabel || !label" :for="name">{{ label }}</span>
      <BFormCheckbox
        :id="name"
        :name="name"
        :modelValue="value"
        @update:modelValue="onModelUpdate"
        :disabled="disabled"
      />
    </BFormGroup>
  </BContainer>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import { BFormCheckbox, BFormGroup } from 'bootstrap-vue-next'
import type { CheckboxValue } from 'bootstrap-vue-next'

defineProps({
  name: {
    type: String,
    required: true,
  },
  label: {
    type: String,
    default: '',
  },
  value: {
    type: Boolean,
    default: null,
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
const emit = defineEmits<{ (e: 'update:value', value: boolean | null): void }>()

function onModelUpdate(v: CheckboxValue | readonly CheckboxValue[] | undefined) {
  // BFormCheckbox can emit various shapes; convert to boolean|null for our API
  if (v === undefined) {
    emit('update:value', null)
  } else if (Array.isArray(v)) {
    emit('update:value', Boolean(v.length))
  } else {
    emit('update:value', Boolean(v))
  }
}
</script>

<style scoped>
.borderless label {
  display: none !important;
}
</style>
