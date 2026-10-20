import React, { useState } from 'react'
import { Search, MapPin, Briefcase, Clock, Building2, SlidersHorizontal, ArrowRight, Loader2 } from 'lucide-react'
import type { SearchRequest } from '../types'

interface SearchBarProps {
  onSearch: (request: SearchRequest) => void
  isLoading: boolean
}

const SAMPLE_TAGS = [
  { label: 'Python Developer Intern', query: 'Python Developer Intern', location: 'Remote', type: 'Internship' },
  { label: 'React Frontend Fresher', query: 'React Frontend Developer', location: 'India', level: 'Fresher' },
  { label: 'AI/ML Engineering Intern', query: 'Machine Learning Intern', location: 'Remote', type: 'Internship' },
  { label: 'Backend Node.js Remote', query: 'Backend Developer', location: 'Remote', mode: 'Remote' },
]

export const SearchBar: React.FC<SearchBarProps> = ({ onSearch, isLoading }) => {
  const [query, setQuery] = useState('')
  const [location, setLocation] = useState('')
  const [workMode, setWorkMode] = useState<string>('')
  const [employmentType, setEmploymentType] = useState<string>('')
  const [experienceLevel, setExperienceLevel] = useState<string>('')
  const [showFilters, setShowFilters] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || isLoading) return

    onSearch({
      query: query.trim(),
      location: location.trim() || undefined,
      work_mode: workMode || undefined,
      employment_type: employmentType || undefined,
      experience_level: experienceLevel || undefined,
    })
  }

  const handleTagClick = (tag: typeof SAMPLE_TAGS[0]) => {
    setQuery(tag.query)
    if (tag.location) setLocation(tag.location)
    if (tag.type) setEmploymentType(tag.type)
    if (tag.level) setExperienceLevel(tag.level)
    if (tag.mode) setWorkMode(tag.mode)

    onSearch({
      query: tag.query,
      location: tag.location,
      employment_type: tag.type,
      experience_level: tag.level,
      work_mode: tag.mode,
    })
  }

  return (
    <div className="search-section">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-inputs-grid">
          {/* Query input */}
          <div className="input-group">
            <Search className="input-icon" size={18} aria-hidden="true" />
            <input
              type="text"
              id="search-query"
              name="query"
              aria-label="Job title, keywords, or role"
              className="search-input"
              placeholder="Job title, keywords, or role (e.g. Python Developer Intern)..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>

          {/* Location input */}
          <div className="input-group location-group">
            <MapPin className="input-icon" size={18} aria-hidden="true" />
            <input
              type="text"
              id="search-location"
              name="location"
              aria-label="Location"
              className="search-input"
              placeholder="Location (e.g. Delhi NCR, Remote, Bengaluru)..."
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              disabled={isLoading}
            />
          </div>

          {/* Action buttons */}
          <div className="search-actions">
            <button
              type="button"
              className={`filter-toggle-btn ${showFilters ? 'active' : ''}`}
              onClick={() => setShowFilters(!showFilters)}
              aria-expanded={showFilters}
              aria-controls="filters-tray"
              title="Toggle smart filters"
            >
              <SlidersHorizontal size={17} aria-hidden="true" />
              <span>Filters</span>
            </button>

            <button
              type="submit"
              className="search-submit-btn"
              disabled={isLoading || !query.trim()}
              aria-label={isLoading ? "Searching for opportunities..." : "Find Opportunities"}
            >
              {isLoading ? (
                <>
                  <Loader2 size={18} className="spinner" aria-hidden="true" />
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <span>Find Opportunities</span>
                  <ArrowRight size={18} aria-hidden="true" />
                </>
              )}
            </button>
          </div>
        </div>

        {/* Filters bar */}
        {showFilters && (
          <div id="filters-tray" className="filters-tray animate-fade-in" role="region" aria-label="Search filters">
            <div className="filter-item">
              <label htmlFor="filter-work-mode"><Briefcase size={14} aria-hidden="true" /> Work Mode</label>
              <select
                id="filter-work-mode"
                name="work_mode"
                value={workMode}
                onChange={(e) => setWorkMode(e.target.value)}
                disabled={isLoading}
              >
                <option value="">Any Work Mode</option>
                <option value="Remote">Remote</option>
                <option value="Hybrid">Hybrid</option>
                <option value="On-site">On-site</option>
              </select>
            </div>

            <div className="filter-item">
              <label htmlFor="filter-employment-type"><Clock size={14} aria-hidden="true" /> Employment Type</label>
              <select
                id="filter-employment-type"
                name="employment_type"
                value={employmentType}
                onChange={(e) => setEmploymentType(e.target.value)}
                disabled={isLoading}
              >
                <option value="">Any Type</option>
                <option value="Internship">Internship</option>
                <option value="Full-time">Full-time</option>
                <option value="Part-time">Part-time</option>
                <option value="Contract">Contract</option>
              </select>
            </div>

            <div className="filter-item">
              <label htmlFor="filter-experience-level"><Building2 size={14} aria-hidden="true" /> Experience</label>
              <select
                id="filter-experience-level"
                name="experience_level"
                value={experienceLevel}
                onChange={(e) => setExperienceLevel(e.target.value)}
                disabled={isLoading}
              >
                <option value="">Any Experience</option>
                <option value="Fresher">Fresher / Entry level</option>
                <option value="0-1 years">0-1 Years</option>
                <option value="Mid-level">Mid-level</option>
                <option value="Senior">Senior</option>
              </select>
            </div>
          </div>
        )}
      </form>

      {/* Suggested Quick Searches */}
      <div className="quick-tags">
        <span className="tags-label">Popular student searches:</span>
        <div className="tags-list">
          {SAMPLE_TAGS.map((tag, idx) => (
            <button
              key={idx}
              type="button"
              className="quick-tag-chip"
              onClick={() => handleTagClick(tag)}
              disabled={isLoading}
            >
              {tag.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
