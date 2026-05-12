<template>
    <div class="footer">
        <BButton v-if="clientStore().getNFCCapability" class="primary p-1 me-2" variant="success" size="lg" @click="showNFCModal = true">
            <IMaterialSymbolsNfc class="nfc-icon" />
        </BButton>
        <BButton class="primary p-1" variant="success" size="lg" @click="showQRReaderModal = true">
            <IMaterialSymbolsQrCodeScanner class="qr-icon" />
        </BButton>
    </div>
    <BModal v-if="showQRReaderModal" v-model="showQRReaderModal" title="QR Code Scanner" size="lg" hide-footer>
        <QRReader @scan="showQRReaderModal = false" />
    </BModal>
    <BModal v-if="showNFCModal" v-model="showNFCModal" title="NFC Reader"
        size="lg" hide-footer>
        <NFCReader @scan="showNFCModal = false" />
    </BModal>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { clientStore } from '@/stores/clientStore';

const showQRReaderModal = ref(false)
const showNFCModal = ref(false)     
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

.qr-icon, .nfc-icon {
    font-size: 2rem;
}
</style>