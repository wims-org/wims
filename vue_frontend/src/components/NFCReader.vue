<template>
    <div>
        <div class="nfc-controls">
            <BButton v-if="!scanning" class="primary p-1" variant="success" size="lg" @click="startNFCReading">
                Start NFC Scan
            </BButton>
            <BButton v-else class="primary p-1" variant="danger" size="lg" @click="stopNFCReading">
                Stop NFC Scan
            </BButton>
            <BSpinner v-if="scanning" class="ms-2" />
        </div>

        <p class="decode-result">
            Last result: <b>{{ result }}</b>
        </p>
        <p class="error">{{ error }}</p>
    </div>
</template>

<script setup lang="ts">
import { onUnmounted, ref } from 'vue'
import NFCService, { type NFCScanResult } from '@/services/NFCService'
import ScanService from '@/services/ScanService'

const result = ref('')
const error = ref('')
const scanning = ref(true)

const emit = defineEmits<{
    (event: 'scan', tag_id: string): void
}>()

async function startNFCReading() {
    error.value = ''

    if (!NFCService.isSecureContext()) {
        error.value = 'NFC access is only permitted in secure context. Use HTTPS or localhost rather than HTTP.'
        return
    }

    if (!NFCService.isSupported()) {
        error.value = 'Web NFC is not supported on this device/browser.'
        return
    }

    try {
        await NFCService.start(onRead, onServiceError)
        scanning.value = true
    } catch (err) {
        onServiceError(err as Error & { name?: string })
    }
}

function stopNFCReading() {
    NFCService.stop()
    scanning.value = false
}

function onRead(scanResult: NFCScanResult) {
    result.value = scanResult.tag_id
    ScanService.sendScanResult(scanResult.tag_id, scanResult.records)
    emit('scan', scanResult.tag_id)
}

function onServiceError(err: Error & { name?: string }) {
    scanning.value = false

    if (err.name === 'NotAllowedError') {
        error.value = 'you need to grant NFC access permission'
    } else if (err.name === 'NotSupportedError') {
        error.value = 'Web NFC is not supported in this browser/device'
    } else if (err.name === 'InsecureContextError') {
        error.value = 'NFC access is only permitted in secure context. Use HTTPS or localhost rather than HTTP.'
    } else {
        error.value = err.message
    }
}

onUnmounted(() => {
    stopNFCReading()
})
</script>

<style>
.nfc-controls {
    display: flex;
    align-items: center;
}
</style>
