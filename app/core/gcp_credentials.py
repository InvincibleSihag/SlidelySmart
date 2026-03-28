"""Resolve GCP credentials from file path, JSON string (e.g. Secret Manager), or ADC."""

from google.oauth2 import service_account

from app.core.config import settings


def get_gcp_credentials() -> service_account.Credentials | None:
    """
    Return service account credentials when key is provided via file path or JSON string.
    Return None to use Application Default Credentials (e.g. Cloud Run runtime SA).
    """
    if settings.google_application_credentials:
        return service_account.Credentials.from_service_account_file(
            settings.google_application_credentials
        )
    return None
