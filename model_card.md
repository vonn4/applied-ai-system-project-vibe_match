# 🎧 Model Card: VibeMatch AI — Hybrid Music Recommendation Advisor

## 1. Model Name

**VibeMatch AI 2.0** — a transparent, rule-based music recommender wrapped in a
retrieval-grounded, hybrid AI explanation layer.

---

## 2. Intended Use

VibeMatch AI recommends songs from a small fixed catalog based on a listener's
stated taste (favorite genre, favorite mood, target energy, target tempo, and
whether they like acoustic music) and then explains each pick in a structured,
user-friendly way.

- **What it produces:** a ranked top-k list of songs, each with a structured
  explanation (`summary`, `why_it_fits`, `genre_mood_context`, `caveat`).
- **Who it is for:** a **classroom applied-AI exploration project**, not a
  product for real listeners. It exists to demonstrate how a deterministic
  decision engine can be combined with input guardrails, a retrieval step, and a
  language-model explanation layer into a complete, defensible system.
- **Division of responsibility:** the rule-based recommender decides *what* to
  recommend and in what order; the AI layer only explains *why*. The language
  model never re-ranks or overrides the rules.

---

## 3. How the Model Works

For every song, the rule-based engine hands out points: genre match (+2.0),
mood match (+1.5), and up to +1.0 each for energy closeness, tempo closeness,
and acoustic fit. Points are summed, songs are sorted high-to-low, and the top
few are returned along with the plain-language reasons that actually scored.

Around that engine, three layers were added for Project 4:

- **Guardrails** (`src/guardrails.py`) validate and normalize the listener
  profile (unknown genres/moods are flagged, bad numbers are coerced or
  clamped, missing values default safely) and hard-reject an empty or malformed
  catalog.
- **Retrieval** (`src/retrieval.py`) reads a local music guide
  (`data/music_guide.md`), splits it into genre/mood sections, and returns the
  sections matching the listener's preferences.
- **Hybrid AI explanation** (`src/explainer.py`) turns the reasons + retrieved
  context into a structured explanation. When `ANTHROPIC_API_KEY` is set and the
  `anthropic` package is installed, it calls Claude (`claude-haiku-4-5`);
  otherwise, or on any failure, it uses a deterministic offline template. Both
  paths return the identical structure.

**Changes from the original project:** the original returned a ranked list with
a single reason string. VibeMatch AI adds validation/guardrails, a retrieval
corpus and retriever, a structured hybrid explanation layer, an end-to-end demo
with a guardrail case, an automated reliability evaluator, and an architecture
diagram — while preserving the original scoring engine and its two passing
tests.

---

## 4. Data

- **Catalog:** 20 songs in `data/songs.csv` (id, title, artist, genre, mood,
  energy, tempo_bpm, valence, danceability, acousticness).
- **Music guide:** `data/music_guide.md`, a hand-written reference with one
  section per genre (9) and per mood (6). This is the retrieval corpus, not
  training data — nothing is learned from it.
- **What's missing:** whole families of music (hip-hop, classical, country,
  most non-English music) are absent, and there are only a handful of artists,
  so the catalog cannot represent real musical diversity.

---

## 5. Strengths

- **Explainable end to end.** Ranking is a transparent weighted sum, and every
  explanation is grounded in the exact factors that scored plus verifiable guide
  context.
- **Robust to bad input.** Guardrails keep the demo running on messy profiles
  and fail loudly only when the catalog itself is unusable.
- **Runs anywhere.** The offline fallback means the whole system — demo,
  evaluation, tests — works with no API key and no network, which is exactly
  what a grader needs.
- **Predictable and tunable.** Changing a single weight constant produces an
  understandable change in rankings.

---

## 6. Limitations and Bias

- **Small catalog.** With 20 songs, "top 3" is a large slice of everything.
- **No behavioral data.** No history, likes, skips, or playlists — only stated
  preferences.
- **Exact-match brittleness.** "indie pop" scores zero against a "pop"
  preference; unknown genres/moods simply never match.
- **Filter-bubble / frequency bias.** Genre and mood carry the most weight, and
  genres that appear more often in the catalog get more chances to land on top.
- **Ignored signals:** lyrics, language, artist, release year, popularity, and
  the stored-but-unused `valence` and `danceability`.

---

