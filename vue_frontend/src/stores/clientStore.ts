import { acceptHMRUpdate, defineStore } from 'pinia'
import { v4 as uuidv4 } from 'uuid'
import { serverStream } from './serverStream'
import { EventAction } from '@/interfaces/EventAction'

import type { components } from '@/interfaces/api-types'
import axios from 'axios'

type User = components['schemas']['User'] & { [key: string]: unknown }

export const clientStore = defineStore('client', {
  state: () => ({
    client_id: uuidv4(),
    reader_id: '',
    reader: {} as components['schemas']['Reader'],
    expected_event_action: EventAction.REDIRECT,
    user: undefined as User | undefined,
    backend_config: {} as components['schemas']['ConfigResponseModel'],
    selectedBarcodeFormats: [
      "aztec",
      "code_128",
      "code_39",
      "code_93",
      "codabar",
      "databar",
      "databar_expanded",
      "data_matrix",
      "dx_film_edge",
      "ean_13",
      "ean_8",
      "itf",
      "maxi_code",
      "micro_qr_code",
      "pdf417",
      "qr_code",
      "rm_qr_code",
      "upc_a",
      "upc_e",
      "linear_codes",
      "matrix_codes",
    ] as string[],
    cameraConstraints: null as Record<string, unknown> | null
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
    },
    getUser(): User | undefined {
      return this.user
    },
    getSelectedBarcodeFormats(): string[] {
      return this.selectedBarcodeFormats
    },
    getCameraConstraints(): Record<string, unknown> | null {
      return this.cameraConstraints
    }
  },
  actions: {
    setClientId(client_id: string) {
      this.client_id = client_id
    },
    setUser(userId: string) {
      if (this.user && this.user.id === userId) {
        return
      }
      axios
        .get(`/users/${userId}`)
        .then((response) => {
          this.user = response.data
          sessionStorage.setItem('user_id', userId)
          sessionStorage.setItem('user_id_time', Date.now().toString())
        })
        .catch((error) => {
          console.error('Error fetching user:', error)
        })
    },
    unsetUser() {
      this.user = undefined
      sessionStorage.removeItem('user_id')
      sessionStorage.removeItem('user_id_time')
    },

    async setReaderId(reader_id: string) {
      if (this.reader_id.length && this.reader_id !== reader_id) {
        await serverStream()
          .unsubscribe(this.client_id, this.reader_id)
          .then(async () => {
            this.reader_id = 'loading'
          })
          .catch(() => { })
      }
      console.log('connecting serverstream with reader_id %s', reader_id)
      await serverStream()
        .subscribe(this.client_id, reader_id)
        .then(async () => {
          this.reader_id = reader_id
          this.reader = await axios.get(`/readers/${reader_id}`).then(res => res.data)
        })
        .catch(() => {
          this.reader_id = ''
        })
    },
    async unsetReaderId() {
      await serverStream()
        .unsubscribe(this.client_id, this.reader_id)
        .then(() => {
          this.reader_id = ''
        })
        .catch((error) => {
          console.error('Error unsubscribing from reader_id:', error)
          if (error.status === 404) {
            this.reader_id = ''
          }
        })
        .catch(() => { })
    },
    setExpectedEventAction(expected_event_action: EventAction) {
      this.expected_event_action = expected_event_action
    },
    async fetchBackendConfig() {
      axios
        .get('/config/')
        .then((response) => {
          this.backend_config = response.data
        })
        .catch((error) => {
          console.error('Error fetching backend config:', error)
        })
    },
    setSelectedBarcodeFormats(selectedBarcodeFormats: string[]) {
      this.selectedBarcodeFormats = selectedBarcodeFormats
    },
    setCameraConstraints(cameraConstraints: Record<string, unknown>) {
      sessionStorage.setItem('camera_constraints', JSON.stringify(cameraConstraints))
      this.cameraConstraints = cameraConstraints
    }
  },
})
if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(clientStore, import.meta.hot))
}
