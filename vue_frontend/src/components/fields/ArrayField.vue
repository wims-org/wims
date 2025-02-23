<template>
  <div class="form-group">
    <label :for="name">{{ label }}</label>
    <div class="pills-container">
      <span v-for="(item, index) in value" :key="index" class="pill">
        {{ item }}
        <button type="button" @click="removeItem(index)" class="pill-remove">&times;</button>
      </span>
    </div>
    <input
      type="text"
      v-model="newItem"
      :disabled="disabled"
      @keyup.enter="addItem"
      class="form-control"
      placeholder="Add item"
      :required="!value.length && required || undefined"
        />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import type { PropType } from 'vue';

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
  },
  emits: ['update:value'],
  setup(props, { emit }) {
    const newItem = ref('');

    const addItem = () => {
      if (newItem.value.trim() !== '') {
        emit('update:value', [...props.value, newItem.value.trim()]);
        newItem.value = '';
      }
    };

    const removeItem = (index: number) => {
      const newValue = [...props.value];
      newValue.splice(index, 1);
      emit('update:value', newValue);
    };

    return {
      newItem,
      addItem,
      removeItem,
    };
  },
});
</script>

<style scoped>
.pills-container {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
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
</style>