"""Manager for SlideDeckVersion operations."""

from uuid import UUID

from app.core.schemas.presentation import Presentation
from app.db.models import SlideDeck, SlideDeckVersion
from app.db.session import SlidelySyncSession
from app.services.slide_renderer import render_presentation
from app.services.storage import upload_version_html


class VersionManager:
    """Handles creation and retrieval of SlideDeckVersion records."""

    def __init__(self, session: SlidelySyncSession):
        self._session = session

    def get_latest(self, slide_deck: SlideDeck) -> SlideDeckVersion | None:
        """Return the latest version for a slide deck, or None."""
        if slide_deck.current_version == 0:
            return None

        return (
            self._session.query(SlideDeckVersion)
            .filter(
                SlideDeckVersion.slide_deck_id == slide_deck.id,
                SlideDeckVersion.version_num == slide_deck.current_version,
            )
            .first()
        )

    def get_presentation(self, slide_deck: SlideDeck) -> Presentation | None:
        """Load the Presentation model from the latest version, or None."""
        latest = self.get_latest(slide_deck)
        if not latest:
            return None
        return Presentation.model_validate(latest.content)

    @staticmethod
    def format_slide_summary(presentation: Presentation) -> str:
        """Build a concise slide inventory for injection into follow-up messages.

        Gives the LLM a reliable mapping of slide IDs, layouts, and content
        hints so it can reference or edit slides by ID without relying on
        conversation history alone.
        """
        lines: list[str] = [f"Current presentation has {len(presentation.slides)} slides:"]
        for slide in presentation.slides:
            hint = ""
            if slide.elements:
                el = slide.elements[0]
                first = el.content
                if isinstance(first, str):
                    hint = first
                elif isinstance(first, list) and first:
                    hint = first[0]
                elif el.table_data:
                    hint = f"Table: {len(el.table_data)} rows"
                if len(hint) > 60:
                    hint = hint[:57] + "..."
            lines.append(f'- {slide.id} ({slide.layout}): "{hint}"')
        return "\n".join(lines)

    def create(
        self,
        slide_deck: SlideDeck,
        presentation: Presentation,
        message_id: UUID | None = None,
    ) -> SlideDeckVersion:
        """Create a new version with rendered HTML uploaded to storage.

        Bumps slide_deck.current_version and persists the version row.
        Caller is responsible for committing the session.
        """
        version_num = slide_deck.current_version + 1

        slides_html = render_presentation(presentation)
        html_path = upload_version_html(str(slide_deck.id), version_num, slides_html)

        version = SlideDeckVersion(
            slide_deck_id=slide_deck.id,
            version_num=version_num,
            content=presentation.model_dump(),
            html_storage_path=html_path,
            message_id=message_id,
        )
        self._session.add(version)

        slide_deck.current_version = version_num
        self._session.add(slide_deck)

        return version
