import { ref } from 'vue'
import { defineStore } from 'pinia'
import { onMounted, onUnmounted } from 'vue'

export const serverStream = defineStore('ServerStream', () => {
  const messages = ref<string[]>([])
  let eventSource: EventSource | null = null
  const alive = ref<boolean>(false)
  function connect(reader_id: string, source: string) {
    console.log('connecting to server with %s: %s', source, reader_id)
    eventSource = new EventSource(
        import.meta.env.VITE_APP_API_HOST +
        ':' +
        import.meta.env.VITE_APP_API_PORT +
        '/stream?reader=' +
        reader_id,
    )

    let aliveTimeout: number | null = null

    eventSource.addEventListener('REDIRECT', (event) => {
      console.log('redirecting')
      messages.value.push(event.data)
    })
    eventSource.addEventListener('COMPLETION', (event) => {
      messages.value.push(event.data)
    })
    eventSource.addEventListener('ALIVE', () => {
      console.log('alive')
      alive.value = true
      if (aliveTimeout) {
        clearTimeout(aliveTimeout)
      }
      aliveTimeout = setTimeout(() => {
        alive.value = false
      }, 6000)
    })
  }

  function disconnect() {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
  }

  onMounted(() => {})

  onUnmounted(() => {
    disconnect()
  })

  return { messages, connect, disconnect, alive }
})
