<template>
  <container>
    <div class="form-group d-flex align-items-center justify-content-between flex-wrap p-2"
      data-testid="text-area-field">
      <label v-if="!hideLabel || !label" :for="name">{{ label }}</label>
      <textarea :name="name" :disabled="disabled ?? undefined" :value="value" @input="updateField" class="form-control"
        :class="[{ 'is-invalid': required && !value }, { 'borderless-input': borderless }]" :required="required"
        :placeholder="hideLabel ? '' : label"></textarea>
    </div>
  </container>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'TextAreaField',
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
  },
  emits: ['update:value'],
  methods: {
    updateField(event: Event) {
      const target = event.target as HTMLTextAreaElement
      this.$emit('update:value', target.value)
    },
  },
})
</script>

<style scoped></style>
