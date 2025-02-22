<template>
  <div class="container mt-5" ref="itemForm">
    <button @click="toggleDetails" class="btn btn-secondary mb-3">
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
            <!-- && (!field.details || (showDetails && field.details))"> // dont exclude details with changes-->
            <td>
              <label>{{ field.label || key }}</label>
              <input
                v-if="
                  field.type !== 'textarea' && field.type !== 'object' && field.type !== 'loading'
                "
                :type="field.type || 'text'"
                :name="String(key)"
                :disabled="field.disabled ?? undefined"
                :value="getFieldModel(formData_org, String(key), field.type)"
                :required="field.required"
                @input="updateFieldModel(formData_org, $event, String(key), field.type)"
                @click="handleInputClick(key)"
                class="form-control"
                :class="{ 'is-invalid': field.required && !item_org[key] }"
              />
              <div v-else-if="field.type === 'object'" class="card p-3">
                <div
                  v-for="(subValue, subKey) in item_org[key]"
                  :key="subKey"
                  class="form-group"
                  v-show="subValue !== null && subValue !== undefined"
                >
                  <label :for="`${key}-${subKey}`">{{ subKey }}</label>
                  <input
                    :type="typeof subValue === 'number' ? 'number' : 'text'"
                    :name="`${key}-${subKey}`"
                    :value="subValue"
                    :disabled="field.disabled ?? undefined"
                    @input="
                      updateFieldModel(formData_org, $event, `${key}.${subKey}`, typeof subValue)
                    "
                    class="form-control"
                  />
                </div>
              </div>
              <div v-else-if="field.type === 'loading'" class="card">
                <div
                  class="d-flex flex-column justify-content-center align-items-center"
                  style="height: 100px"
                >
                  <div class="m-2 spinner-border text-primary" role="status">
                    <font-awesome-icon icon="spinner" spin />
                  </div>
                  <span>Container will be fetched after saving...</span>
                </div>
              </div>
              <textarea
                v-else
                :name="String(key)"
                :disabled="field.disabled ?? undefined"
                :v-model="item_org[key]"
                class="form-control"
                :class="{ 'is-invalid': field.required && !item_org[key] }"
              ></textarea>
            </td>
            <td class="text-center">
              <button
                type="button"
                @click="() => (formData_org[key] = formData_new[key])"
                class="btn btn-primary mt-3"
                :disabled="
                  !(key in formData_new) ||
                  formData_new[key] == null ||
                  formData_org[key] == formData_new[key]
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
import SearchModal from './SearchModal.vue'
import { EventAction } from '@/interfaces/EventAction'
import { clientStore as useClientStore } from '@/stores/clientStore'
import { getFieldModel, updateFieldModel } from '@/utils'

export default defineComponent({
  name: 'ItemComparison',
  components: {
    SearchModal,
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

    console.log(formData_org)
    console.log(props)
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

    return {
      formData_org,
      formData_new,
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
      applyNewValuesToOrg,
    }
  },
})
</script>

<style scoped>
.sub-fields {
  margin-left: 20px;
}
</style>
