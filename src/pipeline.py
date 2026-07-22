"""
End-to-end VibeMatch AI pipeline.

Ties the pieces together in one place so both ``run_demo.py`` and ``evaluate.py``
share the exact same flow:

    load catalog -> validate catalog -> validate profile
        -> rule-based recommend -> retrieve guide context -> AI explanation

The pipeline is backend-agnostic: the explanation layer decides on its own
whether to use the Claude API or the deterministic fallback, and everything
downstream treats both the same.
"""

from pathlib import Path
from typing import Dict, List, Optional

from src.recommender import load_songs, score_song, _reasons_to_text
from src.retrieval import MusicGuide
from src.guardrails import validate_user_profile, validate_catalog
from src.explainer import explain

# Default data locations, resolved relative to the project root.
_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = _ROOT / "data" / "songs.csv"
DEFAULT_GUIDE = _ROOT / "data" / "music_guide.md"


def recommend_with_explanations(
    prefs: Dict,
    songs: List[Dict],
    guide: MusicGuide,
    k: int = 3,
) -> Dict:
    """
    Run the full pipeline for one already-loaded catalog.

    Returns a dict with:
        - ``warnings``: guardrail messages about the (normalized) profile
        - ``clean_prefs``: the validated preferences actually used
        - ``recommendations``: list of per-song dicts (song, score, reasons,
          reasons_text, explanation)

    Raises ``GuardrailError`` (from :mod:`src.guardrails`) if the catalog is
    unusable. Profile problems are corrected and reported as warnings instead.
    """
    validate_catalog(songs)
    clean_prefs, warnings = validate_user_profile(prefs)

    scored = []
    for song in songs:
        score, reasons = score_song(clean_prefs, song)
        scored.append((song, score, reasons))
    scored.sort(key=lambda item: item[1], reverse=True)

    recommendations = []
    for song, score, reasons in scored[:k]:
        guide_context = guide.retrieve(clean_prefs.get("genre"), clean_prefs.get("mood"))
        explanation = explain(clean_prefs, song, score, reasons, guide_context)
        recommendations.append(
            {
                "song": song,
                "score": score,
                "reasons": reasons,
                "reasons_text": _reasons_to_text(reasons),
                "explanation": explanation,
            }
        )

    return {
        "warnings": warnings,
        "clean_prefs": clean_prefs,
        "recommendations": recommendations,
    }


def run_profile(
    prefs: Dict,
    k: int = 3,
    catalog_path: Optional[str] = None,
    guide_path: Optional[str] = None,
) -> Dict:
    """Convenience wrapper that loads the catalog and guide from disk first."""
    songs = load_songs(str(catalog_path or DEFAULT_CATALOG))
    guide = MusicGuide.load(str(guide_path or DEFAULT_GUIDE))
    return recommend_with_explanations(prefs, songs, guide, k=k)
