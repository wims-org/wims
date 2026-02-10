<template>
    <select v-model="selectedConstraints">
        <option v-for="option in constraintOptions" :key="option.label" :value="option.constraints">
            {{ option.label }}
        </option>
    </select>
    <div>
        <BButton v-if="constraintOptions.length > 1" class="primary p-1" variant="success" size="lg" to="/qr-reader"
            @click="toggleFrontReader()">
            <IMaterialSymbolsCameraswitch class="cam-switch-icon" />
        </BButton>
        <qrcode-stream :constraints="selectedConstraints" :track="trackFunctionSelected.value"
            :formats="selectedBarcodeFormats" @error="onError" @detect="onDetect" @camera-on="onCameraReady" />
        <p class="decode-result">
            Last result: <b>{{ result }}</b>
        </p>
        <p class="error">{{ error }}</p>
    </div>
</template>

<script setup lang="ts">
import { QrcodeStream } from 'vue-qrcode-reader'

import { ref, computed } from 'vue'
import { clientStore } from '@/stores/clientStore'
import ScanService from '@/services/ScanService'


/*** This is mostly the example code of the demo https://gruhn.github.io/vue-qrcode-reader/demos/FullDemo.html ***/

/*** detection handling ***/

const result = ref('')

// Emits
const emit = defineEmits<{
    (event: 'scan', tag_id: string): void
}>()

function onDetect(detectedCodes: { rawValue: string }[]) {
    console.log(detectedCodes)
    result.value = JSON.stringify(detectedCodes.map((code) => code.rawValue))
    ScanService.sendScanResult(result.value)

    setTimeout(() => {
        result.value = ''
    }, 2000)
    emit('scan', result.value)
}

/*** select camera ***/

const selectedConstraints = ref<Record<string, unknown>>({ facingMode: 'environment' })
const defaultConstraintOptions = [
    { label: 'rear camera', constraints: { facingMode: 'environment' } },
    { label: 'front camera', constraints: { facingMode: 'user' } }
]
const constraintOptions = ref<{ label: string; constraints: Record<string, unknown> }[]>(defaultConstraintOptions)
const frontNotRearCamera = ref(false)
const selectedBarcodeFormats = computed(() => {
    return clientStore().getSelectedBarcodeFormats
})

const toggleFrontReader = () => {
    if (!frontNotRearCamera.value) {
        frontNotRearCamera.value = true
        selectedConstraints.value = constraintOptions.value[+frontNotRearCamera.value].constraints
    } else {
        frontNotRearCamera.value = false
        selectedConstraints.value = constraintOptions.value[+frontNotRearCamera.value].constraints
    }
}

async function onCameraReady() {
    // NOTE: on iOS we can't invoke `enumerateDevices` before the user has given
    // camera access permission. `QrcodeStream` internally takes care of
    // requesting the permissions. The `camera-on` event should guarantee that this
    // has happened.
    const devices = await navigator.mediaDevices.enumerateDevices()
    const videoDevices = devices.filter(({ kind }) => kind === 'videoinput')

    constraintOptions.value = [
        // ...defaultConstraintOptions,
        ...videoDevices.map(({ deviceId, label }) => ({
            label: `${label} (ID: ${deviceId})`,
            constraints: { deviceId }
        }))
    ]
    selectedConstraints.value = constraintOptions.value[0].constraints
    console.log('Available video devices:', constraintOptions.value)
    error.value = ''
}

/*** track functons ***/

function paintOutline(detectedCodes: { cornerPoints: { x: number, y: number }[] }[], ctx: CanvasRenderingContext2D) {
    for (const detectedCode of detectedCodes) {
        const [firstPoint, ...otherPoints] = detectedCode.cornerPoints

        ctx.strokeStyle = 'red'

        ctx.beginPath()
        ctx.moveTo(firstPoint.x, firstPoint.y)
        for (const { x, y } of otherPoints) {
            ctx.lineTo(x, y)
        }
        ctx.lineTo(firstPoint.x, firstPoint.y)
        ctx.closePath()
        ctx.stroke()
    }
}
function paintBoundingBox(detectedCodes: { boundingBox: { x: number, y: number, width: number, height: number } }[], ctx: CanvasRenderingContext2D) {
    for (const detectedCode of detectedCodes) {
        const {
            boundingBox: { x, y, width, height }
        } = detectedCode

        ctx.lineWidth = 2
        ctx.strokeStyle = '#007bff'
        ctx.strokeRect(x, y, width, height)
    }
}
function paintCenterText(detectedCodes: { boundingBox: { x: number, y: number, width: number, height: number }, rawValue: string }[], ctx: CanvasRenderingContext2D) {
    for (const detectedCode of detectedCodes) {
        const { boundingBox, rawValue } = detectedCode

        const centerX = boundingBox.x + boundingBox.width / 2
        const centerY = boundingBox.y + boundingBox.height / 2

        const fontSize = Math.max(12, (50 * boundingBox.width) / ctx.canvas.width)

        ctx.font = `bold ${fontSize}px sans-serif`
        ctx.textAlign = 'center'

        ctx.lineWidth = 3
        ctx.strokeStyle = '#35495e'
        ctx.strokeText(detectedCode.rawValue, centerX, centerY)

        ctx.fillStyle = '#5cb984'
        ctx.fillText(rawValue, centerX, centerY)
    }
}
const trackFunctionOptions = [
    { text: 'nothing (default)', value: undefined },
    { text: 'outline', value: paintOutline },
    { text: 'centered text', value: paintCenterText },
    { text: 'bounding box', value: paintBoundingBox }
]
const trackFunctionSelected = ref(trackFunctionOptions[1])

/*** error handling ***/

const error = ref('')

function onError(err: Error & { name: string }) {
    error.value = `[${err.name}]: `

    if (err.name === 'NotAllowedError') {
        error.value += 'you need to grant camera access permission'
    } else if (err.name === 'NotFoundError') {
        error.value += 'no camera on this device'
    } else if (err.name === 'NotSupportedError') {
        error.value += 'secure context required (HTTPS, localhost)'
    } else if (err.name === 'NotReadableError') {
        error.value += 'is the camera already in use?'
    } else if (err.name === 'OverconstrainedError') {
        error.value += 'installed cameras are not suitable'
    } else if (err.name === 'StreamApiNotSupportedError') {
        error.value += 'Stream API is not supported in this browser'
    } else if (err.name === 'InsecureContextError') {
        error.value +=
            'Camera access is only permitted in secure context. Use HTTPS or localhost rather than HTTP.'
    } else {
        error.value += err.message
    }
}

</script>