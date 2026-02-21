type NdefReaderInstance = {
	scan: (options?: { signal?: AbortSignal }) => Promise<void>
	onreading: ((event: NfcReadingEvent) => void) | null
	onreadingerror: ((event: Event) => void) | null
}

type NdefReaderConstructor = new () => NdefReaderInstance

type NdefRecord = {
	recordType: string
	mediaType?: string
	id?: string
	encoding?: string
	lang?: string
	data?: DataView
}

type NfcReadingEvent = Event & {
	serialNumber?: string
	message: {
		records: NdefRecord[]
	}
}

export interface NFCRecordPayload extends Record<string, unknown> {
	record_type: string
	media_type?: string
	id?: string
	encoding?: string
	lang?: string
	text?: string
}

export interface NFCScanResult {
	tag_id: string
	serial_number?: string
	records: NFCRecordPayload[]
}

class NFCService {
	private reader: NdefReaderInstance | null = null
	private abortController: AbortController | null = null

	public isSupported(): boolean {
		const readerConstructor = (window as Window & { NDEFReader?: NdefReaderConstructor }).NDEFReader
		return typeof readerConstructor === 'function'
	}

	public isSecureContext(): boolean {
		return window.isSecureContext
	}

	public async start(
		onRead: (result: NFCScanResult) => void,
		onError: (error: Error & { name?: string }) => void,
	): Promise<void> {
		if (!this.isSupported()) {
			onError(Object.assign(new Error('Web NFC is not supported in this browser/device.'), { name: 'NotSupportedError' }))
			return
		}

		if (!this.isSecureContext()) {
			onError(
				Object.assign(new Error('NFC access is only permitted in secure context. Use HTTPS or localhost.'), {
					name: 'InsecureContextError',
				}),
			)
			return
		}

		const readerConstructor = (window as Window & { NDEFReader?: NdefReaderConstructor }).NDEFReader
		if (!readerConstructor) {
			onError(Object.assign(new Error('NDEFReader API unavailable.'), { name: 'NotSupportedError' }))
			return
		}

		this.abortController = new AbortController()
		this.reader = new readerConstructor()

		this.reader.onreading = (event: NfcReadingEvent) => {
			try {
				const records = event.message.records.map((record) => this.parseRecord(record))
				const tagId = this.getTagId(event.serialNumber, records)
				onRead({
					tag_id: tagId,
					serial_number: event.serialNumber,
					records,
				})
			} catch (error) {
				onError(Object.assign(new Error('Failed to parse NFC payload.'), { name: 'NFCParseError', cause: error }))
			}
		}

		this.reader.onreadingerror = () => {
			onError(Object.assign(new Error('NFC tag was detected but could not be read.'), { name: 'NFCReadError' }))
		}

		await this.reader.scan({ signal: this.abortController.signal })
	}

	public stop(): void {
		this.abortController?.abort()
		this.abortController = null
		if (this.reader) {
			this.reader.onreading = null
			this.reader.onreadingerror = null
		}
		this.reader = null
	}

	private parseRecord(record: NdefRecord): NFCRecordPayload {
		const text = this.decodeRecordText(record)

		return {
			record_type: record.recordType,
			media_type: record.mediaType,
			id: record.id,
			encoding: record.encoding,
			lang: record.lang,
			text,
		}
	}

	private decodeRecordText(record: NdefRecord): string | undefined {
		if (!record.data) {
			return undefined
		}

		try {
			if (record.recordType === 'text' || record.recordType === 'url') {
				const encoding = record.encoding ?? 'utf-8'
				const decoder = new TextDecoder(encoding)
				return decoder.decode(record.data)
			}

			return undefined
		} catch {
			return undefined
		}
	}

	private getTagId(serialNumber: string | undefined, records: NFCRecordPayload[]): string {
		const firstText = records.find((record) => typeof record.text === 'string' && record.text.trim().length > 0)?.text

		if (firstText) {
			return firstText
		}

		if (serialNumber && serialNumber.length > 0) {
			return serialNumber
		}

		return 'unknown-nfc-tag'
	}
}

export default new NFCService()
