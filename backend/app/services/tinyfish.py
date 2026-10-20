import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import httpx

logger = logging.getLogger(__name__)


def get_tinyfish_api_key() -> str:
    """Dynamically read the latest TINYFISH_API_KEY from project-root .env."""
    root_env = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    if root_env.exists():
        load_dotenv(dotenv_path=root_env, override=True)
    return os.getenv("TINYFISH_API_KEY", "").strip()


class TinyFishError(Exception):
    """Base exception for TinyFish API interactions."""
    def __init__(self, message: str, code: str = "TINYFISH_ERROR", details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details


class TinyFishAuthError(TinyFishError):
    """Raised when authentication fails (missing, invalid, or expired key)."""
    def __init__(self, message: str = "TinyFish API key is missing or invalid. Check TINYFISH_API_KEY.", details: Optional[Any] = None):
        super().__init__(message, code="AUTH_FAILED", details=details)


class TinyFishTimeoutError(TinyFishError):
    """Raised when the TinyFish API request times out."""
    def __init__(self, message: str = "TinyFish API request timed out.", details: Optional[Any] = None):
        super().__init__(message, code="TIMEOUT", details=details)


class TinyFishRateLimitError(TinyFishError):
    """Raised when the rate limit is exceeded."""
    def __init__(self, message: str = "TinyFish API rate limit reached.", details: Optional[Any] = None):
        super().__init__(message, code="RATE_LIMITED", details=details)


class TinyFishAPIError(TinyFishError):
    """Raised when TinyFish returns a non-2xx status code or invalid response."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Any] = None):
        super().__init__(message, code=f"API_ERROR_{status_code}", details=details)
        self.status_code = status_code


class TinyFishClient:
    """Official TinyFish REST client for NextRole web search and extraction."""

    BASE_SEARCH_URL = "https://api.search.tinyfish.ai"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 30.0):
        self.api_key = (api_key or get_tinyfish_api_key()).strip()
        self.timeout = timeout

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _get_headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise TinyFishAuthError(
                "TINYFISH_API_KEY is not configured in backend environment. "
                "Please configure a valid key in .env or the system environment."
            )
        return {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
            "User-Agent": "NextRole-JobFinder/1.0",
        }

    def build_job_query(
        self,
        query: str,
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        work_mode: Optional[str] = None,
        employment_type: Optional[str] = None,
    ) -> str:
        """
        Construct a targeted search query for live job postings and internships
        across premier career platforms.
        """
        parts = [query.strip()]

        if location and location.strip():
            parts.append(location.strip())

        if experience_level and experience_level.strip():
            parts.append(experience_level.strip())

        if work_mode and work_mode.strip():
            parts.append(work_mode.strip())

        if employment_type and employment_type.strip():
            parts.append(employment_type.strip())
        else:
            parts.append("jobs OR internships")

        # Focus query on recognized hiring portals and career listings
        targeted_query = " ".join(parts)
        return targeted_query

    async def search(
        self,
        query: str,
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        work_mode: Optional[str] = None,
        employment_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a search request against TinyFish Web API.
        Returns the raw parsed response from TinyFish.
        """
        headers = self._get_headers()
        full_query = self.build_job_query(
            query=query,
            location=location,
            experience_level=experience_level,
            work_mode=work_mode,
            employment_type=employment_type,
        )

        params: Dict[str, Any] = {"query": full_query}

        # Resolve country location code if standard recognized
        loc_clean = (location or "").strip().lower()
        if "india" in loc_clean or "delhi" in loc_clean or "bangalore" in loc_clean or "mumbai" in loc_clean:
            params["location"] = "IN"
        elif "us" in loc_clean or "usa" in loc_clean or "united states" in loc_clean:
            params["location"] = "US"

        logger.info(f"Querying TinyFish API with search query: {full_query}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.BASE_SEARCH_URL,
                    headers=headers,
                    params=params,
                )

                if response.status_code == 401:
                    err_json = {}
                    try:
                        err_json = response.json()
                    except Exception:
                        pass
                    msg = err_json.get("error", {}).get("message", "Invalid or expired TinyFish API key.")
                    raise TinyFishAuthError(msg, details=err_json)

                if response.status_code == 429:
                    raise TinyFishRateLimitError("TinyFish search rate limit exceeded. Please retry in a moment.")

                if response.status_code != 200:
                    err_text = response.text[:200]
                    raise TinyFishAPIError(
                        f"TinyFish API returned status {response.status_code}: {err_text}",
                        status_code=response.status_code,
                    )

                data = response.json()
                if not isinstance(data, dict):
                    raise TinyFishAPIError("Malformed response received from TinyFish: root is not a dictionary.")

                return data

        except httpx.TimeoutException as exc:
            logger.error(f"TinyFish request timed out: {exc}")
            raise TinyFishTimeoutError("Request to TinyFish API timed out after 30 seconds.") from exc
        except httpx.RequestError as exc:
            logger.error(f"Network error communicating with TinyFish: {exc}")
            raise TinyFishAPIError(f"Network error communicating with TinyFish: {str(exc)}") from exc
