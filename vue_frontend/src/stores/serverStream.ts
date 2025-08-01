import { ref } from 'vue'
import { defineStore } from 'pinia'
import { onMounted, onUnmounted } from 'vue'
import eventBus from './eventBus'
import { EventAction, StreamEvent } from '@/interfaces/EventAction'
import { clientStore } from './clientStore'
import axios from 'axios'

export const serverStream = defineStore('ServerStream', {
  state: () => ({
    messages: ref<string[]>([]),
    eventSource: null as EventSource | null,
    alive: ref<boolean>(false),
  }),
  getters: {},
  actions: {
    async connect() {
      this.eventSource = new EventSource(
        import.meta.env.VITE_API_URL + '/stream?reader=' + clientStore().getReaderId + '&stream_id=' + clientStore().getClientId,
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
        // event data contains all subscriptions but setting them is quite flaky
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

    async subscribe(client_id: string, reader_id: string) {
      await axios.post('/stream/subscription', {
        stream_id: client_id,
        reader_id: reader_id
      })
    },
    async unsubscribe(client_id: string, reader_id: string) {
      await axios.delete('/stream/subscription', {
        data: {
          stream_id: client_id,
          reader_id: reader_id,
        },
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
