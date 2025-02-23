<template>
  <div class="container">
    <div class="col border p-3">
      <h3 class="row p-2">Object Identification</h3>
      <div class="row p-2 justify-content-between align-items-center">
        <input type="text" class="form-control" v-model="stringInput" placeholder="Add Item by Description or Name..." />
        <input ref="fileInput" type="file" class="form-control-file d-none" @change="uploadPhoto" />
        <button class="btn btn-secondary" @click="() => fileInput?.click()">Upload Photo</button>
        <button class="btn btn-secondary" @click="clearFileInput">Clear File</button>
        <button class="btn btn-primary " @click="fetchIdentification()">Start Identification</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { clientStore } from '@/stores/clientStore'
import axios from 'axios'
import { ref } from 'vue'

const stringInput = ref('')
const formData = new FormData()
const fileInput = ref<HTMLInputElement | null>(null)

const fetchIdentification = async () => {
  try {
    const body = { query: stringInput.value, client_id: clientStore().client_id }
    formData.set('data', JSON.stringify(body))
    const response = await axios({ method: 'post', url: '/completion/identification', data: formData })
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
      formData.append('images', file)
    }
  }
}

const clearFileInput = () => {
  if (fileInput.value) {
    fileInput.value.value = ''
    formData.delete('images')
  }
}
</script>
