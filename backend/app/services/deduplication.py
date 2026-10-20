import re
from typing import List, Tuple
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from app.models import JobListing

# Tracking / analytics parameters to remove during URL canonicalization
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "refId", "trackingId", "fbclid", "gclid", "source", "trk",
    "origin", "position", "pageNum", "sessionId", "midToken"
}


def canonicalize_url(raw_url: str) -> str:
    """
    Standardize URL by lowercasing scheme & netloc, stripping tracking query params,
    and removing trailing slashes and fragments.
    """
    if not raw_url:
        return ""

    raw_url = raw_url.strip()
    if not raw_url.startswith(("http://", "https://")):
        return raw_url

    try:
        parts = urlsplit(raw_url)
        scheme = parts.scheme.lower()
        netloc = parts.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]

        path = parts.path.rstrip("/")

        # Filter out tracking query parameters
        clean_query_pairs = [
            (k, v) for k, v in parse_qsl(parts.query, keep_blank_values=False)
            if k.lower() not in TRACKING_PARAMS
        ]
        # Sort query params for consistent canonicalization
        clean_query_pairs.sort()
        query = urlencode(clean_query_pairs)

        return urlunsplit((scheme, netloc, path, query, ""))
    except Exception:
        return raw_url.strip().rstrip("/")


def normalize_string(val: str) -> str:
    """Normalize string to lowercase alphanumeric tokens."""
    if not val:
        return ""
    return re.sub(r"[^a-z0-9]", "", val.lower())


def deduplicate_jobs(listings: List[JobListing]) -> Tuple[List[JobListing], int]:
    """
    Deduplicate a list of JobListing objects in order of preference:
    1. Exact canonical URL
    2. Normalized (company + job title) pair when both are present
    
    Returns (deduplicated_listings, count_of_removed_duplicates).
    Preserves the original source and application link of the first encountered listing.
    """
    seen_urls = set()
    seen_company_titles = set()
    deduped: List[JobListing] = []
    duplicates_count = 0

    for job in listings:
        # Rule 1: Canonical URL matching
        canon_url = canonicalize_url(job.url)
        if canon_url and canon_url in seen_urls:
            duplicates_count += 1
            continue

        # Rule 2: Normalized company name + job title matching
        norm_title = normalize_string(job.title)
        norm_company = normalize_string(job.company or "")

        # Only merge if BOTH company and title match, never on title alone!
        if norm_company and norm_title:
            comp_title_key = (norm_company, norm_title)
            if comp_title_key in seen_company_titles:
                duplicates_count += 1
                continue
            seen_company_titles.add(comp_title_key)

        if canon_url:
            seen_urls.add(canon_url)

        deduped.append(job)

    return deduped, duplicates_count
