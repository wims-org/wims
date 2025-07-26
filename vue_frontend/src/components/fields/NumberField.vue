<template>
  <div
    class="form-group d-flex align-items-center justify-content-between flex-wrap p-2"
    data-testid="number-field"
  >
    <span v-if="!hideLabel || !label" :for="name" class="me-2">{{ label }}</span>
    <div class="number-input-wrapper d-flex align-items-center">
      <input
        type="number"

        :name="name"
        :disabled="disabled ?? undefined"
        :value="value"
        :required="required"
        @input="updateField"
        class="form-control text-center"
        :class="[{ 'is-invalid': required && !value }, { 'borderless-input': borderless }]"
        style="width: 70px"
      />
      <button
        type="button"
        class="arrow-btn"
        :disabled="disabled"
        @click="decrement"
        tabindex="-1"
        aria-label="Decrease"
      >
        <span>&#8722;</span>
      </button>
      <button
        type="button"
        class="arrow-btn"
        :disabled="disabled"
        @click="increment"
        tabindex="-1"
        aria-label="Increase"
      >
        <span>&#43;</span>
      </button>
    </div>
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
      default: '',
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
      this.$emit('update:value', Number(target.value))
    },
    increment() {
      if (this.disabled) return
      let val = Number(this.value) || 0
      val++
      this.$emit('update:value', val)
    },
    decrement() {
      if (this.disabled) return
      let val = Number(this.value) || 0
      val--
      this.$emit('update:value', val)
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
.number-input-wrapper {
  gap: 0.25rem;
}
.arrow-btn {
  background: #f5f5f5;
  border: 1px solid #ccc;
  color: #333;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2em;
  transition:
    background 0.15s,
    border 0.15s;
  margin: 0 2px;
  padding: 0;
  cursor: pointer;
  user-select: none;
}
.arrow-btn:active {
  background: #e0e0e0;
}
.arrow-btn:disabled {
  background: #f5f5f5;
  color: #bbb;
  border-color: #eee;
  cursor: not-allowed;
}

/*
 Hide spin buttons in number input
*/
input[type=number]::-webkit-inner-spin-button, 
input[type=number]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>
