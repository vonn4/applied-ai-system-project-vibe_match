from src.retrieval import MusicGuide, _parse_sections

SAMPLE = """# Title

## Genres

### pop
Pop is catchy.

### lofi
Lofi is chill.

## Moods

### happy
Happy is bright.
"""


def test_parse_sections_only_captures_level_three_headings():
    sections = _parse_sections(SAMPLE)
    assert set(sections) == {"pop", "lofi", "happy"}
    assert sections["pop"] == "Pop is catchy."


def test_lookup_is_case_insensitive_and_trims():
    guide = MusicGuide(_parse_sections(SAMPLE))
    assert guide.lookup("POP ") == "Pop is catchy."
    assert guide.lookup("Lofi") == "Lofi is chill."


def test_lookup_unknown_returns_none():
    guide = MusicGuide(_parse_sections(SAMPLE))
    assert guide.lookup("techno") is None
    assert guide.lookup("") is None


def test_retrieve_returns_both_contexts():
    guide = MusicGuide(_parse_sections(SAMPLE))
    ctx = guide.retrieve("pop", "happy")
    assert ctx["genre_context"] == "Pop is catchy."
    assert ctx["mood_context"] == "Happy is bright."


def test_retrieve_handles_unknown_and_none_terms():
    guide = MusicGuide(_parse_sections(SAMPLE))
    ctx = guide.retrieve("techno", None)
    assert ctx["genre_context"] is None
    assert ctx["mood_context"] is None


def test_missing_guide_file_loads_empty():
    guide = MusicGuide.load("does/not/exist.md")
    assert guide.sections == {}
    assert guide.retrieve("pop", "happy") == {"genre_context": None, "mood_context": None}


def test_real_guide_loads_expected_sections():
    guide = MusicGuide.load()
    # The shipped data/music_guide.md should have all catalog genres/moods.
    for term in ("pop", "lofi", "rock", "ambient", "focused", "chill", "intense"):
        assert guide.lookup(term), f"missing guide section: {term}"
