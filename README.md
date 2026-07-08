# 🎵 Music Recommender Simulation

## Project Summary

This is a small, rule-based music recommender that I built and tuned. It stores
a catalog of 20 songs (each described by features like genre, mood, energy, and
tempo) and a short "taste profile" for a user. For any profile, my version
scores every song with a simple weighted formula, sorts the songs from best to
worst match, and prints the top 5 along with a plain-language reason for each
pick.

There is no machine learning here. The "intelligence" is a transparent scoring
rule you can read and change by hand, which is exactly why it is a good way to
see how a recommender turns raw data into ranked predictions.

---

## How The System Works

**How real recommenders work.** Large services like Spotify or YouTube learn
from data such as your likes, skips, saved playlists, and listening history, as
well as song attributes like genre, mood, and tempo. They generally combine two
ideas:

- **Collaborative filtering** — recommends items based on *other users'*
  behavior ("people who liked what you liked also played this").
- **Content-based filtering** — recommends items based on the *attributes of the
  items themselves* (genre, mood, energy, tempo, etc.) compared to what you like.

**What this project does.** This project is a simple **content-based weighted
scoring system**. It does not use other users' behavior and it does not learn
over time. It only compares one user's stated preferences to each song's
attributes and adds up points.

**Song features used.** Each `Song` has: `genre`, `mood`, `energy` (0–1),
`tempo_bpm`, `valence` (0–1), `danceability` (0–1), and `acousticness` (0–1).
The scoring rule uses **genre, mood, energy, tempo_bpm, and acousticness**.
(`valence` and `danceability` are stored in the data but not scored yet.)

**What the user profile stores.** A profile is a small dictionary of
preferences: favorite `genre`, favorite `mood`, target `energy`, a
`target_tempo` (BPM), and a boolean `likes_acoustic`.

**How a score is computed.** Each song earns points from five factors that are
added together:

| Factor | Rule | Max points |
|---|---|---|
| Genre match | exact match with favorite genre | +2.0 |
| Mood match | exact match with favorite mood | +1.5 |
| Energy similarity | `1 - |song.energy - target_energy|` | +1.0 |
| Tempo similarity | `1 - |song.tempo - target_tempo| / 60` (min 0) | +1.0 |
| Acoustic preference | `acousticness` if the user likes acoustic, else `1 - acousticness` | +1.0 |

The highest possible score is about **6.5**. Genre and mood dominate, so songs
in the right style rise to the top, while energy, tempo, and acousticness act as
tie-breakers.

**Data flow.**

```
user preferences  ->  score each song  ->  sort/rank (high to low)  ->  show top recommendations
```

Every song is scored, the list is sorted from highest score to lowest, and the
top `k` (default 5) are returned. Each recommendation also carries a reason
string built from the factors that actually contributed. The weights live as
named constants at the top of `src/recommender.py` (`GENRE_WEIGHT`,
`MOOD_WEIGHT`, etc.), so they are easy to experiment with.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

#### Test Verification

Actual `pytest` result from a local run:

```
======================== test session starts =========================
platform win32 -- Python 3.14.5, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\Owner\source\ai110\ai110-module3show-musicrecommendersimulation-starter
plugins: anyio-4.13.0
collected 2 items

tests\test_recommender.py ..                                    [100%]

========================= 2 passed in 0.04s ==========================
```

---

## Sample Recommendation Output

Real output of `python -m src.main`:

