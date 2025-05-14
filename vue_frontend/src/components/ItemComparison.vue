<template>
  <div class="container mt-5" ref="itemForm">
    <button @click="toggleDetails" class="btn btn-secondary mb-3" data-testid="toggle-details-button">
      {{ showDetails ? 'Hide Details' : 'Show Details' }}
    </button>
    <h1 class="mb-4">Compare {{ item_org.short_name }}</h1>
    <form v-if="item_org && formData_org" @submit.prevent="handleSubmit">
      <div class="row p-2 justify-content-between align-items-center">
        <div class="col-2">Old Value</div>
        <button type="button" class="btn btn-primary mt-3" @click="applyNewValuesToOrg">
          <font-awesome-icon icon="arrow-left" />
          <font-awesome-icon icon="arrow-left" />
          <span class="ml-1">Apply All</span>
        </button>
        <div class="col-2">New Value</div>
      </div>
      <table class="table table-bordered">
        <tbody>
          <tr
            v-for="(field, key) in formFields"
            :key="key"
            :class="{
              'table-danger':
                key in formData_new &&
                formData_new[key] != null &&
                formData_org[key] !== formData_new[key],
            }"
            v-show="!field.hidden"
          >
            <td>
              <component
                :is="getFieldComponent(field.type)"
                :name="String(key)"
                :label="field.label || key"
                :value="formData_org[key]"
                :disabled="field.disabled ?? undefined"
                :required="field.required"
                @update:value="updateFieldModel($event, String(key), field.type)"
                @click="handleInputClick(key)"
                :class="{ 'is-invalid': field.required && !item_org[key] }"
              />
            </td>
            <td class="text-center">
              <button
                type="button"
                @click="() => (formData_org[key] = formData_new[key])"
                class="btn btn-primary mt-3"
                :disabled="
                  (!(key in formData_new) ||
                  formData_new[key] == null ||
                  formData_org[key] == formData_new[key]) ?? undefined
                "
              >
                <font-awesome-icon
                  v-if="
                    key in formData_new &&
                    formData_new[key] != null &&
                    formData_org[key] != formData_new[key]
                  "
                  icon="arrow-left"
                />
                <font-awesome-icon v-else icon="equals" />
              </button>
              <button
                type="button"
                :v-if="formData_new[key]"
                @click="formData_new[key]?copyToClipboard(formData_new[key]):''"
                class="btn btn-secondary mt-3"
              >
                <font-awesome-icon icon="clipboard" />
              </button>
            </td>
            <td>{{ getFieldModel(formData_new, String(key), field.type) }}</td>
          </tr>
        </tbody>
      </table>
      <button type="submit" class="btn btn-primary mt-3">Submit</button>
    </form>
    <div v-else>
      <p>Error loading item details. Please try again later.</p>
    </div>
    <div
      v-if="Array.isArray(item_org.errors) && item_org.errors.length"
      class="alert alert-danger mt-3"
    >
      <p>There were errors in the data model from the database:</p>
      <ul>
        <li v-for="(error, index) in item_org.errors" :key="index">{{ error }}</li>
      </ul>
    </div>
    <SearchModal :show="showModal" @close="closeModal" @select="handleSelect" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue'
import { formFields } from '@/interfaces/FormField.interface'
import SearchModal from '@/components/shared/SearchModal.vue'
import { EventAction } from '@/interfaces/EventAction'
import { clientStore as useClientStore } from '@/stores/clientStore'
import { getFieldModel } from '@/utils'
import TextField from '@/components/fields/TextField.vue'
import TextAreaField from '@/components/fields/TextAreaField.vue'
import ObjectField from '@/components/fields/ObjectField.vue'
import LoadingField from '@/components/fields/LoadingField.vue'
import CheckboxField from '@/components/fields/CheckboxField.vue'
import ArrayField from '@/components/fields/ArrayField.vue'
import ModalField from '@/components/fields/ModalField.vue'
import NumberField from '@/components/fields/NumberField.vue'
import ImageThumbnailField from '@/components/fields/ImageThumbnailField.vue'

export default defineComponent({
  name: 'ItemComparison',
  components: {
    SearchModal,
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
    item_org: {
      type: Object as () => Record<string, unknown>,
      required: true,
    },
    item_new: {
      type: Object as () => Record<string, unknown>,
      required: true,
    },
    newItem: {
      type: Boolean,
      required: true,
    },
  },
  setup(props, { emit }) {
    const formData_org = ref<{ [x: string]: unknown }>({ ...props.item_org }) // form data is the live data in the form
    const formData_new = ref<{ [x: string]: unknown }>({ ...props.item_new })
    const showModal = ref(false)
    const clientStore = useClientStore()

    watch(
      () => props.item_org,
      (item_org) => {
        formData_org.value = { ...item_org }
      },
      { immediate: true, deep: true },
    )
    watch(
      () => props.item_new,
      (item_new) => {
        formData_new.value = { ...item_new }
      },
      { immediate: true, deep: true },
    )

    const showDetails = ref(false)

    const toggleDetails = () => {
      showDetails.value = !showDetails.value
    }

    const handleSubmit = () => {
      emit('submit', formData_org.value)
      formFields.container.type = 'object' // After saving, the container will be fetched
    }

    const handleInputClick = (key: string) => {
      if (key === 'container_tag_uuid') {
        showModal.value = true
      }
    }

    const handleSelect = (tag: string) => {
      formData_org.value.container_tag_uuid = tag
      formFields.container.type = 'loading' // show loading spinner
    }

    const closeModal = () => {
      showModal.value = false
      clientStore.expected_event_action = EventAction.REDIRECT
    }

    const applyNewValuesToOrg = () => {
      for (const key in formData_new.value) {
        if (formData_new.value[key] !== undefined && formData_new.value[key] !== null) {
          formData_org.value[key] = formData_new.value[key]
        }
      }
    }

    const getFieldComponent = (type: string) => {
      switch (type) {
        case 'textarea':
          return 'TextAreaField'
        case 'object':
          return 'ObjectField'
        case 'loading':
          return 'LoadingField'
        case 'checkbox':
          return 'CheckboxField'
        case 'array':
          return 'ArrayField'
        case 'uuid':
          return 'ModalField'
        case 'images':
          return 'ImageThumbnailField'
        case 'number':
          return 'NumberField'
        default:
          return 'TextField'
      }
    }

    const updateFieldModel = (value: unknown, key: string, type: string) => {
      console.log('updateFieldModel', value, key, type)
      if (type === 'checkbox') {
        formData_org.value[key] = Boolean(value)
      } else if (type === 'epoch') {
        formData_org.value[key] = new Date(value as string).getTime() / 1000
      } else if (type === 'number') {
        formData_org.value[key] = Number(value)
      } else if (type === 'array') {
        formData_org.value[key] = (value as string).split(',|;').map((item) => item.trim())
      } else {
        // text uuid object
        formData_org.value[key] = value
      }
    }
    const copyToClipboard = (value: string | unknown | undefined ) => {
      if (value && typeof value == 'string') navigator.clipboard.writeText(value)
    }
    return {
      formData_org,
      formData_new,
      formFields,
      showDetails,
      toggleDetails,
      handleSubmit,
      getFieldComponent,
      getFieldModel,
      updateFieldModel,
      showModal,
      handleInputClick,
      handleSelect,
      closeModal,
      applyNewValuesToOrg,
      copyToClipboard,
    }
  },
})
</script>

<style scoped>
.sub-fields {
  margin-left: 20px;
}
</style>
