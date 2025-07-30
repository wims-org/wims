<template>
  <BContainer>
    <div class="form-group d-flex align-items-center justify-content-between flex-wrap p-2" data-testid="modal-field">
      <label v-if="!hideLabel || !label" :for="name">{{ label }}</label>
      <input type="text" :name="name" :disabled="disabled" :value="value" @input="updateField" @click="openModal"
        class="form-control" :class="[{ 'is-invalid': required && !value }, { 'borderless-input': borderless }]"
        :placeholder="hideLabel ? '' : 'click to open search'" />
      <SearchModal :show="showModal" @close="closeModal" @select="handleSelect" />
    </div>
  </BContainer>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue'
import SearchModal from '@/components/shared/SearchModal.vue'

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
    type: String,
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

const showModal = ref(false)

function updateField(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:value', target.value)
}

function openModal() {
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

function handleSelect(tag: string) {
  if (props.disabled) return
  emit('update:value', tag)
  closeModal()
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
</style>
