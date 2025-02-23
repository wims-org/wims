
<template>
  <div class="form-group">
    <label :for="name">{{ label }}</label>
    <textarea
      :name="name"
      :disabled="disabled"
      :value="value"
      @input="updateField"
      class="form-control"
      :class="{ 'is-invalid': required && !value }"
    ></textarea>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'TextAreaField',
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
      default: '',
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
  methods: {
    updateField(event: Event) {
      const target = event.target as HTMLTextAreaElement;
      this.$emit('update:value', target.value);
    },
  },
});
</script>