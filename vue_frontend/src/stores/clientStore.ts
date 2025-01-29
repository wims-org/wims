import { acceptHMRUpdate, defineStore } from 'pinia'
import { v4 as uuidv4 } from 'uuid'
import { serverStream } from './serverStream'
export const clientStore = defineStore('client', {
  state: () => ({
    client_id: uuidv4(),
    reader_id: '',
  }),
  getters: {},
  actions: {
    setClientId(client_id: string) {
      this.client_id = client_id
    },
    setReaderId(reader_id: string) {
      this.reader_id = reader_id
      console.log('connecting serverstream with reader_id %s', this.reader_id)
      serverStream().connect(this.reader_id, 'reader_id')
    },
  },
})
if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(clientStore, import.meta.hot))
}
