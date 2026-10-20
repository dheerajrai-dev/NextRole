import React, { useState, useEffect } from 'react'
import { Header } from './components/Header'
import { SearchBar } from './components/SearchBar'
import { JobCard } from './components/JobCard'
import {
  InitialStateView,
  LoadingStateView,
  EmptyResultsView,
  AuthErrorView,
  TimeoutErrorView,
  GenericErrorView,
} from './components/StatusViews'
import type { SearchRequest, SearchResponse, SearchState } from './types'
import { checkBackendHealth, executeSearch, ApiError } from './services/api'
import { Layers } from 'lucide-react'

export const App: React.FC = () => {
  const [backendOnline, setBackendOnline] = useState<boolean>(false)
  const [tinyfishConfigured, setTinyfishConfigured] = useState<boolean>(false)

  const [searchState, setSearchState] = useState<SearchState>('idle')
  const [lastRequest, setLastRequest] = useState<SearchRequest | null>(null)
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState<string>('')

  // Check health on mount
  useEffect(() => {
    const probeHealth = async () => {
      const health = await checkBackendHealth()
      setBackendOnline(health.status === 'healthy')
      setTinyfishConfigured(health.tinyfish_configured)
    }
    probeHealth()
    const timer = setInterval(probeHealth, 15000)
    return () => clearInterval(timer)
  }, [])

  const handleSearch = async (req: SearchRequest) => {
    setLastRequest(req)
    setSearchState('searching')
    setErrorMessage('')

    try {
      const data = await executeSearch(req)
      setSearchResponse(data)

      if (data.results.length === 0) {
        setSearchState('empty')
      } else {
        setSearchState('success')
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'An unexpected error occurred.')
      if (err instanceof ApiError) {
        if (err.code === 'AUTH_ERROR' || err.status === 401) {
          setSearchState('auth_error')
          return
        }
        if (err.code === 'TIMEOUT_ERROR' || err.status === 504) {
          setSearchState('timeout')
          return
        }
      }
      setSearchState('error')
    }
  }

  const handleRetry = () => {
    if (lastRequest) {
      handleSearch(lastRequest)
    }
  }

  const handleReset = () => {
    setSearchState('idle')
    setSearchResponse(null)
    setLastRequest(null)
    setErrorMessage('')
  }

  return (
    <div className="app-container">
      <Header backendOnline={backendOnline} tinyfishConfigured={tinyfishConfigured} />

      <main className="main-content">
        <SearchBar onSearch={handleSearch} isLoading={searchState === 'searching'} />

        {/* Search Results Summary Header */}
        {searchState === 'success' && searchResponse && (
          <div className="results-meta-banner animate-fade-in">
            <div className="meta-stats-group">
              <span className="results-count-pill">
                <strong>{searchResponse.results.length}</strong> opportunities found
              </span>
              <span className="dedup-stat-pill">
                <Layers size={13} className="inline-icon" />
                <strong>{searchResponse.deduplicated_count}</strong> duplicates filtered
              </span>
              <span className="provider-pill">
                Powered by TinyFish Web API
              </span>
            </div>

            {Object.keys(searchResponse.applied_filters).length > 0 && (
              <div className="active-filters-chips">
                <span className="filters-label">Filters:</span>
                {Object.entries(searchResponse.applied_filters).map(([k, v]) => (
                  <span key={k} className="filter-badge">
                    {k.replace('_', ' ')}: <strong>{v}</strong>
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Dynamic State Views */}
        {searchState === 'idle' && <InitialStateView />}
        {searchState === 'searching' && <LoadingStateView />}
        {searchState === 'empty' && (
          <EmptyResultsView
            query={lastRequest?.query || ''}
            onReset={handleReset}
          />
        )}
        {searchState === 'auth_error' && (
          <AuthErrorView errorDetail={errorMessage} onRetry={handleRetry} />
        )}
        {searchState === 'timeout' && (
          <TimeoutErrorView errorDetail={errorMessage} onRetry={handleRetry} />
        )}
        {searchState === 'error' && (
          <GenericErrorView errorDetail={errorMessage} onRetry={handleRetry} />
        )}

        {/* Results List */}
        {searchState === 'success' && searchResponse && (
          <div className="job-cards-grid animate-fade-in">
            {searchResponse.results.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          NextRole MVP — Unified Job & Internship Discovery with TinyFish Web API.
        </p>
      </footer>
    </div>
  )
}

export default App
