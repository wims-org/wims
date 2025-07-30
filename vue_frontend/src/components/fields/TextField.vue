<template>
  <BContainer>
    <div
      class="form-group d-flex align-items-center justify-content-between flex-wrap p-2"
      data-testid="text-field"
    >
      <span v-if="!hideLabel || !label" :for="name">{{ label }}</span>
      <input
        :type="type || 'text'"
        :name="name"
        :disabled="disabled ?? undefined"
        :value="value"
        :required="required"
        @input="updateField"
        class="form-control"
        :class="[{ 'is-invalid': required && !value }, { 'borderless-input': borderless }]"
        :placeholder="hideLabel ? '' : label"
      />
    </div>
  </BContainer>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
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

const emit = defineEmits<{
  (e: 'update:value', value: string): void
}>()

function updateField(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:value', target.value)
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
