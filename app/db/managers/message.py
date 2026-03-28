"""Manager for persisting client-facing chat messages to the database."""

from uuid import UUID

from app.db.models import Message
from app.db.session import SlidelySyncSession


class MessageManager:
    """Persists user/assistant message pairs for client-facing display."""

    def __init__(self, session: SlidelySyncSession):
        self._session = session

    def persist_pair(
        self,
        slide_deck_id: UUID,
        user_query: str | None,
        agent_messages: list,
    ) -> Message | None:
        """Persist the user query + last AI text response for this run.

        Previous run messages were already stored. UI only needs
        user/assistant pairs per run, with the AI message linked to the version.

        Returns the last AI message record, or None.
        """
        last_ai_message: Message | None = None

        # Store user query
        if user_query and user_query.strip():
            self._session.add(Message(
                slide_deck_id=slide_deck_id,
                message_type="human",
                message_content=user_query.strip(),
            ))

        # Find and store last AI text response
        for msg in reversed(agent_messages):
            if msg.type != "ai":
                continue
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            if not content.strip():
                continue
            last_ai_message = Message(
                slide_deck_id=slide_deck_id,
                message_type="ai",
                message_content=content,
            )
            self._session.add(last_ai_message)
            break

        self._session.flush()
        return last_ai_message
