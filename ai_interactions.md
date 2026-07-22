# AI Interactions Log

## Scope

This file documents how I used AI while building **VibeMatch AI**, the applied-AI
system for Project 4. It extends the earlier log from the original Music
Recommender Simulation (kept below for continuity).

## AI Tool Used

Claude (Claude Code CLI), model Opus 4.8.

---

## Project 4 — VibeMatch AI

### Main tasks I asked AI to help with

- Inspect the existing rule-based recommender and produce a file-by-file plan to
  turn it into an applied AI system (recommender + guardrails + retrieval +
  hybrid AI explanation + demo + evaluation + docs + diagram) **before editing**.
- Design and implement the hybrid AI explanation layer.
- Implement input validation/guardrails, a local-document retrieval component,
  an end-to-end demo, and a reliability evaluation script.
- Add tests for the new layers and keep the original two tests passing.
- Write the architecture diagram and update the README, model card, and this log.

### Example prompts I used

Summaries rather than full pasted prompts:

1. "Inspect this repo and give me a file-by-file implementation plan to turn it
   into an applied AI system, with risks. Don't edit anything yet."
2. "Implement the hybrid explainer: use the Claude API (`claude-haiku-4-5`) only
   when `ANTHROPIC_API_KEY` is set; otherwise fall back to a deterministic
   explanation. Both must return the same structure."
3. "Make `evaluate.py` run fully without an API key and print pass/fail plus a
   reliability summary."
4. "Run the demo and evaluation and make sure the README samples match real
   output."

### Helpful AI suggestions

- **Turning the rubric into a concrete plan** with a component-per-file layout
  (`guardrails.py`, `retrieval.py`, `explainer.py`, `pipeline.py`) was the most
  useful contribution — it made the rest of the work mechanical.
- **Surfacing the key design fork instead of guessing it.** The AI explicitly
  asked how the "AI explanation layer" should be built rather than assuming, and
  recommended the hybrid Claude-API-plus-offline-fallback design. This is the
  decision that makes the project both a real AI system and reproducible offline.
- **Keeping the recommender as the source of truth** and having the LLM only
  *explain* (grounded in the recommender's reasons + retrieved guide) was a clean
  way to get an LLM into the system without letting it fabricate rankings.
- **Sharing one `pipeline.py`** between the demo and the evaluator so both
  exercise the identical flow.

### Flawed / adjusted AI suggestions

- **A context-labeling bug in the generated fallback explanation.** The first
  version labeled the genre/mood context with the *song's* mood, but the context
  was retrieved for the *listener's* preferred mood — so a cross-over pick showed
  the wrong label. I caught it by reading the real demo output and fixed the
  label to follow the preferences.
- **An invented README sample.** A draft sample output for the messy-input
  profile listed a song and score the code never actually produces. I re-ran the
  demo and replaced it with the true output. Lesson: verify every "sample" against
  a real run.
- **Initial instinct to hard-reject unknown genres/moods.** We changed this to
  warn-and-continue, because the recommender already handles a non-match as a
  zero score and rejecting would make the system more brittle.

### Implementation decisions I made

- Hybrid explainer with a strict, identical output shape across both backends,
  and a `try/except` so any API failure degrades to the fallback silently.
- `anthropic` is an **optional** import; the project runs without it installed.
- Guardrails normalize profiles with warnings but hard-fail only on an unusable
  catalog.
- Retrieval uses simple heading matching (no embeddings) — appropriate for a
  ~15-section guide and fully offline.

### What I verified manually

- Ran `python run_demo.py`, `python evaluate.py` (28/28 checks pass), and
  `pytest` (33 passed) — all offline, with `anthropic` not installed.
- Confirmed the explainer returns the `fallback` backend with all four fields
  when no key is set, and that a simulated API failure still yields a valid
  fallback.
- Checked that README sample outputs match real runs.

---

## Original project log (Music Recommender Simulation)

Kept for continuity. This covered the required/core version of the original
project; no stretch features were implemented or claimed there.

- Reviewed the starter files and produced a file-by-file plan before editing.
- Expanded `data/songs.csv` from 10 to 20 songs with valid ranges.
- Implemented CSV loading, weighted scoring, ranking, and explanation strings in
  `src/recommender.py`.
- Updated `src/main.py` to run three profiles and print readable top-5 output.
- Drafted and polished the README and model card with real output, limitations,
  evaluation notes, and reflection.
- Verified by running `python -m src.main` and `pytest` (2 passed) and checking
  that reasons matched the actual scoring factors.
