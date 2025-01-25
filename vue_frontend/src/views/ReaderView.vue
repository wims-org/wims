<template>
  <div>
    <h1>Readers</h1>
    <ul class="list-group block-item-list">
      <li
        v-for="reader in readers"
        :key="reader.reader_id"
        @click="selectReader(reader.reader_id)"
        class="list-group-item"
        :class="{ active: reader?.reader_id === (clientStoreInstance?.reader_id ?? '') }"
      >
        {{ reader.reader_name }}
        <br />
        <span class="text-muted">{{ reader.reader_id }}</span>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import axios from 'axios'
import { ref, onMounted, defineComponent } from 'vue'
import { clientStore } from '@/stores/clientStore'
const clientStoreInstance = clientStore()

export default defineComponent({
  name: 'ReaderView',
  setup() {
    const readers = ref([])

    const fetchReaders = async (): Promise<void> => {
      try {
        const response = await axios.get('/readers')
        console.log('Readers:', response.data)
        readers.value = response.data
      } catch (error) {
        console.error('Error fetching readers:', error)
      }
    }

    const selectReader = (readerId: string) => {
      console.log('Selected reader:', readerId)
      clientStoreInstance.reader_id = readerId
      console.log('clientStoreInstance.reader_id:', clientStoreInstance)
    }

    onMounted(() => {
      fetchReaders()
    })

    return {
      readers,
      selectReader,
      clientStoreInstance,
    }
  },
})
</script>

<style scoped>

</style>
