<template>
  <BContainer>
    <div
      class="form-group d-flex align-items-center justify-content-between flex-wrap p-2"
      data-testid="checkbox-field"
    >
      <span v-if="!hideLabel || !label" :for="name">{{ label }}</span>
      <input
        type="checkbox"
        :name="name"
        :checked="value"
        :disabled="disabled"
        @change="updateField"
        class="ml-3"
        :required="required"
      />
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
    type: Boolean,
    default: undefined,
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
const emit = defineEmits(['update:value'])

const updateField = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:value', target.checked)
}
</script>

<style scoped>
.borderless label {
  display: none !important;
}
</style>
