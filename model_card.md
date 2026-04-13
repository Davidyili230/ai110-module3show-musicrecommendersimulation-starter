# Model Card: VibeFinder 1.0

---

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder takes a user's preferred genre, mood, and energy level and returns the top 5 best-matching songs from a catalog of 20 tracks. It also explains in plain language why each song was recommended.

The goal is not to predict what a user will like with certainty. The goal is to demonstrate how a simple scoring function can produce recommendation-like behavior — and what happens when the weights are changed.

---

## 3. Data Used

The dataset contains **20 songs** stored in `data/songs.csv`.

Each song has these features: title, artist, genre, mood, energy (0.0–1.0), tempo in BPM, valence, danceability, and acousticness.

**Genres covered:** pop, lofi, rock, ambient, jazz, hip-hop, classical, metal, r&b, country, folk, blues, electronic, synthwave — 14 total.

**Moods covered:** happy, chill, intense, focused, melancholic, relaxed, sad, angry, moody, dreamy, energetic.

**Limits:** Some genres have only one song (jazz, metal, classical). There are no Latin, K-pop, reggae, or gospel tracks. Only three features — genre, mood, and energy — are actually used in scoring, even though tempo, danceability, and valence are in the dataset.

---

## 4. Algorithm Summary

Scoring works like a judge with a three-item scorecard. Every song gets evaluated against the user's preferences:

1. **Genre match** — If the song's genre matches what the user wants, it gets +1.0 point.
2. **Mood match** — If the song's mood matches, it gets +2.0 points. This is the strongest signal.
3. **Energy closeness** — The closer the song's energy is to the user's target, the more points it earns — up to +2.0. A perfect match gets +2.0; a song very far off can even score near zero or negative.
4. **Acoustic bonus** (OOP version only) — If the user likes acoustic songs and the song has high acousticness, it gets +1.0.

All songs get scored, then sorted from highest to lowest. The top 5 are returned.

**Weight-shift experiment:** Genre was originally worth +2.0. Energy was originally worth up to +1.0. After the experiment, genre dropped to +1.0 and energy rose to +2.0. This made the system care more about "vibe" than category.

---

## 5. Observed Behavior / Biases

**Mood overrides energy in conflicts.** When a user asked for "sad" mood and energy=0.9 (a metal listener), the top result was a slow blues song with energy=0.44. The mood match (+2.0) outweighed the large energy gap. A real listener who wants loud, heavy metal would be confused and frustrated.

**Over-representation near middle energy.** Songs with energy in the 0.5–0.8 range appear in many different users' results, because their energy penalty is always small. They show up in recommendations even when their genre and mood don't match.

**Niche genre users get weaker results.** With only one jazz, one metal, and one classical song in the catalog, users who prefer those genres quickly run out of genre-matched options. Their remaining recommendations come from unrelated genres matched only on energy.

**Unused features.** Tempo, danceability, and valence are never used in scoring. A user who wants to dance might not get danceable songs just because those attributes are ignored.

---

## 6. Evaluation Process

Five user profiles were tested manually by running the recommender and inspecting the ranked output:

- **High-Energy Pop** (genre=pop, mood=happy, energy=0.9): Results were accurate. "Sunrise City" ranked first with a triple match. "Rooftop Lights" (indie pop) ranked second due to mood and energy closeness — confirming that mood weight is meaningful.

- **Chill Lofi** (genre=lofi, mood=chill, energy=0.3): Excellent results. Top 3 songs all had low energy and calm moods. An ambient song naturally fit even without a "lofi" genre label.

- **Deep Intense Rock** (genre=rock, mood=intense, energy=0.95): Mostly correct. A pop song ("Gym Hero") appeared in second place because it shares the "intense" mood and has close energy. A rock listener might not want a pop track despite the vibe similarity.

- **Adversarial — Sad Rage** (genre=metal, mood=sad, energy=0.9): This profile was designed to expose contradictions. It succeeded — the top result was a slow Delta Blues song. This is the system's biggest failure case.

- **Edge Case — Jazz Minimalist** (genre=jazz, mood=relaxed, energy=0.5): The single jazz song ranked first by a wide margin. Everything after it was a fallback based on energy proximity only.

The weight-shift experiment was also evaluated by comparing rank order before and after. Doubling energy and halving genre caused small shuffles in mid-list rankings but did not change the top-1 result for most profiles.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
- A classroom tool to explore how scoring functions create recommendation behavior.
- A testbed for experimenting with feature weights and observing how small changes shift results.
- A clear, readable example of a rule-based system before learning about machine learning alternatives.

**Not intended for:**
- Real music discovery or deployment in a product.
- Users with niche genre preferences who expect diverse, high-quality matches.
- Any context where the recommendations need to be accurate, fair, or personalized beyond three simple attributes.
- Replacing a real recommender system that uses listening history, collaborative filtering, or neural embeddings.

---

## 8. Ideas for Improvement

1. **Add tempo and danceability to the score.** These are already in the dataset but ignored. A gym user and a study user both want "high energy," but they need very different tempos. Including these would separate those audiences correctly.

2. **Add a conflict resolution mechanism.** When a user's mood and energy preferences point in opposite directions (sad mood + high energy), the system should detect the tension and apply a penalty, or ask the user which matters more, rather than blindly rewarding whichever has the higher weight.

3. **Expand the catalog.** Going from 20 to 200+ songs — especially in underrepresented genres like jazz, classical, and metal — would give every user enough genre-matched options for a full top-5 list without falling back on cross-genre energy matches.

---

## 9. Personal Reflection

**Biggest learning moment:** The adversarial test profile was the most surprising part of building this. A user who says "I want sad, high-energy metal" gets recommended a quiet Delta Blues song — and the math is completely correct from the system's point of view. Mood matched, so it won. That gap between what the algorithm "thinks" and what a human would expect is exactly where real recommender systems spend enormous engineering effort. It made me think differently about why Spotify's "Daily Mix" needs hundreds of weight-tuning decisions, not just three.

**Using AI tools:** AI tools helped me set up the initial project structure, write boilerplate code for the `Song` and `UserProfile` dataclasses, and draft the scoring logic. Where I had to double-check was in the weight-shift experiment — the AI's first version didn't update both the functional `score_song` and the OOP `Recommender._score` method consistently, so I had to verify the changes were applied everywhere. It's a good reminder that AI-generated code requires the same review as any other code.

**What surprised me about simple algorithms:** Even with only three rules, the output *feels* like a recommendation. When the Chill Lofi profile surfaces "Library Rain" and "Spacewalk Thoughts" — two completely different songs from different artists that both evoke quietness — it seems like the system "understood" something. It didn't. It just did math. The illusion of intelligence comes entirely from which numbers were chosen as weights. That was a genuinely surprising thing to realize.

**What I'd try next:** I'd add collaborative filtering — the idea that users who agreed on past songs will likely agree on future ones — to layer on top of the content-based score. Even a simple version (find users with similar genre/mood preferences, surface their top-rated songs) would make the system feel much more alive than a fixed formula.
