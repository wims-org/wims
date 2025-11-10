<template>
  <div class="container">
    <div class="col border p-3">
      <div class="row p-2 justify-content-between align-items-center">
        <input
          type="text"
          class="form-control"
          v-model="stringInput"
          placeholder="Add Item by Description or Name..."
        />
        <div class="p-2" v-if="clientStore().backend_config?.camera_enabled">
          <div @click="() => (useCam = !useCam)">
            <font-awesome-icon
              :icon="!useCam ? 'chevron-up' : 'chevron-down'"
              aria-label="Toggle Cam"
            />
            Use Cam
          </div>
          <div v-if="webCamUrl && useCam">
            <div>
              <font-awesome-icon icon="camera" aria-label="Camera" />Webcam camera is currenly not
              working and under development.
            </div>
            <div class="wrap mb-2">
              <iframe id="scaled-frame" :src="webCamUrl" />
            </div>

            <button type="button" class="btn btn-secondary" @click="takePhoto()">Take Photo</button>
          </div>
          <div v-else class="d-flex mt-3 ml-0 col-12 justify-content-between">
            <input
              ref="fileInput"
              type="file"
              class="form-control-file d-none"
              @change="uploadPhoto"
            />
            <input
              ref="cameraInput"
              type="file"
              class="form-control-file d-none"
              accept="image/*"
              capture="environment"
              @change="uploadPhoto"
            />
          </div>
        </div>
      </div>
      <div class="row mt-3">
        <h5>Upload Images:</h5>
        <ImageThumbnailField :value="uploadedImages" @update:value="updateImage($event)" />
      </div>
      <div class="row mt-3" v-if="images && images.length > 0">
        <h5>Select existing Images:</h5>
        <ImageThumbnailField
          :value="images"
          disabled
          selector
          @update:selectedImages="selectedImages = $event"
        />
      </div>

      <button
        type="button"
        class="btn btn-primary"
        @click="fetchIdentification()"
        :disabled="
          requestInProgress ||
          (uploadedImages.length === 0 && !stringInput && selectedImages.length === 0)
        "
      >
        <span v-if="requestInProgress"
          ><font-awesome-icon icon="spinner" spin /> Processing...</span
        >
        <span v-else>Start Identification</span>
      </button>
      <div v-if="requestError" class="alert alert-danger mt-3">
        Error processing request. Please try again. {{ requestError }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { clientStore } from '@/stores/clientStore'
import axios from 'axios'
import { ref, onMounted } from 'vue'
import ImageThumbnailField from '@/components/fields/ImageThumbnailField.vue'
import eventBus, { type Events } from '../stores/eventBus'
import { EventAction } from '@/interfaces/EventAction'

const stringInput = ref('')
const uploadedImages = ref<string[]>([]) // Store base64-encoded image URLs
const selectedImages = ref<string[]>([]) // Store base64-encoded image URLs
const fileInput = ref<HTMLInputElement | null>(null)
const cameraInput = ref<HTMLInputElement | null>(null)
const webCamUrl = ref<string>()
const requestInProgress = ref(false)
const requestError = ref<string>()
const useCam = ref(false)

defineProps<{
  images?: Array<string>
}>()

onMounted(() => {
  // Fetch the camera URL from the backend
  axios
    .get('/camera')
    .then((response) => {
      webCamUrl.value = response.data.url
    })
    .catch((error) => {
      console.error('Error fetching camera URL:', error)
    })
})

eventBus.on(EventAction.COMPLETION, (data: Events[EventAction.COMPLETION]) => {
  requestError.value = ''
  console.log('Completion event received:', data)
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
      imageUrls: [...uploadedImages.value, ...selectedImages.value],
    }
    const response = await axios.post('/completion/identification', body)
    console.log({ ...response.data })
  } catch (error) {
    console.error('Error posting ident data:', error)
    requestError.value = error instanceof Error ? error.message : 'Unknown error'
    requestInProgress.value = false
  }
}

const takePhoto = () => {
  // save the current webcam image to the imageUrls array
  // WIP
  axios
    .get('/camera/snapshot', { responseType: 'blob' })
    .then((response) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        if (e.target?.result) {
          const imageUrl = e.target.result as string
          uploadedImages.value.push(imageUrl) // Add base64-encoded URL to the list
        }
      }
      reader.readAsDataURL(response.data)
    })
    .catch((error) => {
      console.error('Error taking photo:', error)
    })
}

const uploadPhoto = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const maxSize = 5 * 1024 * 1024 // 5MB in bytes
  if (input.files && input.files.length > 0) {
    for (const file of input.files) {
      if (file.size > maxSize) {
        alert('File size exceeds 5MB limit.')
        return
      }
      const reader = new FileReader()
      reader.onload = (e) => {
        if (e.target?.result) {
          const imageUrl = e.target.result as string
          uploadedImages.value.push(imageUrl) // Add base64-encoded URL to the list
        }
      }
      reader.readAsDataURL(file)
    }
  }
}

const updateImage = (updatedValue: Array<string>) => {
  uploadedImages.value.length = 0 // Clear the existing array
  uploadedImages.value.push(...updatedValue) // Add the new URLs
}
</script>

<style scoped>
.wrap {
  display: block;
  overflow: hidden;
  border: 1px solid #ccc;
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
