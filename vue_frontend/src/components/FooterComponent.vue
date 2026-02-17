<template>
    <div class="footer">
        <BButton class="primary p-1" variant="success" size="lg" @click="showQRReaderModal = true">
            <IMaterialSymbolsQrCodeScanner class="qr-icon" />
        </BButton>
    </div>
    <BModal v-if="showQRReaderModal" v-model="showQRReaderModal" title="QR Code Scanner" size="lg" hide-footer>
        <QRReader @scan="showQRReaderModal = false" />
    </BModal>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showQRReaderModal = ref(false)
</script>

<style>
.footer {
    position: fixed;
    display: flex;
    justify-content: right;
    padding: 1rem;
    bottom: 0;
    right: 0;
    font-size: 5rem;
}
.qr-icon {
    font-size: 2rem;
}
</style>