import React from 'react'
import { ExternalLink, Building, MapPin, Calendar, DollarSign, ShieldAlert } from 'lucide-react'
import type { JobListing } from '../types'

interface JobCardProps {
  job: JobListing
}

export const JobCard: React.FC<JobCardProps> = ({ job }) => {
  const formattedDate = job.posting_date || 'Recently discovered'

  return (
    <div className="job-card">
      <div className="job-card-header">
        <div className="job-title-company">
          <h3 className="job-title">{job.title}</h3>
          <div className="job-company-row">
            <span className="company-name">
              <Building size={14} className="inline-icon" />
              {job.company || 'Hiring Organization'}
            </span>
            {job.location && (
              <span className="job-meta-item">
                <MapPin size={13} className="inline-icon" />
                {job.location}
              </span>
            )}
            <span className="source-tag">
              via {job.source || 'Web'}
            </span>
          </div>
        </div>

        <div className="badges-group">
          {job.work_mode && (
            <span className={`pill-badge badge-${job.work_mode.toLowerCase()}`}>
              {job.work_mode}
            </span>
          )}
          {job.employment_type && (
            <span className="pill-badge badge-type">
              {job.employment_type}
            </span>
          )}
          {job.experience_level && (
            <span className="pill-badge badge-exp">
              {job.experience_level}
            </span>
          )}
        </div>
      </div>

      {job.description && (
        <p className="job-description">
          {job.description}
        </p>
      )}

      {/* Skills list */}
      {job.skills && job.skills.length > 0 && (
        <div className="skills-row">
          {job.skills.map((skill, idx) => (
            <span key={idx} className="skill-chip">
              {skill}
            </span>
          ))}
        </div>
      )}

      {/* Footer with Salary, Freshness status, and Apply link */}
      <div className="job-card-footer">
        <div className="footer-meta-left">
          {job.salary && (
            <span className="salary-tag">
              <DollarSign size={13} className="inline-icon" />
              {job.salary}
            </span>
          )}

          <span
            className="status-verification-badge"
            title="NextRole retrieved this listing via live web search. The posting status has not been confirmed by automated form submission."
          >
            <ShieldAlert size={12} className="inline-icon" />
            {job.status}
          </span>

          <span className="posting-time">
            <Calendar size={12} className="inline-icon" />
            {formattedDate}
          </span>
        </div>

        <a
          href={job.url}
          target="_blank"
          rel="noopener noreferrer"
          className="apply-button"
          aria-label={`Apply for ${job.title} at ${job.company || 'hiring company'} (opens in a new tab)`}
        >
          <span>Apply / View Job</span>
          <ExternalLink size={14} aria-hidden="true" />
        </a>
      </div>
    </div>
  )
}
