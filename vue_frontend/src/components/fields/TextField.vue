<template>
  <div
    class="form-group"
    data-testid="text-field"
  >
    <label v-if="!hideLabel" :for="name">{{ label }}</label>
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
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'TextField',
  props: {
    name: {
      type: String,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      default: 'text',
    },
    value: {
      type: [String, Number, Boolean],
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
  },
  emits: ['update:value'],
  methods: {
    updateField(event: Event) {
      const target = event.target as HTMLInputElement
      this.$emit('update:value', target.value)
    },
  },
})
</script>

<style scoped>
.borderless label {
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
