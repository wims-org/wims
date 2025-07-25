import { ref } from 'vue'
import { defineStore } from 'pinia'
import { onMounted, onUnmounted } from 'vue'
import eventBus from './eventBus'
import { EventAction, StreamEvent } from '@/interfaces/EventAction'
import { clientStore } from './clientStore'

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
        import.meta.env.VITE_API_URL + '/stream?reader=' + reader_id,
      )

      let aliveTimeout: ReturnType<typeof setTimeout> | null = null

      this.eventSource.addEventListener(StreamEvent.SCAN, (event) => {
        console.log(StreamEvent.SCAN, event.data)
        const parsedData = JSON.parse(event.data.replace(/'/g, '"'))
        eventBus.emit(clientStore().expected_event_action, parsedData)
      })
      this.eventSource.addEventListener(StreamEvent.COMPLETION, (event) => {
        console.log(StreamEvent.COMPLETION, event.data)
        const parsedData = JSON.parse(event.data.replace(/'/g, '"'))
        eventBus.emit(EventAction.COMPLETION, parsedData)
      })
      this.eventSource.addEventListener(StreamEvent.ERROR, (event) => {
        console.error(StreamEvent.ERROR, event.data)
        const parsedData = JSON.parse(event.data.replace(/'/g, '"'))
        eventBus.emit(EventAction.ERROR, parsedData)
      })
      this.eventSource.addEventListener(StreamEvent.ALIVE, () => {
        console.log(StreamEvent.ALIVE)
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
