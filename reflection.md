# Reflection: Comparing User Profile Outputs

This file compares the recommendation results across the five test profiles to explain what changed between them and why it makes intuitive sense.

---

## High-Energy Pop vs. Chill Lofi

These two profiles are near-opposites in energy and genre. The High-Energy Pop profile (energy=0.9) surfaced fast, danceable pop songs — "Sunrise City" and "Gym Hero" both have energy above 0.8 and upbeat moods. The Chill Lofi profile (energy=0.3) surfaced slow, ambient tracks — "Library Rain" and "Spacewalk Thoughts" both sit below energy=0.35.

What is interesting is that the scores were actually higher for the Chill Lofi results. "Library Rain" scored 4.90 vs. "Sunrise City" at 4.84. This is not because lofi is a better genre — it is because the lofi songs happened to sit very close to the target energy of 0.3, while the pop songs had a slightly larger gap from 0.9. The math rewards closeness regardless of the direction.

**Why it makes sense:** A chill listener and a hype listener want fundamentally different feelings from music. The system correctly separates these two audiences into completely non-overlapping top-5 lists. No song appeared in both results.

---

## High-Energy Pop vs. Deep Intense Rock

Both profiles want high energy (0.9 and 0.95), but they differ in genre and mood. The pop profile wants "happy," the rock profile wants "intense." This one difference caused "Rooftop Lights" — a happy indie-pop song — to rank 2nd for the pop user but disappear entirely from the rock user's list. Meanwhile, "Gym Hero" (pop, intense, energy=0.93) appeared 3rd for the pop user because of genre match, but rose to 2nd for the rock user because its "intense" mood matched.

**Why it makes sense:** The same song can serve two very different audiences depending on which attribute the scoring function values. "Gym Hero" is a pop song but sounds intense — so the rock listener's mood preference pulls it up even though the genre does not match. This is actually realistic: genre labels are rough, and vibes cross boundaries.

---

## Deep Intense Rock vs. Adversarial — Sad Rage (metal, sad, energy=0.9)

This comparison reveals the most significant system weakness. The rock profile and the adversarial profile both want high energy (0.95 and 0.9), but the adversarial profile asks for "sad" mood instead of "intense." The result was dramatic: the adversarial profile's top recommendation was "Delta Blues Revival," a slow blues song with energy=0.44 — 0.46 points away from the desired 0.9 energy.

"Delta Blues Revival" won because its "sad" mood gave it +2.0 points, and the energy penalty only subtracted about 0.92 points (energy gap of 0.46 × 2.0). That left it at 3.08, which beat "Iron Curtain" (the closest genre match at 2.86) and every high-energy song.

**Why it makes sense (and why it does not):** In isolation, the math is correct — a sad-mood match is worth more than an energy match by design. But from a human perspective, someone who says "I want sad, high-energy metal" probably means something like Linkin Park or post-hardcore, not acoustic Delta Blues. The system cannot understand that "sad" can coexist with high energy in a genre like metal. It treats mood and energy as independent, which causes it to collapse toward whichever dimension has the highest weight — and in this case, mood wins at the expense of energy and genre.

---

## Chill Lofi vs. Edge Case — Jazz Minimalist

Both profiles want low energy and calm moods, but in different genres. The chill lofi profile had multiple songs to choose from — three lofi songs exist in the dataset. The jazz minimalist profile had only one jazz song: "Coffee Shop Stories." After that single match, the system had to fall back entirely on mood and energy similarity, surfacing "Golden Hour" (r&b, relaxed) as the second-best option.

**Why it makes sense:** This is a dataset coverage problem, not a logic problem. If you are a very specific listener — jazz only — the system runs out of strong matches quickly. The chill lofi user gets a richer, more satisfying list because the dataset happens to include their genre more often. This is the real-world "filter bubble" risk: users who prefer popular or well-represented genres get better service from the system than users with niche tastes.

---

## Key Takeaway

Small changes in user preferences — one mood word, a 0.05 energy shift, or a genre with only one song in the dataset — produce surprisingly large changes in recommendations. The system is not exploring musical space; it is following a fixed formula. Understanding the weights behind the formula is the only way to predict (and trust) what it will recommend.
