import { ref } from 'vue'
import { defineStore } from 'pinia'
import { onMounted, onUnmounted } from 'vue'



export const serverStream = defineStore('ServerStream', () => {
  const messages = ref<string[]>([])
  let eventSource: EventSource | null = null

  function connect(reader_id: string) {
    console.log('connecting to server with reader id: ', reader_id)
    eventSource = new EventSource('http://localhost:5005/stream?reader=' + reader_id)

    eventSource.addEventListener('REDIRECT', (event) => {
      console.log('redirecting')
      messages.value.push(event.data)
    })
  }

  function disconnect() {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
  }

  onMounted(() => {
    
  })

  onUnmounted(() => {
    disconnect()
  })

  return {  messages, connect, disconnect }
})