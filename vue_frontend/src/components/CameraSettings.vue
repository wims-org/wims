<template>
    <div >
        <span v-for="option in Object.keys(barcodeFormats)" :key="option" class="barcode-format-checkbox">
            <input type="checkbox" v-model="barcodeFormats[option]" :id="option" />
            <label :for="option">{{ option }}</label>
        </span>
    </div>
</template>

<script setup lang="ts">
import { clientStore } from '@/stores/clientStore'
import { ref, watch } from 'vue'
clientStore()

/*** barcode formats ***/

const barcodeFormats = ref<Record<string, boolean>>({
    aztec: false,
    code_128: false,
    code_39: false,
    code_93: false,
    codabar: false,
    databar: false,
    databar_expanded: false,
    data_matrix: false,
    dx_film_edge: false,
    ean_13: false,
    ean_8: false,
    itf: false,
    maxi_code: false,
    micro_qr_code: false,
    pdf417: false,
    qr_code: true,
    rm_qr_code: false,
    upc_a: false,
    upc_e: false,
    linear_codes: false,
    matrix_codes: false
})

watch(barcodeFormats, () => {
    clientStore().setSelectedBarcodeFormats(Object.keys(barcodeFormats.value).filter((format) => barcodeFormats.value[format]))
}, { deep: true })

</script>