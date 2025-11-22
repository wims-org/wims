<template>
  <BContainer>
    <BFormGroup class="d-flex p-2 justify-content-between" data-testid="text-area-field">
      <label v-if="!hideLabel || !label" :for="name">{{ label }}</label>
      <BFormTextarea
        :id="name"
        :name="name"
        :disabled="disabled ?? undefined"
        :modelValue="(value as any)"
        @update:modelValue="onModelUpdate"
        :required="required"
        :placeholder="hideLabel ? '' : label"
      />
    </BFormGroup>
  </BContainer>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import { BFormTextarea, BFormGroup } from 'bootstrap-vue-next'

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
    type: String,
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

const emit = defineEmits<{ (e: 'update:value', value: string | null): void }>()

function onModelUpdate(v: string | number | null) {
  emit('update:value', v === null ? null : String(v))
}
</script>

<style scoped></style>
