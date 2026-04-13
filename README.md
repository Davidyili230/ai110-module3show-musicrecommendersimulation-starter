# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This version uses a content-based scoring system that compares a fixed user taste profile against every song in `data/songs.csv`. Each song receives a numeric score based on genre match, mood match, energy proximity, and acoustic preference. The top-k highest-scoring songs are returned as recommendations. Every score is fully explainable — you can point to exactly which features drove a song up or down the ranking.

---

## How The System Works

Real-world recommendation systems like Spotify or YouTube learn a dense mathematical model of user taste from billions of listening events, then use techniques like collaborative filtering (finding users who behave like you) and content-based filtering (finding items that share attributes with things you liked) to rank a massive catalog in milliseconds. They also factor in recency, session context, and business goals. This simulation prioritizes the content-based side: it compares explicit user taste preferences directly against song attributes to produce an interpretable score. The goal is transparency — every recommendation can be explained by pointing to exactly which features matched — rather than the black-box accuracy of a large production model.

### Data Flow

```mermaid
flowchart TD
    A([User Preferences\ngenre · mood · energy · likes_acoustic]) --> B

    B[/Load songs.csv\n20 songs/] --> C

    C{For each song\nin catalog}

    C --> D[Genre match?\n+2.0 pts if yes]
    C --> E[Mood match?\n+1.0 pt if yes]
    C --> F[Energy similarity\n+1.5 × (1 − |song.energy − target|)]
    C --> G[Acoustic similarity\n+1.0 × (1 − |song.acousticness − pref|)]

    D --> H([Song Score])
    E --> H
    F --> H
    G --> H

    H --> I[Rank all songs\nby score descending]
    I --> J([Top-K Recommendations\nwith explanations])
```

### Algorithm Recipe

Weights are applied as follows when scoring a single song against the user profile:

| Feature | Points | Condition |
|---|---|---|
| Genre match | +2.0 | `song.genre == user.favorite_genre` |
| Mood match | +1.0 | `song.mood == user.favorite_mood` |
| Energy proximity | +1.5 × (1 − \|song.energy − user.target_energy\|) | Continuous 0–1.5 |
| Acoustic preference | +1.0 × (1 − \|song.acousticness − pref\|) | Continuous 0–1.0 |

**Max possible score: 5.5** (genre + mood + perfect energy + perfect acoustic match)

Genre is weighted highest (2.0) because genre is the broadest filter — a jazz fan rarely wants metal regardless of mood. Mood is second (1.0) because within a genre, mood captures the session context ("I want chill lofi right now"). Energy and acousticness are continuous so they reward partial matches rather than all-or-nothing alignment.

### Sample User Profile

```python
user = UserProfile(
    favorite_genre="lofi",
    favorite_mood="chill",
    target_energy=0.38,
    likes_acoustic=True,
)
```

This profile targets low-energy, acoustic, chill lofi tracks. It will clearly separate "Library Rain" (score ≈ 5.0) from "Storm Runner" (score ≈ 0.6), demonstrating the system can distinguish "intense rock" from "chill lofi."

**Critique:** The binary `likes_acoustic` flag loses nuance — a user who likes *slightly* acoustic tracks will score the same as one who only listens to purely acoustic recordings. A float `target_acousticness` (as used in scoring) would be more expressive. The current profile may also under-serve users whose preferences straddle two genres (e.g., indie pop and pop) since genre is an exact match.

### Expected Bias

This system may **over-prioritize genre**, potentially burying a high-energy hip-hop track that perfectly matches the user's mood and energy when the user's favorite genre is set to lofi. Genre's 2.0 weight means even a poor non-matching song with a perfect mood+energy score (2.5 pts) can lose to a genre-match song with low mood/energy alignment (2.0 + partial = ~2.5). Tuning the genre weight downward (e.g., 1.5) would reduce this effect.

### Song Features Used

Each `Song` object carries these attributes that feed into scoring:

- **genre** — categorical label (pop, rock, lofi, jazz, etc.) used for exact-match preference alignment
- **mood** — categorical label (happy, chill, intense, etc.) matched against the user's preferred mood
- **energy** — float 0–1, how driving or subdued the track feels; scored by closeness to the user's target
- **acousticness** — float 0–1, how acoustic vs. electronic the track is; matched against the user's acoustic preference
- **tempo_bpm** — beats per minute; available for future weighting experiments
- **valence** — float 0–1, musical positivity; available for future weighting experiments
- **danceability** — float 0–1; available for future weighting experiments

### UserProfile Features Used

Each `UserProfile` stores four preference dimensions:

- **favorite_genre** — the genre the user wants prioritized
- **favorite_mood** — the emotional tone the user is seeking right now
- **target_energy** — a float 0–1 representing the user's desired energy level
- **likes_acoustic** — boolean flag indicating whether the user prefers acoustic over electronic sounds

### How a Score Is Computed

```
score(user, song) =
    genre_weight   × (1 if song.genre == user.favorite_genre else 0)
  + mood_weight    × (1 if song.mood  == user.favorite_mood  else 0)
  + energy_weight  × (1 - |song.energy - user.target_energy|)
  + acoustic_weight× (1 - |song.acousticness - (1.0 if user.likes_acoustic else 0.0)|)
```

Songs are then ranked by score descending and the top-k are returned.

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

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

- **Tiny catalog:** 20 songs means ties are common and results aren't meaningful at k > 5.
- **Genre over-weighting:** A 2.0 genre bonus can overshadow mood + energy signals combined (see Algorithm Recipe above).
- **No listening history:** Every session starts cold — the system has no memory of past plays or skips.
- **Binary acoustic flag:** `likes_acoustic` is boolean in the profile but continuous in the song data; this mismatch loses granularity.
- **No cross-feature interactions:** The score treats energy and mood as independent; in reality a "chill + high energy" combination is less common and shouldn't score the same as "chill + low energy."

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

