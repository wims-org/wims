<template>
  <div
    class="form-group d-flex align-items-center justify-content-between flex-wrap p-2"
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
import { defineComponent } from 'vue'
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
  data() {
    return {
      showModal: false,
    }
  },
  methods: {
    updateField(event: Event) {
      const target = event.target as HTMLInputElement
      this.$emit('update:value', target.value)
    },

    openModal() {
      this.showModal = true
    },

    closeModal() {
      this.showModal = false
    },

    handleSelect(tag: string) {
      if (this.disabled) return
      console.log('Selected tag:', tag)
      this.$emit('update:value', tag)
      this.closeModal()
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
