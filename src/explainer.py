"""
AI explanation layer for VibeMatch AI (hybrid backend).

This module turns a recommendation into a short, structured, user-friendly
explanation. It has two backends behind a single :func:`explain` function:

1. **LLM backend** - used only when ``ANTHROPIC_API_KEY`` is set and the
   ``anthropic`` package is installed. It calls the Claude API
   (model ``claude-haiku-4-5``) with a prompt built from the recommender's own
   reasons plus the retrieved music-guide context, so the language model
   explains a decision the rule-based system already made rather than inventing
   its own ranking.

2. **Fallback backend** - a fully offline, deterministic explanation assembled
   from the same reasons and retrieved context. Used when there is no API key,
   the ``anthropic`` package is missing, or the API call fails for any reason.

Both backends return the **same dictionary shape** so the rest of the system is
backend-agnostic:

    {
        "summary": str,             # one-line headline
        "why_it_fits": str,         # the concrete reasons this song was picked
        "genre_mood_context": str,  # background from the local music guide
        "caveat": str,              # an honest limitation of this recommendation
        "backend": str,             # "llm" or "fallback" (which path produced this)
    }
"""

import json
import os
from typing import Dict, List, Optional

# The Claude model used for the LLM backend. Haiku is fast and inexpensive,
# which suits a classroom project that may explain several songs per run.
LLM_MODEL = "claude-haiku-4-5"

# JSON schema the LLM must fill in. Keeping the keys identical to the fallback
# output means callers never have to know which backend ran.
_EXPLANATION_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "why_it_fits": {"type": "string"},
        "genre_mood_context": {"type": "string"},
        "caveat": {"type": "string"},
    },
    "required": ["summary", "why_it_fits", "genre_mood_context", "caveat"],
    "additionalProperties": False,
}


def explain(
    prefs: Dict,
    song: Dict,
    score: float,
    reasons: List[str],
    guide_context: Dict[str, Optional[str]],
) -> Dict[str, str]:
    """
    Produce a structured explanation for one recommended song.

    Tries the LLM backend when it is available and configured; otherwise (or on
    any failure) returns the deterministic fallback. Never raises - a broken or
    missing model must not take down the recommender.
    """
    if os.environ.get("ANTHROPIC_API_KEY"):
        llm_result = _try_llm_explanation(prefs, song, score, reasons, guide_context)
        if llm_result is not None:
            return llm_result
    return _fallback_explanation(prefs, song, score, reasons, guide_context)


def _fallback_explanation(
    prefs: Dict,
    song: Dict,
    score: float,
    reasons: List[str],
    guide_context: Dict[str, Optional[str]],
) -> Dict[str, str]:
    """Deterministic, offline explanation built from the scoring reasons."""
    title = song.get("title", "This song")
    artist = song.get("artist", "an unknown artist")

    if reasons:
        why = "This song " + "; ".join(reasons) + "."
    else:
        why = (
            "This song does not strongly match any single preference, but it "
            "scored well enough overall to be a reasonable suggestion."
        )

    context_parts: List[str] = []
    genre_context = guide_context.get("genre_context")
    mood_context = guide_context.get("mood_context")
    # Label with the preferences the context was retrieved for (not the song's
    # own genre/mood, which can differ from what the listener asked for).
    if genre_context:
        context_parts.append(f"About {prefs.get('genre')} music: {genre_context}")
    if mood_context:
        context_parts.append(f"About a {prefs.get('mood')} mood: {mood_context}")
    genre_mood_context = (
        "\n\n".join(context_parts)
        if context_parts
        else "No extra genre or mood context was found in the music guide."
    )

    return {
        "summary": f"{title} by {artist} scored {score:.2f} for your taste.",
        "why_it_fits": why,
        "genre_mood_context": genre_mood_context,
        "caveat": (
            "This pick comes from a small fixed catalog scored by simple rules, "
            "so it reflects your stated preferences only - not your listening "
            "history or how the song actually sounds to you."
        ),
        "backend": "fallback",
    }


def _try_llm_explanation(
    prefs: Dict,
    song: Dict,
    score: float,
    reasons: List[str],
    guide_context: Dict[str, Optional[str]],
) -> Optional[Dict[str, str]]:
    """
    Attempt an LLM-generated explanation.

    Returns the explanation dict on success, or ``None`` on any problem (package
    missing, API/network error, malformed response) so the caller can fall back.
    """
    try:
        import anthropic  # imported lazily so the project runs without it
    except ImportError:
        return None

    prompt = _build_prompt(prefs, song, score, reasons, guide_context)

    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=1024,
            system=(
                "You explain music recommendations produced by a rule-based "
                "recommender. Be warm, concise, and honest. Only use the reasons "
                "and music-guide context provided - never invent facts about the "
                "song, artist, or genre. Fill in every field."
            ),
            messages=[{"role": "user", "content": prompt}],
            output_config={"format": {"type": "json_schema", "schema": _EXPLANATION_SCHEMA}},
        )
    except Exception:
        # Any failure (auth, network, rate limit, bad response) -> fall back.
        return None

    text = next((block.text for block in response.content if block.type == "text"), None)
    if not text:
        return None
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return None

    # Validate the shape before trusting it; fall back if anything is missing.
    required = ("summary", "why_it_fits", "genre_mood_context", "caveat")
    if not all(isinstance(data.get(key), str) and data[key].strip() for key in required):
        return None

    return {
        "summary": data["summary"],
        "why_it_fits": data["why_it_fits"],
        "genre_mood_context": data["genre_mood_context"],
        "caveat": data["caveat"],
        "backend": "llm",
    }


def _build_prompt(
    prefs: Dict,
    song: Dict,
    score: float,
    reasons: List[str],
    guide_context: Dict[str, Optional[str]],
) -> str:
    """Assemble the grounded prompt for the LLM backend."""
    reason_lines = "\n".join(f"- {reason}" for reason in reasons) or "- (no specific factors matched)"
    genre_context = guide_context.get("genre_context") or "(none available)"
    mood_context = guide_context.get("mood_context") or "(none available)"

    return f"""A rule-based recommender picked this song for a listener. Explain WHY, using only the information below.

LISTENER PREFERENCES:
- favorite genre: {prefs.get('genre')}
- favorite mood: {prefs.get('mood')}
- target energy (0-1): {prefs.get('energy')}
- target tempo (BPM): {prefs.get('target_tempo')}
- likes acoustic: {prefs.get('likes_acoustic')}

RECOMMENDED SONG:
- title: {song.get('title')}
- artist: {song.get('artist')}
- genre: {song.get('genre')}
- mood: {song.get('mood')}
- energy: {song.get('energy')}
- tempo: {song.get('tempo_bpm')} BPM
- acousticness: {song.get('acousticness')}
- match score: {score:.2f}

WHY THE RECOMMENDER PICKED IT (the factors that scored):
{reason_lines}

MUSIC-GUIDE CONTEXT (use for the genre_mood_context field; do not add outside facts):
- genre: {genre_context}
- mood: {mood_context}

Return a JSON object with exactly these fields:
- summary: one friendly sentence naming the song and why it broadly fits.
- why_it_fits: 1-2 sentences expanding on the scoring factors above in plain language.
- genre_mood_context: 1-2 sentences of background drawn only from the music-guide context.
- caveat: one honest sentence about a limitation of this recommendation.
"""
