import { defineStore } from 'pinia'
import { onMounted, onUnmounted } from 'vue'


export const clientStore = defineStore('ClientStore', () => {
  let reader_id: String = 'asdasdasd'

  onMounted(() => {
  })

  onUnmounted(() => {

  })

  return { reader_id }
})