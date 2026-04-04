
import type { components } from '@/interfaces/api-types'

type FilePublic = components['schemas']['FilePublic']

interface File extends FilePublic {
    asset_url: string
}

export type { File }