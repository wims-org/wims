<template>
  <div class="form-group" data-testid="number-field">
    <label :for="name">{{ label }}</label>
    <input
      type="number"
      :name="name"
      :disabled="disabled ?? undefined"
      :value="value"
      :required="required"
      @input="updateField"
      class="form-control"
      :class="{ 'is-invalid': required && !value }"
      
    />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'NumberField',
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
      type: [String, Number],
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
  },
  emits: ['update:value'],
  methods: {
    updateField(event: Event) {
      const target = event.target as HTMLInputElement
      this.$emit('update:value', Number(target.value))
    },
  },
})
</script>