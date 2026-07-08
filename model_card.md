# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0** — a transparent, rule-based music recommender.

---

## 2. Intended Use

VibeMatch recommends songs from a small fixed catalog based on a user's stated
taste. Given a favorite genre, favorite mood, target energy level, target tempo,
and whether the user likes acoustic music, it returns a ranked top-5 list with a
plain-language reason for each pick.

- **What it generates:** a short, ordered list of song recommendations with
  explanations.
- **Assumptions about the user:** that the user can describe their taste as a
  single favorite genre and mood plus a few numeric preferences. It assumes one
  clear taste per run, not a mix.
- **Who it is for:** this is a **classroom exploration project**, not a product
  for real listeners. It exists to show how a scoring rule turns song data into
  ranked recommendations.

---

## 3. How the Model Works

Imagine each song has a small "report card" of traits: its genre, its mood, how
energetic it is, how fast it is (tempo), and how acoustic it sounds. The user
fills out a matching wish list: their favorite genre and mood, the energy and
tempo they want, and whether they like acoustic music.

For every song, the model hands out points:

- **Genre match** gives points if the song's genre equals the user's favorite.
- **Mood match** gives points if the song's mood equals the user's favorite.
- **Energy similarity** gives points based on how *close* the song's energy is
  to the target — closer means more points.
- **Tempo similarity** gives points based on how *close* the song's tempo (BPM)
  is to the target — closer means more points.
- **Acoustic preference** adds points based on whether the user prefers acoustic
  or non-acoustic songs: if they like acoustic, more acoustic songs score
  higher; if they don't, less acoustic songs score higher.

All the points are added into one score, the songs are sorted from highest score
to lowest, and the top few are shown.

- **Song features used in scoring:** genre, mood, energy, tempo, acousticness.
- **Features stored but not scored yet:** valence, danceability.
- **User preferences considered:** favorite genre, favorite mood, target energy,
  target tempo, likes-acoustic (yes/no).
- **Turning that into a score:** a weighted sum — +2.0 genre, +1.5 mood, up to
  +1.0 each for energy closeness, tempo closeness, and acoustic fit.
- **Changes from the starter logic:** the starter code just returned the first
  few songs unchanged. This version loads the CSV with correct number types,
  scores each song on five features, sorts by score, and produces a reason for
  every recommendation.

---

## 4. Data

- **Catalog size:** 20 songs, stored in `data/songs.csv`.
- **Attributes per song:** `genre`, `mood`, `energy`, `tempo_bpm`, `valence`,
  `danceability`, and `acousticness` (plus `id`, `title`, and `artist`).
- **Genres represented:** pop, indie pop, lofi, rock, ambient, jazz, synthwave,
  folk, and edm.
- **Moods represented:** happy, chill, intense, relaxed, focused, and moody.
- **Changes made:** the starter file had 10 songs; 10 more were added (ids
  11–20) to reach 20, spreading across the genres and moods above.
- **What's missing:** the catalog is tiny and hand-made. Whole families of music
  (hip-hop, classical, country, global/regional styles, and most non-English
  music) are absent, and there are only a handful of artists, so it cannot
  represent the real diversity of musical taste.

---

## 5. Strengths

- **Clear, obvious matches rise to the top.** For each of the three test
  profiles, the songs a person would expect appear in the top spots (pop/happy
  songs for Pop Party, lofi/focused songs for the study profile, rock/intense
  songs for the workout profile).
- **Every recommendation is explainable.** Because the score is a simple sum of
  named factors, the model can honestly say *why* a song was picked.
- **Predictable and easy to tune.** Changing a single weight constant produces an
  understandable change in the rankings, which is great for experimentation.
- It matched intuition best for users with one strong, well-defined taste.

---

## 6. Limitations and Bias

- **Small catalog.** With only 20 songs, "top 5" is a quarter of everything, so
  the results are not very selective.
- **No real behavioral data.** There is no listening history, and no likes,
  skips, or playlists — the model only sees stated preferences, not what a user
  actually does.
- **Filter-bubble risk.** Because genre and mood carry the most weight, the model
  can over-reward genre/mood matches and keep showing the same style, so a user
  who enjoys several genres mostly sees their single stated favorite.
- **Dataset-frequency bias.** Genres or artists that appear more often in the
  catalog have more chances to land in the top 5, so the model can
  over-recommend whatever is over-represented in the data.
- **Features it ignores:** lyrics, language, artist, release year, popularity,
  and the stored-but-unused `valence` and `danceability`.
- **Exact-match brittleness:** "indie pop" scores zero against a "pop"
  preference even though they are closely related.

---

## 7. Evaluation

- **Profiles tested (via `python -m src.main`):**
  1. **Pop Party** — pop, happy, energy 0.85, tempo 124, not acoustic.
  2. **Lofi Study Session** — lofi, focused, energy 0.40, tempo 78, acoustic.
  3. **Rock Workout** — rock, intense, energy 0.92, tempo 148, not acoustic.
- **What changed between the outputs:**
  - **Pop Party** returned happy, high-energy, non-acoustic pop songs on top
    (*Dancefloor Gold* 6.32, *Sunrise City* 6.19).
  - **Lofi Study Session** shifted the whole list toward lower-energy, slower,
    acoustic lofi songs (*Focus Flow* and *Late Night Study* tied at 6.25).
  - **Rock Workout** shifted toward intense, fast-tempo rock songs
    (*Adrenaline Rush* 6.40, *Deadlift Anthem* 6.36, *Storm Runner* 6.32).
  - **Cross-over case:** *Gym Hero* appears in both the Pop Party and Rock
    Workout top 5 because it is high energy and non-acoustic, so it partially
    satisfies both profiles even though it doesn't match every preference.
- **What I looked for:** whether the #1 pick matched the profile's genre and
  mood, and whether the reasons made sense.
- **Automated tests:** `tests/test_recommender.py` checks that `recommend`
  returns songs sorted by score (the pop/happy song ranks first) and that
  `explain_recommendation` returns a non-empty string. Both pass
  (`2 passed in 0.04s`).
- **What surprised me:** how strongly the genre weight controls the results —
  once genre matches, the rest of the list order is mostly decided by tempo and
  energy tie-breakers.

---

## 8. Future Work

- **Add real user feedback** (likes, skips, saves) so the model can adapt to
  behavior instead of only stated preferences.
- **Add a diversity penalty** so the top 5 isn't dominated by one artist or one
  genre.
- **Add more songs and more balanced genres** so under-represented styles get a
  fair chance.
- **Maybe add lyrics or popularity data**, and start using the already-stored
  `valence` and `danceability` features.

---

## 9. Personal Reflection

I learned that simple scoring rules can still feel like recommendations when the
features are clear. AI helped with structure and debugging, but I had to
double-check correctness, test the output, and confirm the documentation was
accurate. If I continued, I would add feedback and diversity logic.
