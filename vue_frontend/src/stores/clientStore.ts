import { defineStore } from 'pinia'
import { onMounted, onUnmounted } from 'vue'


export const clientStore = defineStore('ClientStore', () => {
  const reader_id: string = 'asdasdasd'

  onMounted(() => {
  })

  onUnmounted(() => {

  })

  return { reader_id }
})