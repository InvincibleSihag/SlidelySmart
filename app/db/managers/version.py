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
    # TODO: This method can be improved, better way of creating summary
    @staticmethod
    def format_slide_summary(presentation: Presentation) -> str:
        """Build a slide inventory for injection into follow-up messages.

        Includes theme, slide IDs, layouts, element IDs with types and content
        hints so the LLM can target EditElement precisely without guessing.
        """
        theme = presentation.theme or "default"
        lines: list[str] = [f"Presentation: theme={theme} | {len(presentation.slides)} slides"]
        for slide in presentation.slides:
            el_parts: list[str] = []
            for el in slide.elements:
                tag = f"{el.id}:{el.type}"
                # Content hint
                if isinstance(el.content, str):
                    preview = el.content[:40] + "..." if len(el.content) > 40 else el.content
                    tag += f' "{preview}"'
                elif isinstance(el.content, list):
                    tag += f"({len(el.content)})"
                elif el.table_data:
                    tag += f"(table:{len(el.table_data)}rows)"
                # Column placement
                if el.metadata and getattr(el.metadata, "column", None):
                    tag += f"{{{el.metadata.column}}}"
                el_parts.append(tag)
            lines.append(f"- {slide.id} ({slide.layout}): [{', '.join(el_parts)}]")
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
