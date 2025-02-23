import { type Router } from 'vue-router'
import { clientStore } from './stores/clientStore'
import { serverStream } from './stores/serverStream'

const formatDate = (timestamp: number): string => {
  if (!timestamp) return ''
  const date = new Date(timestamp * 1000)
  return isNaN(date.getTime()) ? '' : date.toISOString().split('T')[0]
}

const getFieldModel = (
  formData: { [x: string]: unknown },
  key: string,
  type: string,
): string | undefined => {
  if (formData === undefined) {
    return undefined
  } else if (type === 'checkbox') {
    return (formData as { [key: string]: boolean })[key] ? 'checked' : ''
  } else if (type === 'epoch') {
    return formatDate((formData as { [key: string]: number })[key])
  }
  if (formData && typeof formData === 'object' && key in formData) {
    console.log((formData as { [key: string]: unknown })[key])
  }
  return (formData as { [key: string]: never })[key]
}

const updateFieldModel = (
  formData: { [x: string]: unknown },
  event: Event,
  key: string,
  type: string,
) => {
  const target = event.target as HTMLInputElement
  if (type === 'checkbox') {
    ;(formData as { [key: string]: boolean })[key] = target.checked
  } else if (type === 'epoch') {
    ;(formData as { [key: string]: number })[key] = new Date(target.value).getTime() / 1000
  } else if (type === 'number') {
    ;(formData as { [key: string]: number })[key] = Number(target.value)
  } else if (type === 'array') {
    ;(formData as { [key: string]: string[] })[key] = target.value
      .split(',|;')
      .map((item) => item.trim())
  } else {
    ;(formData as { [key: string]: string })[key] = target.value
  }
}

const setReaderId = (router: Router) => {
  const client_store = clientStore()
  const server_stream = serverStream()

  const route_param_reader = Array.isArray(router.currentRoute.value.query.reader)
    ? router.currentRoute.value.query.reader[0] || undefined
    : router.currentRoute.value.query.reader || undefined

  const stored_reader_id_ttl = 1 * (60 * 60 * 1000) // 1 hour
  const stored_reader_id = sessionStorage.getItem('reader_id')
  const stored_reader_id_time = sessionStorage.getItem('reader_id_time')

  if (route_param_reader) {
    client_store.reader_id = route_param_reader
    // Only store reader_id in sessionStorage if it was passed as a query parameter
    sessionStorage.setItem('reader_id', route_param_reader)
    sessionStorage.setItem('reader_id_time', Date.now().toString())
  } else if (
    stored_reader_id &&
    stored_reader_id_time &&
    Date.now() - parseInt(stored_reader_id_time) < stored_reader_id_ttl
  ) {
    client_store.reader_id = stored_reader_id
  } else {
    sessionStorage.removeItem('reader_id')
    sessionStorage.removeItem('reader_id_time')
  }

  if (client_store.reader_id) {
    server_stream.connect(client_store.reader_id, 'reader_id')
  } else {
    server_stream.connect(client_store.client_id, 'client_id')
  }
}

export { formatDate, getFieldModel, updateFieldModel, setReaderId }
