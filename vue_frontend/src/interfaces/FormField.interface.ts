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
  id: { label: 'ID', type: 'text', disabled: true, hidden: true, details: false, required: false },
  short_name: { label: 'Short Name', type: 'text', disabled: false, hidden: false, details: false, required: true },
  description: { label: 'Description', type: 'textarea', disabled: false, hidden: false, details: false, required: false },
  images: { label: 'Images', type: 'images', disabled: false, hidden: false, details: false, required: false },
  category: { label: 'Category', type: 'category', disabled: false, hidden: false, details: false, required: false, search_type: SearchType.CATEGORY, resolves: 'category_id' },
  tags: { label: 'Tags', type: 'array', disabled: false, hidden: false, details: false, required: false },
  container: { label: 'Container', type: 'item', disabled: false, hidden: false, details: false, required: false, search_type: SearchType.ITEM, qrSearch: true, nfcSearch: true, resolves: 'container_id' },
  code: { label: 'Code (Barcode/RFID/Other)', type: 'uuid', disabled: false, hidden: false, details: false, required: false },
  // Details:
  amount: { label: 'Amount', type: 'number', disabled: false, hidden: false, details: true, required: false },
  consumable: { label: 'Consumable', type: 'checkbox', disabled: false, hidden: false, details: true, required: false },
  created_at: { label: 'Created At', type: 'epoch', disabled: true, hidden: false, details: true, required: false },
  created_by: { label: 'Created By', type: 'user', disabled: true, hidden: false, details: true, required: false, search_type: SearchType.USER, resolves: 'created_by_id' },
  min_amount: { label: 'Minimum Amount', type: 'number', disabled: false, hidden: false, details: true, required: false },
  cost_new: { label: 'Cost New', type: 'number', disabled: false, hidden: false, details: true, required: false },
  acquisition_date: { label: 'Acquisition Date', type: 'epoch', disabled: false, hidden: true, details: false, required: false },
  manufacturing_date: { label: 'Manufacturing Date', type: 'epoch', disabled: false, hidden: true, details: false, required: false },
  changes: { label: 'Changes', type: 'array', disabled: true, hidden: true, details: true, required: false },
  ai_generated: { label: 'AI Generated', type: 'array', disabled: true, hidden: true, details: true, required: false },
  cost_used: { label: 'Cost Used', type: 'number', disabled: false, hidden: false, details: true, required: false },
  manufacturer: { label: 'Manufacturer', type: 'text', disabled: false, hidden: false, details: true, required: false },
  model_number: { label: 'Model Number', type: 'text', disabled: false, hidden: false, details: true, required: false },
  upc: { label: 'UPC', type: 'text', disabled: false, hidden: false, details: true, required: false },
  asin: { label: 'ASIN', type: 'text', disabled: false, hidden: false, details: true, required: false },
  serial_number: { label: 'Serial Number', type: 'text', disabled: false, hidden: false, details: true, required: false },
  vendors: { label: 'Vendors', type: 'array', disabled: false, hidden: false, details: true, required: false },
  shop_url: { label: 'Shop URL', type: 'array', disabled: false, hidden: false, details: true, required: false },
  size: { label: 'Size', type: 'object', disabled: false, hidden: false, details: true, required: false },
  documentation: { label: 'Documentation', type: 'array', disabled: false, hidden: false, details: true, required: false },
  related_items: { label: 'Related Items', type: 'array', disabled: false, hidden: false, details: true, required: false },
  current_location: { label: 'Current Location', type: 'text', disabled: false, hidden: false, details: true, required: false },
  borrower: { label: 'Borrowed By', type: 'user', disabled: false, hidden: false, details: true, required: false, search_type: SearchType.USER, resolves: 'borrower_id' },
  borrowed_at: { label: 'Borrowed At', type: 'epoch', disabled: false, hidden: false, details: true, required: false },
  borrowed_until: { label: 'Borrowed Until', type: 'epoch', disabled: false, hidden: false, details: true, required: false },
  owner: { label: 'Owner', type: 'user', disabled: false, hidden: false, details: true, required: false, search_type: SearchType.USER, resolves: 'owner_id' },
};