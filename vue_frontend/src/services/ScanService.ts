import { clientStore } from "@/stores/clientStore"
import axios from "axios"

class ScanService {
    private static instance: ScanService

    private constructor() {
        // Private constructor to prevent direct instantiation
    }

    public static getInstance(): ScanService {
        if (!ScanService.instance) {
            ScanService.instance = new ScanService()
        }
        return ScanService.instance
    }

    public async sendScanResult(result: string, data: Record<string, unknown>[] | null = null): Promise<void> {
        if (!result) return
        axios.post('/scan', {
            reader_id: clientStore().getClientId, // set client_id as reader_id since the client is the reader.
            tag_id: result,
            data: data
        }).catch((error) => {
            if (error.status === 404) {
                console.log('New item scanned')
                return
            }
            console.error('Error sending scan result:', error)
        })

    }
}

export default ScanService.getInstance()    