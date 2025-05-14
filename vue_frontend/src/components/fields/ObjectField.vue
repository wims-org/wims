<template>
  <div>
    <label :for="name">{{ label }}</label>
    <div class="card p-3" data-testid="object-field">
      <div
        v-for="(subValue, subKey) in value"
        :key="subKey"
        class="form-group"
        v-show="subValue !== null && subValue !== undefined"
        data-testid="object-field-text-field"
      >
        <label :for="`${name}-${subKey}`">{{ subKey }}</label>
        <input
          :type="typeof subValue === 'number' ? 'number' : 'text'"
          :name="`${name}-${subKey}`"
          :value="subValue"
          :disabled="disabled"
          @input="updateField($event, subKey)"
          class="form-control"
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
  },
  emits: ['update:value'],
  methods: {
    updateField(event: Event, subKey: string | number) {
      const target = event.target as HTMLInputElement
      const newValue = { ...this.value, [subKey]: target.value }
      this.$emit('update:value', newValue)
    },
  },
})
</script>
