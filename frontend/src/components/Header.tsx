import React from 'react'
import { Sparkles, CheckCircle2, AlertCircle } from 'lucide-react'

interface HeaderProps {
  backendOnline: boolean
  tinyfishConfigured: boolean
}

export const Header: React.FC<HeaderProps> = ({ backendOnline, tinyfishConfigured }) => {
  return (
    <header className="header-container">
      <div className="brand-bar">
        <div className="logo-group">
          <div className="logo-badge">
            <Sparkles className="logo-icon" size={24} />
          </div>
          <div>
            <div className="brand-title-wrap">
              <h1 className="brand-title">NextRole</h1>
              <span className="version-pill">MVP</span>
            </div>
            <p className="brand-subtitle">
              Unified Job & Internship Finder powered by TinyFish Web API
            </p>
          </div>
        </div>

        <div className="status-indicators">
          <div className={`status-pill ${backendOnline ? 'online' : 'offline'}`} title="FastAPI Backend">
            <span className="status-dot"></span>
            <span>API: {backendOnline ? 'Connected' : 'Offline'}</span>
          </div>
          <div
            className={`status-pill ${tinyfishConfigured ? 'configured' : 'warning'}`}
            title="TinyFish API Key configured on backend"
          >
            {tinyfishConfigured ? (
              <CheckCircle2 size={13} className="text-emerald-400" />
            ) : (
              <AlertCircle size={13} className="text-amber-400" />
            )}
            <span>TinyFish: {tinyfishConfigured ? 'Configured' : 'Needs Key'}</span>
          </div>
        </div>
      </div>
    </header>
  )
}
