# 🎵 VibeMatch AI — Hybrid Music Recommendation Advisor

## Project Summary

VibeMatch AI is an **applied AI system** built on top of my original rule-based
Music Recommender Simulation. The original project scored a 20-song catalog
against a listener's stated taste (genre, mood, energy, tempo, acoustic
preference) and printed a ranked top list. VibeMatch AI keeps that transparent
rule-based engine as the decision-maker and wraps it with four new layers that
make it a complete, defensible AI system:

1. **Rule-based recommender** (preserved) — the deterministic, explainable
   scoring engine that decides *what* to recommend.
2. **Input validation & guardrails** — validates and normalizes listener
   profiles and hard-checks the catalog before anything is scored.
3. **Retrieval** — pulls genre/mood context from a local music guide document so
   explanations are grounded in real background, not invented facts.
4. **Hybrid AI explanation layer** — explains *why* each song was picked in a
   structured, user-friendly way, using the Claude API when available and a
   deterministic offline fallback otherwise.

The rule-based recommender remains the single source of truth for ranking. The
AI layer only *explains* decisions the rules already made — it never re-ranks.

---

## Architecture

```
User profile ─▶ Guardrails ─▶ Rule-based Recommender ─▶ Retrieval ─▶ AI Explanation ─▶ Output
   (raw)         validate/       weighted scoring          genre/mood      Claude API
                 normalize        + ranking                context          or fallback
```

The full diagram lives in [diagrams/architecture.mmd](diagrams/architecture.mmd)
(Mermaid). Component code:

| Layer | File |
|-------|------|
| Rule-based recommender | [src/recommender.py](src/recommender.py) |
| Guardrails | [src/guardrails.py](src/guardrails.py) |
| Retrieval | [src/retrieval.py](src/retrieval.py) |
| AI explanation (hybrid) | [src/explainer.py](src/explainer.py) |
| End-to-end pipeline | [src/pipeline.py](src/pipeline.py) |
| Music guide (retrieval corpus) | [data/music_guide.md](data/music_guide.md) |
| Song catalog | [data/songs.csv](data/songs.csv) |

### How the hybrid explanation layer works

`explain(...)` returns the **same structured shape** regardless of backend, so
the demo, the evaluator, and the tests are all backend-agnostic:

```
{ summary, why_it_fits, genre_mood_context, caveat, backend }
```

- **Claude API backend** — used only when `ANTHROPIC_API_KEY` is set *and* the
  `anthropic` package is installed. Calls model `claude-haiku-4-5` with a prompt
  built from the recommender's own reasons plus the retrieved guide context, and
  requests a structured JSON response.
- **Deterministic fallback** — used when there is no key, the package is not
  installed, or the API call fails for any reason. Assembles the same four
  fields directly from the scoring reasons and retrieved context.

This means `run_demo.py`, `evaluate.py`, and `pytest` **all run fully offline**;
the live model is a genuine enhancement, not a dependency.

### The scoring rule (unchanged from the original)

Each song earns points from five factors that are summed:

| Factor              | Rule                                                                      | Max points |
| ------------------- | ------------------------------------------------------------------------- | ---------- |
| Genre match         | Exact match with favorite genre                                           | +2.0       |
| Mood match          | Exact match with favorite mood                                            | +1.5       |
| Energy similarity   | `1 - abs(song_energy - target_energy)`                                    | +1.0       |
| Tempo similarity    | Closer tempo to the user's target BPM earns more points                   | +1.0       |
| Acoustic preference | Acousticness if the user likes acoustic music; otherwise non-acousticness | +1.0       |

Weights live as named constants at the top of `src/recommender.py`.

---

## Getting Started

### Setup

1. (Optional) Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   `pytest` is the only required dependency. `anthropic` is optional — install
   it only if you want live Claude-generated explanations.

### Commands

```bash
python run_demo.py     # full end-to-end workflow for 3 profiles + 1 messy profile
python evaluate.py     # reliability harness: PASS/FAIL checks + summary
pytest                 # unit tests for every layer
```

### Enabling the Claude API backend (optional)

```bash
export ANTHROPIC_API_KEY=sk-ant-...    # Mac/Linux
$env:ANTHROPIC_API_KEY = "sk-ant-..."  # Windows PowerShell
pip install anthropic
python run_demo.py
```

Without a key, the demo header prints `explanation backend: offline fallback`
and everything still works.

---

## Sample Outputs

### 1. `python run_demo.py` — a well-formed profile (offline fallback)

