<template>
  <div class="container mt-5" ref="itemForm">
    <div class="row mb-3">
      <button @click="toggleDetails" class="btn btn-secondary mt-3 mr-auto">
        {{ showDetails ? 'Hide Details' : 'Show Details' }}
      </button>
      <button @click="handleSubmit" class="btn btn-primary mt-3">Submit</button>
    </div>
    <h1 class="mb-4">{{ item.short_name }}</h1>
    <form v-if="item && formData" @submit.prevent="handleSubmit">
      <component
        v-for="(field, key) in formFields"
        :is="getFieldComponent(field.type)"
        :key="key"
        :name="String(key)"
        :label="field.label || key"
        :value="formData[key]"
        :disabled="field.disabled ?? undefined"
        :required="field.required"
        @update:value="updateFieldModel($event, String(key), field.type)"
        v-show="!field.hidden && (!field.details || (showDetails && field.details))"
      />
      <button type="submit" class="btn btn-primary mt-3">Submit</button>
    </form>
    <div v-else>
      <p>Error loading item details. Please try again later.</p>
    </div>
    <div v-if="Array.isArray(item.errors) && item.errors.length" class="alert alert-danger mt-3">
      <p>There were errors in the data model from the database:</p>
      <ul>
        <li v-for="(error, index) in item.errors" :key="index">{{ error }}</li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';
import { formFields } from '@/interfaces/FormField.interface';
import TextField from '@/components/fields/TextField.vue';
import TextAreaField from '@/components/fields/TextAreaField.vue';
import ObjectField from '@/components/fields/ObjectField.vue';
import LoadingField from '@/components/fields/LoadingField.vue';
import CheckboxField from '@/components/fields/CheckboxField.vue';
import ArrayField from '@/components/fields/ArrayField.vue';
import ModalField from '@/components/fields/ModalField.vue';
import NumberField from '@/components/fields/NumberField.vue';
import ImageThumbnailField from '@/components/fields/ImageThumbnailField.vue';

export default defineComponent({
  name: 'ItemForm',
  components: {
    TextField,
    TextAreaField,
    ObjectField,
    LoadingField,
    CheckboxField,
    ArrayField,
    ModalField,
    NumberField,
    ImageThumbnailField,
  },
  props: {
    item: {
      type: Object as () => Record<string, unknown>,
      required: true,
    },
    newItem: {
      type: Boolean,
      required: true,
    },
  },
  setup(props, { emit }) {
    const formData = ref<{ [x: string]: unknown | undefined; }>({ ...props.item }); // form data is the live data in the form

    watch(
      () => props.item,
      (newItem) => {
        formData.value = { ...newItem };
      },
      { immediate: true, deep: true }
    );

    const showDetails = ref(false);

    const toggleDetails = () => {
      showDetails.value = !showDetails.value;
    };

    const handleSubmit = () => {
      emit('submit', formData.value);
      formFields.container.type = 'object'; // After saving, the container will be fetched
    };

    const getFieldComponent = (type: string) => {
      switch (type) {
        case 'textarea':
          return 'TextAreaField';
        case 'object':
          return 'ObjectField';
        case 'loading':
          return 'LoadingField';
        case 'checkbox':
          return 'CheckboxField';
        case 'array':
          return 'ArrayField';
        case 'uuid':
          return 'ModalField';
        case 'number':
          return 'NumberField';
        case 'images':
          return 'ImageThumbnailField';
        default:
          return 'TextField';
      }
    };

    const formatDate = (timestamp: number): string => {
      if (!timestamp) return '';
      const date = new Date(timestamp * 1000);
      return isNaN(date.getTime()) ? '' : date.toISOString().split('T')[0];
    };

    const getFieldModel = (key: string, type: string) => {
      if (type === 'checkbox') {
        return formData.value[key] ? 'checked' : '';
      } else if (type === 'epoch') {
        return formatDate(formData.value[key] as number);
      }
      return formData.value[key];
    };

    const updateFieldModel = (value: unknown, key: string, type: string) => {
      if (type === 'checkbox') {
        formData.value[key] = Boolean(value);
      } else if (type === 'epoch') {
        formData.value[key] = new Date(value as string).getTime() / 1000;
      } else if (type === 'number') {
        formData.value[key] = Number(value);
      } else if (type === 'array') {
        formData.value[key] = (value as string).split(',|;').map(item => item.trim());
      } else { // text uuid object 
        formData.value[key] = value;
      }
    };

    const removeImage = (index: number) => {
      if (!Array.isArray(formData.value.imageUrls)) return;
      formData.value.imageUrls.splice(index, 1);
    };

    return {
      formData,
      formFields,
      showDetails,
      toggleDetails,
      handleSubmit,
      getFieldComponent,
      getFieldModel,
      updateFieldModel,
      removeImage,
    };
  },
});
</script>

<style scoped>
.sub-fields {
  margin-left: 20px;
}
</style>
