import os
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from app.models import SearchRequest, SearchResponse, HealthResponse, JobListing
from app.services.tinyfish import (
    TinyFishClient,
    TinyFishAuthError,
    TinyFishTimeoutError,
    TinyFishRateLimitError,
    TinyFishAPIError,
    get_tinyfish_api_key,
)
from app.services.job_parser import parse_job_item
from app.services.deduplication import deduplicate_jobs

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify backend status and configuration."""
    api_key = get_tinyfish_api_key()
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
        tinyfish_configured=bool(api_key),
    )


@router.post("/search", response_model=SearchResponse)
async def search_jobs(request: SearchRequest):
    """
    Execute a live job search using the TinyFish Web API, parse results,
    apply duplicate elimination, and return normalized listings.
    """
    client = TinyFishClient()

    if not client.is_configured:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="TINYFISH_API_KEY is not configured on the backend server. "
                   "Please set the TINYFISH_API_KEY environment variable in your .env file."
        )

    try:
        raw_data = await client.search(
            query=request.query,
            location=request.location,
            experience_level=request.experience_level,
            work_mode=request.work_mode,
            employment_type=request.employment_type,
        )
    except TinyFishAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"TinyFish authentication failed: {exc.message}. Please check your TINYFISH_API_KEY."
        )
    except TinyFishTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Search request timed out: {exc.message}. Please retry in a moment."
        )
    except TinyFishRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"TinyFish API rate limit exceeded: {exc.message}. Please wait a moment."
        )
    except TinyFishAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TinyFish API error: {exc.message}"
        )
    except Exception as exc:
        logger.exception("Unexpected error during job search")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal error occurred: {str(exc)}"
        )

    raw_results = raw_data.get("results", [])
    parsed_jobs = []
    for item in raw_results:
        parsed = parse_job_item(item)
        if parsed:
            parsed_jobs.append(parsed)

    # Simple, understandable deduplication in Python
    deduped_jobs, removed_count = deduplicate_jobs(parsed_jobs)

    # Respect user limit
    limit = request.limit or 20
    final_results = deduped_jobs[:limit]

    applied_filters = {
        "location": request.location,
        "experience_level": request.experience_level,
        "work_mode": request.work_mode,
        "employment_type": request.employment_type,
    }

    return SearchResponse(
        query=request.query,
        total_found=len(raw_results),
        deduplicated_count=removed_count,
        results=final_results,
        applied_filters={k: v for k, v in applied_filters.items() if v is not None},
        search_metadata={
            "source": "TinyFish Web API",
            "provider_total": raw_data.get("total_results", len(raw_results)),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        },
    )
