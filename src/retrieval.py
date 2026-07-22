"""
Retrieval component for VibeMatch AI.

This module reads the local music guide (``data/music_guide.md``) and lets the
explanation layer pull the relevant genre and mood descriptions for a
recommendation. It is a small, dependency-free "retrieval" step: the guide is
split into sections by their Markdown headings, and lookups are done by matching
a genre or mood name to a heading.

There is no embedding model or vector database here. For a guide this small,
exact heading matching is simpler, fully offline, and easy to explain in a
classroom setting.
"""

from pathlib import Path
from typing import Dict, List, Optional

# Absolute path to the guide so retrieval works regardless of the current
# working directory.
DEFAULT_GUIDE_PATH = Path(__file__).resolve().parents[1] / "data" / "music_guide.md"


class MusicGuide:
    """
    Loads the music guide and exposes lookups by genre and mood.

    Sections are keyed by their lower-cased heading text (for example "pop" or
    "focused"). Lookups are case-insensitive and always safe: a missing term
    returns ``None`` rather than raising.
    """

    def __init__(self, sections: Dict[str, str]):
        self.sections = sections

    @classmethod
    def load(cls, guide_path: Optional[str] = None) -> "MusicGuide":
        """
        Build a MusicGuide from a Markdown file.

        If the file does not exist, an empty guide is returned so the rest of the
        system keeps working (explanations simply won't include extra context).
        """
        path = Path(guide_path) if guide_path else DEFAULT_GUIDE_PATH
        if not path.exists():
            return cls({})
        text = path.read_text(encoding="utf-8")
        return cls(_parse_sections(text))

    def lookup(self, term: str) -> Optional[str]:
        """Return the section body for a genre or mood name, or None."""
        if not term:
            return None
        return self.sections.get(term.strip().lower())

    def retrieve(self, genre: Optional[str], mood: Optional[str]) -> Dict[str, Optional[str]]:
        """
        Retrieve the guide context for a recommendation.

        Returns a dict with ``genre_context`` and ``mood_context`` (either may be
        ``None`` if the term is unknown or the guide is empty).
        """
        return {
            "genre_context": self.lookup(genre) if genre else None,
            "mood_context": self.lookup(mood) if mood else None,
        }


def _parse_sections(text: str) -> Dict[str, str]:
    """
    Split the guide text into ``{heading: body}`` pairs.

    Only the lowest-level headings (### ...) are treated as retrievable sections;
    those are the individual genre and mood entries. Higher-level headings like
    "## Genres" are ignored as group labels.
    """
    sections: Dict[str, str] = {}
    current_key: Optional[str] = None
    current_body: List[str] = []

    def flush() -> None:
        if current_key is not None:
            body = "\n".join(current_body).strip()
            if body:
                sections[current_key] = body

    for line in text.splitlines():
        if line.startswith("### "):
            flush()
            current_key = line[4:].strip().lower()
            current_body = []
        elif line.startswith("#"):
            # A higher-level heading ends the current section.
            flush()
            current_key = None
            current_body = []
        elif current_key is not None:
            current_body.append(line)

    flush()
    return sections
