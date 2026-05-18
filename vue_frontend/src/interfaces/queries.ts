import type { components } from "./api-types"

type SearchQuery = components['schemas']['Query'] 
export interface Query {
  _id: string
  name: string
  query: SearchQuery
  description?: string | null
  created_at?: string | null
  updated_at?: string | null

}