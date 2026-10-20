import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from app.models import SearchRequest, SearchResponse, HealthResponse

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify backend status and configuration."""
    api_key = os.getenv("TINYFISH_API_KEY", "").strip()
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
        tinyfish_configured=bool(api_key),
    )