```
============================================================
User profile: Pop Party
  genre=pop, mood=happy, energy=0.85, target_tempo=124, likes_acoustic=False
------------------------------------------------------------
Top recommendations:

1. Dancefloor Gold - Neon Echo (score: 6.32)
   Because: matches your favorite genre (pop); fits the mood you want (happy); energy 0.88 is close to your target 0.85; tempo 126 BPM is close to your target 124 BPM; is mostly non-acoustic, as you prefer
2. Sunrise City - Neon Echo (score: 6.19)
   Because: matches your favorite genre (pop); fits the mood you want (happy); energy 0.82 is close to your target 0.85; tempo 118 BPM is close to your target 124 BPM; is mostly non-acoustic, as you prefer
3. Gym Hero - Max Pulse (score: 4.74)
   Because: matches your favorite genre (pop); energy 0.93 is close to your target 0.85; tempo 132 BPM is close to your target 124 BPM; is mostly non-acoustic, as you prefer
4. Festival Lights - Max Pulse (score: 4.32)
   Because: fits the mood you want (happy); energy 0.90 is close to your target 0.85; tempo 128 BPM is close to your target 124 BPM; is mostly non-acoustic, as you prefer
5. Rooftop Lights - Indigo Parade (score: 4.06)
   Because: fits the mood you want (happy); energy 0.76 is close to your target 0.85; tempo 124 BPM is close to your target 124 BPM; is mostly non-acoustic, as you prefer

============================================================
User profile: Lofi Study Session
  genre=lofi, mood=focused, energy=0.4, target_tempo=78, likes_acoustic=True
------------------------------------------------------------
Top recommendations:

1. Focus Flow - LoRoom (score: 6.25)
   Because: matches your favorite genre (lofi); fits the mood you want (focused); energy 0.40 is close to your target 0.40; tempo 80 BPM is close to your target 78 BPM; has the acoustic sound you enjoy
2. Late Night Study - LoRoom (score: 6.25)
   Because: matches your favorite genre (lofi); fits the mood you want (focused); energy 0.38 is close to your target 0.40; tempo 76 BPM is close to your target 78 BPM; has the acoustic sound you enjoy
3. Quiet Pages - Paper Lanterns (score: 4.74)
   Because: matches your favorite genre (lofi); energy 0.36 is close to your target 0.40; tempo 74 BPM is close to your target 78 BPM; has the acoustic sound you enjoy
4. Library Rain - Paper Lanterns (score: 4.71)
   Because: matches your favorite genre (lofi); energy 0.35 is close to your target 0.40; tempo 72 BPM is close to your target 78 BPM; has the acoustic sound you enjoy
5. Midnight Coding - LoRoom (score: 4.69)
   Because: matches your favorite genre (lofi); energy 0.42 is close to your target 0.40; tempo 78 BPM is close to your target 78 BPM; has the acoustic sound you enjoy

============================================================
User profile: Rock Workout
  genre=rock, mood=intense, energy=0.92, target_tempo=148, likes_acoustic=False
------------------------------------------------------------
Top recommendations:

1. Adrenaline Rush - Voltline (score: 6.40)
   Because: matches your favorite genre (rock); fits the mood you want (intense); energy 0.92 is close to your target 0.92; tempo 150 BPM is close to your target 148 BPM; is mostly non-acoustic, as you prefer
2. Deadlift Anthem - Max Pulse (score: 6.36)
   Because: matches your favorite genre (rock); fits the mood you want (intense); energy 0.95 is close to your target 0.92; tempo 146 BPM is close to your target 148 BPM; is mostly non-acoustic, as you prefer
3. Storm Runner - Voltline (score: 6.32)
   Because: matches your favorite genre (rock); fits the mood you want (intense); energy 0.91 is close to your target 0.92; tempo 152 BPM is close to your target 148 BPM; is mostly non-acoustic, as you prefer
4. Gym Hero - Max Pulse (score: 4.17)
   Because: fits the mood you want (intense); energy 0.93 is close to your target 0.92; tempo 132 BPM is close to your target 148 BPM; is mostly non-acoustic, as you prefer
5. Festival Lights - Max Pulse (score: 2.59)
   Because: energy 0.90 is close to your target 0.92; tempo 128 BPM is close to your target 148 BPM; is mostly non-acoustic, as you prefer
```

---

## Experiments You Tried

I tested three distinct user profiles to see how the scoring behaves for
different kinds of listeners:

- **Pop Party** — `pop`, `happy`, energy 0.85, target tempo 124, not acoustic.
  A high-energy, upbeat listener.
- **Lofi Study Session** — `lofi`, `focused`, energy 0.40, target tempo 78,
  acoustic. A calm, low-energy studying listener.
- **Rock Workout** — `rock`, `intense`, energy 0.92, target tempo 148, not
  acoustic. A high-intensity, fast-tempo listener.

**Comparing the outputs:**

- **Pop Party** favored happy, high-energy, non-acoustic pop songs
  (*Dancefloor Gold*, *Sunrise City* on top).
- **Lofi Study Session** shifted toward lower-energy, slower, more acoustic lofi
  songs (*Focus Flow*, *Late Night Study* on top).
- **Rock Workout** favored intense, fast-tempo, high-energy rock songs
  (*Adrenaline Rush*, *Deadlift Anthem*, *Storm Runner* on top).
- **Gym Hero** appears in both the Pop Party and Rock Workout lists because it is
  high energy and non-acoustic, even though it does not match every preference
  (it is a pop song with an intense mood, so it partially fits both profiles).

Because the weight constants live at the top of `src/recommender.py`, you can
rerun `python -m src.main` after changing them to see how the rankings shift.

---

## Limitations and Risks

- It only works on a tiny 20-song catalog, so "top 5" is a large fraction of
  everything available.
- It requires **exact** genre and mood strings; "indie pop" is treated as
  completely different from "pop", and a typo would score zero on that factor.
- It does not understand lyrics, language, artist, listening history, likes, or
  skips.
- It can over-favor whatever the biggest weights are (currently genre), so a
  user who likes several genres only ever sees their single favorite.
- `valence` and `danceability` are collected but not used by the current score.

I go deeper on these in the model card.

---

## Stretch Features

I did **not** implement any stretch features for this project. Everything above
is the core, required functionality only, and no stretch credit is claimed.

---

## Reflection

This project helped me understand how recommendation systems turn simple data
into ranked predictions. My recommender does not learn like Spotify or YouTube,
but it shows the basic idea: compare user preferences to item features, score
every item, and rank the results. Claude helped me move faster with CSV loading,
the scoring logic, and readable terminal output, but I still had to verify that
the output made sense and that the explanations matched the actual scoring rules.

Read and complete the model card for the full reflection:

[**Model Card**](model_card.md)
