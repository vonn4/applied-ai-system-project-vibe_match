"""
Input validation and guardrails for VibeMatch AI.

The rule-based recommender assumes clean input. In a real system the input is
rarely clean, so this module checks a user profile and a song catalog before
they reach the scoring logic.

Design choice: guardrails are *forgiving where it is safe and strict where it is
not*.

- A user profile is **normalized with warnings**. Unknown genres/moods, missing
  values, and out-of-range numbers are corrected to safe defaults and reported,
  so the demo can keep running and show the user what was adjusted.
- A catalog is **hard-validated**. An empty catalog or one missing required
  columns cannot produce meaningful recommendations, so those raise a
  ``GuardrailError``.
"""

from typing import Dict, List, Tuple

# Vocabulary known to the catalog / music guide. Unknown values are allowed
# through (with a warning) because the recommender simply scores them as a
# non-match, but flagging them helps the user catch typos like "poop" for "pop".
KNOWN_GENRES = {
    "pop", "indie pop", "lofi", "rock", "ambient",
    "jazz", "synthwave", "folk", "edm",
}
KNOWN_MOODS = {
    "happy", "chill", "intense", "relaxed", "focused", "moody",
}

# Columns every song row must have for scoring to work.
REQUIRED_SONG_FIELDS = [
    "id", "title", "artist", "genre", "mood",
    "energy", "tempo_bpm", "valence", "danceability", "acousticness",
]

# Safe defaults used when a preference is missing or invalid.
DEFAULT_ENERGY = 0.5
DEFAULT_TEMPO = 120.0


class GuardrailError(ValueError):
    """Raised when input is too broken to produce a meaningful result."""


def _coerce_number(value, default: float, name: str, warnings: List[str]) -> float:
    """Convert value to float; on failure fall back to default with a warning."""
    if value is None or value == "":
        warnings.append(f"{name} was missing; defaulted to {default}.")
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        warnings.append(f"{name} {value!r} is not a number; defaulted to {default}.")
        return default
    if number != number:  # NaN check (NaN != NaN)
        warnings.append(f"{name} was NaN; defaulted to {default}.")
        return default
    return number


def validate_user_profile(prefs: Dict) -> Tuple[Dict, List[str]]:
    """
    Validate and normalize a user-preference dict.

    Returns ``(clean_prefs, warnings)``. ``clean_prefs`` is always safe to pass to
    the recommender; ``warnings`` lists every adjustment that was made.

    Accepts the same keys the recommender uses: ``genre``, ``mood``, ``energy``,
    ``target_tempo``, ``likes_acoustic``.
    """
    if not isinstance(prefs, dict):
        raise GuardrailError("User preferences must be provided as a dictionary.")

    warnings: List[str] = []
    clean: Dict = {}

    # Genre / mood: keep as lower-cased strings; warn on unknown or missing.
    genre = prefs.get("genre")
    if not genre or not str(genre).strip():
        warnings.append("Favorite genre was missing; scoring will skip the genre match.")
        clean["genre"] = None
    else:
        genre = str(genre).strip().lower()
        if genre not in KNOWN_GENRES:
            warnings.append(
                f"Genre {genre!r} is not in the known catalog; it will simply not match any song."
            )
        clean["genre"] = genre

    mood = prefs.get("mood")
    if not mood or not str(mood).strip():
        warnings.append("Favorite mood was missing; scoring will skip the mood match.")
        clean["mood"] = None
    else:
        mood = str(mood).strip().lower()
        if mood not in KNOWN_MOODS:
            warnings.append(
                f"Mood {mood!r} is not in the known catalog; it will simply not match any song."
            )
        clean["mood"] = mood

    # Energy: must be within 0.0-1.0. Clamp out-of-range values.
    energy = _coerce_number(prefs.get("energy"), DEFAULT_ENERGY, "Target energy", warnings)
    if energy < 0.0 or energy > 1.0:
        clamped = min(1.0, max(0.0, energy))
        warnings.append(f"Target energy {energy} is outside 0.0-1.0; clamped to {clamped}.")
        energy = clamped
    clean["energy"] = energy

    # Tempo: must be a positive BPM.
    tempo = _coerce_number(prefs.get("target_tempo"), DEFAULT_TEMPO, "Target tempo", warnings)
    if tempo <= 0:
        warnings.append(f"Target tempo {tempo} is not positive; defaulted to {DEFAULT_TEMPO}.")
        tempo = DEFAULT_TEMPO
    clean["target_tempo"] = tempo

    # likes_acoustic: coerce to a real boolean.
    likes_acoustic = prefs.get("likes_acoustic", False)
    if not isinstance(likes_acoustic, bool):
        warnings.append(
            f"likes_acoustic {likes_acoustic!r} was not a boolean; interpreted as {bool(likes_acoustic)}."
        )
        likes_acoustic = bool(likes_acoustic)
    clean["likes_acoustic"] = likes_acoustic

    return clean, warnings


def validate_catalog(songs: List[Dict]) -> List[str]:
    """
    Hard-validate a song catalog.

    Raises ``GuardrailError`` if the catalog is empty or any row is missing a
    required field. Returns a list of warnings for non-fatal issues (currently
    none, but kept symmetric with :func:`validate_user_profile`).
    """
    if not songs:
        raise GuardrailError("The song catalog is empty; there is nothing to recommend.")

    warnings: List[str] = []
    for index, song in enumerate(songs):
        if not isinstance(song, dict):
            raise GuardrailError(f"Song at position {index} is not a valid record.")
        missing = [field for field in REQUIRED_SONG_FIELDS if field not in song]
        if missing:
            raise GuardrailError(
                f"Song at position {index} is missing required fields: {', '.join(missing)}."
            )
    return warnings
