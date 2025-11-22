<template>
  <BContainer>
    <BFormGroup class="d-flex align-items-center p-2 justify-content-between" data-testid="number-field">
      <label v-if="!hideLabel || !label" :for="name" class="me-2">{{ label }}</label>
      <div class="d-flex align-items-center">
        <BFormInput
          :id="name"
          type="number"
          :name="name"
          :disabled="disabled ?? undefined"
          :modelValue="(value as any)"
          @update:modelValue="onModelUpdate"
          :required="required"
          class="text-center"
          style="width: 80px"
        />
        <BButton size="sm" class="arrow-btn" :disabled="disabled" @click="decrement" aria-label="Decrease">-</BButton>
        <BButton size="sm" class="arrow-btn" :disabled="disabled" @click="increment" aria-label="Increase">+</BButton>
      </div>
    </BFormGroup>
  </BContainer>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import { BFormInput, BFormGroup, BButton } from 'bootstrap-vue-next'

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  label: {
    type: String,
    default: '',
  },
  value: {
    type: [String, Number, null],
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

const emit = defineEmits<{ (e: 'update:value', value: number | null): void }>()

function onModelUpdate(v: string | number | null) {
  emit('update:value', v === null ? null : Number(v))
}

function increment() {
  if (props.disabled) return
  let val = Number(props.value) || 0
  val++
  emit('update:value', val)
}

function decrement() {
  if (props.disabled) return
  let val = Number(props.value) || 0
  val--
  emit('update:value', val)
}
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
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  color: var(--primary-text-color);
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
  background: var(--hover-bg);
}

.arrow-btn:disabled {
  background: var(--card-bg);
  color: var(--color-muted);
  border-color: var(--border-color);
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
