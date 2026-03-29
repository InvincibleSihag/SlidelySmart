"""Image search service using Unsplash API."""

import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"


def search_image(query: str, orientation: str = "landscape") -> str:
    """Search Unsplash for a photo matching the query. Returns URL or error message."""
    if not settings.unsplash_access_key:
        logger.warning("unsplash_key_not_configured")
        return "Error: Unsplash API key is not configured. Cannot search for images."
    try:
        response = httpx.get(
            UNSPLASH_SEARCH_URL,
            params={"query": query, "per_page": 1, "orientation": orientation},
            headers={"Authorization": f"Client-ID {settings.unsplash_access_key}"},
            timeout=10.0,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            logger.info("unsplash_no_results", query=query)
            return f"Error: No images found for query '{query}'. Try a different description."
        url = results[0]["urls"]["regular"]
        logger.info("unsplash_image_found", query=query, url=url[:80])
        return url
    except httpx.HTTPStatusError as exc:
        logger.exception("unsplash_search_failed", query=query)
        return f"Error: Unsplash API returned status {exc.response.status_code}."
    except Exception as exc:
        logger.exception("unsplash_search_failed", query=query)
        return f"Error: Image search failed — {exc}"
