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
        <input type="file" class="form-control-file" @change="uploadPhoto" />
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

const fetchIdentification = async (query: string) => {
  try {
    const body = { query, client_id: clientStore().client_id }
    //   const json = JSON.stringify(body)
    //  const blob = new Blob([json], {
    //   type: 'application/json',
    // })

    formData.append('data', JSON.stringify(body))
    //formData.append('query', query)
    //formData.append('client_id', clientStore().client_id)
    console.log(formData)
    const response = await axios({ method: 'post', url: '/identification', data: formData })
    console.log({ ...response.data })
  } catch (error) {
    console.error('Error posting ident data:', error)
  }
}

const uploadPhoto = async (event: Event) => {
  const fileInput = event.target as HTMLInputElement
  const maxSize = 5 * 1024 * 1024 // 5MB in bytes
  if (fileInput.files && fileInput.files.length > 0) {
    for (const file of fileInput.files) {
      if (file.size > maxSize) {
        alert('File size exceeds 5MB limit.')
        return
      }

      formData.append('images', file)
    }
  }
}
</script>
