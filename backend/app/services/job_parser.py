import re
import hashlib
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from app.models import JobListing

COMMON_SKILLS = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "Java", "C++", "C#",
    "Go", "Rust", "FastAPI", "Django", "Flask", "SQL", "PostgreSQL", "MongoDB",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Git", "HTML", "CSS", "Tailwind",
    "Machine Learning", "Data Analysis", "Deep Learning", "NLP", "Pandas", "NumPy"
]

PLATFORM_DOMAINS = {
    "linkedin.com": "LinkedIn",
    "internshala.com": "Internshala",
    "indeed.com": "Indeed",
    "naukri.com": "Naukri",
    "wellfound.com": "Wellfound",
    "angel.co": "Wellfound",
    "glassdoor.com": "Glassdoor",
    "weworkremotely.com": "We Work Remotely",
    "remoteok.com": "RemoteOK",
    "ycombinator.com": "Y Combinator",
    "greenhouse.io": "Greenhouse",
    "lever.co": "Lever",
    "workday.com": "Workday",
    "smartrecruiters.com": "SmartRecruiters",
}


def clean_text(value: Optional[str]) -> str:
    """Normalize whitespace and strip HTML entities/tags."""
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", "", str(value))
    return re.sub(r"\s+", " ", text).strip()


def extract_domain_source(url: str) -> Optional[str]:
    """Identify clean source platform name from URL domain."""
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        for domain, name in PLATFORM_DOMAINS.items():
            if domain in netloc:
                return name
        return netloc if netloc else None
    except Exception:
        return None


def extract_skills_from_text(text: str) -> List[str]:
    """Identify explicitly mentioned technical skills."""
    if not text:
        return []
    found = []
    text_lower = f" {text.lower()} "
    for skill in COMMON_SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"
        if re.search(pattern, text_lower):
            found.append(skill)
    return found


def extract_company_and_title(raw_title: str, snippet: str, site_name: Optional[str]) -> tuple[str, Optional[str]]:
    """
    Parse out job title and hiring company from typical listing titles:
    e.g. 'Software Engineer at Acme Corp' or 'Acme Corp hiring Software Engineer'
    or 'Python Intern | TechCorp'
    """
    clean_t = clean_text(raw_title)
    company: Optional[str] = None

    if " at " in clean_t:
        parts = clean_t.split(" at ", 1)
        title = parts[0].strip()
        comp = parts[1].split(" - ")[0].split(" | ")[0].strip()
        return title, comp if comp else None

    if " is hiring " in clean_t:
        parts = clean_t.split(" is hiring ", 1)
        company = parts[0].strip()
        title = parts[1].split(" - ")[0].split(" | ")[0].strip()
        return title, company if company else None

    if " | " in clean_t:
        parts = clean_t.split(" | ")
        title = parts[0].strip()
        if len(parts) > 1:
            candidate = parts[-1].strip()
            # If candidate isn't just the platform name, use it as company
            platform_names = [p.lower() for p in PLATFORM_DOMAINS.values()]
            if candidate.lower() not in platform_names:
                company = candidate
        return title, company

    if " - " in clean_t:
        parts = clean_t.split(" - ")
        title = parts[0].strip()
        if len(parts) > 1:
            candidate = parts[-1].strip()
            if len(candidate) < 40 and not any(loc in candidate.lower() for loc in ["remote", "india", "delhi", "usa"]):
                platform_names = [p.lower() for p in PLATFORM_DOMAINS.values()]
                if candidate.lower() not in platform_names:
                    company = candidate
        return title, company

    return clean_t, company


def detect_work_mode(text: str) -> Optional[str]:
    """Detect whether listing mentions remote, hybrid, or on-site."""
    lower = text.lower()
    if "remote" in lower or "work from home" in lower or "wfh" in lower:
        return "Remote"
    if "hybrid" in lower:
        return "Hybrid"
    if "on-site" in lower or "onsite" in lower or "in-office" in lower:
        return "On-site"
    return None


def detect_employment_type(text: str) -> Optional[str]:
    """Detect employment type (internship vs full-time vs contract)."""
    lower = text.lower()
    if "intern" in lower or "internship" in lower:
        return "Internship"
    if "full-time" in lower or "full time" in lower or "permanent" in lower:
        return "Full-time"
    if "part-time" in lower or "part time" in lower:
        return "Part-time"
    if "contract" in lower or "freelance" in lower:
        return "Contract"
    return None


def detect_salary(text: str) -> Optional[str]:
    """Extract salary or stipend mentions."""
    salary_patterns = [
        r"[\$₹£€]\s?\d+(?:,\d+)*(?:\s?k|\s?K)?(?:\s?-\s?[\$₹£€]?\s?\d+(?:,\d+)*(?:\s?k|\s?K)?)?(?:\s?per\s?month|\s?per\s?year|\s?\/month|\s?\/mo\b|\s?\/year|\s?\/yr\b|\s?LPA\b)?",
        r"\b\d+\s?-\s?\d+\s?LPA\b",
        r"\b\d+(?:,\d+)*\s?(?:INR|USD|EUR)\b",
    ]
    for pat in salary_patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return None


def parse_job_item(raw_item: Dict[str, Any]) -> Optional[JobListing]:
    """
    Parse a single item from TinyFish search results into a validated JobListing model.
    Never invents nonexistent details.
    """
    if not isinstance(raw_item, dict):
        return None

    url = clean_text(raw_item.get("url"))
    raw_title = clean_text(raw_item.get("title"))
    snippet = clean_text(raw_item.get("snippet"))
    site_name = clean_text(raw_item.get("site_name"))

    if not url or not raw_title:
        return None

    generic_patterns = [
        r"^jobs in\b", r"^job search\b", r"^search jobs\b", r"^top \d+ jobs\b",
        r"^browse jobs\b", r"^find jobs\b"
    ]
    if any(re.search(pat, raw_title.lower()) for pat in generic_patterns):
        return None

    title, company = extract_company_and_title(raw_title, snippet, site_name)
    source = extract_domain_source(url) or site_name or "Web"

    combined_text = f"{raw_title} {snippet}"
    work_mode = detect_work_mode(combined_text)
    employment_type = detect_employment_type(combined_text)
    salary = detect_salary(combined_text)
    skills = extract_skills_from_text(combined_text)

    exp_level = None
    if any(term in combined_text.lower() for term in ["fresher", "entry level", "graduate", "0-1 year"]):
        exp_level = "Fresher / Entry level"
    elif "senior" in combined_text.lower():
        exp_level = "Senior"
    elif "mid" in combined_text.lower():
        exp_level = "Mid-level"

    item_id = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]

    return JobListing(
        id=item_id,
        title=title,
        company=company,
        location=None,
        description=snippet if snippet else None,
        skills=skills,
        employment_type=employment_type,
        experience_level=exp_level,
        work_mode=work_mode,
        salary=salary,
        source=source,
        url=url,
        posting_date=raw_item.get("publish_date") or None,
        status="Needs verification",
    )
