# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder is a rule-based music recommender designed for classroom exploration of how scoring systems work. Given a user's preferred genre, mood, and energy level, it ranks a catalog of 20 songs and returns the top 5 best matches with a plain-English explanation for each.

The system assumes the user can describe their preferences in three simple terms: genre (e.g., "pop" or "lofi"), mood (e.g., "happy" or "chill"), and a numeric energy level between 0.0 (very quiet) and 1.0 (very intense). It is not designed for production use — it is a learning tool to demonstrate how small weight decisions in a scoring function create real-world recommendation behavior.

---

## 3. How the Model Works

Think of the system as a judge at a talent show with three criteria on a scorecard:

1. **Genre match** — If the song's genre matches what the user asked for, it earns 1 point (halved from the original 2 points in the weight-shift experiment). Genre is important, but not everything.

2. **Mood match** — If the song's mood matches what the user wants to feel, it earns 2 points. Mood is the strongest signal in the current weighting.

3. **Energy closeness** — If the song's energy level is very close to what the user wants, it earns up to 2 points (doubled from the original 1 point maximum in the weight-shift experiment). A song with exactly the right energy gets the full 2 points; one that is very far off gets close to 0 or even negative points.

Each song gets a total score from these three criteria. The system then sorts all songs by score from highest to lowest and returns the top 5.

The weight-shift experiment (Step 3) doubled the importance of energy and halved the importance of genre. Before the experiment, a genre match was worth twice as much as a perfect energy score. After the experiment, energy and mood dominate, meaning the system now cares more about how a song "feels" than whether it belongs to the right genre bucket.

---

## 4. Data

The catalog contains **20 songs** spanning 14 distinct genres: pop, lofi, rock, ambient, jazz, hip-hop, classical, metal, r&b, country, folk, blues, electronic, and synthwave. Moods represented include happy, chill, intense, focused, melancholic, relaxed, sad, angry, moody, dreamy, and energetic.

No songs were added or removed from the provided dataset. Several areas of musical taste are missing: there are no Latin, K-pop, reggae, or gospel songs. Within genres, coverage is thin — only one jazz song, one metal song, and one classical song exist in the catalog, meaning users who prefer those genres quickly run out of genre-matched options and must rely on mood and energy for their remaining recommendations.

---

## 5. Strengths

The system works best for users whose preferences align cleanly with the most common genres in the dataset. A "Chill Lofi" user gets excellent results: both lofi songs appear in the top 2, and an ambient song that shares the same mood and energy level naturally fills the third slot. The scoring logic correctly captures that a song can still be a good recommendation even without an exact genre match, as long as the mood and energy feel right.

The energy proximity scoring is mathematically sound — it rewards closeness on a continuous scale rather than treating it as a binary yes/no. This means the ranking within a tier (e.g., among songs that all match mood but not genre) is still meaningful and reflects real musical similarity.

---

## 6. Limitations and Bias

**Over-representation of high-energy songs.** Because energy proximity contributes up to 2.0 points regardless of genre or mood, songs with energy levels near the midpoint (0.5–0.8) appear frequently across many different user profiles. Songs like "Block Party Anthem" and "Storm Runner" regularly appear in the bottom slots of recommendations for users who did not ask for hip-hop or rock, simply because their energy is close enough.

**Mood overrides energy in conflict.** The adversarial test profile (metal genre, sad mood, energy=0.9) revealed a serious flaw: the top recommendation was "Delta Blues Revival," a slow blues song with energy=0.44 — the opposite of what a high-energy metal listener expects. This happened because the mood match (+2.0) outweighed the large energy gap. A real listener who wants angry, high-energy metal would be confused and frustrated by a slow blues recommendation just because it is also "sad."

**Genre under-representation creates a ceiling.** With only one jazz, one metal, and one classical song in the catalog, users who prefer those genres reach the top result quickly and then receive mood-and-energy-based suggestions from completely different genres. The system cannot provide meaningful diversity for niche genre listeners.

**No consideration of tempo, danceability, or valence.** The dataset includes richly detailed attributes — tempo in BPM, danceability, and musical valence (positivity) — that the scoring function ignores entirely. A user who wants to dance would not necessarily get danceable songs just by specifying "pop" and "happy."

---

## 7. Evaluation

Five user profiles were tested:

- **High-Energy Pop** (genre=pop, mood=happy, energy=0.9): Results felt accurate. "Sunrise City" correctly ranked first with a genre+mood+energy triple match. Surprisingly, "Rooftop Lights" (indie pop) ranked second despite not matching the genre exactly — its happy mood and high energy were enough. This confirmed that mood weight is doing meaningful work.

- **Chill Lofi** (genre=lofi, mood=chill, energy=0.3): Excellent results. The top 3 recommendations all had energy below 0.45 and calm moods, and the ambient song "Spacewalk Thoughts" naturally fit even without a genre label of "lofi."

- **Deep Intense Rock** (genre=rock, mood=intense, energy=0.95): Mostly good, but "Gym Hero" (a pop song) appeared second place because it shares the "intense" mood and has close energy. A real rock listener might not want a pop track regardless of mood similarity.

- **Adversarial — Sad Rage** (metal genre, sad mood, energy=0.9): This was the biggest surprise. The system recommended a slow Delta Blues song as the top result because the "sad" mood match outweighed the large energy gap. This profile was designed to expose contradictions and it succeeded — the system cannot balance conflicting signals intelligently.

- **Edge Case — Jazz Minimalist** (genre=jazz, mood=relaxed, energy=0.5): The single jazz song in the dataset ranked first by a large margin. After that, the recommendations dropped to general energy-proximity matches. This shows the catalog is too small for niche genres.

**Weight-shift experiment:** Doubling energy and halving genre caused "Rooftop Lights" (indie pop) to stay in second place for the pop profile because its energy was close. For the rock profile, the ordering of lower-ranked songs shifted, but the top recommendation stayed the same. The change made recommendations feel slightly more varied across genres but reduced the "exactness" of genre-specific results.

---

## 8. Future Work

The most impactful improvement would be adding **tempo and danceability as scoring criteria**, since those are the attributes most directly tied to what a listener physically wants from music at a given moment. A gym user and a study user might both want "high energy," but they want very different tempos.

A **conflict resolution mechanism** would address the adversarial bias: when a user's mood and energy preferences point in opposite directions (high energy + sad mood), the system should detect the conflict and weight the preference that is stronger or ask the user which matters more.

**Expanding the dataset** from 20 to at least 200 songs — especially in underrepresented genres like jazz, classical, and metal — would allow the system to provide meaningful diversity within each genre rather than defaulting to cross-genre energy matches.

Finally, a **diversity penalty** would prevent the same artist or genre from dominating all five slots. Currently, a lofi user could theoretically receive a top 5 list that includes all three lofi songs plus two ambient tracks with zero variety.

---

## 9. Personal Reflection

Building this recommender taught me how much the choice of weights shapes the personality of a recommendation system. Halving the genre weight and doubling the energy weight felt like a small technical change, but it noticeably shifted which songs rose to the top — suddenly the system cared more about vibe than category. The adversarial test was the most eye-opening moment: a user who wants loud, angry metal gets recommended a quiet blues song, and the math is completely "correct" from the system's perspective. That gap between what the math says and what a human would expect is exactly where real recommender systems spend enormous engineering effort to close. It made me think differently about Spotify's "Daily Mix" — there are likely hundreds of weight-tuning decisions behind even a simple playlist, each one shaping what kind of listener the algorithm is optimized to serve.
