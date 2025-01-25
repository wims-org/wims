import { acceptHMRUpdate, defineStore } from 'pinia'
import { onMounted, onUnmounted } from 'vue'
import { v4 as uuidv4 } from 'uuid'

export const clientStore = defineStore('ClientStore', () => {
  const client_id: string = uuidv4()
  const reader_id: string = ''

  onMounted(() => {})

  onUnmounted(() => {})

  return { reader_id, client_id }
})
if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(clientStore, import.meta.hot))
}
