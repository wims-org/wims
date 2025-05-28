<template>
  <div
    class="form-group"
    data-testid="object-field"
  >
    <label v-if="!hideLabel" :for="name">{{ label }}</label>
    <div class="card p-3">
      <div
        v-for="(subValue, subKey) in value"
        :key="subKey"
        class="form-group"
        v-show="subValue !== null && subValue !== undefined"
        data-testid="object-field-text-field"
      >
        <label v-if="!hideLabel" :for="`${name}-${subKey}`">{{ subKey }}</label>
        <input
          :type="typeof subValue === 'number' ? 'number' : 'text'"
          :name="`${name}-${subKey}`"
          :value="subValue"
          :disabled="disabled"
          @input="updateField($event, subKey)"
          class="form-control"
          :class="{ 'borderless-input': borderless }"
          :required="required"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue'

export default defineComponent({
  name: 'ObjectField',
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
      type: Object as PropType<Record<string, unknown>>,
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
    updateField(event: Event, subKey: string | number) {
      const target = event.target as HTMLInputElement
      const value = target.type === 'number' ? Number(target.value) : target.value
      const newValue = { ...this.value, [subKey]: value }
      this.$emit('update:value', newValue)
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
