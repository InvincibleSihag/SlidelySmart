"""
Slidely Database Session Management Module

Follows the PreOrder pattern: auto-commit on success, auto-rollback on error,
with callback-after-commit support and proper pool configuration.
"""

import json
from contextlib import contextmanager
from functools import lru_cache
from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# ---------------------
# Callback Session Mixin
# ---------------------


class SlidelyCallbackSessionMixin:
    """
    A mixin to add callback functionality to a SQLAlchemy session.
    Enables submitting callbacks after the session transaction is committed.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._callbacks = []

    def queue_callback_after_commit(self, callback_func, *args, **kwargs):
        """Queue a callback to be executed after the commit."""
        self._callbacks.append((callback_func, args or [], kwargs or {}))

    def submit_queued_callbacks(self) -> None:
        """Submit all the queued callbacks."""
        if not self._callbacks:
            return

        for callback_func, args, kwargs in self._callbacks:
            callback_func(*args, **kwargs)

        self._callbacks = []


# ---------------------
# Custom Session Class
# ---------------------


class SlidelySyncSession(SlidelyCallbackSessionMixin, Session):
    """Synchronous SQLAlchemy session with callback support."""

    def commit(self) -> None:
        """Commit the transaction and submit the queued callbacks."""
        super().commit()
        self.submit_queued_callbacks()


# ---------------------
# Database Connection Utility
# ---------------------


@lru_cache(5)
def sync_session_maker(sync_uri: str, class_=Session) -> sessionmaker:
    """Create a synchronous SQLAlchemy sessionmaker."""
    engine = create_engine(
        sync_uri,
        echo=False,
        pool_size=10,
        max_overflow=50,
        pool_timeout=30,
        pool_recycle=300,
        pool_pre_ping=True,
        json_serializer=json.dumps,
    )
    return sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=class_,
    )


# ---------------------
# Session Context Manager
# ---------------------


@contextmanager
def get_sync_session(db_uri: str | None = None) -> Generator[SlidelySyncSession, None, None]:
    """Get a synchronous database session.

    Auto-commits on success, auto-rollbacks on error.
    """
    uri = db_uri or settings.database_url
    session = sync_session_maker(uri, class_=SlidelySyncSession)()
    try:
        yield session
        session.commit()
    except Exception:
        logger.exception("Error in session, rolling back")
        session.rollback()
        raise
    finally:
        session.close()


# ---------------------
# FastAPI Dependency
# ---------------------


def _get_sync_session() -> Generator[SlidelySyncSession, None, None]:
    """A dependency to get a SQLAlchemy session."""
    with get_sync_session() as db:
        yield db


# Type alias for FastAPI dependency injection.
#
# scope="function" ensures the generator cleanup (session.commit) runs
# BEFORE the HTTP response is sent to the client. The default scope for
# yield-dependencies is "request", whose cleanup runs AFTER the response
# is sent — creating a race where a follow-up request can arrive before
# the previous transaction is committed.
SessionDep = Annotated[SlidelySyncSession, Depends(_get_sync_session, scope="function")]
