import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict

# --- Scoring weights -------------------------------------------------------
# These constants control how much each feature matters. They are kept at the
# top of the file so they are easy to find and tweak for experiments.
GENRE_WEIGHT = 2.0      # exact genre match
MOOD_WEIGHT = 1.5       # exact mood match
ENERGY_WEIGHT = 1.0     # how close the song's energy is to what the user wants
TEMPO_WEIGHT = 1.0      # how close the song's tempo (BPM) is to the user's target
ACOUSTIC_WEIGHT = 1.0   # reward acoustic/non-acoustic based on user preference

# A song within this many BPM of the target counts as a good tempo match.
TEMPO_TOLERANCE = 60.0


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # Optional so existing tests that omit it still work; defaults to a
    # medium-tempo preference.
    target_tempo: float = 120.0

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py

    This class reuses the functional score_song() below so there is a single
    source of truth for how songs are scored.
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _prefs_from_user(self, user: UserProfile) -> Dict:
        """Turn a UserProfile into the plain dict that score_song() expects."""
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "target_tempo": user.target_tempo,
            "likes_acoustic": user.likes_acoustic,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        prefs = self._prefs_from_user(user)
        # Score every song, then sort from highest score to lowest.
        scored = []
        for song in self.songs:
            score, _reasons = score_song(prefs, asdict(song))
            scored.append((song, score))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [song for song, _score in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        prefs = self._prefs_from_user(user)
        _score, reasons = score_song(prefs, asdict(song))
        return _reasons_to_text(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file and converts numbers to the correct types.
    Returns a list of dictionaries (one per song).
    Required by src/main.py
    """
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.

    Recipe:
      +2.0 for a genre match
      +1.5 for a mood match
      up to +1.0 for energy similarity
      up to +1.0 for tempo similarity
      up to +1.0 for the acoustic preference (uses likes_acoustic)

    Returns (score, reasons) where reasons is a list of plain-language strings.
    """
    score = 0.0
    reasons: List[str] = []

    # Genre match ----------------------------------------------------------
    if user_prefs.get("genre") and song["genre"] == user_prefs["genre"]:
        score += GENRE_WEIGHT
        reasons.append(f"matches your favorite genre ({song['genre']})")

    # Mood match -----------------------------------------------------------
    if user_prefs.get("mood") and song["mood"] == user_prefs["mood"]:
        score += MOOD_WEIGHT
        reasons.append(f"fits the mood you want ({song['mood']})")

    # Energy similarity: closer energy -> higher points (0.0 to 1.0) -------
    if user_prefs.get("energy") is not None:
        target_energy = user_prefs["energy"]
        energy_similarity = max(0.0, 1.0 - abs(song["energy"] - target_energy))
        score += energy_similarity * ENERGY_WEIGHT
        if energy_similarity >= 0.6:
            reasons.append(
                f"energy {song['energy']:.2f} is close to your target {target_energy:.2f}"
            )

    # Tempo similarity: within TEMPO_TOLERANCE BPM -> higher points --------
    if user_prefs.get("target_tempo") is not None:
        target_tempo = user_prefs["target_tempo"]
        tempo_diff = abs(song["tempo_bpm"] - target_tempo)
        tempo_similarity = max(0.0, 1.0 - tempo_diff / TEMPO_TOLERANCE)
        score += tempo_similarity * TEMPO_WEIGHT
        if tempo_similarity >= 0.6:
            reasons.append(
                f"tempo {song['tempo_bpm']:.0f} BPM is close to your target {target_tempo:.0f} BPM"
            )

    # Acoustic preference --------------------------------------------------
    likes_acoustic = user_prefs.get("likes_acoustic", False)
    if likes_acoustic:
        score += song["acousticness"] * ACOUSTIC_WEIGHT
        if song["acousticness"] >= 0.6:
            reasons.append("has the acoustic sound you enjoy")
    else:
        score += (1.0 - song["acousticness"]) * ACOUSTIC_WEIGHT
        if song["acousticness"] <= 0.4:
            reasons.append("is mostly non-acoustic, as you prefer")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Scores every song, sorts them from highest score to lowest, and returns
    the top k as (song_dict, score, explanation) tuples.
    Required by src/main.py
    """
    scored: List[Tuple[Dict, float, str]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, _reasons_to_text(reasons)))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]

def _reasons_to_text(reasons: List[str]) -> str:
    """Join a list of reasons into one readable sentence (never empty)."""
    if not reasons:
        return "a general match for your taste"
    return "; ".join(reasons)
