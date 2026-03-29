"""Application configuration from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database (PostgreSQL)
    database_url: str

    # GCP
    google_application_credentials: str | None = None
    gcs_bucket_name: str = "slidely-presentations"
    gcp_project_id: str = ""

    # Celery / Redis
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Logging
    log_level: str = "INFO"
    log_json: bool = True

    # Pusher
    pusher_app_id: str = ""
    pusher_key: str = ""
    pusher_secret: str = ""
    pusher_cluster: str = "mt1"

    # Unsplash (image search for slides)
    unsplash_access_key: str = ""


settings = Settings()
