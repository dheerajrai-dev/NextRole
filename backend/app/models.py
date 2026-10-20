from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, HttpUrl


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Job title or keywords (e.g. Python Developer Intern)")
    location: Optional[str] = Field(None, description="Preferred location (e.g. Delhi NCR, Remote, India)")
    experience_level: Optional[str] = Field(None, description="Experience level (e.g. Fresher, 0-1 years, Mid-level)")
    work_mode: Optional[str] = Field(None, description="Work mode (e.g. Remote, Hybrid, On-site)")
    employment_type: Optional[str] = Field(None, description="Employment type (e.g. Internship, Full-time)")
    limit: Optional[int] = Field(20, ge=1, le=50, description="Maximum number of listings to return")


class JobListing(BaseModel):
    id: str = Field(..., description="Unique deterministic identifier")
    title: str = Field(..., description="Job title")
    company: Optional[str] = Field(None, description="Hiring company name")
    location: Optional[str] = Field(None, description="Job location")
    description: Optional[str] = Field(None, description="Summary or snippet of the role")
    skills: List[str] = Field(default_factory=list, description="Extracted required skills")
    employment_type: Optional[str] = Field(None, description="Internship, Full-time, etc.")
    experience_level: Optional[str] = Field(None, description="Experience requirement")
    work_mode: Optional[str] = Field(None, description="Remote, Hybrid, On-site")
    salary: Optional[str] = Field(None, description="Salary or stipend information")
    source: Optional[str] = Field(None, description="Source platform name")
    url: str = Field(..., description="Canonical link to the original listing")
    posting_date: Optional[str] = Field(None, description="Date posted if available")
    extracted_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp when retrieved by NextRole"
    )
    status: str = Field(
        default="Needs verification",
        description="Freshness/verification status indicator"
    )


class SearchResponse(BaseModel):
    query: str
    total_found: int
    deduplicated_count: int
    results: List[JobListing]
    applied_filters: Dict[str, Any]
    search_metadata: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "0.1.0"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tinyfish_configured: bool = False
