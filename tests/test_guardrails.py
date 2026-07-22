import pytest

from src.guardrails import (
    validate_user_profile,
    validate_catalog,
    GuardrailError,
)


def _valid_song(**overrides):
    song = {
        "id": 1,
        "title": "T",
        "artist": "A",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.5,
        "tempo_bpm": 120,
        "valence": 0.5,
        "danceability": 0.5,
        "acousticness": 0.5,
    }
    song.update(overrides)
    return song


def test_valid_profile_passes_without_warnings():
    clean, warnings = validate_user_profile(
        {"genre": "pop", "mood": "happy", "energy": 0.8, "target_tempo": 120, "likes_acoustic": True}
    )
    assert warnings == []
    assert clean["genre"] == "pop"
    assert clean["energy"] == 0.8
    assert clean["likes_acoustic"] is True


def test_genre_and_mood_are_lowercased_and_trimmed():
    clean, _ = validate_user_profile(
        {"genre": "  POP ", "mood": "Happy", "energy": 0.5, "target_tempo": 120, "likes_acoustic": False}
    )
    assert clean["genre"] == "pop"
    assert clean["mood"] == "happy"


def test_unknown_genre_and_mood_warn_but_pass_through():
    clean, warnings = validate_user_profile(
        {"genre": "polka", "mood": "nostalgic", "energy": 0.5, "target_tempo": 120, "likes_acoustic": False}
    )
    assert clean["genre"] == "polka"
    assert clean["mood"] == "nostalgic"
    assert any("polka" in w for w in warnings)
    assert any("nostalgic" in w for w in warnings)


def test_non_numeric_energy_defaults_with_warning():
    clean, warnings = validate_user_profile(
        {"genre": "pop", "mood": "happy", "energy": "loud", "target_tempo": 120, "likes_acoustic": False}
    )
    assert clean["energy"] == 0.5
    assert any("energy" in w.lower() for w in warnings)


def test_out_of_range_energy_is_clamped():
    clean, warnings = validate_user_profile(
        {"genre": "pop", "mood": "happy", "energy": 5.0, "target_tempo": 120, "likes_acoustic": False}
    )
    assert clean["energy"] == 1.0
    assert any("clamped" in w for w in warnings)


def test_non_positive_tempo_is_replaced():
    clean, warnings = validate_user_profile(
        {"genre": "pop", "mood": "happy", "energy": 0.5, "target_tempo": -20, "likes_acoustic": False}
    )
    assert clean["target_tempo"] > 0
    assert any("tempo" in w.lower() for w in warnings)


def test_missing_genre_and_mood_are_skipped_with_warnings():
    clean, warnings = validate_user_profile(
        {"energy": 0.5, "target_tempo": 120, "likes_acoustic": False}
    )
    assert clean["genre"] is None
    assert clean["mood"] is None
    assert len(warnings) >= 2


def test_non_dict_profile_raises():
    with pytest.raises(GuardrailError):
        validate_user_profile(["not", "a", "dict"])


def test_empty_catalog_raises():
    with pytest.raises(GuardrailError):
        validate_catalog([])


def test_catalog_missing_field_raises():
    bad = _valid_song()
    del bad["energy"]
    with pytest.raises(GuardrailError):
        validate_catalog([bad])


def test_valid_catalog_passes():
    assert validate_catalog([_valid_song(), _valid_song(id=2)]) == []
