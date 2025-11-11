<template>
  <BContainer>
    <BRow align-v="center">
      <BCol>
        <span v-if="!hideLabel || !label" :for="name" class="mr-auto">{{ label }}</span>
      </BCol>
      <BCol cols="12" md="auto">
        <div class="pills-wrapper">
          <span v-for="(item, index) in currentValue" :key="index" class="pill" data-testid="pill">
            {{ item }}
            <button type="button" @click="removeItem(index)" class="pill-remove" title="Remove item">&times;</button>
          </span>
        </div>
      </BCol>
      <BCol>
        <BInputGroup v-if="!disabled" class="borderless-input flex-nowrap">
          <BInput
            v-model="newItem"
            :disabled="disabled"
            @keydown.enter.prevent="addItem"
            placeholder="Add items separated by ,"
            :class="{ 'borderless-input': borderless }"
          />
          <BButton :disabled="!newItem.trim()" @click="addItem" title="Add items">
            <font-awesome-icon icon="fa-solid fa-plus" />
          </BButton>
        </BInputGroup>
      </BCol>
    </BRow>
  </BContainer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { PropType } from 'vue';

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
    type: Array as PropType<string[] | null>,
    default: null,
  },
  disabled: {
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
});

const emit = defineEmits(['update:value']);

const newItem = ref('');
const currentValue = computed(() => props.value ?? []);

const addItem = () => {
  if (newItem.value.trim() !== '') {
    const itemsToAdd = newItem.value
      .trim()
      .split(new RegExp(',|;'))
      .map((item) => item.trim())
      .filter((item) => item !== '');

    const base = props.value ? [...props.value] : [];
    emit('update:value', [...base, ...itemsToAdd]);
    newItem.value = '';
  }
};

const removeItem = (index: number) => {
  const base = props.value ? [...props.value] : [];
  base.splice(index, 1);
  // emit null when list becomes empty to allow explicit null state if desired
  emit('update:value', base.length ? base : null);
};
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
