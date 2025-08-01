import { acceptHMRUpdate, defineStore } from 'pinia'
import { v4 as uuidv4 } from 'uuid'
import { serverStream } from './serverStream'
import { EventAction } from '@/interfaces/EventAction'

export const clientStore = defineStore('client', {
  state: () => ({
    client_id: uuidv4(),
    reader_id: '',
    expected_event_action: EventAction.REDIRECT
  }),
  getters: {
    getClientId(): string {
      return this.client_id
    },
    getReaderId(): string {
      return this.reader_id
    },
    getExpectedEventAction(): EventAction {
      return this.expected_event_action
    }
  },
  actions: {
    setClientId(client_id: string) {
      this.client_id = client_id
    },
    async setReaderId(reader_id: string) {
      if (!serverStream().alive) {
        setTimeout(() => { }, 1000)
      }
      if (this.reader_id.length) {
        await serverStream().unsubscribe(this.client_id, this.reader_id)
          .then(() => { this.reader_id = 'loading' }).catch(() => { })
      }
      console.log('connecting serverstream with reader_id %s', reader_id)
      await serverStream().subscribe(this.client_id, reader_id)
        .then(() => { this.reader_id = reader_id }).catch(() => { this.reader_id = '' })
    },
    async unsetReaderId() {
      await serverStream().unsubscribe(this.client_id, this.reader_id)
        .then(() => { this.reader_id = '' }).catch((error) => {
          console.error('Error unsubscribing from reader_id:', error)
          if (error.status === 404) {
            this.reader_id = ''
          }
        }).catch(() => { })
    },
    setExpectedEventAction(expected_event_action: EventAction) {
      this.expected_event_action = expected_event_action
    }
  },
})
if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(clientStore, import.meta.hot))
}
