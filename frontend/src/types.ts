export interface JobListing {
  id: string
  title: string
  company?: string | null
  location?: string | null
  description?: string | null
  skills: string[]
  employment_type?: string | null
  experience_level?: string | null
  work_mode?: string | null
  salary?: string | null
  source?: string | null
  url: string
  posting_date?: string | null
  extracted_at: string
  status: string
}

export interface SearchRequest {
  query: string
  location?: string
  experience_level?: string
  work_mode?: string
  employment_type?: string
  limit?: number
}

export interface SearchResponse {
  query: string
  total_found: number
  deduplicated_count: number
  results: JobListing[]
  applied_filters: Record<string, string>
  search_metadata: {
    source: string
    provider_total?: number
    retrieved_at: string
  }
}

export type SearchState = 
  | 'idle' 
  | 'searching' 
  | 'success' 
  | 'empty' 
  | 'error' 
  | 'auth_error' 
  | 'timeout'
