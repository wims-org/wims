<template>


  <BContainer>
    <BRow align-v="center">
      <BCol>
        <span v-if="!hideLabel || !label" :for="name" class="mr-auto">{{ label }}</span>
      </BCol>
      <BCol cols="12" md="auto">
        <div class="pills-wrapper">
          <span v-for="(item, index) in value" :key="index" class="pill" data-testid="pill">
            {{ item }}
            <button type="button" @click="removeItem(index)" class="pill-remove" title="Remove item">&times;</button>
          </span>
        </div>
      </BCol>
      <BCol sm=7>
        <BInputGroup v-if="!disabled" class="borderless-input flex-nowrap">
          <BInput v-model="newItem" :disabled="disabled" @keydown.enter.prevent="addItem"
            placeholder="Add items separated by ," :class="{ 'borderless-input': borderless }"
            :required="!value.length && required" />
          <BButton :disabled="!newItem.trim()" @click="addItem" title="Add items"><font-awesome-icon
              icon="fa-solid fa-plus" /></BButton>
        </BInputGroup>
      </BCol>
    </BRow>
  </BContainer>
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
      default: '',
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
        const itemsToAdd = newItem.value
          .trim()
          .split(new RegExp(',|;'))
          .map((item) => item.trim())
          .filter((item) => item !== '')

        emit('update:value', [...props.value, ...itemsToAdd])
        newItem.value = '' // Clear the input after adding items
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
  justify-content: space-between;
}

.pills-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 0.2rem;
}

.pill {
  display: flex;
  align-items: center;
  background-color: #e0e0e0;
  border-radius: 15px;
  padding: 0px .75rem;
}

.pill-remove {
  background: none;
  border: none;
  font-size: 1.2em;
  margin: 0;
  cursor: pointer;
}

.borderless-input {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 0.1rem 0.2rem !important;
  min-width: 0;
}
</style>
