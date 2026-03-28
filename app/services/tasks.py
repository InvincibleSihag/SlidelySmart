"""Celery tasks for async job processing."""

import asyncio

from app.core.logging import get_logger
from app.services.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="process_job", bind=True, max_retries=0)
def process_job_task(self, payload_dict: dict) -> None:
    """Celery task wrapper — deserializes payload and calls process_slide_deck().

    Uses asyncio.run() to bridge the sync Celery worker with the async agent code.
    Session lifecycle (commit/rollback/close) is handled by get_sync_session().
    """
    from app.core.schemas.presentation import SlideDeckPayload
    from app.db.session import get_sync_session
    from app.services.job_processor import process_slide_deck

    deck_id = payload_dict.get("slide_deck_id", "unknown")
    logger.info("celery_task_start", slide_deck_id=deck_id, task_id=self.request.id)

    payload = SlideDeckPayload(**payload_dict)
    with get_sync_session() as session:
        asyncio.run(process_slide_deck(session, payload))

    logger.info("celery_task_complete", slide_deck_id=deck_id)
