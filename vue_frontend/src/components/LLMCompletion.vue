<template>
  <div class="container">
    <div class="row mt-3 border p-3">
      <h3 class="col-md-8 mb-3">Object Identification</h3>
      <div class="col-md-8 mb-3">
        <input
          ref="string-identification-input"
          type="text"
          class="form-control string-ident-input"
          placeholder="Add Item by Description or Name..."
        />
      </div>
      <div class="col-md-2 mb-3">
        <input ref="fileInput" type="file" class="form-control-file" @change="uploadPhoto" />
        <button class="btn btn-secondary mt-2" @click="clearFileInput">Clear File</button>
      </div>
      <div class="col-md-2">
        <button class="btn btn-primary" @click="fetchIdentification(stringIdentInput)">
          Start Identification
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { clientStore } from '@/stores/clientStore'
import axios from 'axios'
import { ref } from 'vue'

const stringIdentInput = ref("string-identification-input")
const formData = new FormData()
const fileInput = ref<HTMLInputElement | null>(null)

const fetchIdentification = async (query: string) => {
  try {
    const body = { query, client_id: clientStore().client_id }
    formData.append('data', JSON.stringify(body))
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
