<template>
    <div class="footer">
        <BButton class="primary p-1" variant="success" size="lg" @click="showReaderModal = true">
            <IMaterialSymbolsQrCodeScanner class="qr-icon" />
        </BButton>
    </div>
    <BModal v-if="showReaderModal" v-model="showReaderModal" title="QR Code Scanner" size="lg" hide-footer>
        
        <NFCReader @scan="showReaderModal = false" />
        <QRReader @scan="showReaderModal = false" />
    </BModal>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showReaderModal = ref(false)
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