## 7. Misuse Risks

- **Fabricated music facts.** The biggest risk of adding a language model is that
  it invents plausible-sounding but false claims about songs, artists, or genres.
  **Mitigation:** the LLM is prompted to use *only* the recommender's reasons and
  the retrieved guide text, its output is constrained to a fixed JSON schema, and
  the deterministic fallback removes the model from the loop entirely. It
  explains a decision the rules already made rather than generating facts.
- **False authority / over-trust.** Fluent explanations can make a tiny toy
  recommender feel more capable than it is. **Mitigation:** every explanation
  carries an honest `caveat` field, and the model card and README state plainly
  that this is a classroom toy on a 20-song catalog.
- **Taste stereotyping.** Grounding text in genre/mood generalizations could
  reinforce stereotypes about who listens to what. The guide is kept factual and
  descriptive (sound, tempo, typical use) rather than demographic.
- **Silent dependency on an external service.** If the LLM path were mandatory, a
  network outage or an unexpected charge could break or surprise a user.
  **Mitigation:** the API path is strictly optional and degrades gracefully.

---

## 8. Evaluation and Reliability

`evaluate.py` runs four listener profiles plus guardrail and retrieval checks
and prints PASS/FAIL for each — **28/28 checks pass**, fully offline. It verifies:

- The #1 pick matches each profile's genre and mood; scores are sorted.
- Every recommendation carries a complete, non-empty explanation.
- Messy input is normalized (energy clamped to 0–1, non-positive tempo replaced)
  and still produces recommendations, with warnings.
- An empty catalog raises `GuardrailError`.
- Retrieval returns context for known genres/moods and `None` for unknown terms.

The unit suite (`pytest`) adds 33 tests across the recommender, guardrails,
retrieval, explainer (including the fallback and API-failure paths), and the
pipeline.

### Reliability-testing surprises

- **The AI layer's failure mode was harder to test than its success.** Writing a
  meaningful test meant asserting that a *missing key* and a *failing API call*
  both silently produce a valid fallback — the interesting behavior was the
  graceful degradation, not the happy path. That reframed how I thought about
  "reliability": the offline path is the real product.
- **A subtle labeling bug only surfaced in the demo, not the scores.** The
  fallback explanation originally labeled its genre/mood context using the
  *song's* mood, while the context was actually retrieved for the *listener's*
  preferred mood — so a cross-over pick (a pop song with an "intense" mood shown
  to a "happy" listener) displayed the happy description under an "intense"
  label. The scoring was correct; only the explanation text was misleading. It's
  a good reminder that an explanation layer can be wrong even when the decision
  is right.
- **Guardrails let unknown genres/moods through on purpose.** My first instinct
  was to reject a typo like `party-vibes`. But the recommender already treats a
  non-match as a zero score, so the safer, less surprising behavior is to warn
  and continue — rejecting would have made the system more brittle, not less.

---

## 9. Future Work

- Add real feedback (likes/skips) so ranking can adapt to behavior.
- Add a diversity penalty so the top list isn't dominated by one artist/genre.
- Grow and balance the catalog; start using `valence` and `danceability`.
- Optionally use embeddings for retrieval if the guide grows large.

---

## 10. AI Collaboration Reflection

I used Claude (in the Claude Code CLI) as a collaborator throughout Project 4.
The most useful thing it did was turn the rubric into a concrete, file-by-file
plan and then flag the one decision that actually shaped the architecture — how
the "AI explanation layer" should be implemented — instead of silently picking
one. Choosing the **hybrid Claude-API-with-offline-fallback** approach on that
prompt is why the system is both a genuine applied-AI project *and* reproducible
for grading without a key.

Where I had to push back or verify: I kept the rule-based recommender as the
source of truth so the language model couldn't quietly change rankings, and I
insisted the explanation layer be grounded in the recommender's own reasons plus
the retrieved guide rather than free-form generation, which is the core mitigation
for fabricated facts. I also verified every sample output in the README against
real runs rather than trusting generated text — that's how the context-labeling
bug and an incorrect sample song got caught and fixed. The lesson I'm taking
away is that AI is excellent at scaffolding and structure, but the human still
has to own correctness, honest limitations, and the decisions that trade off
capability against reliability.

A full prompt-by-prompt log is in [ai_interactions.md](ai_interactions.md).
