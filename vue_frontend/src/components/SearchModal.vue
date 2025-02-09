<template>
    <div class="modal" tabindex="-1" role="dialog" v-if="show">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Search Container</h5>
                    <button type="button" class="close" @click="closeModal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <p>Search or scan RFID tag of container</p>
                    <SearchComponent @select="handleSelect" />
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" @click="closeModal">Close</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import SearchComponent from './SearchComponent.vue';
import eventBus from '@/stores/eventBus';

export default defineComponent({
    name: 'SearchModal',
    components: {
        SearchComponent,
    },
    props: {
        show: {
            type: Boolean,
            required: true,
        },
    },
    emits: ['close', 'select'],
    mounted() {
        this.listenToScanEvent();
    },
    methods: {
        listenToScanEvent() {
            eventBus.on('scan', (event: unknown) => {
                const parsedData = JSON.parse(event.replace(/'/g, '"'));
                this.handleSelect(parsedData.rfid);
            });
        },
        closeModal() {
            this.$emit('close');
        },
        handleSelect(tag: string) {
            this.$emit('select', tag);
            this.closeModal();
        },
    },
});
</script>

<style scoped>
.modal {
    display: block;
    background: rgba(0, 0, 0, 0.5);
}
</style>