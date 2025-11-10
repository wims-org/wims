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
}

export enum SearchType {
  USER = 'user',
  ITEM = 'item',
  QUERY = 'query'
}

export const SearchTypeEndpoint: Record<SearchType, string> = {
  [SearchType.ITEM]: '/items/search',
  [SearchType.USER]: '/users',
  [SearchType.QUERY]: '/search'
}
export const formFields: Record<string, FormField> = {
  tag_uuid: { label: 'Item UUID', type: 'text', disabled: true, hidden: false, details: false, required: true },
  short_name: { label: 'Short Name', type: 'text', disabled: false, hidden: false, details: false, required: true },
  description: { label: 'Description', type: 'textarea', disabled: false, hidden: false, details: false, required: false },
  images: { label: 'Images', type: 'images', disabled: false, hidden: false, details: false, required: false },
  amount: { label: 'Amount', type: 'number', disabled: false, hidden: false, details: false, required: true },
  item_type: { label: 'Item Type', type: 'text', disabled: false, hidden: false, details: false, required: true },
  consumable: { label: 'Consumable', type: 'checkbox', disabled: false, hidden: false, details: false, required: false },
  created_at: { label: 'Created At', type: 'epoch', disabled: true, hidden: false, details: false, required: false },
  created_by: { label: 'Created By', type: 'user', disabled: true, hidden: false, details: false, required: false, search_type: SearchType.USER },
  min_amount: { label: 'Minimum Amount', type: 'number', disabled: false, hidden: false, details: false, required: false },
  cost_new: { label: 'Cost New', type: 'number', disabled: false, hidden: false, details: false, required: false },
  acquisition_date: { label: 'Acquisition Date', type: 'epoch', disabled: false, hidden: false, details: false, required: false },
  manufacturing_date: { label: 'Manufacturing Date', type: 'epoch', disabled: false, hidden: false, details: false, required: false },
  container_tag_uuid: { label: 'Container UUID', type: 'uuid', disabled: false, hidden: false, details: false, required: false },

  container: { label: 'Container', type: 'item', disabled: true, hidden: false, details: true, required: false },
  changes: { label: 'Changes', type: 'array', disabled: true, hidden: true, details: true, required: false },
  ai_generated: { label: 'AI Generated', type: 'array', disabled: true, hidden: true, details: true, required: false },
  tags: { label: 'Tags', type: 'array', disabled: false, hidden: false, details: true, required: false },
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
  borrowed_by: { label: 'Borrowed By', type: 'user', disabled: false, hidden: false, details: true, required: false, search_type: SearchType.USER },
  borrowed_at: { label: 'Borrowed At', type: 'epoch', disabled: false, hidden: false, details: true, required: false },
  borrowed_until: { label: 'Borrowed Until', type: 'epoch', disabled: false, hidden: false, details: true, required: false },
  owner_id: { label: 'Owner', type: 'user', disabled: false, hidden: false, details: true, required: false, search_type: SearchType.USER },
  // owner: { label: 'Owner', type: 'object', disabled: false, hidden: false, details: true, required: false, search_type: SearchType.USER },
};