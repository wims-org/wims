import mitt from 'mitt';

type Events = {
    scan: { tag_uuid: string };
    completion: { data: unknown };
  };

const eventBus = mitt<Events>();

export default eventBus;
export type { Events };