import type { SearchRequest, SearchResponse } from '../types'

export class ApiError extends Error {
  status: number
  code: string

  constructor(message: string, status: number, code: string = 'API_ERROR') {
    super(message)
    this.status = status
    this.code = code
  }
}

export async function checkBackendHealth(): Promise<{ status: string; tinyfish_configured: boolean }> {
  try {
    const res = await fetch('/api/health')
    if (!res.ok) {
      throw new Error(`Health check failed with status ${res.status}`)
    }
    return await res.json()
  } catch {
    return { status: 'offline', tinyfish_configured: false }
  }
}

export async function executeSearch(req: SearchRequest): Promise<SearchResponse> {
  const res = await fetch('/api/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req),
  })

  if (!res.ok) {
    let errorDetail = 'Job search request failed.'
    try {
      const errorJson = await res.json()
      if (errorJson.detail) {
        errorDetail = errorJson.detail
      }
    } catch {
      errorDetail = await res.text() || errorDetail
    }

    if (res.status === 401) {
      throw new ApiError(errorDetail, 401, 'AUTH_ERROR')
    }
    if (res.status === 504) {
      throw new ApiError(errorDetail, 504, 'TIMEOUT_ERROR')
    }
    if (res.status === 429) {
      throw new ApiError(errorDetail, 429, 'RATE_LIMIT')
    }

    throw new ApiError(errorDetail, res.status, 'API_ERROR')
  }

  return await res.json()
}
