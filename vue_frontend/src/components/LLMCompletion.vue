<template>
  <div class="container">
    <div class="col border p-3">
      <h3 class="row p-2">Object Identification</h3>
      <div class="row p-2 justify-content-between align-items-center">
        <input type="text" class="form-control" v-model="stringInput"
          placeholder="Add Item by Description or Name..." />
        <div class="p-2">
          <div v-if="webCamUrl" class="d-flex align-items-center">
            <label for="useCamera" class="form-check-label m-3">Use Camera for Identification</label>
            <input type="checkbox" v-model="useCamera" class="ml-3" id="useCamera" />
          </div>
          <div v-if="webCamUrl && useCamera" class="mt-3 ml-0 col-12 justify-content-between">
            <div id="iframe-container">
              <iframe id="scaled-iframe" :src="webCamUrl">
                Your browser does not support iframes.
              </iframe>
            </div>

            <button type="button" class="btn btn-primary" @click="fetchIdentification()">Start Identification</button>
          </div>
          <div v-else class="d-flex mt-3 ml-0 col-12 justify-content-between">
            <input ref="fileInput" type="file" class="form-control-file d-none" @change="uploadPhoto" />
            <input ref="cameraInput" type="file" class="form-control-file d-none" accept="image/*" capture="environment"
              @change="uploadPhoto" />
            <button type="button" class="btn btn-secondary" @click="clearFileInput">Clear File</button>
            <button type="button" class="btn btn-primary" @click="fetchIdentification()">Start Identification</button>
          </div>
        </div>
      </div>
      <div class="row p-2 justify-content-between align-items-center">
      </div>
      <div class="row mt-3">
        <ImageThumbnailField :value="imageUrls" @update:value="updateImage($event)" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { clientStore } from '@/stores/clientStore'
import axios from 'axios'
import { ref, reactive, watch, onMounted } from 'vue'
import ImageThumbnailField from '@/components/fields/ImageThumbnailField.vue'

const stringInput = ref('')
const imageUrls = reactive<string[]>([]) // Store base64-encoded image URLs
const fileInput = ref<HTMLInputElement | null>(null)
const cameraInput = ref<HTMLInputElement | null>(null)
const useCamera = ref(true)
const webCamUrl = ref<string>()

// Reactive property for the checkbox
watch(useCamera, (newValue) => {
  console.log(`Use Camera: ${newValue}`)
  // Add logic to enable/disable camera functionality
})

onMounted(() => {
  // Fetch the camera URL from the backend
  axios.get('/camera')
    .then(response => {
      webCamUrl.value = response.data.url
    })
    .catch(error => {
      console.error('Error fetching camera URL:', error)
    })
  if (!webCamUrl.value) {
    useCamera.value = false // Disable camera option if URL is not available
  }
})

const fetchIdentification = async () => {
  try {
    const body = {
      query: stringInput.value,
      client_id: clientStore().client_id,
      imageUrls: [...imageUrls],
    }
    const response = await axios.post('/completion/identification', body)
    console.log({ ...response.data })
  } catch (error) {
    console.error('Error posting ident data:', error)
  }
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
          imageUrls.push(imageUrl) // Add base64-encoded URL to the list
        }
      }
      reader.readAsDataURL(file)
    }
  }
}

const updateImage = (updatedValue: Array<string>) => {
  imageUrls.length = 0 // Clear the existing array
  imageUrls.push(...updatedValue) // Add the new URLs
}

const clearFileInput = () => {
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  if (cameraInput.value) {
    cameraInput.value.value = ''
  }
  imageUrls.length = 0 // Clear all image URLs
}
</script>

<style scoped>
#iframe-container {
  resize: both;
  overflow: hidden;
  border: 1px solid #ccc;
  width: 320px;
  height: 180px;
}

iframe {
  -ms-transform: scale(0.25);
  -moz-transform: scale(0.25);
  -o-transform: scale(0.25);
  -webkit-transform: scale(0.25);
  transform: scale(0.25);
  width: 100vw;
  height: 100vh;
  -ms-transform-origin: 0 0;
  -moz-transform-origin: 0 0;
  -o-transform-origin: 0 0;
  -webkit-transform-origin: 0 0;
  transform-origin: 0 0;
  border: none;
}
</style>
