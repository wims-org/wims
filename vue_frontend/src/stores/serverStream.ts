import { ref } from 'vue'
import { defineStore } from 'pinia'
import { onMounted, onUnmounted } from 'vue'

export const serverStream = defineStore('ServerStream', {
  state: () => ({
    messages: ref<string[]>([]),
    reader_id: ref<string>(''),
    eventSource: null as EventSource | null,
    alive: ref<boolean>(false),
  }),
  getters: {},
  actions: {
    connect(reader_id: string, source: string) {
      console.log('connecting to server with %s: %s', source, reader_id)
      if (source === 'reader_id') {
        console.log('setting serverstream to reader_id %s', reader_id)
        this.reader_id = reader_id
      }
      this.eventSource = new EventSource(
        import.meta.env.VITE_APP_API_HOST +
          ':' +
          import.meta.env.VITE_APP_API_PORT +
          '/stream?reader=' +
          reader_id,
      )

      let aliveTimeout: number | null = null

      this.eventSource.addEventListener('REDIRECT', (event) => {
        console.log('redirecting')
        this.messages.push(event.data)
      })
      this.eventSource.addEventListener('COMPLETION', (event) => {
        this.messages.push(event.data)
      })
      this.eventSource.addEventListener('ALIVE', () => {
        console.log('alive')
        this.alive = true
        if (aliveTimeout) {
          clearTimeout(aliveTimeout)
        }
        aliveTimeout = setTimeout(() => {
          this.alive = false
        }, 6000)
      })
    },

    disconnect() {
      if (this.eventSource) {
        this.eventSource.close()
        this.eventSource = null
      }
    },
    onMounted() {
      onMounted(() => {
        console.log('mounted')
      })
    },
    onUnmounted() {
      onUnmounted(() => this.eventSource?.close())
    },
  },
})
