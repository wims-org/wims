<template>
    <div>
        <span v-for="option in Object.keys(barcodeFormats)" :key="option" class="barcode-format-checkbox">
            <input type="checkbox" v-model="barcodeFormats[option as BarcodeFormats[number]]" :id="option" />
            <label :for="option">{{ option }}</label>
        </span>
    </div>
</template>

<script setup lang="ts">
import type { BarcodeFormats } from '@/interfaces/reader.interface'
import { clientStore } from '@/stores/clientStore'
import {  ref, watch } from 'vue'
const barcodeFormats = ref<Record<BarcodeFormats[number], boolean>>(clientStore().getSelectedBarcodeFormats.reduce((acc, format) => {
    acc[format] = true
    return acc
}, {} as Record<BarcodeFormats[number], boolean>))

watch(barcodeFormats, (newFormats) => {
    const selectedFormats = Object.keys(newFormats).filter(format => newFormats[format as BarcodeFormats[number]]) as BarcodeFormats
    clientStore().setSelectedBarcodeFormats(selectedFormats)
}, { deep: true })

</script>