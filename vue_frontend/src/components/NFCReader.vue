<template>
  <div class="nfc-reader">
    <div v-if="!supported" class="alert alert-warning mb-0">
      Web NFC is not supported on this device or browser.
    </div>
    <template v-else>
      <div class="d-flex align-items-center gap-2 row justify-content-center">
        <BSpinner class="me-2" v-if="scanning" size="lg" />
      </div>
      <div v-if="scanning" class="mt-2 text-muted small">
        Hold an NFC tag near the back of your device…
      </div>
      <div v-if="result" class="mt-2 decode-result">
        Last read: <b>{{ result }}</b>
      </div>
      <details closed>
        <summary class="small text-muted">Debug log</summary>
        <pre class="debug-log">{{ debugLog.join('\n') }}</pre>
        <div v-if="error" class="mt-2 alert alert-danger small mb-0">{{ error }}</div>
      </details>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { clientStore } from '@/stores/clientStore'
import type { ScanResult } from '@/interfaces/reader.interface'

const emit = defineEmits<{
  (event: 'scan', value: ScanResult): void
}>()

// Web NFC API types (not yet in the standard TypeScript lib)
interface NDEFRecord {
  recordType: string
  mediaType?: string
  data?: DataView
}
interface NDEFReadingEvent extends Event {
  serialNumber: string
  message: { records: NDEFRecord[] }
}
interface NDEFReader extends EventTarget {
  scan(options?: { signal?: AbortSignal }): Promise<void>
}
declare const NDEFReader: { new(): NDEFReader }

const supported = ref('NDEFReader' in window)
const scanning = ref(true)
const result = ref<ScanResult | null>(null)
const error = ref('')
const debugLog = ref<string[]>([])

let abortController: AbortController | null = null
let ndefReader: InstanceType<typeof NDEFReader> | null = null

function log(msg: string) {
  const ts = new Date().toISOString().slice(11, 23)
  debugLog.value.push(`[${ts}] ${msg}`)
}
/**
 * Decode an NDEF text record payload.
 * Byte 0: status byte — bit 7 = encoding (0=UTF-8, 1=UTF-16), bits 5–0 = language code length.
 * Bytes 1..(1+langLen): language code (e.g. "en").
 * Remaining bytes: the actual text.
 */
function decodeTextRecord(data: DataView): string {
  const statusByte = data.getUint8(0)
  const encoding = statusByte & 0x80 ? 'utf-16' : 'utf-8'
  const langCodeLen = statusByte & 0x3f
  const textBytes = new Uint8Array(data.buffer, data.byteOffset + 1 + langCodeLen)
  return new TextDecoder(encoding).decode(textBytes)
}

async function startScan() {
  error.value = ''
  result.value = null
  debugLog.value = []
  scanning.value = true
  abortController = new AbortController()

  try {
    ndefReader = new NDEFReader()

    // Listeners MUST be added before scan() is called so no reading event is missed.
    ndefReader.addEventListener('reading', (evt) => {
      const e = evt as NDEFReadingEvent
      let value = e.serialNumber
      for (const record of e.message.records) {
        if (record.recordType === 'text' && record.data) {
          try {
            value = decodeTextRecord(record.data)
            log(`  decoded text record: "${value}"`)
          } catch (decodeErr) {
            log(`  text decode failed: ${decodeErr}`)
          }
          break
        }
      }

      result.value = { reader_id: clientStore().getClientId, code_value: value, code_format: 'uuid' }

      setTimeout(() => {
        result.value = null
      }, 2000)
      emit('scan', result.value)
    })

    ndefReader.addEventListener('readingerror', () => {
      error.value = 'Could not read NFC tag — tag may not be NDEF-formatted.'
    })

    log('Calling reader.scan()…')
    await ndefReader.scan({ signal: abortController.signal })
    log('reader.scan() resolved — scanning active.')

    // Check permission state — if not "granted" events will never fire.
    try {
      const perm = await navigator.permissions.query({ name: 'nfc' as PermissionName })
      log(`NFC permission state: ${perm.state}`)
      if (perm.state !== 'granted') {
        error.value = `NFC permission is "${perm.state}" — events will not fire.`
      }
    } catch (permErr) {
      log(`Permission query not supported: ${permErr}`)
    }
  } catch (err) {
    scanning.value = false
    if (err instanceof Error && err.name !== 'AbortError') {
      error.value = err.message
    }
  }
}

function stopScan() {
  abortController?.abort()
  ndefReader = null
  scanning.value = false
}

onMounted(async () => {
  stopScan()
  if (supported.value) {
    await startScan()
  }
})

onUnmounted(() => {
  stopScan()
  abortController?.abort()
  ndefReader = null
})
</script>

<style scoped>
.nfc-reader {
  padding: 0.5rem 0;
}
</style>
