"""
Command line runner for the Music Recommender Simulation.

Challenge 2: Switch between scoring modes via SCORING_MODE constant.
Challenge 3: Enable diversity penalty via DIVERSITY flag.
Challenge 4: Recommendations rendered as a formatted table using tabulate.
"""

try:
    from recommender import load_songs, recommend_songs, SCORING_MODES
except ModuleNotFoundError:
    from src.recommender import load_songs, recommend_songs, SCORING_MODES

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


# ── Challenge 2: Scoring Mode Selection ───────────────────────────────────────
# Switch between "genre-first", "mood-first", or "energy-focused"
SCORING_MODE = "mood-first"

# ── Challenge 3: Diversity Flag ────────────────────────────────────────────────
# Set True to apply artist/genre diversity penalty during recommendation
DIVERSITY = True


# ── User profiles for stress-testing ──────────────────────────────────────────

PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.9,
        "preferred_decade": "2020s",
        "preferred_mood_tags": ["euphoric", "energizing"],
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.3,
        "likes_acoustic": True,
        "preferred_mood_tags": ["serene", "nostalgic"],
        "likes_instrumental": True,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.95,
        "preferred_mood_tags": ["aggressive"],
    },
    # Adversarial: high energy but sad mood — conflicting preferences
    "Adversarial - Sad Rage (energy=0.9, mood=sad)": {
        "genre": "metal",
        "mood": "sad",
        "energy": 0.9,
        "preferred_mood_tags": ["aggressive", "brooding"],
    },
    # Edge case: rare genre with only one match in the dataset
    "Edge Case - Jazz Minimalist (rare genre)": {
        "genre": "jazz",
        "mood": "relaxed",
        "energy": 0.5,
        "likes_acoustic": True,
        "preferred_decade": "2010s",
        "preferred_mood_tags": ["nostalgic", "serene"],
        "likes_instrumental": True,
    },
    # New: Nostalgic Instrumentalist — exercises most new features at once
    "Nostalgic Instrumentalist": {
        "genre": "classical",
        "mood": "melancholic",
        "energy": 0.25,
        "likes_acoustic": True,
        "preferred_decade": "1990s",
        "preferred_mood_tags": ["nostalgic", "dreamy"],
        "likes_instrumental": True,
        "min_popularity": 0,
    },
}


# ── Challenge 4: Tabulate Output ──────────────────────────────────────────────

def _truncate(text: str, max_len: int = 38) -> str:
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def run_profile(
    name: str,
    user_prefs: dict,
    songs: list,
    k: int = 5,
    mode_key: str = "mood-first",
    diversity: bool = False,
) -> None:
    strategy = SCORING_MODES[mode_key]

    print("\n" + "=" * 70)
    print(f"  Profile : {name}")
    print(f"  Mode    : {strategy.name}")
    print(f"  Prefs   : {user_prefs}")
    print(f"  Diversity penalty: {'ON' if diversity else 'OFF'}")
    print("=" * 70)

    recommendations = recommend_songs(user_prefs, songs, k=k, strategy=strategy, diversity=diversity)

    # Challenge 4: Build table rows
    rows = []
    for rank, rec in enumerate(recommendations, 1):
        song, score, explanation = rec
        rows.append([
            rank,
            _truncate(song["title"]),
            _truncate(song["artist"], 18),
            song["genre"],
            song["mood"],
            f"{song['energy']:.2f}",
            song.get("popularity", "?"),
            song.get("release_decade", "?"),
            f"{score:.2f}",
            _truncate(explanation, 50),
        ])

    headers = ["#", "Title", "Artist", "Genre", "Mood", "Energy",
               "Pop", "Decade", "Score", "Reasons"]

    if HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    else:
        # Fallback: simple ASCII table when tabulate is not installed
        col_widths = [max(len(str(h)), max(len(str(r[i])) for r in rows))
                      for i, h in enumerate(headers)]
        separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
        fmt_row = lambda cells: "|" + "|".join(
            f" {str(c):<{col_widths[i]}} " for i, c in enumerate(cells)
        ) + "|"
        print(separator)
        print(fmt_row(headers))
        print(separator)
        for row in rows:
            print(fmt_row(row))
        print(separator)

    print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Demonstrate all three scoring modes (Challenge 2)
    demo_modes = ["genre-first", "mood-first", "energy-focused"]
    demo_profile_name = "High-Energy Pop"
    demo_prefs = PROFILES[demo_profile_name]

    print("\n" + "█" * 70)
    print("  CHALLENGE 2 DEMO — Same profile, three scoring modes")
    print("█" * 70)
    for mode_key in demo_modes:
        run_profile(demo_profile_name, demo_prefs, songs, k=5,
                    mode_key=mode_key, diversity=False)

    # Run all profiles with the configured mode and diversity setting
    print("\n" + "█" * 70)
    print(f"  FULL RUN — Mode: {SCORING_MODES[SCORING_MODE].name} | Diversity: {'ON' if DIVERSITY else 'OFF'}")
    print("█" * 70)
    for name, prefs in PROFILES.items():
        run_profile(name, prefs, songs, k=5, mode_key=SCORING_MODE, diversity=DIVERSITY)


if __name__ == "__main__":
    main()
