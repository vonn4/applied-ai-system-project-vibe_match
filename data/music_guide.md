# VibeMatch Music Guide

This is a small reference document that describes the genres and moods used by
the VibeMatch catalog. The retrieval component (`src/retrieval.py`) reads this
file and pulls the matching genre and mood sections so the explanation layer can
add real context to each recommendation instead of inventing facts.

Each section below is a plain-language description. Keep one heading per genre
and per mood so the retriever can find them by name.

---

## Genres

### pop
Pop is mainstream, hook-driven music built around catchy melodies and clear
vocals. It usually sits at medium-to-high energy with danceable tempos around
100-130 BPM. Good for parties, driving, and easy everyday listening.

### indie pop
Indie pop keeps pop's catchy melodies but has a more independent, lo-fi or
handmade feel. Energy is moderate and the mood is often bright and upbeat. It
appeals to listeners who want something poppy but a little less polished.

### lofi
Lofi (low-fidelity) is relaxed, beat-driven background music with a warm, hazy
sound. Energy and tempo are low (roughly 70-90 BPM) and it is often instrumental.
It is popular for studying, focusing, and winding down.

### rock
Rock is guitar-driven, high-energy music with strong drums. Tempos are often
fast (130-160 BPM) and the mood ranges from intense to defiant. It suits
workouts and high-energy moments.

### ambient
Ambient is atmospheric, slow, and often beatless music meant to create a mood
rather than grab attention. Energy is very low and tempos are slow. It works for
relaxation, sleep, and deep focus.

### jazz
Jazz is expressive music built on improvisation, swing, and rich harmony. It
spans relaxed lounge styles to energetic bebop, but the catalog leans toward
mellow, relaxed jazz good for coffee shops and calm evenings.

### synthwave
Synthwave is retro, synthesizer-driven electronic music inspired by 1980s film
and game soundtracks. It has a moody, neon feel with steady mid-tempo beats.
Good for night drives and focused work.

### folk
Folk is acoustic, story-driven music centered on guitar and vocals. Energy is
low-to-moderate and the mood is usually relaxed and warm. It suits quiet,
reflective listening.

### edm
EDM (electronic dance music) is high-energy, production-heavy music built for
dancing. Tempos are fast (around 120-130 BPM) and the mood is euphoric and
upbeat. Good for parties and festivals.

---

## Moods

### happy
Happy music is bright, upbeat, and positive. It tends to have higher energy and
major-key melodies that lift the listener's mood. Common in pop, indie pop, and
edm.

### chill
Chill music is calm and easygoing without being sleepy. Energy is low-to-medium
and the feel is smooth and unhurried. Common in lofi, ambient, and mellow jazz.

### intense
Intense music is driving, powerful, and high-energy. It pushes the listener
forward and is common in rock and workout playlists.

### relaxed
Relaxed music is soft, slow, and soothing. It lowers tension and is common in
folk, jazz, and ambient styles for quiet moments.

### focused
Focused music is steady and low-distraction, designed to help concentration.
It usually has a repetitive, gentle beat and is common in lofi and ambient
music for studying or working.

### moody
Moody music is atmospheric and emotionally shaded, often darker or more
introspective. It has a mid-tempo, brooding feel common in synthwave and some
alternative styles.
