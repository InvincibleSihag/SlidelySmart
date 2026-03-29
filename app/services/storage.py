"""Platform-agnostic object storage with pluggable backends."""

from __future__ import annotations

from abc import ABC, abstractmethod

from google.api_core.exceptions import NotFound

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Abstract storage client
# ---------------------------------------------------------------------------

class StorageClient(ABC):
    """Platform-agnostic blob storage interface."""

    @abstractmethod
    def upload(self, path: str, data: str | bytes, content_type: str = "application/octet-stream") -> str:
        """Upload data to the given logical path. Returns the stored path."""

    @abstractmethod
    def download(self, path: str) -> str | None:
        """Download text content from the given logical path. Returns None on failure."""


# ---------------------------------------------------------------------------
# GCS implementation
# ---------------------------------------------------------------------------

class GCSStorageClient(StorageClient):
    """Google Cloud Storage backend."""

    def __init__(self, bucket_name: str, project_id: str | None = None):
        from app.core.gcp_credentials import get_gcp_credentials
        from google.cloud import storage

        credentials = get_gcp_credentials()
        self._client = storage.Client(
            credentials=credentials if credentials else None,
            project=project_id,
        )
        self._bucket = self._client.bucket(bucket_name)

    def upload(self, path: str, data: str | bytes, content_type: str = "application/octet-stream") -> str:
        blob = self._bucket.blob(path)
        blob.upload_from_string(data, content_type=content_type)
        return path

    def download(self, path: str) -> str | None:
        try:
            blob = self._bucket.blob(path)
            return blob.download_as_text()
        except NotFound:
            logger.debug("storage_blob_not_found", path=path)
            return None
        except Exception:
            logger.exception("storage_download_failed", path=path)
            return None


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_client: StorageClient | None = None


def get_storage_client() -> StorageClient:
    """Return a singleton StorageClient instance."""
    global _client
    if _client is None:
        _client = GCSStorageClient(
            bucket_name=settings.gcs_bucket_name,
            project_id=settings.gcp_project_id,
        )
    return _client


# ---------------------------------------------------------------------------
# Domain helpers — thin wrappers so call sites stay simple
# ---------------------------------------------------------------------------

SLIDE_DECKS_PREFIX = "slide-decks"


def upload_version_html(slide_deck_id: str, version_num: int, html: str) -> str:
    """Upload rendered HTML for a version. Returns the logical storage path."""
    path = f"{SLIDE_DECKS_PREFIX}/{slide_deck_id}/v{version_num}/slides.html"
    return get_storage_client().upload(path, html, content_type="text/html")


def get_version_html(path: str | None) -> str | None:
    """Download rendered HTML from storage by path."""
    if not path:
        return None
    return get_storage_client().download(path)
