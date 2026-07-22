from src.explainer import explain, _fallback_explanation

PREFS = {
    "genre": "lofi",
    "mood": "focused",
    "energy": 0.4,
    "target_tempo": 78,
    "likes_acoustic": True,
}
SONG = {
    "title": "Focus Flow",
    "artist": "LoRoom",
    "genre": "lofi",
    "mood": "focused",
    "energy": 0.4,
    "tempo_bpm": 80,
    "acousticness": 0.78,
}
GUIDE_CTX = {
    "genre_context": "Lofi is relaxed background music.",
    "mood_context": "Focused music aids concentration.",
}

REQUIRED_FIELDS = ("summary", "why_it_fits", "genre_mood_context", "caveat")


def test_fallback_has_all_fields_and_backend_label():
    exp = _fallback_explanation(PREFS, SONG, 6.25, ["matches your favorite genre (lofi)"], GUIDE_CTX)
    for field in REQUIRED_FIELDS:
        assert isinstance(exp[field], str) and exp[field].strip()
    assert exp["backend"] == "fallback"


def test_fallback_uses_reasons_in_why():
    exp = _fallback_explanation(PREFS, SONG, 6.25, ["matches your favorite genre (lofi)"], GUIDE_CTX)
    assert "lofi" in exp["why_it_fits"]


def test_fallback_labels_context_with_preferences_not_song():
    # Song mood differs from the preferred mood; the context label should follow
    # the preference the context was retrieved for.
    song = dict(SONG, mood="chill")
    exp = _fallback_explanation(PREFS, song, 5.0, [], GUIDE_CTX)
    assert "focused mood" in exp["genre_mood_context"]


def test_fallback_handles_no_reasons():
    exp = _fallback_explanation(PREFS, SONG, 1.0, [], GUIDE_CTX)
    assert exp["why_it_fits"].strip()


def test_fallback_handles_missing_guide_context():
    exp = _fallback_explanation(PREFS, SONG, 6.25, ["x"], {"genre_context": None, "mood_context": None})
    assert exp["genre_mood_context"].strip()


def test_explain_without_api_key_uses_fallback(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    exp = explain(PREFS, SONG, 6.25, ["matches your favorite genre (lofi)"], GUIDE_CTX)
    assert exp["backend"] == "fallback"
    for field in REQUIRED_FIELDS:
        assert exp[field].strip()


def test_explain_falls_back_when_api_call_fails(monkeypatch):
    # With a key set but the SDK forced to error, explain() must still return a
    # valid fallback rather than raising.
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    import src.explainer as explainer

    monkeypatch.setattr(explainer, "_try_llm_explanation", lambda *a, **k: None)
    exp = explain(PREFS, SONG, 6.25, ["x"], GUIDE_CTX)
    assert exp["backend"] == "fallback"
