"""
VibeMatch AI - evaluation and reliability harness.

Runs a set of listener profiles plus guardrail/retrieval checks through the
pipeline and prints PASS/FAIL for each, followed by a reliability summary.

This script runs **fully offline** - it never requires an API key. The AI
explanation layer falls back to its deterministic backend automatically, so the
pass/fail results are reproducible for grading. (If a key happens to be set the
same checks still apply; they test structure and correctness, not exact wording.)

Run from the project root:

    python evaluate.py

Exit code is 0 if every check passes, 1 otherwise.
"""

import sys
from typing import Callable, List, Tuple

from src.pipeline import run_profile
from src.retrieval import MusicGuide
from src.guardrails import GuardrailError, validate_catalog

# Profiles with the genre/mood we expect the top pick to match.
EVAL_PROFILES = [
    {"name": "Pop Party", "prefs": {"genre": "pop", "mood": "happy", "energy": 0.85, "target_tempo": 124, "likes_acoustic": False}, "expect_genre": "pop", "expect_mood": "happy"},
    {"name": "Lofi Study Session", "prefs": {"genre": "lofi", "mood": "focused", "energy": 0.40, "target_tempo": 78, "likes_acoustic": True}, "expect_genre": "lofi", "expect_mood": "focused"},
    {"name": "Rock Workout", "prefs": {"genre": "rock", "mood": "intense", "energy": 0.92, "target_tempo": 148, "likes_acoustic": False}, "expect_genre": "rock", "expect_mood": "intense"},
    {"name": "Ambient Wind-down", "prefs": {"genre": "ambient", "mood": "chill", "energy": 0.25, "target_tempo": 60, "likes_acoustic": True}, "expect_genre": "ambient", "expect_mood": "chill"},
]

_EXPLANATION_FIELDS = ("summary", "why_it_fits", "genre_mood_context", "caveat")


def _check(results: List[Tuple[str, bool, str]], name: str, passed: bool, detail: str = "") -> None:
    results.append((name, passed, detail))


def evaluate() -> List[Tuple[str, bool, str]]:
    results: List[Tuple[str, bool, str]] = []

    # --- Per-profile recommendation quality ------------------------------
    for profile in EVAL_PROFILES:
        name = profile["name"]
        result = run_profile(profile["prefs"], k=3)
        recs = result["recommendations"]

        _check(results, f"[{name}] returns recommendations", len(recs) > 0, f"{len(recs)} returned")

        if recs:
            top = recs[0]["song"]
            _check(
                results,
                f"[{name}] top pick genre == {profile['expect_genre']}",
                top["genre"] == profile["expect_genre"],
                f"got {top['genre']!r}",
            )
            _check(
                results,
                f"[{name}] top pick mood == {profile['expect_mood']}",
                top["mood"] == profile["expect_mood"],
                f"got {top['mood']!r}",
            )
            _check(
                results,
                f"[{name}] scores are sorted descending",
                all(recs[i]["score"] >= recs[i + 1]["score"] for i in range(len(recs) - 1)),
            )

            exp = recs[0]["explanation"]
            complete = all(isinstance(exp.get(f), str) and exp[f].strip() for f in _EXPLANATION_FIELDS)
            _check(results, f"[{name}] explanation has all fields, non-empty", complete,
                   f"backend={exp.get('backend')}")

    # --- Guardrails: messy profile is normalized, not crashed ------------
    messy = run_profile(
        {"genre": "POP", "mood": "party-vibes", "energy": "loud", "target_tempo": -20, "likes_acoustic": "yes"},
        k=3,
    )
    _check(results, "[guardrails] messy profile produces warnings", len(messy["warnings"]) > 0,
           f"{len(messy['warnings'])} warnings")
    _check(results, "[guardrails] messy profile still recommends", len(messy["recommendations"]) > 0)
    _check(results, "[guardrails] bad energy clamped into 0-1",
           0.0 <= messy["clean_prefs"]["energy"] <= 1.0, f"energy={messy['clean_prefs']['energy']}")
    _check(results, "[guardrails] non-positive tempo replaced with positive",
           messy["clean_prefs"]["target_tempo"] > 0, f"tempo={messy['clean_prefs']['target_tempo']}")

    # --- Guardrails: empty catalog is rejected ---------------------------
    empty_rejected = False
    try:
        validate_catalog([])
    except GuardrailError:
        empty_rejected = True
    _check(results, "[guardrails] empty catalog raises GuardrailError", empty_rejected)

    # --- Retrieval: known terms return context, unknown returns None -----
    guide = MusicGuide.load()
    ctx = guide.retrieve("lofi", "focused")
    _check(results, "[retrieval] known genre returns context", bool(ctx["genre_context"]))
    _check(results, "[retrieval] known mood returns context", bool(ctx["mood_context"]))
    unknown = guide.retrieve("polka", "nostalgic")
    _check(results, "[retrieval] unknown terms return None safely",
           unknown["genre_context"] is None and unknown["mood_context"] is None)

    return results


def main() -> int:
    results = evaluate()
    print("VibeMatch AI - reliability evaluation\n")
    for name, passed, detail in results:
        status = "PASS" if passed else "FAIL"
        suffix = f"  ({detail})" if detail else ""
        print(f"  [{status}] {name}{suffix}")

    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    print("\n" + "-" * 50)
    print(f"Reliability: {passed}/{total} checks passed ({passed / total * 100:.0f}%).")
    if passed == total:
        print("Result: RELIABLE - all checks passed.")
        return 0
    print("Result: NEEDS ATTENTION - some checks failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
