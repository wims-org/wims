import axios from 'axios'

import type { File } from '@/interfaces/file.interface'
import type { Item } from '@/interfaces/items.interface'
import type { components } from '@/interfaces/api-types'


type Query = components['schemas']['Query'] & { [key: string]: unknown }
type ItemUpdate = components['schemas']['ItemUpdate'] & { [key: string]: unknown }

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

    private addBaseUrlAndSplitByFileType(item: Item): Item {
        // Adds asset_url based on asset_path if asset_url is not already a full URL
        if (Array.isArray(item.files) && item.files.length) {
            item.images = []
            item.attachments = []
            item.files.map((file) => {
                if (!file.asset_path) { return }
                let f: File
                if (!file.asset_path.startsWith('http')) {
                    f = { ...file, asset_url: `${axios.defaults.baseURL}/${file.asset_path}` }
                } else {
                    f = { ...file, asset_url: file.asset_path }
                }
                if (f.filetype && f.filetype.startsWith('image')) {
                    item.images?.push(f)
                } else {
                    item.attachments?.push(f)
                }
            })
        }
        return item
    }

    public async getItem(itemId: number): Promise<Item> {
        try {
            return axios.get<Item>(`/items/${itemId}`).then((response) => {
                // File paths in item data are relative to the backend, so we need to prepend the base URL to them
                const item: Item = response.data
                this.addBaseUrlAndSplitByFileType(item)
                return item
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
                items.forEach((item) => this.addBaseUrlAndSplitByFileType(item))
                return items
            })
        } catch (error) {
            console.error('Error searching items:', error)
            throw error
        }
    }

    public async createItem(itemData: Item): Promise<Item> {
        try {
            return axios.post<Item>('/items', itemData).then((response) => {
                const item: Item = response.data
                this.addBaseUrlAndSplitByFileType(item)
                return item
            })
        } catch (error) {
            console.error('Error creating item:', error)
            throw error
        }
    }

    public async updateItem(itemId: number, item: ItemUpdate): Promise<void> {
        //        for (const fileArray of ['files', 'images']) { if (Array.isArray(item[fileArray]) && item[fileArray].length) { this.removeBaseUrlFromFilePaths(item[fileArray] as File[]) } }
        try {
            console.log('Updating item with ID:', itemId, 'and data:', item)
            await axios.put(`/items/${itemId}`, item)
        } catch (error) {
            console.error('Error updating item:', error)
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
                if (file.asset_path && !file.asset_path.startsWith('http')) {
                    file.asset_url = `${axios.defaults.baseURL}/${file.asset_path}`
                }
                return file
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
