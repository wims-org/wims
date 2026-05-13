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
          <button type="button" class="btn btn-danger" @click="returnNone">Clear</button>
          <button type="button" class="btn btn-secondary" @click="closeModal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import SearchComponent from '@/components/shared/SearchComponent.vue'
import eventBus, { type Events } from '@/stores/eventBus'
import { clientStore } from '@/stores/clientStore'
import { EventAction } from '@/interfaces/EventAction'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'select', id: number|undefined): void
}>()

const saved_action = ref(EventAction.REDIRECT)

function listenToScanEvent() {
  saved_action.value = clientStore().expected_event_action
  clientStore().setExpectedEventAction(EventAction.CONTAINER_SCAN)
  eventBus.on(EventAction.CONTAINER_SCAN, (data: Events[EventAction.CONTAINER_SCAN]) => {
    console.log(
      'SearchModal received scan event:',
      data,
      clientStore().expected_event_action,
      clientStore().expected_event_action === EventAction.CONTAINER_SCAN,
    )
    handleSelect(data.id)
  })
}

function returnNone() {
  emit('select', undefined)
  closeModal()
}

function closeModal() {
  eventBus.off(EventAction.CONTAINER_SCAN)
  clientStore().setExpectedEventAction(saved_action.value)
  emit('close')
}

function handleSelect(id: number) {
  console.log('SearchModal handleSelect called with id:', id)
  emit('select', id)
  closeModal()
}

watch(() => props.show, (newVal) => {
  console.log('SearchModal show changed:', newVal)
  if (newVal) {
    listenToScanEvent()
  } else {
    closeModal()
  }
})
</script>

<style scoped>
.modal {
  display: block;
  background: rgba(0, 0, 0, 0.5);
}
</style>
