from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.models import JobListing, SearchRequest
from app.services.job_parser import (
    parse_job_item,
    clean_text,
    extract_company_and_title,
    detect_work_mode,
    detect_employment_type,
    detect_salary,
    extract_skills_from_text,
    extract_domain_source,
)
from app.services.deduplication import canonicalize_url, deduplicate_jobs
from app.services.tinyfish import (
    TinyFishClient,
    TinyFishAuthError,
    TinyFishTimeoutError,
    TinyFishRateLimitError,
)

client = TestClient(app)


def test_health_check_endpoint():
    """Verify health endpoint returns status healthy and timestamp."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data
    assert "tinyfish_configured" in data


def test_search_request_validation():
    """Verify validation on empty or missing query string."""
    response = client.post("/api/search", json={"query": ""})
    assert response.status_code == 422  # Pydantic validation error

    response_missing = client.post("/api/search", json={})
    assert response_missing.status_code == 422


def test_clean_text_and_url_canonicalization():
    """Verify tracking parameters, fragments, and formatting are cleaned."""
    dirty_text = "  Senior   Python \n Developer  <b>Remote</b> "
    assert clean_text(dirty_text) == "Senior Python Developer Remote"

    url1 = "https://www.linkedin.com/jobs/view/12345/?utm_source=share&utm_medium=ios#section"
    url2 = "https://linkedin.com/jobs/view/12345"
    assert canonicalize_url(url1) == canonicalize_url(url2)
    assert canonicalize_url("https://internshala.com/internship/detail/123/?ref=search") == "https://internshala.com/internship/detail/123"


def test_job_parser_fields():
    """Verify parser extracts company, title, skills, work mode, and handles missing fields."""
    raw_item = {
        "title": "Python Developer Intern at TechCorp",
        "snippet": "We are looking for a remote Python and React intern with stipend ₹25,000/month. Freshers welcome.",
        "url": "https://internshala.com/internship/detail/python-intern-101",
        "site_name": "Internshala",
        "publish_date": "2026-10-18",
    }
    job = parse_job_item(raw_item)
    assert job is not None
    assert job.title == "Python Developer Intern"
    assert job.company == "TechCorp"
    assert job.source == "Internshala"
    assert job.work_mode == "Remote"
    assert job.employment_type == "Internship"
    assert "Python" in job.skills
    assert "React" in job.skills
    assert job.salary is not None
    assert "₹25,000/month" in job.salary
    assert job.status == "Needs verification"
    assert job.posting_date == "2026-10-18"


def test_job_parser_malformed_and_missing_fields():
    """Verify malformed or empty items are safely handled and never invent fields."""
    assert parse_job_item({}) is None
    assert parse_job_item({"title": "Job"}) is None  # Missing URL
    assert parse_job_item({"url": "https://example.com"}) is None  # Missing title

    # Item with no company, no salary, no skills
    minimal_item = {
        "title": "Junior Associate",
        "url": "https://example.com/jobs/assoc",
        "snippet": "Join our team today.",
    }
    job = parse_job_item(minimal_item)
    assert job is not None
    assert job.title == "Junior Associate"
    assert job.company is None
    assert job.salary is None
    assert job.skills == []


def test_deduplication_exact_url_and_company_title():
    """Verify deduplication removes exact canonical URLs and company+title duplicates, but keeps distinct companies."""
    job1 = JobListing(
        id="1",
        title="Frontend Engineer",
        company="Acme Corp",
        url="https://linkedin.com/jobs/view/100?utm_source=twitter",
    )
    job2 = JobListing(
        id="2",
        title="Frontend Engineer",
        company="Acme Corp",
        url="https://linkedin.com/jobs/view/100",  # Duplicate URL
    )
    job3 = JobListing(
        id="3",
        title="Frontend Engineer",
        company="Acme Corp",
        url="https://indeed.com/jobs/acme-frontend",  # Same company + title duplicate
    )
    job4 = JobListing(
        id="4",
        title="Frontend Engineer",
        company="Beta Ltd",  # Same title, different company -> MUST BE PRESERVED
        url="https://indeed.com/jobs/beta-frontend",
    )

    deduped, removed_count = deduplicate_jobs([job1, job2, job3, job4])
    assert len(deduped) == 2
    assert removed_count == 2
    assert deduped[0].company == "Acme Corp"
    assert deduped[1].company == "Beta Ltd"


def test_api_auth_failure_handling():
    """Verify 401 is properly raised and surfaced when TinyFish API key is invalid."""
    with patch.object(TinyFishClient, "search", side_effect=TinyFishAuthError("Invalid API key")):
        response = client.post("/api/search", json={"query": "Software Engineer"})
        assert response.status_code == 401
        assert "authentication failed" in response.json()["detail"].lower()


def test_api_timeout_handling():
    """Verify 504 is raised when TinyFish request times out."""
    with patch.object(TinyFishClient, "search", side_effect=TinyFishTimeoutError("Timed out")):
        response = client.post("/api/search", json={"query": "Software Engineer"})
        assert response.status_code == 504
        assert "timed out" in response.json()["detail"].lower()


def test_empty_search_results():
    """Verify empty response when TinyFish returns zero results."""
    mock_data = {"total_results": 0, "results": []}
    with patch.object(TinyFishClient, "search", new_callable=AsyncMock, return_value=mock_data):
        response = client.post("/api/search", json={"query": "NonexistentRareRoleXYZ"})
        assert response.status_code == 200
        data = response.json()
        assert data["total_found"] == 0
        assert data["deduplicated_count"] == 0
        assert data["results"] == []


def test_api_missing_key_handling():
    """Verify 401 is returned when TINYFISH_API_KEY is unset or empty."""
    with patch.object(TinyFishClient, "is_configured", False):
        response = client.post("/api/search", json={"query": "Software Engineer"})
        assert response.status_code == 401
        assert "not configured" in response.json()["detail"].lower()
