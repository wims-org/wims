export interface Query {
  _id: string
  name: string
  query: Record<string, unknown>
  description?: string | null
  created_at?: string | null
  updated_at?: string | null

}