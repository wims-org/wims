<template>
  <div
    class="form-group d-flex align-items-center flex-wrap pills-container p-2"
    data-testid="array-field"
  >
    <span v-if="!hideLabel" :for="name" class="mr-auto">{{ label }}</span>
    <span v-for="(item, index) in value" :key="index" class="pill" data-testid="pill">
      {{ item }}
      <button type="button" @click="removeItem(index)" class="pill-remove">&times;</button>
    </span>
    <input
      v-if="!disabled"
      type="text"
      v-model="newItem"
      :disabled="disabled"
      @keyup.enter="addItem()"
      class="form-control"
      :class="{ 'borderless-input': borderless }"
      :placeholder="hideLabel ? '' : 'Add item'"
      :required="!value.length && required"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import type { PropType } from 'vue'

export default defineComponent({
  name: 'ArrayField',
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
      type: Array as PropType<string[]>,
      default: () => [],
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
  setup(props, { emit }) {
    const newItem = ref('')

    const addItem = () => {
      if (newItem.value.trim() !== '') {
        emit('update:value', [
          ...props.value,
          ...newItem.value
            .trim()
            .split(new RegExp(',|;'))
            .map((item) => item.trim()),
        ])
        newItem.value = ''
      }
    }

    const removeItem = (index: number) => {
      const newValue = [...props.value]
      newValue.splice(index, 1)
      emit('update:value', newValue)
    }

    return {
      newItem,
      addItem,
      removeItem,
    }
  },
})
</script>

<style scoped>
.pills-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.2rem;
  margin-bottom: 10px;
}

.pill {
  display: flex;
  align-items: center;
  background-color: #e0e0e0;
  border-radius: 15px;
  padding: 5px 10px;
}

.pill-remove {
  background: none;
  border: none;
  font-size: 1.2em;
  margin-left: 5px;
  cursor: pointer;
}

.borderless-input {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 0.1rem 0.2rem !important;
  min-width: 0;
}
.borderless label {
  display: none !important;
}
</style>
