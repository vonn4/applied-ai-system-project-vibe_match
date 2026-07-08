# AI Interactions Log

## Scope

This file documents how I used Claude during the required/core version of the Music Recommender Simulation project. I did not implement or claim any stretch features.

## AI Tool Used

Claude in VS Code.

## Main Tasks I Asked AI To Help With

* Review the starter project files and propose a file-by-file implementation plan before making changes.
* Expand `data/songs.csv` from 10 songs to 20 songs while keeping the existing headers and valid numeric ranges.
* Implement CSV loading, weighted scoring, recommendation ranking, and explanation strings in `src/recommender.py`.
* Update `src/main.py` so it runs three distinct user profiles and prints readable top-5 recommendations.
* Help draft and polish `README.md` and `model_card.md` with real output, limitations, evaluation notes, and reflection.

## Example Prompts Used

Brief summaries rather than huge pasted prompts:

1. "Inspect the current project files and give me a file-by-file implementation plan before editing anything."
2. "Implement the approved plan using a weighted scoring recipe with genre, mood, energy, tempo, and acoustic preference."
3. "Update the README and model card with real terminal output, profile comparisons, limitations, and a reflection."
4. "Do a final audit only and check for missing placeholders, inaccurate claims, or stretch features being claimed."

## What AI Generated or Changed

* Added 10 new songs to the catalog for 20 total songs.
* Implemented `load_songs`, `score_song`, and `recommend_songs`.
* Kept the existing `Song`, `UserProfile`, and `Recommender` classes working for the tests.
* Added three demo profiles: Pop Party, Lofi Study Session, and Rock Workout.
* Helped write the README sections explaining how the system works, the scoring recipe, sample output, experiments, limitations, and reflection.
* Helped fill out the model card in plain language.

## What I Verified Manually

* I ran `python -m src.main` and confirmed all three profiles printed top-5 recommendations with scores and reasons.
* I ran `pytest` and confirmed the tests passed.
* I checked that the reasons matched the actual scoring factors instead of being generic.
* I checked that the documentation did not claim machine learning or stretch features.
* I reviewed the model card to make sure the limitations and bias section was honest.

## Helpful AI Suggestions

Claude was helpful for turning the rubric into a file-by-file plan. It also helped keep the scoring logic simple and explainable by using a weighted formula instead of a more complicated algorithm. The suggestion to return both a score and reasons made the output easier to understand and helped match the rubric.

## Suggestions I Double-Checked or Adjusted

I asked Claude to wait for approval before editing so changes would not be made arbitrarily. I also adjusted the scoring plan to include tempo because `tempo_bpm` was already in the dataset and made the recommender easier to explain. I avoided claiming stretch features because the final project only implements the required/core functionality.

## Final Verification

Commands run locally:

```powershell
python -m src.main
pytest
git status
```

Results:

* `python -m src.main` ran successfully.
* `pytest` passed with 2 tests.
* `git status` was clean after the final commits and push.

## Stretch Features

No stretch features were implemented or claimed.
