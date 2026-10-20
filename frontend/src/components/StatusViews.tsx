import React from 'react'
import {
  KeyRound,
  ClockAlert,
  SearchX,
  AlertTriangle,
  RotateCw,
  Compass,
  FileCode,
} from 'lucide-react'

interface StateViewProps {
  onRetry?: () => void
  errorDetail?: string
}

export const InitialStateView: React.FC = () => {
  return (
    <div className="state-panel initial-state">
      <div className="state-icon-circle blue">
        <Compass size={32} />
      </div>
      <h2>Discover Unified Opportunities</h2>
      <p className="state-description">
        Search for internships and early-career jobs across multiple supported platforms
        with one query. Powered by TinyFish Web API extraction and automated duplicate filtering.
      </p>
      <div className="features-highlight-grid">
        <div className="feature-item">
          <h4>Multi-Source Discovery</h4>
          <p>Find postings from LinkedIn, Internshala, Indeed, and direct career sites.</p>
        </div>
        <div className="feature-item">
          <h4>Duplicate Removal</h4>
          <p>Cross-source URL and company-role deduplication keeps your results clean.</p>
        </div>
        <div className="feature-item">
          <h4>Direct Application</h4>
          <p>Links take you straight to the original application portal without middlemen.</p>
        </div>
      </div>
    </div>
  )
}

export const LoadingStateView: React.FC = () => {
  return (
    <div className="state-panel loading-state">
      <div className="skeleton-cards-list">
        {[1, 2, 3].map((n) => (
          <div key={n} className="skeleton-card">
            <div className="skeleton-header">
              <div className="skeleton-line title"></div>
              <div className="skeleton-badge"></div>
            </div>
            <div className="skeleton-line company"></div>
            <div className="skeleton-line desc"></div>
            <div className="skeleton-line desc short"></div>
            <div className="skeleton-footer">
              <div className="skeleton-pill"></div>
              <div className="skeleton-pill"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export const EmptyResultsView: React.FC<{ query: string; onReset: () => void }> = ({ query, onReset }) => {
  return (
    <div className="state-panel empty-state">
      <div className="state-icon-circle gray">
        <SearchX size={32} />
      </div>
      <h2>No Listings Found</h2>
      <p className="state-description">
        No active listings matched your search criteria for "<strong>{query}</strong>".
      </p>
      <div className="empty-tips">
        <p>Suggestions:</p>
        <ul>
          <li>Try broader role terms (e.g., "Developer" or "Software Engineer").</li>
          <li>Remove specific location or work mode restrictions.</li>
          <li>Check for typos in the query.</li>
        </ul>
      </div>
      <button onClick={onReset} className="secondary-button">
        Clear Filters and Retry
      </button>
    </div>
  )
}

export const AuthErrorView: React.FC<StateViewProps> = ({ errorDetail, onRetry }) => {
  return (
    <div className="state-panel error-state auth-error">
      <div className="state-icon-circle amber">
        <KeyRound size={32} />
      </div>
      <h2>TinyFish API Credentials Required</h2>
      <p className="state-description">
        The backend was unable to authenticate with the TinyFish Web API.
      </p>

      {errorDetail && (
        <div className="error-detail-box">
          <code>{errorDetail}</code>
        </div>
      )}

      <div className="setup-guide-card">
        <h3><FileCode size={16} className="inline-icon" /> How to configure your TinyFish API Key:</h3>
        <ol>
          <li>
            Visit <a href="https://agent.tinyfish.ai/api-keys" target="_blank" rel="noopener noreferrer">agent.tinyfish.ai/api-keys</a> and generate an API key.
          </li>
          <li>
            Open or create the <code>.env</code> file in your NextRole project root.
          </li>
          <li>
            Add your key:
            <pre><code>TINYFISH_API_KEY=your_actual_key_here</code></pre>
          </li>
          <li>Restart or reload your FastAPI backend.</li>
        </ol>
      </div>

      {onRetry && (
        <button onClick={onRetry} className="primary-action-btn">
          <RotateCw size={15} /> Retry Search
        </button>
      )}
    </div>
  )
}

export const TimeoutErrorView: React.FC<StateViewProps> = ({ errorDetail, onRetry }) => {
  return (
    <div className="state-panel error-state timeout-error">
      <div className="state-icon-circle amber">
        <ClockAlert size={32} />
      </div>
      <h2>Request Timed Out</h2>
      <p className="state-description">
        The live web extraction request to TinyFish exceeded the timeout threshold.
      </p>
      {errorDetail && (
        <div className="error-detail-box">
          <code>{errorDetail}</code>
        </div>
      )}
      {onRetry && (
        <button onClick={onRetry} className="primary-action-btn">
          <RotateCw size={15} /> Try Again
        </button>
      )}
    </div>
  )
}

export const GenericErrorView: React.FC<StateViewProps> = ({ errorDetail, onRetry }) => {
  return (
    <div className="state-panel error-state">
      <div className="state-icon-circle red">
        <AlertTriangle size={32} />
      </div>
      <h2>Search Encountered An Error</h2>
      <p className="state-description">
        Unable to complete the search request at this time.
      </p>
      {errorDetail && (
        <div className="error-detail-box">
          <code>{errorDetail}</code>
        </div>
      )}
      {onRetry && (
        <button onClick={onRetry} className="primary-action-btn">
          <RotateCw size={15} /> Retry
        </button>
      )}
    </div>
  )
}
