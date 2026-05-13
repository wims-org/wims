import type { EventAction } from '@/interfaces/EventAction';
import mitt from 'mitt'
import type { components } from '@/interfaces/api-types';
type Events = {
  [EventAction.REDIRECT]: components['schemas']['SseEvent']['data']
  [EventAction.NEW_ITEM]: components['schemas']['SseEvent']['data']
  [EventAction.FORM_SCAN_ADD]: components['schemas']['SseEvent']['data']
  [EventAction.CONTAINER_SCAN]: components['schemas']['SseEvent']['data']
  [EventAction.ALIVE]: { reader_id: string }
  [EventAction.IDENTIFICATION]: { data: { response: object } }
  [EventAction.ERROR]: { id: string; reader_id: string, data: { message: string } }
  [EventAction.ELEMENT_UPDATE_READERS]: { element: string }
  [EventAction.ELEMENT_UPDATE_CONTAINER]: { element: string }
  [EventAction.ELEMENT_UPDATE_USERS]: { element: string }
  [EventAction.ELEMENT_UPDATE_CATEGORIES]: { element: string }
}

const eventBus = mitt<Events>()

export default eventBus
export type { Events }
