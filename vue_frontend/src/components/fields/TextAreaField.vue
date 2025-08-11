<template>
  <BContainer>
    <div class="form-group d-flex align-items-center justify-content-between flex-wrap p-2"
      data-testid="text-area-field">
      <label v-if="!hideLabel || !label" :for="name">{{ label }}</label>
      <textarea :name="name" :disabled="disabled ?? undefined" :value="value" @input="updateField" class="form-control"
        :class="[{ 'is-invalid': required && !value }, { 'borderless-input': borderless }]" :required="required"
        :placeholder="hideLabel ? '' : label"></textarea>
    </div>
  </BContainer>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

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
    required: true,
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

const emit = defineEmits<{
  (e: 'update:value', value: string): void
}>()

function updateField(event: Event) {
  const target = event.target as HTMLTextAreaElement
  emit('update:value', target.value)
}
</script>

<style scoped></style>
