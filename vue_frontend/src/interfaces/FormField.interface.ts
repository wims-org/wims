export default interface SearchConfig {
  debounce?: number
  minLength?: number
  query?: object
  endpoint?: string
  method?: 'GET' | 'POST'
}

export interface FormField {
  name?: string
  label: string
  type: string
  value?: string | number | boolean | undefined
  error?: string | null | undefined
  disabled?: boolean
  hidden?: boolean
  details?: boolean
  required?: boolean
  search_type?: SearchType
  qrSearch?: boolean
  nfcSearch?: boolean
  resolves?: string
}


export enum SearchType {
  USER = 'user',
  ITEM = 'item',
  CATEGORY = 'category'
}

export const SearchTypeEndpoint: Record<SearchType, string> = {
  [SearchType.ITEM]: '/items/search',
  [SearchType.USER]: '/users/search',
  [SearchType.CATEGORY]: '/categories/search',
}
export const formFields: Record<string, FormField> = {
  id: { label: 'ID', type: 'text', disabled: true, hidden: true },
  short_name: { label: 'Short Name', type: 'text', required: true },
  description: { label: 'Description', type: 'textarea' },
  images: { label: 'Images', type: 'images' },
  category: { label: 'Category', type: 'category', search_type: SearchType.CATEGORY, resolves: 'category_id' },
  tags: { label: 'Tags', type: 'array' },
  container: { label: 'Container', type: 'item', search_type: SearchType.ITEM, qrSearch: true, nfcSearch: true, resolves: 'container_id' },
  code: { label: 'Code (Barcode/RFID/Other)', type: 'uuid' },
  // Details:
  amount: { label: 'Amount', type: 'number', details: true },
  consumable: { label: 'Consumable', type: 'checkbox', details: true },
  created_at: { label: 'Created At', type: 'epoch', disabled: true, details: true },
  created_by: { label: 'Created By', type: 'user', disabled: true, details: true, search_type: SearchType.USER, resolves: 'created_by_id' },
  min_amount: { label: 'Minimum Amount', type: 'number', details: true },
  cost_new: { label: 'Cost New', type: 'number', details: true },
  acquisition_date: { label: 'Acquisition Date', type: 'epoch', hidden: true },
  manufacturing_date: { label: 'Manufacturing Date', type: 'epoch', hidden: true },
  changes: { label: 'Changes', type: 'array', disabled: true, hidden: true, details: true },
  ai_generated: { label: 'AI Generated', type: 'array', disabled: true, hidden: true, details: true },
  cost_used: { label: 'Cost Used', type: 'number', details: true },
  manufacturer: { label: 'Manufacturer', type: 'text', details: true },
  model_number: { label: 'Model Number', type: 'text', details: true },
  upc: { label: 'UPC', type: 'text', details: true },
  asin: { label: 'ASIN', type: 'text', details: true },
  serial_number: { label: 'Serial Number', type: 'text', details: true },
  vendors: { label: 'Vendors', type: 'array', details: true },
  shop_url: { label: 'Shop URL', type: 'array', details: true },
  size: { label: 'Size', type: 'object', details: true },
  documentation: { label: 'Documentation', type: 'array', details: true },
  related_items: { label: 'Related Items', type: 'array', details: true },
  current_location: { label: 'Current Location', type: 'text', details: true },
  borrower: { label: 'Borrowed By', type: 'user', details: true, search_type: SearchType.USER, resolves: 'borrower_id' },
  borrowed_at: { label: 'Borrowed At', type: 'epoch', details: true },
  borrowed_until: { label: 'Borrowed Until', type: 'epoch', details: true },
  owner: { label: 'Owner', type: 'user', details: true, search_type: SearchType.USER, resolves: 'owner_id' },
};