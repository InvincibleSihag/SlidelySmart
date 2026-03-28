"""Manager for persisting and loading full agent message snapshots."""

from uuid import UUID

from langchain_core.messages import messages_from_dict, messages_to_dict

from app.db.models import AgentSnapshot
from app.db.session import SlidelySyncSession


class SnapshotManager:
    """Persists the full LangChain message history for a slide deck.

    The snapshot is overwritten on each completion so that subsequent
    runs can reconstruct the full conversation context. This includes
    ALL message types (system, human, ai with tool_calls, tool results).
    """

    def __init__(self, session: SlidelySyncSession):
        self._session = session

    def save(self, slide_deck_id: UUID, messages: list) -> None:
        """Serialize and upsert AgentSnapshot. Overwrites on each completion."""
        serialized = messages_to_dict(messages)

        existing = (
            self._session.query(AgentSnapshot)
            .filter(AgentSnapshot.slide_deck_id == slide_deck_id)
            .first()
        )

        if existing:
            existing.messages = serialized
        else:
            self._session.add(AgentSnapshot(
                slide_deck_id=slide_deck_id,
                messages=serialized,
            ))

        self._session.flush()

    def load(self, slide_deck_id: UUID) -> list | None:
        """Load and deserialize snapshot messages. Returns message list or None."""
        snapshot = (
            self._session.query(AgentSnapshot)
            .filter(AgentSnapshot.slide_deck_id == slide_deck_id)
            .first()
        )

        if not snapshot:
            return None

        return messages_from_dict(snapshot.messages)
