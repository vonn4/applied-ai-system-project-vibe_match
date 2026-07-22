import pytest

from src.pipeline import run_profile
from src.guardrails import GuardrailError

REQUIRED_FIELDS = ("summary", "why_it_fits", "genre_mood_context", "caveat")


@pytest.fixture(autouse=True)
def _force_offline(monkeypatch):
    # Keep the pipeline tests deterministic and offline.
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


def test_pipeline_returns_top_k_recommendations():
    result = run_profile(
        {"genre": "pop", "mood": "happy", "energy": 0.85, "target_tempo": 124, "likes_acoustic": False},
        k=3,
    )
    assert len(result["recommendations"]) == 3
    assert result["warnings"] == []


def test_pipeline_top_pick_matches_preferences():
    result = run_profile(
        {"genre": "rock", "mood": "intense", "energy": 0.92, "target_tempo": 148, "likes_acoustic": False},
        k=3,
    )
    top = result["recommendations"][0]["song"]
    assert top["genre"] == "rock"
    assert top["mood"] == "intense"


def test_pipeline_scores_sorted_descending():
    result = run_profile(
        {"genre": "lofi", "mood": "focused", "energy": 0.4, "target_tempo": 78, "likes_acoustic": True},
        k=5,
    )
    scores = [r["score"] for r in result["recommendations"]]
    assert scores == sorted(scores, reverse=True)


def test_pipeline_each_recommendation_has_full_explanation():
    result = run_profile(
        {"genre": "pop", "mood": "happy", "energy": 0.85, "target_tempo": 124, "likes_acoustic": False},
        k=3,
    )
    for rec in result["recommendations"]:
        for field in REQUIRED_FIELDS:
            assert rec["explanation"][field].strip()


def test_pipeline_normalizes_messy_profile():
    result = run_profile(
        {"genre": "POP", "mood": "party-vibes", "energy": "loud", "target_tempo": -20, "likes_acoustic": "yes"},
        k=3,
    )
    assert result["warnings"]
    assert 0.0 <= result["clean_prefs"]["energy"] <= 1.0
    assert result["clean_prefs"]["target_tempo"] > 0
    assert len(result["recommendations"]) == 3


def test_pipeline_rejects_empty_catalog(tmp_path):
    empty = tmp_path / "empty.csv"
    empty.write_text(
        "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness\n",
        encoding="utf-8",
    )
    with pytest.raises(GuardrailError):
        run_profile(
            {"genre": "pop", "mood": "happy", "energy": 0.5, "target_tempo": 120, "likes_acoustic": False},
            catalog_path=str(empty),
        )
