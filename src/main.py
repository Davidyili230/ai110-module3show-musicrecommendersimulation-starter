"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from recommender import load_songs, recommend_songs
except ModuleNotFoundError:
    from src.recommender import load_songs, recommend_songs


# ── User profiles for stress-testing ──────────────────────────────────────────

PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.9,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.3,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.95,
    },
    # Adversarial: high energy but sad mood — conflicting preferences
    "Adversarial - Sad Rage (energy=0.9, mood=sad)": {
        "genre": "metal",
        "mood": "sad",
        "energy": 0.9,
    },
    # Edge case: rare genre with only one match in the dataset
    "Edge Case - Jazz Minimalist (rare genre)": {
        "genre": "jazz",
        "mood": "relaxed",
        "energy": 0.5,
    },
}


def run_profile(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    print("=" * 60)
    print(f"Profile: {name}")
    print(f"Preferences: {user_prefs}")
    print("=" * 60)

    recommendations = recommend_songs(user_prefs, songs, k=k)

    print(f"\nTop {k} recommendations:\n")
    for i, rec in enumerate(recommendations, 1):
        song, score, explanation = rec
        print(f"  {i}. {song['title']} by {song['artist']}")
        print(f"     Genre: {song['genre']} | Mood: {song['mood']} | Energy: {song['energy']}")
        print(f"     Score: {score:.2f}")
        print(f"     Because: {explanation}")
        print()
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    for name, prefs in PROFILES.items():
        run_profile(name, prefs, songs, k=5)


if __name__ == "__main__":
    main()
