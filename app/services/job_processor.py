"""Slide deck processing logic — called by Celery worker.

Single function handles initial runs, follow-ups, and HITL resume flows.
The payload indicates which flow via presence of resume_value.

NOTE: This module uses explicit intermediate commits because the Celery worker
runs long-lived jobs that need to persist state transitions (PROCESSING ->
WAITING_FOR_INPUT / COMPLETED / FAILED) as they happen, so the client can
poll for real-time status.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.core.logging import get_logger
from app.core.schemas.enums import JobStatus
from app.core.schemas.presentation import SlideDeckPayload
from app.db.managers.message import MessageManager
from app.db.managers.snapshot import SnapshotManager
from app.db.managers.version import VersionManager
from app.db.models import SlideDeck
from app.db.session import SlidelySyncSession
from app.services.slide_agent import run_agent
from app.services.pusher import trigger as pusher_trigger

logger = get_logger(__name__)


def _trigger(channel: str, event: str, data: dict) -> None:
    pusher_trigger(channel, event, data)


async def process_slide_deck(
    session: SlidelySyncSession,
    payload: SlideDeckPayload,
) -> None:
    """Process a slide deck — handles initial run, follow-up, and HITL resume."""
    deck_id = payload.slide_deck_id
    channel = f"job-{deck_id}"
    is_resume = payload.resume_value is not None

    logger.info(
        "slide_deck_processing",
        slide_deck_id=deck_id,
        is_resume=is_resume,
    )

    slide_deck = session.get(SlideDeck, UUID(deck_id))
    if not slide_deck:
        logger.error("slide_deck_not_found", slide_deck_id=deck_id)
        return

    # Validate state for resume
    if is_resume and slide_deck.status != JobStatus.WAITING_FOR_INPUT:
        logger.error("slide_deck_invalid_resume_state", slide_deck_id=deck_id, status=slide_deck.status)
        return

    snapshot_manager = SnapshotManager(session)
    version_manager = VersionManager(session)
    snapshot_messages = None
    existing_presentation = None

    if is_resume:
        # HITL resume: use the stored thread_id from the interrupted run
        thread_id = slide_deck.current_thread_id
    else:
        # New run (initial or follow-up): generate unique thread_id
        thread_id = f"presentation-{deck_id}-{uuid4()}"
        slide_deck.current_thread_id = thread_id

        # Try loading snapshot for follow-up context
        snapshot_messages = snapshot_manager.load(slide_deck.id)

        # Load presentation from latest version (if exists)
        existing_presentation = version_manager.get_presentation(slide_deck)

        if snapshot_messages:
            logger.info(
                "slide_deck_followup",
                slide_deck_id=deck_id,
                snapshot_msg_count=len(snapshot_messages),
                has_presentation=existing_presentation is not None,
            )

    # Intermediate commit: mark as PROCESSING so client sees it immediately
    slide_deck.status = JobStatus.PROCESSING
    slide_deck.hitl_request = None  # Clear stale HITL data from previous interrupt
    session.add(slide_deck)
    session.commit()

    def on_status(event: str, data: dict) -> None:
        _trigger(channel, event, data)

    # Next version number for progressive HTML uploads during processing
    next_version_num = slide_deck.current_version + 1

    try:
        output, result = await run_agent(
            thread_id=thread_id,
            on_status=on_status,
            user_query=payload.user_query,
            resume_value=payload.resume_value,
            pusher_channel_id=channel,
            snapshot_messages=snapshot_messages,
            existing_presentation=existing_presentation,
            slide_deck_id=deck_id,
            version_num=next_version_num,
        )
    except Exception as exc:
        logger.exception("slide_deck_error", slide_deck_id=deck_id, error=str(exc))
        slide_deck.status = JobStatus.FAILED
        slide_deck.error_log = str(exc)[:1000]
        session.add(slide_deck)
        session.commit()
        _trigger(channel, "job_failed", {"error": "Processing failed. Please try again."})
        return

    if result.hitl_request:
        slide_deck.status = JobStatus.WAITING_FOR_INPUT
        slide_deck.hitl_request = result.hitl_request.model_dump()
        session.add(slide_deck)
        session.commit()

        _trigger(channel, "job_waiting_for_input", {
            "hitl_request": result.hitl_request.model_dump(),
        })
        logger.info("slide_deck_waiting_for_input", slide_deck_id=deck_id)
        return

    if result.complete and output:
        # 1. Save full snapshot (messages only, overwrite)
        snapshot_manager.save(slide_deck.id, result.messages)

        # 2. Persist AI response (user message already saved at API level)
        message_manager = MessageManager(session)
        last_ai_msg = message_manager.persist_ai_message(
            slide_deck.id,
            agent_messages=result.messages,
        )

        # 3. Create version
        version_manager.create(
            slide_deck,
            output,
            message_id=last_ai_msg.id if last_ai_msg else None,
        )

        slide_deck.status = JobStatus.COMPLETED
        slide_deck.completed_at = datetime.now(timezone.utc)
        slide_deck.error_log = None
        session.add(slide_deck)
        session.commit()

        _trigger(channel, "job_completed", {"job_id": deck_id})
        logger.info("slide_deck_completed", slide_deck_id=deck_id)
        return

    slide_deck.status = JobStatus.FAILED
    slide_deck.error_log = "Agent produced no output"
    session.add(slide_deck)
    session.commit()
    _trigger(channel, "job_failed", {"error": "No output produced"})
