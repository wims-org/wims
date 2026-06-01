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
      this.eventSource.addEventListener(StreamEvent.SCAN_NEW, (event) => {
        console.log(StreamEvent.SCAN_NEW, event.data)
        const parsedData = JSON.parse(event.data.replace(/'/g, '"'))
        
        // TODO: parse clientStore().expected_event_action so new redirect 
        eventBus.emit(EventAction.NEW_ITEM, parsedData)
      })
      this.eventSource.addEventListener(StreamEvent.IDENTIFICATION, (event) => {
        console.log(StreamEvent.IDENTIFICATION, event.data)
        const parsedData = JSON.parse(event.data.replace(/'/g, '"'))
        eventBus.emit(EventAction.IDENTIFICATION, parsedData)
      })
      this.eventSource.addEventListener(StreamEvent.ERROR, (event) => {
        console.error(StreamEvent.ERROR, event.data)
        const parsedData = JSON.parse(event.data.replace(/'/g, '"'))
        eventBus.emit(EventAction.ERROR, parsedData)
      })
      this.eventSource.addEventListener(StreamEvent.ELEMENT_UPDATE, (event) => {
        console.log(StreamEvent.ELEMENT_UPDATE, event.data)
        const parsedData = JSON.parse(event.data.replace(/'/g, '"'))
        if (parsedData.element === 'READERS') {
          eventBus.emit(EventAction.ELEMENT_UPDATE_READERS, parsedData)
        } else if (parsedData.element === 'ITEM') {
          eventBus.emit(EventAction.ELEMENT_UPDATE_ITEM, parsedData)
        } else if (parsedData.element === 'CONTAINER') {
          eventBus.emit(EventAction.ELEMENT_UPDATE_CONTAINER, parsedData)
        } else if (parsedData.element === 'USERS') {
          eventBus.emit(EventAction.ELEMENT_UPDATE_USERS, parsedData)
        } else if (parsedData.element === 'CATEGORIES') {
          eventBus.emit(EventAction.ELEMENT_UPDATE_CATEGORIES, parsedData)
        } else {
          console.warn('Unknown element update', parsedData)
        }
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
        }, 10000)
      })
      return new Promise((resolve) => {
        this.eventSource?.addEventListener('open', () => {
          console.log('EventSource connection established')
          resolve(true)
        })
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
