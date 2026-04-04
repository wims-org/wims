export interface ItemContainers {
    tag_uuid: string
    short_name: string
}
import type { components } from '@/interfaces/api-types'
import type { File } from '@/interfaces/file.interface'

type ItemPublic = components['schemas']['ItemPublic']

export interface Item extends ItemPublic {
    images?: File[]
    attachments?: File[]
}

