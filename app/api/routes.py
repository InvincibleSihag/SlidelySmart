"""Client-facing API endpoints."""

import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.logging import get_logger
from app.core.schemas.enums import JobStatus
from app.core.schemas.presentation import SlideDeckPayload
from app.db.managers import VersionManager
from app.db.models import SlideDeck
from app.db.session import SessionDep
from app.services.storage import get_version_html
from app.services.tasks import process_job_task

router = APIRouter(prefix="/api", tags=["api"])
logger = get_logger(__name__)


class JobCreate(BaseModel):
    prompt: str


class JobResumeRequest(BaseModel):
    human_response: str


class JobResponse(BaseModel):
    job_id: str


@router.post("/jobs", response_model=JobResponse)
def create_job(
    body: JobCreate,
    session: SessionDep,
):
    """Create and queue a new presentation generation job."""
    slide_deck = SlideDeck(status=JobStatus.QUEUED)
    session.add(slide_deck)
    session.flush()

    logger.info("slide_deck_created", slide_deck_id=str(slide_deck.id))

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


class JobContinueRequest(BaseModel):
    prompt: str


@router.post("/jobs/{job_id}/continue", response_model=JobResponse)
def continue_job(
    job_id: str,
    body: JobContinueRequest,
    session: SessionDep,
):
    """Send a follow-up query on a completed slide deck."""
    slide_deck = session.get(SlideDeck, uuid.UUID(job_id))
    if not slide_deck:
        raise HTTPException(status_code=404, detail="Slide deck not found")

    if slide_deck.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Deck not completed. Status: {slide_deck.status}",
        )

    logger.info("slide_deck_continue", slide_deck_id=job_id)

    payload = SlideDeckPayload(
        slide_deck_id=job_id,
        user_query=body.prompt,
    )

    session.queue_callback_after_commit(process_job_task.delay, payload.model_dump())

    return JobResponse(job_id=job_id)


@router.get("/jobs/{job_id}")
def get_job(
    job_id: str,
    session: SessionDep,
):
    """Get job status and result. When complete, includes pre-rendered HTML slides."""
    slide_deck = session.get(SlideDeck, uuid.UUID(job_id))
    if not slide_deck:
        raise HTTPException(status_code=404, detail="Slide deck not found")

    result_data = None
    slides_html = None

    version_manager = VersionManager(session)
    latest_version = version_manager.get_latest(slide_deck)
    if latest_version:
        result_data = latest_version.content
        slides_html = get_version_html(latest_version.html_storage_path)

    return {
        "job_id": str(slide_deck.id),
        "status": slide_deck.status,
        "result": result_data,
        "slides_html": slides_html,
        "error_log": slide_deck.error_log,
        "created_at": slide_deck.created_at.isoformat() if slide_deck.created_at else None,
        "completed_at": slide_deck.completed_at.isoformat() if slide_deck.completed_at else None,
        "current_version": slide_deck.current_version,
    }
