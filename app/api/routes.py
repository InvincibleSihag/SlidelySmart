"""Client-facing API endpoints."""

import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.logging import get_logger
from app.core.schemas.enums import JobStatus
from app.core.schemas.presentation import SlideDeckPayload
from app.db.managers.message import MessageManager
from app.db.managers.version import VersionManager
from app.db.models import SlideDeck
from app.db.session import SessionDep
from app.services.storage import SLIDE_DECKS_PREFIX, get_version_html
from app.services.tasks import process_job_task

router = APIRouter(prefix="/api", tags=["api"])
logger = get_logger(__name__)


class JobRequest(BaseModel):
    prompt: str
    job_id: str | None = None


class JobResumeRequest(BaseModel):
    human_response: str


class JobResponse(BaseModel):
    job_id: str


@router.post("/jobs", response_model=JobResponse)
def create_or_continue_job(
    body: JobRequest,
    session: SessionDep,
):
    """Create a new presentation job, or send a follow-up on an existing one.

    If job_id is omitted, a new slide deck is created.
    If job_id is provided, a follow-up query is sent on that completed deck.
    """
    if body.job_id:
        slide_deck = session.get(SlideDeck, uuid.UUID(body.job_id))
        if not slide_deck:
            raise HTTPException(status_code=404, detail="Slide deck not found")

        if slide_deck.status != JobStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Deck not completed. Status: {slide_deck.status}",
            )

        logger.info("slide_deck_continue", slide_deck_id=body.job_id)
    else:
        slide_deck = SlideDeck(status=JobStatus.QUEUED)
        session.add(slide_deck)
        session.flush()

        logger.info("slide_deck_created", slide_deck_id=str(slide_deck.id))

    # Persist user message immediately so it's visible to GET
    MessageManager(session).persist_user_message(slide_deck.id, body.prompt)

    payload = SlideDeckPayload(
        slide_deck_id=str(slide_deck.id),
        user_query=body.prompt,
    )

    session.queue_callback_after_commit(process_job_task.delay, payload.model_dump())

    return JobResponse(job_id=str(slide_deck.id))


@router.post("/jobs/{job_id}/resume", response_model=JobResponse)
def resume_job(
    job_id: str,
    body: JobResumeRequest,
    session: SessionDep,
):
    """Resume a job waiting for human input."""
    slide_deck = session.get(SlideDeck, uuid.UUID(job_id))
    if not slide_deck:
        raise HTTPException(status_code=404, detail="Slide deck not found")

    if slide_deck.status != JobStatus.WAITING_FOR_INPUT:
        raise HTTPException(
            status_code=400,
            detail=f"Not waiting for input. Status: {slide_deck.status}",
        )

    logger.info("slide_deck_resume", slide_deck_id=job_id)

    payload = SlideDeckPayload(
        slide_deck_id=job_id,
        resume_value=body.human_response,
    )

    session.queue_callback_after_commit(process_job_task.delay, payload.model_dump())

    return JobResponse(job_id=job_id)


@router.get("/jobs/{job_id}")
def get_job(
    job_id: str,
    session: SessionDep,
):
    """Get full job state: status, messages, slides HTML, HITL request.

    Serves as the single source of truth for UI state recovery on page refresh.
    During processing, returns in-progress slides from the next version's GCS path.
    """
    slide_deck = session.get(SlideDeck, uuid.UUID(job_id))
    if not slide_deck:
        raise HTTPException(status_code=404, detail="Slide deck not found")

    # Load persisted chat messages
    message_manager = MessageManager(session)
    messages = message_manager.get_all(slide_deck.id)

    # Determine slides HTML and count from latest version
    result_data = None
    slides_html = None
    slide_count = 0

    version_manager = VersionManager(session)
    latest_version = version_manager.get_latest(slide_deck)
    if latest_version:
        result_data = latest_version.content
        slides_html = get_version_html(latest_version.html_storage_path)
        slide_count = len((latest_version.content or {}).get("slides", []))

    # During processing, check for in-progress HTML at the next version path
    if slide_deck.status == JobStatus.PROCESSING:
        next_version_path = (
            f"{SLIDE_DECKS_PREFIX}/{slide_deck.id}"
            f"/v{slide_deck.current_version + 1}/slides.html"
        )
        live_html = get_version_html(next_version_path)
        if live_html:
            slides_html = live_html

    return {
        "job_id": str(slide_deck.id),
        "status": slide_deck.status,
        "result": result_data,
        "messages": [
            {
                "id": str(m.id),
                "message_type": m.message_type,
                "message_content": m.message_content,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
        "hitl_request": slide_deck.hitl_request,
        "slides_html": slides_html,
        "slide_count": slide_count,
        "error_log": slide_deck.error_log,
        "created_at": slide_deck.created_at.isoformat() if slide_deck.created_at else None,
        "completed_at": slide_deck.completed_at.isoformat() if slide_deck.completed_at else None,
        "current_version": slide_deck.current_version,
    }
