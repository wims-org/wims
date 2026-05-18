import type { components } from "@/interfaces/api-types"
import axios from "axios"

type ScanRequest = components['schemas']['ScanRequest']
type ScanResponse = components['schemas']['ScanResponse']

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

    public async sendScanResult(data: ScanRequest): Promise<ScanResponse | void> {
        console.log('Sending scan result:', data)
        axios.post('/scan', data).then(response => {
            console.log('Received scan result:', response.data)
            return response.data as ScanResponse
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