"""Manager for persisting client-facing chat messages to the database."""

from uuid import UUID

from app.db.models import Message
from app.db.session import SlidelySyncSession


class MessageManager:
    """Persists user/assistant messages for client-facing display."""

    def __init__(self, session: SlidelySyncSession):
        self._session = session

    def get_all(self, slide_deck_id: UUID) -> list[Message]:
        """Return all messages for a slide deck, ordered by creation time."""
        return (
            self._session.query(Message)
            .filter(Message.slide_deck_id == slide_deck_id)
            .order_by(Message.created_at)
            .all()
        )

    def persist_user_message(
        self,
        slide_deck_id: UUID,
        content: str,
    ) -> Message:
        """Persist user message immediately when job starts.

        Called eagerly so the message is visible to GET even while
        the agent is still processing.
        """
        msg = Message(
            slide_deck_id=slide_deck_id,
            message_type="human",
            message_content=content.strip(),
        )
        self._session.add(msg)
        self._session.flush()
        return msg

    def persist_ai_message(
        self,
        slide_deck_id: UUID,
        agent_messages: list,
    ) -> Message | None:
        """Persist the last AI text response on completion.

        Scans agent messages in reverse to find the final assistant
        text response (ignoring tool calls and empty messages).

        Returns the AI message record, or None if no text response found.
        """
        for msg in reversed(agent_messages):
            if msg.type != "ai":
                continue
            content = str(msg.text)
            if not content.strip():
                continue
            ai_msg = Message(
                slide_deck_id=slide_deck_id,
                message_type="ai",
                message_content=content,
            )
            self._session.add(ai_msg)
            self._session.flush()
            return ai_msg

        return None
