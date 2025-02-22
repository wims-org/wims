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
      <div class="form-group" v-for="(field, key) in formFields" :key="key"
        v-show="!field.hidden && (!field.details || (showDetails && field.details))">
        <label :for="String(key)">{{ field.label || key }}</label>
        <input v-if="field.type !== 'textarea' && field.type !== 'object' && field.type !== 'loading'"
          :type="field.type || 'text'" :name="String(key)" :disabled="field.disabled ?? undefined"
          :value="getFieldModel(String(key), field.type)" :required="field.required"
          @input="updateFieldModel($event, String(key), field.type)" @click="handleInputClick(key)" class="form-control"
          :class="{ 'is-invalid': field.required && !item[key] }" />
        <div v-else-if="field.type === 'object'" class="card p-3">
          <div v-for="(subValue, subKey) in item[key]" :key="subKey" class="form-group"
            v-show="subValue !== null && subValue !== undefined">
            <label :for="`${key}-${subKey}`">{{ subKey }}</label>
            <input :type="typeof subValue === 'number' ? 'number' : 'text'" :name="`${key}-${subKey}`" :value="subValue"
              :disabled="field.disabled ?? undefined"
              @input="updateFieldModel($event, `${key}.${subKey}`, typeof subValue)" class="form-control" />
          </div>
        </div>
        <div v-else-if="field.type === 'loading'" class="card">
          <div class="d-flex flex-column justify-content-center align-items-center" style="height: 100px;">
            <div class="m-2 spinner-border text-primary" role="status"> </div>
            <span>Container will be fetched after saving...</span>
          </div>
        </div>
        <textarea v-else :name="String(key)" :disabled="field.disabled ?? undefined" :v-model="item[key]"
          class="form-control" :class="{ 'is-invalid': field.required && !item[key] }"></textarea>
      </div>
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
    <SearchModal :show="showModal" @close="closeModal" @select="handleSelect" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';
import { formFields } from '@/interfaces/FormField.interface';
import SearchModal from './SearchModal.vue';
import { EventAction } from '@/interfaces/EventAction';
import { clientStore as useClientStore } from '@/stores/clientStore';
// import { getFieldModel, updateFieldModel } from '@/utils';

export default defineComponent({
  name: 'ItemForm',
  components: {
    SearchModal,
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
    const formData = ref<{ [x: string]: unknown; }>({ ...props.item }); // form data is the live data in the form
    const showModal = ref(false);
    const clientStore = useClientStore();

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

    const updateFieldModel = (event: Event, key: string, type: string) => {
      const target = event.target as HTMLInputElement;
      if (type === 'checkbox') {
        formData.value[key] = target.checked;
      } else if (type === 'epoch') {
        formData.value[key] = new Date(target.value).getTime() / 1000;
      } else if (type === 'number') {
        formData.value[key] = Number(target.value);
      } else if (type === 'array') {
        formData.value[key] = target.value.split(',|;').map(item => item.trim());
      } else {
        formData.value[key] = target.value;
      }
    };

    const handleInputClick = (key: string) => {
      if (key === 'container_tag_uuid') {
        showModal.value = true;
      }
    };

    const handleSelect = (tag: string) => {
      formData.value.container_tag_uuid = tag;
      formFields.container.type = 'loading'; // show loading spinner
    };

    const closeModal = () => {
      showModal.value = false;
      clientStore.expected_event_action = EventAction.REDIRECT
    };

    return {
      formData,
      formFields,
      showDetails,
      toggleDetails,
      handleSubmit,
      getFieldModel,
      updateFieldModel,
      showModal,
      handleInputClick,
      handleSelect,
      closeModal,
    };
  },
});
</script>

<style scoped>
.sub-fields {
  margin-left: 20px;
}
</style>
