<template>
  <div
    class="form-group"
    data-testid="modal-field"
  >
    <label v-if="!hideLabel" :for="name">{{ label }}</label>
    <input
      type="text"
      :name="name"
      :disabled="disabled"
      :value="value"
      @input="updateField"
      @click="openModal"
      class="form-control"
      :class="[{ 'is-invalid': required && !value }, { 'borderless-input': borderless }]"
      :placeholder="hideLabel ? '' : 'click to open search'"
    />
    <SearchModal :show="showModal" @close="closeModal" @select="handleSelect" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import SearchModal from '@/components/shared/SearchModal.vue'

export default defineComponent({
  name: 'ModalField',
  components: {
    SearchModal,
  },
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
      type: String,
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
  setup(props, { emit }) {
    const showModal = ref(false)

    const updateField = (event: Event) => {
      const target = event.target as HTMLInputElement
      emit('update:value', target.value)
    }

    const openModal = () => {
      showModal.value = true
    }

    const closeModal = () => {
      showModal.value = false
    }

    const handleSelect = (tag: string) => {
      emit('update:value', tag)
      closeModal()
    }

    return {
      showModal,
      updateField,
      openModal,
      closeModal,
      handleSelect,
    }
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
