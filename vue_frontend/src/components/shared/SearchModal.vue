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

<script lang="ts">
import { defineComponent } from 'vue'
import SearchComponent from '@/components/shared/SearchComponent.vue'
import eventBus, { type Events } from '@/stores/eventBus'
import { clientStore } from '@/stores/clientStore'
import { EventAction } from '@/interfaces/EventAction'

export default defineComponent({
  name: 'SearchModal',
  components: {
    SearchComponent,
  },
  data() {
    return {
      saved_action: EventAction.REDIRECT,
    }
  },
  props: {
    show: {
      type: Boolean,
      required: true,
    },
  },
  emits: ['close', 'select'],

  mounted() {
    console.log('SearchModal mounted')
  },
  
  onChange() {
    console.log('SearchModal onChange')
    if (this.show) {
      this.listenToScanEvent()
    } else {
      this.closeModal()
    }
  },

  methods: {
    listenToScanEvent() {
      this.saved_action = clientStore().expected_event_action
      clientStore().setExpectedEventAction(EventAction.CONTAINER_SCAN)
      eventBus.on('scan', (data: Events['scan']) => {
        if (clientStore().expected_event_action !== EventAction.CONTAINER_SCAN) {
          this.handleSelect(data.rfid)
        }
      })
    },
    returnNone() {
      this.$emit('select', '')
      this.closeModal()
    },
    closeModal() {
      eventBus.off('scan')
      clientStore().setExpectedEventAction(this.saved_action)
      this.$emit('close')
    },
    handleSelect(tag: string) {
      this.$emit('select', tag)
      this.closeModal()
    },
  },
})
</script>

<style scoped>
.modal {
  display: block;
  background: rgba(0, 0, 0, 0.5);
}
</style>
