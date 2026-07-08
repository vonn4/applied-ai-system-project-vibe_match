"""
Command line runner for the Music Recommender Simulation.

This file loads the song catalog and prints the top recommendations for a few
different user profiles so you can see how the scoring behaves.

Run it from the project root with:

    python -m src.main
"""

from pathlib import Path

from src.recommender import load_songs, recommend_songs

# Build an absolute path to data/songs.csv relative to this file so the app
# works no matter which folder you run it from.
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "songs.csv"

# Three distinct user profiles used to demonstrate the recommender.
USER_PROFILES = [
    {
        "name": "Pop Party",
        "prefs": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.85,
            "target_tempo": 124,
            "likes_acoustic": False,
        },
    },
    {
        "name": "Lofi Study Session",
        "prefs": {
            "genre": "lofi",
            "mood": "focused",
            "energy": 0.40,
            "target_tempo": 78,
            "likes_acoustic": True,
        },
    },
    {
        "name": "Rock Workout",
        "prefs": {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.92,
            "target_tempo": 148,
            "likes_acoustic": False,
        },
    },
]


def main() -> None:
    songs = load_songs(str(DATA_PATH))

    for profile in USER_PROFILES:
        prefs = profile["prefs"]
        print("=" * 60)
        print(f"User profile: {profile['name']}")
        print(
            f"  genre={prefs['genre']}, mood={prefs['mood']}, "
            f"energy={prefs['energy']}, target_tempo={prefs['target_tempo']}, "
            f"likes_acoustic={prefs['likes_acoustic']}"
        )
        print("-" * 60)

        recommendations = recommend_songs(prefs, songs, k=5)

        print("Top recommendations:\n")
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            print(f"{rank}. {song['title']} - {song['artist']} (score: {score:.2f})")
            print(f"   Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
