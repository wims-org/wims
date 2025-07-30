<template>
    <BContainer class="mt-4">
        <BCard>
            <BCardTitle>{{ isEditing ? "Edit Query" : "Create Query" }}</BCardTitle>
            <BCardBody>
                <BForm @submit.prevent="submitQuery">
                    <BFormGroup label="Query Name:" label-for="name">
                        <BForm-input id="name" v-model="query.name" required
                            placeholder="Enter query name"></BForm-input>
                    </BFormGroup>

                    <BFormGroup label="Description:" label-for="description">
                        <BFormTextarea id="description" v-model="query.description"
                            placeholder="Enter query description"></BFormTextarea>
                    </BFormGroup>

                    <BFormGroup label="Query (JSON):" label-for="query">
                    <BFormTextarea id="query" v-model="queryInput" required
                        placeholder="Enter MongoDB query as JSON" rows="5"></BFormTextarea>
                    </BFormGroup>

                    <BButton type="button" @click="submitQuery" variant="primary" class="mt-3">
                        {{ isEditing ? "Update Query" : "Create Query" }}
                    </BButton>
                </BForm>

                <BAlert v-if="errorMessage" variant="danger" dismissible class="mt-3">
                    {{ errorMessage }}
                </BAlert>
                <BAlert v-if="successMessage" variant="success" dismissible class="mt-3">
                    {{ successMessage }}
                </BAlert>
            </BCardBody>
        </BCard>
    </BContainer>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue'
import axios from 'axios'
import type { Query } from '@/interfaces/queries'
import { logger } from '@sentry/vue'

const props = defineProps<{
  existingQuery?: Query | null
}>()

const emit = defineEmits<{
  (e: 'update:query', query: Query): void
}>()

const query = ref<Omit<Query, 'query'>>({
  _id: '',
  name: '',
  description: '',
})
const queryInput = ref('')
const isEditing = ref(false)
const errorMessage = ref<string | null>(null)
const successMessage = ref<string | null>(null)

if (props.existingQuery) {
  query.value = {
    _id: props.existingQuery._id || '',
    name: props.existingQuery.name || '',
    description: props.existingQuery.description ?? '',
  }
  queryInput.value = typeof props.existingQuery.query === 'string'
    ? props.existingQuery.query
    : JSON.stringify(props.existingQuery.query ?? {}, null, 2)
  isEditing.value = true
}

async function submitQuery(): Promise<void> {
  try {
    errorMessage.value = null
    successMessage.value = null
    let parsedQuery
    try {
      const input = queryInput.value
        .replace(/'/g, '"')
        .replace(/,\s*}/g, '}')
        .replace(/,\s*]/g, ']')
      parsedQuery = JSON.parse(input)
    } catch (e) {
      logger.error('Invalid JSON format in query {e}', { e })
      if (e instanceof Error) {
        errorMessage.value = 'Invalid JSON format in query. Please check your input.' + (e.message ?? '')
      }
      return
    }
    const submit_query: Query = { ...query.value, query: parsedQuery }
    console.log('Submitting query:', submit_query)

    const endpoint = isEditing.value
      ? `/queries/${query.value._id}`
      : '/queries'

    const method = isEditing.value ? 'put' : 'post'

    const response = await axios[method](endpoint, submit_query)
    query.value = {
      _id: response.data._id,
      name: response.data.name,
      description: response.data.description,
    }
    queryInput.value = JSON.stringify(response.data.query, null, 2)
    successMessage.value = isEditing.value
      ? 'Query updated successfully!'
      : 'Query created successfully!'
    emit('update:query', response.data)
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      errorMessage.value =
        error.response?.data?.detail || 'An error occurred while saving the query.'
    } else {
      errorMessage.value = 'An unexpected error occurred.'
    }
  }
}
</script>

<style scoped>
.mt-4 {
    margin-top: 1.5rem;
}
</style>