import type { EventAction } from '@/interfaces/EventAction';
import mitt from 'mitt'
import type { components } from '@/interfaces/api-types';
type Events = {
  [EventAction.REDIRECT]: components['schemas']['ScanRequest']
  [EventAction.FORM_SCAN_ADD]: components['schemas']['ScanRequest']
  [EventAction.CONTAINER_SCAN]: components['schemas']['ScanRequest']
  [EventAction.ALIVE]: { reader_id: string }
  [EventAction.COMPLETION]: { data: { response: object } }
  [EventAction.ERROR]: { id: string; reader_id: string, data: { message: string } }
}

const eventBus = mitt<Events>()

export default eventBus
export type { Events }
