<template>
  <BContainer>
    <BCol>
      <BRow>
        <BCol>
          <BRow>
            <label for="stringInput" class="form-label">Text Input</label>
            <input type="text" id="stringInput" class="form-control" v-model="stringInput"
              placeholder="Add Item by Description or Name..." />
          </BRow>
        </BCol>
        <BCol>
          <BRow>
            <ImageThumbnailField :label="'Upload Images'" :value="uploadedImages" @update:value="updateImage($event)" />
          </BRow>
          <BRow v-if="images && images.length > 0">
            <ImageThumbnailField :label="'Select existing Images'" :value="images" disabled selector
              @update:selectedImages="selectedImages = $event" />
          </BRow>
        </BCol>
      </BRow>
      <button type="button" class="btn btn-primary" @click="fetchIdentification()" :disabled="requestInProgress ||
        (uploadedImages.length === 0 && !stringInput && selectedImages.length === 0)
        ">
        <span v-if="requestInProgress"><font-awesome-icon icon="spinner" spin /> Processing...</span>
        <span v-else>Start Identification</span>
      </button>
      <div v-if="requestError" class="alert alert-danger mt-3">
        Error processing request. Please try again. {{ requestError }}
      </div>
    </BCol>
    <hr />
  </BContainer>
</template>

<script setup lang="ts">
import { clientStore } from '@/stores/clientStore'
import axios from 'axios'
import { ref, onMounted } from 'vue'
import ImageThumbnailField from '@/components/fields/ImageThumbnailField.vue'
import eventBus, { type Events } from '../stores/eventBus'
import { EventAction } from '@/interfaces/EventAction'
import type { File } from '@/interfaces/file.interface'

const props = defineProps<{
  description?: string
  images?: Array<File>
}>()

const stringInput = ref(props.description || '')
const uploadedImages = ref<File[]>([])
const selectedImages = ref<File[]>([])
const requestInProgress = ref(false)
const requestError = ref<string>()

onMounted(() => {
  if (clientStore().backend_config.llm_enabled === false) {
    return
  }

})

eventBus.on(EventAction.IDENTIFICATION, (data: Events[EventAction.IDENTIFICATION]) => {
  requestError.value = ''
  console.log('Identification event received:', data)
  requestInProgress.value = false
})
eventBus.on(EventAction.ERROR, (data: Events[EventAction.ERROR]) => {
  requestError.value = data?.data?.message
  requestInProgress.value = false
})

const fetchIdentification = async () => {
  try {
    if (requestInProgress.value) {
      console.warn('Request already in progress, ignoring new request')
      return
    }
    requestInProgress.value = true

    const body = {
      query: stringInput.value,
      client_id: clientStore().client_id,
      file_ids: [...uploadedImages.value, ...selectedImages.value].map((f) => f.id),
    }
    const response = await axios.post('/identification', body)
    console.log({ ...response.data })
  } catch (error) {
    console.error('Error posting ident data:', error)
    requestError.value = error instanceof Error ? error.message : 'Unknown error'
    requestInProgress.value = false
  }
}

const updateImage = (updatedValue: Array<File>) => {
  uploadedImages.value.length = 0 // Clear the existing array
  uploadedImages.value.push(...updatedValue) // Add the new URLs
}
</script>

<style scoped>
.wrap {
  display: block;
  overflow: hidden;
  border: 1px solid var(--border-color);
  width: 450px;
  height: 250px;
}

iframe {
  -ms-transform: scale(0.25);
  -moz-transform: scale(0.25);
  -o-transform: scale(0.25);
  -webkit-transform: scale(0.25);
  transform: scale(0.25);
  transform-origin: 0 0;
  width: 1600px;
  height: 900px;
  position: absolute;
  border: 0;
}
</style>
