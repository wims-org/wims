<template>
  <div class="container">
    <div class="col border p-3">
      <h3 class="row p-2">Object Identification</h3>
      <div class="row p-2 justify-content-between align-items-center">
        <input
          type="text"
          class="form-control"
          v-model="stringInput"
          placeholder="Add Item by Description or Name..."
        />
        <input ref="fileInput" type="file" class="form-control-file d-none" @change="uploadPhoto" />
        <input
          ref="cameraInput"
          type="file"
          class="form-control-file d-none"
          accept="image/*"
          capture="environment"
          @change="uploadPhoto"
        />
        <button class="btn btn-secondary" @click="clearFileInput">Clear File</button>
        <button class="btn btn-primary" @click="fetchIdentification()">Start Identification</button>
      </div>
    <div class="row mt-3">
      <ImageThumbnailField
        :value="imageUrls"
        @update:value="updateImage($event)"
      />
    </div>
  </div>
  </div>
</template>

<script setup lang="ts">
import { clientStore } from '@/stores/clientStore'
import axios from 'axios'
import { ref, reactive } from 'vue'
import ImageThumbnailField from '@/components/fields/ImageThumbnailField.vue'

const stringInput = ref('')
const imageUrls = reactive<string[]>([]) // Store base64-encoded image URLs
const fileInput = ref<HTMLInputElement | null>(null)
const cameraInput = ref<HTMLInputElement | null>(null)

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

const updateImage = (updatedValue: Array<string> ) => {
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
</style>
