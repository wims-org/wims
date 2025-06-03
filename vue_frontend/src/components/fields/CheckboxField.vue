<template>
  <div
    class="form-group d-flex align-items-center justify-content-between flex-wrap p-2"
    data-testid="checkbox-field"
  >
    <span v-if="!hideLabel" :for="name">{{ label }}</span>
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
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'CheckboxField',
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
  },
  emits: ['update:value'],
  methods: {
    updateField(event: Event) {
      const target = event.target as HTMLInputElement
      this.$emit('update:value', target.checked)
    },
  },
})
</script>

<style scoped>
.borderless label {
  display: none !important;
}
</style>
