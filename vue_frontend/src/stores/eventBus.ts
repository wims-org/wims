import type { EventAction } from '@/interfaces/EventAction';
import mitt from 'mitt'

type Events = {
  [EventAction.REDIRECT]: { rfid: string; reader_id: string }
  [EventAction.FORM_SCAN_ADD]: { rfid: string; reader_id: string }
  [EventAction.CONTAINER_SCAN]: { rfid: string; reader_id: string }
  [EventAction.ALIVE]: { reader_id: string }
  [EventAction.COMPLETION]: { data: { response: object } }
  [EventAction.ERROR]:  { rfid: string; reader_id: string, data: { message: string } }
}

const eventBus = mitt<Events>()

export default eventBus
export type { Events }
