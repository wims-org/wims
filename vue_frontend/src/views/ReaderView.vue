<template>
  <div>
    <h1>Readers</h1>
    <ul class="list-group block-item-list" data-testid="reader-list">
      <li
        v-for="reader in readers"
        data-testid="reader-item"
        :key="reader.reader_id"
        @click="selectReader(reader.reader_id)"
        class="list-group-item d-flex justify-content-between align-items-center"
        :class="{ active: reader?.reader_id === (clientStoreInstance?.reader_id ?? '') }"
      >
        <div>
          {{ reader.reader_name }}
          <br />
          <span class="text-muted">{{ reader.reader_id }}</span>
        </div>
        <button @click.stop="deleteReader(reader.reader_id)" class="btn btn-danger btn-sm">
          Delete
        </button>
      </li>
      <div v-if="readers.length === 0" class="list-group-item">
        <div class="spinner-border spinner-border-sm" role="status"></div>
        Loading...
      </div>
    </ul>
    <div class="card mt-4">
      <div class="card-header">Add New Reader</div>
      <div class="card-body">
        <form @submit.prevent="submitReader" class="p-3 row">
          <div class="form-group col-md-5">
            <label for="readerName">Reader Name</label>
            <input
              type="text"
              v-model="newReader.reader_name"
              id="readerName"
              class="form-control"
              required
            />
          </div>
          <div class="form-group col-md-5">
            <label for="readerId">Reader ID</label>
            <input
              type="text"
              v-model="newReader.reader_id"
              id="readerId"
              class="form-control"
              required
            />
          </div>
          <div class="form-group col-md-2 d-flex align-items-end">
            <button type="submit" class="btn btn-primary w-100">Add Reader</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { clientStore } from '@/stores/clientStore'
import type Reader from '@/interfaces/reader.interface'
import { useRouter } from 'vue-router'

const clientStoreInstance = clientStore()
const router = useRouter()
const readers = ref<Reader[]>([])
const newReader = ref<Reader>({ reader_id: '', reader_name: '' })

async function fetchReaders(): Promise<void> {
  try {
    const response = await axios.get('/readers')
    readers.value = response.data
  } catch (error) {
    console.error('Error fetching readers:', error)
  }
}

function selectReader(readerId: string) {
  clientStoreInstance.setReaderId(readerId)
  sessionStorage.setItem('reader_id', readerId)
  sessionStorage.setItem('reader_id_time', Date.now().toString())
  const params = router.currentRoute.value.query
  if (readerId !== '') {
    params.reader_id = readerId
  }
  history.replaceState(
    {},
    '',
    router.currentRoute.value.path +
      '?' +
      Object.keys(params)
        .map((key) => {
          return encodeURIComponent(key) + '=' + encodeURIComponent('' + (params[key] ?? ''))
        })
        .join('&'),
  )
}

async function submitReader(): Promise<void> {
  try {
    await axios.post('/readers', Object(newReader.value))
    fetchReaders()
  } catch (error) {
    console.error('Error submitting reader:', error)
  }
}

async function deleteReader(readerId: string): Promise<void> {
  try {
    await axios.delete(`/readers/${readerId}`)
    fetchReaders()
  } catch (error) {
    console.error('Error deleting reader:', error)
  }
}

onMounted(() => {
  fetchReaders()
})
</script>

<style scoped>
/* Add your styles here */
</style>