```
======================================================================
User profile: Lofi Study Session
  raw input: {'genre': 'lofi', 'mood': 'focused', 'energy': 0.4, 'target_tempo': 78, 'likes_acoustic': True}
----------------------------------------------------------------------
1. Focus Flow - LoRoom (score: 6.25)
   Summary:  Focus Flow by LoRoom scored 6.25 for your taste.
   Why:      This song matches your favorite genre (lofi); fits the mood you want (focused); energy 0.40 is close to your target 0.40; tempo 80 BPM is close to your target 78 BPM; has the acoustic sound you enjoy.
   Context:  About lofi music: Lofi (low-fidelity) is relaxed, beat-driven background music with a warm, hazy sound. Energy and tempo are low (roughly 70-90 BPM) and it is often instrumental. It is popular for studying, focusing, and winding down. About a focused mood: Focused music is steady and low-distraction, designed to help concentration. It usually has a repetitive, gentle beat and is common in lofi and ambient music for studying or working.
   Caveat:   This pick comes from a small fixed catalog scored by simple rules, so it reflects your stated preferences only - not your listening history or how the song actually sounds to you.
```

### 2. `python run_demo.py` — the guardrail demo profile

The last demo profile is deliberately broken (unknown mood, non-numeric energy,
negative tempo) to show validation firing before any scoring happens:

```
======================================================================
User profile: Messy Input (guardrail demo)
  raw input: {'genre': 'POP', 'mood': 'party-vibes', 'energy': 'loud', 'target_tempo': -20, 'likes_acoustic': 'yes'}
----------------------------------------------------------------------
Guardrails adjusted the input:
  ! Mood 'party-vibes' is not in the known catalog; it will simply not match any song.
  ! Target energy 'loud' is not a number; defaulted to 0.5.
  ! Target tempo -20.0 is not positive; defaulted to 120.0.
  ! likes_acoustic 'yes' was not a boolean; interpreted as True.
  -> using: {'genre': 'pop', 'mood': 'party-vibes', 'energy': 0.5, 'target_tempo': 120.0, 'likes_acoustic': True}
----------------------------------------------------------------------
1. Sunrise City - Neon Echo (score: 3.83)
   Summary:  Sunrise City by Neon Echo scored 3.83 for your taste.
   Why:      This song matches your favorite genre (pop); energy 0.82 is close to your target 0.50; tempo 118 BPM is close to your target 120 BPM.
   Context:  About pop music: Pop is mainstream, hook-driven music built around catchy melodies and clear vocals. It usually sits at medium-to-high energy with danceable tempos around 100-130 BPM. Good for parties, driving, and easy everyday listening.
   Caveat:   This pick comes from a small fixed catalog scored by simple rules, so it reflects your stated preferences only - not your listening history or how the song actually sounds to you.
```

### 3. `python evaluate.py` — reliability harness

```
VibeMatch AI - reliability evaluation

  [PASS] [Pop Party] returns recommendations  (3 returned)
  [PASS] [Pop Party] top pick genre == pop  (got 'pop')
  [PASS] [Pop Party] top pick mood == happy  (got 'happy')
  [PASS] [Pop Party] scores are sorted descending
  [PASS] [Pop Party] explanation has all fields, non-empty  (backend=fallback)
  ...
  [PASS] [guardrails] messy profile produces warnings  (4 warnings)
  [PASS] [guardrails] bad energy clamped into 0-1  (energy=0.5)
  [PASS] [guardrails] empty catalog raises GuardrailError
  [PASS] [retrieval] known genre returns context
  [PASS] [retrieval] unknown terms return None safely

--------------------------------------------------
Reliability: 28/28 checks passed (100%).
Result: RELIABLE - all checks passed.
```

---

## Testing

```bash
pytest
```

Covers the recommender, guardrails, retrieval, the explainer (including the
offline-fallback path and API-failure handling), and the end-to-end pipeline:

```
33 passed
```

---

## Limitations and Risks

- Works on a tiny **20-song catalog**, so "top 3" is a large fraction of what's
  available.
- Requires **exact** genre/mood strings; "indie pop" is treated as unrelated to
  "pop", and an unknown value simply scores zero on that factor (guardrails warn
  about it but don't correct the meaning).
- Does not use listening history, likes, skips, lyrics, or audio itself.
- The LLM backend can, in principle, phrase things loosely; explanations are
  **grounded** in the recommender's reasons and the local guide to limit this,
  and the deterministic fallback removes the model from the loop entirely.

See [model_card.md](model_card.md) for misuse risks, reliability-testing
surprises, and the AI-collaboration reflection.

---

## Documentation

- [model_card.md](model_card.md) — intended use, limitations, misuse risks,
  evaluation, reliability surprises, AI-collaboration reflection.
- [ai_interactions.md](ai_interactions.md) — log of AI prompts, useful
  suggestions, flawed suggestions, and implementation decisions.
