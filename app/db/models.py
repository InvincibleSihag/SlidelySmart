"""SQLAlchemy model definitions for PostgreSQL."""

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship

from app.core.schemas.enums import JobStatus


class BaseDbModel(DeclarativeBase):
    """Abstract base with UUID primary key."""

    __abstract__ = True
    __allow_unmapped__ = True

    id = Column(UUID, primary_key=True, default=uuid.uuid4, nullable=False, index=True)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        pk = getattr(self, "id", None)
        return f"<{class_name}(id={pk})>"

    def to_dict(self) -> dict[str, Any]:
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, uuid.UUID):
                value = str(value)
            elif isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result


class BaseDefaultMixinDbModel:
    """Mixin providing created_at and updated_at timestamp columns."""

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SlideDeck(BaseDefaultMixinDbModel, BaseDbModel):
    """Primary entity replacing Job — tracks a presentation generation session."""

    __tablename__ = "slide_deck"
    __abstract__ = False

    user_id: Optional[str] = Column(String, nullable=True, index=True)
    status: str = Column(Enum(JobStatus), nullable=False, default=JobStatus.QUEUED)
    current_version: int = Column(Integer, nullable=False, default=0)
    current_thread_id: Optional[str] = Column(String, nullable=True)
    error_log: Optional[str] = Column(String, nullable=True)
    completed_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    versions = relationship(
        "SlideDeckVersion",
        back_populates="slide_deck",
        order_by="SlideDeckVersion.version_num",
    )
    messages = relationship(
        "Message",
        back_populates="slide_deck",
        order_by="Message.created_at",
    )
    agent_snapshot = relationship(
        "AgentSnapshot",
        back_populates="slide_deck",
        uselist=False,
    )


class Message(BaseDefaultMixinDbModel, BaseDbModel):
    """Persisted chat message for client-facing conversation display."""

    __tablename__ = "message"
    __abstract__ = False

    slide_deck_id = Column(UUID, ForeignKey("slide_deck.id"), nullable=False, index=True)
    message_type: str = Column(String, nullable=False)  # "human", "ai"
    message_content: str = Column(Text, nullable=False)

    slide_deck = relationship("SlideDeck", back_populates="messages")
    versions = relationship("SlideDeckVersion", back_populates="message")


class SlideDeckVersion(BaseDefaultMixinDbModel, BaseDbModel):
    """Versioned snapshot of a presentation — created on completion."""

    __tablename__ = "slide_deck_version"
    __abstract__ = False

    slide_deck_id = Column(UUID, ForeignKey("slide_deck.id"), nullable=False, index=True)
    version_num: int = Column(Integer, nullable=False)
    content: dict = Column(JSONB, nullable=False)  # Full Presentation JSON
    html_storage_path: Optional[str] = Column(String(1000), nullable=True)  # GCS blob path
    message_id = Column(UUID, ForeignKey("message.id"), nullable=True)

    slide_deck = relationship("SlideDeck", back_populates="versions")
    message = relationship("Message", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("slide_deck_id", "version_num", name="uq_slide_deck_version"),
    )


class AgentSnapshot(BaseDefaultMixinDbModel, BaseDbModel):
    """Full agent message history — overwritten on each completion.

    Stores ALL LangChain message types (system, human, ai with tool_calls,
    tool messages) serialized via messages_to_dict(). Used to inject full
    conversation context into subsequent runs on the same slide deck.

    Presentation data is NOT stored here — it lives in SlideDeckVersion.content.
    """

    __tablename__ = "agent_snapshot"
    __abstract__ = False

    slide_deck_id = Column(UUID, ForeignKey("slide_deck.id"), nullable=False, unique=True, index=True)
    messages = Column(JSONB, nullable=False)  # Serialized via messages_to_dict()

    slide_deck = relationship("SlideDeck", back_populates="agent_snapshot")
