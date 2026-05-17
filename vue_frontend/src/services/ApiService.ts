import axios from 'axios'

import type { File } from '@/interfaces/file.interface'
import type { Item } from '@/interfaces/items.interface'
import type { components } from '@/interfaces/api-types'


type Query = components['schemas']['Query']
type ItemPublic = components['schemas']['ItemPublic']
type FilePublic = components['schemas']['FilePublic']

type ItemContainer = components["schemas"]["ContainerObject"]
class ApiService {
    private static instance: ApiService

    private constructor() {
        // Private constructor to prevent direct instantiation
    }

    public static getInstance(): ApiService {
        if (!ApiService.instance) {
            ApiService.instance = new ApiService()
        }
        return ApiService.instance
    }

    private filePublicToFile(filePub: FilePublic): File {
        if (filePub.uri && !filePub.uri.startsWith('http')) {
            const base = axios.defaults.baseURL ?? ''
            return { ...filePub, asset_url: `${base}${filePub.uri.startsWith('/') ? '' : '/'}${filePub.uri}` }
        }
        return { ...filePub, asset_url: filePub.uri || '' }
    }

    itemPublicToItem(itemPub: ItemPublic): Item {
        // Adds asset_url based on uri if asset_url is not already a full URL
        const item = { ...itemPub } as Item
        if (Array.isArray(item.files) && item.files.length) {
            item.images = []
            item.attachments = []
            itemPub.files?.map((file) => {
                const f = this.filePublicToFile(file)
                if (f.filetype && f.filetype === 'image') {
                    item.images?.push(f)
                } else {
                    item.attachments?.push(f)
                }
            })
        }
        return item
    }

    itemToItemPublic(item: Item): ItemPublic {
        const itemPub = { ...item } as ItemPublic
        if (Array.isArray(itemPub.files) && itemPub.files.length) {
            itemPub.files = (item.images?.concat(item.attachments || []) || []).map((file) => {
                return { ...file } as FilePublic
            })
        }
        return itemPub
    }

    public async getItem(itemId: number): Promise<Item> {
        try {
            return axios.get<Item>(`/items/${itemId}`).then((response) => {
                // File paths in item data are relative to the backend, so we need to prepend the base URL to them
                const item: Item = response.data
                return this.itemPublicToItem(item)
            })
        } catch (error) {
            console.error('Error fetching item:', error)
            throw error
        }
    }

    public async searchItems(searchQuery: Query): Promise<Item[]> {
        try {
            return axios.post('/items/search', searchQuery).then((response) => {
                const items: Item[] = response.data
                items.forEach((item, index) => { items[index] = this.itemPublicToItem(item) })
                return items
            })
        } catch (error) {
            console.error('Error searching items:', error)
            throw error
        }
    }

    public async createItem(itemData: Item): Promise<Item> {
        try {
            return axios.post<Item>('/items', this.itemToItemPublic(itemData)).then((response) => {
                const item: Item = response.data
                return this.itemPublicToItem(item)
            })
        } catch (error) {
            console.error('Error creating item:', error)
            throw error
        }
    }

    public async updateItem(itemId: number, item: Item): Promise<void> {
        try {
            await axios.put(`/items/${itemId}`, this.itemToItemPublic(item))
        } catch (error) {
            console.error('Error updating item:', error)
            throw error
        }
    }

    public async deleteItem(itemId: number): Promise<void> {
        try {
            await axios.delete(`/items/${itemId}`)
        } catch (error) {
            console.error('Error deleting item:', error)
            throw error
        }
    }

    public async createFile(fileData: FormData): Promise<File> {
        try {
            return axios.post<File>('/files', fileData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                }
            }).then((response) => {
                const file: File = response.data
                return this.filePublicToFile(file)
            }).catch((error) => {
                if (error.response && error.response.status === 413) {
                    console.error('File size too large:', error)
                }
                throw error
            })
        } catch (error) {
            console.error('Error creating file:', error)
            throw error
        }
    }

    public async getItemContainers(itemId: number): Promise<ItemContainer[]> {
        try {
            return axios.get<ItemContainer[]>(`/items/${itemId}/containers`).then((response) => response.data)
        } catch (error) {
            console.error('Error fetching item containers:', error)
            throw error
        }
    }
}

export default ApiService.getInstance()
