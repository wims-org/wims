import mitt from 'mitt'

type Events = {
  scan: { rfid: string; reader_id: string }
  completion:  {data:{response:object}}
}

const eventBus = mitt<Events>()

export default eventBus
export type { Events }
