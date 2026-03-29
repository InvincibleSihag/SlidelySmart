"""Skill store: scan skills/ directory, parse SKILL.md, serve catalog and content.

Skills follow a progressive disclosure pattern:
  1. Catalog (always in system prompt) — just names + descriptions
  2. Full instructions (on demand via LoadSkill) — the SKILL.md body
  3. Reference files (on demand via ReadSkillFile) — specific docs, templates, specs

Adding a new skill requires zero code changes — just drop a folder with
a SKILL.md into the skills directory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from app.core.logging import get_logger

logger = get_logger(__name__)

# Default skills directory: project_root/skills/
_SKILLS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "skills"


@dataclass(frozen=True)
class SkillMeta:
    """Parsed frontmatter metadata from a SKILL.md file."""

    name: str
    description: str
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Skill:
    """A loaded skill: metadata + full instruction body + directory path."""

    meta: SkillMeta
    body: str
    directory: Path


class SkillStore:
    """Scans a directory of skill folders and provides catalog/content access.

    Each skill folder must contain a SKILL.md with YAML frontmatter:

        ---
        name: slide_design
        description: Layouts, elements, and design principles
        tags: [design, layout, elements]
        ---
        <markdown body with full instructions>

    Additional files in the folder (e.g. refs/) are accessible via
    read_skill_file().
    """

    def __init__(self, skills_dir: Path | None = None) -> None:
        self._skills_dir = skills_dir or _SKILLS_DIR
        self._skills: dict[str, Skill] = {}
        self._scan()

    def _scan(self) -> None:
        """Walk skills_dir, find folders with SKILL.md, parse them."""
        if not self._skills_dir.is_dir():
            logger.warning("skills_dir_not_found", path=str(self._skills_dir))
            return
        for child in sorted(self._skills_dir.iterdir()):
            if not child.is_dir():
                continue
            skill_md = child / "SKILL.md"
            if not skill_md.is_file():
                continue
            try:
                meta, body = self._parse_skill_md(skill_md)
                self._skills[meta.name] = Skill(meta=meta, body=body, directory=child)
                logger.info("skill_loaded", name=meta.name, tags=meta.tags)
            except Exception:
                logger.exception("skill_parse_error", path=str(skill_md))

    @staticmethod
    def _parse_skill_md(path: Path) -> tuple[SkillMeta, str]:
        """Parse YAML frontmatter and markdown body from SKILL.md."""
        text = path.read_text(encoding="utf-8")

        if not text.startswith("---"):
            raise ValueError(f"No YAML frontmatter in {path}")

        # Split on the closing --- (skip the opening one)
        parts = text.split("---", 2)
        if len(parts) < 3:
            raise ValueError(f"Malformed frontmatter in {path}")

        frontmatter = yaml.safe_load(parts[1])
        body = parts[2].strip()

        if not isinstance(frontmatter, dict):
            raise ValueError(f"Frontmatter is not a YAML mapping in {path}")

        name = frontmatter.get("name")
        if not name:
            raise ValueError(f"SKILL.md missing 'name' in frontmatter: {path}")

        return SkillMeta(
            name=name,
            description=frontmatter.get("description", ""),
            tags=frontmatter.get("tags", []),
        ), body

    @property
    def skill_names(self) -> list[str]:
        """List all loaded skill names."""
        return list(self._skills.keys())

    def catalog_data(self) -> list[dict[str, str | list[str]]]:
        """Return structured skill metadata for Jinja2 template rendering.

        Each entry has 'name', 'description', and 'tags' keys.
        """
        return [
            {
                "name": skill.meta.name,
                "description": skill.meta.description,
                "tags": skill.meta.tags,
            }
            for skill in self._skills.values()
        ]

    def load_skill(self, skill_name: str) -> str:
        """Return the full SKILL.md body for a skill (tier 2 disclosure)."""
        skill = self._skills.get(skill_name)
        if not skill:
            available = ", ".join(self._skills.keys())
            return f"Error: Unknown skill '{skill_name}'. Available: {available}"
        return skill.body

    def read_skill_file(self, skill_name: str, file_path: str) -> str:
        """Read a reference file from within a skill's directory (tier 3).

        file_path is relative to the skill directory. Path traversal is blocked.
        """
        skill = self._skills.get(skill_name)
        if not skill:
            available = ", ".join(self._skills.keys())
            return f"Error: Unknown skill '{skill_name}'. Available: {available}"

        resolved = (skill.directory / file_path).resolve()
        # Security: ensure resolved path is inside the skill directory
        if not str(resolved).startswith(str(skill.directory.resolve())):
            return f"Error: Path traversal not allowed: '{file_path}'"

        if not resolved.is_file():
            available_files = [
                str(f.relative_to(skill.directory))
                for f in skill.directory.rglob("*")
                if f.is_file() and f.name != "SKILL.md"
            ]
            return (
                f"Error: File not found: '{file_path}'. "
                f"Available: {available_files}"
            )

        return resolved.read_text(encoding="utf-8")
