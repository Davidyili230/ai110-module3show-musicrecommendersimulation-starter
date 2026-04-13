import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


# ── Data Models ───────────────────────────────────────────────────────────────

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py

    Challenge 1 additions: popularity, release_decade, mood_tag, liveness, instrumentalness
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # Challenge 1: Advanced features (default values preserve backward compatibility)
    popularity: int = 50
    release_decade: str = "2020s"
    mood_tag: str = "neutral"
    liveness: float = 0.10
    instrumentalness: float = 0.10


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py

    Challenge 1 additions: preferred_decade, preferred_mood_tags, likes_instrumental, min_popularity
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # Challenge 1: Advanced preference fields (all optional with safe defaults)
    preferred_decade: str = ""
    preferred_mood_tags: List[str] = field(default_factory=list)
    likes_instrumental: bool = False
    min_popularity: int = 0


# ── Challenge 2: Strategy Pattern for Scoring Modes ───────────────────────────

class ScoringStrategy(ABC):
    """Abstract base class defining the interface for a scoring strategy."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable strategy name."""

    @abstractmethod
    def weights(self) -> Dict[str, float]:
        """
        Returns per-dimension weight multipliers.

        Keys used by _score():
          genre, mood, energy, acoustic, popularity, decade, mood_tag, instrumental
        """


class GenreFirstStrategy(ScoringStrategy):
    """
    Genre-First mode: triples the genre-match reward.
    Best for users who care deeply about staying inside one genre.
    """

    @property
    def name(self) -> str:
        return "Genre-First"

    def weights(self) -> Dict[str, float]:
        return {
            "genre": 3.0,
            "mood": 1.0,
            "energy": 1.0,
            "acoustic": 0.5,
            "popularity": 0.5,
            "decade": 1.0,
            "mood_tag": 1.0,
            "instrumental": 0.5,
        }


class MoodFirstStrategy(ScoringStrategy):
    """
    Mood-First mode: triples mood and detailed mood-tag rewards.
    Best for users who want a specific emotional atmosphere regardless of genre.
    """

    @property
    def name(self) -> str:
        return "Mood-First"

    def weights(self) -> Dict[str, float]:
        return {
            "genre": 0.5,
            "mood": 3.0,
            "energy": 1.0,
            "acoustic": 0.5,
            "popularity": 0.5,
            "decade": 0.5,
            "mood_tag": 2.5,
            "instrumental": 0.5,
        }


class EnergyFocusedStrategy(ScoringStrategy):
    """
    Energy-Focused mode: quadruples the energy-proximity reward and boosts popularity.
    Best for workout playlists or focus sessions where energy level is paramount.
    """

    @property
    def name(self) -> str:
        return "Energy-Focused"

    def weights(self) -> Dict[str, float]:
        return {
            "genre": 0.5,
            "mood": 0.5,
            "energy": 4.0,
            "acoustic": 0.5,
            "popularity": 1.0,
            "decade": 0.5,
            "mood_tag": 0.5,
            "instrumental": 1.0,
        }


# Registry mapping CLI/config names → strategy instances
SCORING_MODES: Dict[str, ScoringStrategy] = {
    "genre-first": GenreFirstStrategy(),
    "mood-first": MoodFirstStrategy(),
    "energy-focused": EnergyFocusedStrategy(),
}


# ── OOP Recommender ───────────────────────────────────────────────────────────

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py

    Challenge 2: accepts a ScoringStrategy to switch ranking behaviour.
    Challenge 3: recommend() supports a diversity flag to prevent artist/genre repetition.
    """

    def __init__(self, songs: List[Song], strategy: ScoringStrategy = None):
        self.songs = songs
        self.strategy = strategy or MoodFirstStrategy()

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """
        Computes a numeric score and a list of human-readable reasons.

        Scoring rules (Challenge 1 — new rules marked NEW):
          1. Genre match       : +1.0 × genre_weight
          2. Mood match        : +2.0 × mood_weight
          3. Energy proximity  : up to +2.0 × energy_weight  (continuous)
          4. Acoustic bonus    : +1.0 × acoustic_weight       (if user likes acoustic)
          5. [NEW] Popularity  : up to +1.0 × pop_weight      (if popularity > 70)
          6. [NEW] Decade match: +1.0 × decade_weight         (if preferred era matches)
          7. [NEW] Mood-tag    : +1.5 × mood_tag_weight       (detailed tag match)
          8. [NEW] Instrumental: +1.0 × instrumental_weight   (if user prefers instrumental)
          9. [NEW] Liveness pen: −0.4                         (penalty for high-liveness tracks)
        """
        w = self.strategy.weights()
        score = 0.0
        reasons = []

        # 1. Genre match
        if song.genre == user.favorite_genre:
            pts = round(1.0 * w["genre"], 2)
            score += pts
            reasons.append(f"genre match (+{pts:.2f})")

        # 2. Mood match
        if song.mood == user.favorite_mood:
            pts = round(2.0 * w["mood"], 2)
            score += pts
            reasons.append(f"mood match (+{pts:.2f})")

        # 3. Energy proximity (continuous, higher weight → more sensitive to energy)
        energy_diff = abs(song.energy - user.target_energy)
        energy_pts = round(2.0 * w["energy"] * (1.0 - energy_diff), 2)
        score += energy_pts
        reasons.append(f"energy proximity ({energy_pts:+.2f})")

        # 4. Acoustic bonus
        if user.likes_acoustic and song.acousticness > 0.5:
            pts = round(1.0 * w["acoustic"], 2)
            score += pts
            reasons.append(f"acoustic preference (+{pts:.2f})")

        # 5. [NEW] Popularity bonus — rewards mainstream hits proportionally above 70
        if song.popularity > 70:
            pts = round(w["popularity"] * (song.popularity - 70) / 30, 2)
            score += pts
            reasons.append(f"popular track pop={song.popularity} (+{pts:.2f})")

        # 6. [NEW] Release decade match
        if user.preferred_decade and song.release_decade == user.preferred_decade:
            pts = round(1.0 * w["decade"], 2)
            score += pts
            reasons.append(f"preferred era {song.release_decade} (+{pts:.2f})")

        # 7. [NEW] Detailed mood-tag match
        if user.preferred_mood_tags and song.mood_tag in user.preferred_mood_tags:
            pts = round(1.5 * w["mood_tag"], 2)
            score += pts
            reasons.append(f"mood tag '{song.mood_tag}' (+{pts:.2f})")

        # 8. [NEW] Instrumental preference
        if user.likes_instrumental and song.instrumentalness > 0.5:
            pts = round(1.0 * w["instrumental"], 2)
            score += pts
            reasons.append(f"instrumental track (+{pts:.2f})")

        # 9. [NEW] Liveness penalty — live recordings feel less polished in studio playlists
        if song.liveness > 0.6:
            score -= 0.4
            reasons.append("live recording penalty (−0.40)")

        return round(score, 4), reasons

    def recommend(self, user: UserProfile, k: int = 5, diversity: bool = False) -> List[Song]:
        """
        Returns the top-k songs sorted by descending score.

        Challenge 3: When diversity=True applies a greedy diversity penalty so that
        no single artist appears more than once and no genre dominates the top-k.
        """
        scored = [(song, self._score(user, song)[0]) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)

        if diversity:
            return self._apply_diversity(scored, k)
        return [song for song, _ in scored[:k]]

    def _apply_diversity(self, scored: List[Tuple[Song, float]], k: int) -> List[Song]:
        """
        Challenge 3: Greedy diversity selection.

        Penalty rules (applied after each pick):
          - Duplicate artist: −0.8 per additional song from same artist
          - Duplicate genre:  −0.5 per additional song from same genre (first duplicate onwards)

        This prevents a single popular artist/genre from dominating the top-k list.
        """
        artist_count: Dict[str, int] = {}
        genre_count: Dict[str, int] = {}
        selected: List[Song] = []

        for song, base_score in scored:
            artist_penalty = artist_count.get(song.artist, 0) * 0.8
            genre_penalty = max(0, genre_count.get(song.genre, 0) - 1) * 0.5
            adjusted = base_score - artist_penalty - genre_penalty

            if adjusted > 0 or len(selected) < k:
                selected.append(song)
                artist_count[song.artist] = artist_count.get(song.artist, 0) + 1
                genre_count[song.genre] = genre_count.get(song.genre, 0) + 1

            if len(selected) >= k:
                break

        return selected

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable explanation of why a song was recommended."""
        _, reasons = self._score(user, song)
        return "; ".join(reasons) if reasons else "No specific match factors."


# ── Functional API ────────────────────────────────────────────────────────────

def load_songs(csv_path: str) -> List[Dict]:
    """
    Reads songs.csv and returns a list of dicts with numeric fields cast correctly.
    New columns (popularity, release_decade, mood_tag, liveness, instrumentalness)
    are parsed when present; older CSVs without them still work.
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song = {
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": int(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                # Challenge 1: new fields with graceful fallbacks
                "popularity": int(row["popularity"]) if "popularity" in row else 50,
                "release_decade": row.get("release_decade", "2020s"),
                "mood_tag": row.get("mood_tag", "neutral"),
                "liveness": float(row["liveness"]) if "liveness" in row else 0.10,
                "instrumentalness": float(row["instrumentalness"]) if "instrumentalness" in row else 0.10,
            }
            songs.append(song)
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(
    user_prefs: Dict,
    song: Dict,
    strategy: ScoringStrategy = None,
) -> Tuple[float, str]:
    """
    Scores a single song dict against a user preference dict.
    Returns (score, reasons_string).

    Challenge 1 scoring rules applied (see Recommender._score docstring).
    Challenge 2: pass a ScoringStrategy instance to change weight profile.
    """
    w = (strategy or MoodFirstStrategy()).weights()
    score = 0.0
    reasons = []

    # 1. Genre match
    if song["genre"] == user_prefs.get("genre", ""):
        pts = round(1.0 * w["genre"], 2)
        score += pts
        reasons.append(f"genre match (+{pts:.2f})")

    # 2. Mood match
    if song["mood"] == user_prefs.get("mood", ""):
        pts = round(2.0 * w["mood"], 2)
        score += pts
        reasons.append(f"mood match (+{pts:.2f})")

    # 3. Energy proximity
    target_energy = user_prefs.get("energy", 0.5)
    energy_diff = abs(song["energy"] - target_energy)
    energy_pts = round(2.0 * w["energy"] * (1.0 - energy_diff), 2)
    score += energy_pts
    reasons.append(f"energy proximity ({energy_pts:+.2f})")

    # 4. Acoustic bonus
    if user_prefs.get("likes_acoustic") and song.get("acousticness", 0) > 0.5:
        pts = round(1.0 * w["acoustic"], 2)
        score += pts
        reasons.append(f"acoustic preference (+{pts:.2f})")

    # 5. [NEW] Popularity bonus
    pop = song.get("popularity", 50)
    if pop > 70:
        pts = round(w["popularity"] * (pop - 70) / 30, 2)
        score += pts
        reasons.append(f"popular track pop={pop} (+{pts:.2f})")

    # 6. [NEW] Preferred decade
    pref_decade = user_prefs.get("preferred_decade", "")
    if pref_decade and song.get("release_decade") == pref_decade:
        pts = round(1.0 * w["decade"], 2)
        score += pts
        reasons.append(f"preferred era {song['release_decade']} (+{pts:.2f})")

    # 7. [NEW] Detailed mood-tag match
    mood_tags = user_prefs.get("preferred_mood_tags", [])
    if mood_tags and song.get("mood_tag") in mood_tags:
        pts = round(1.5 * w["mood_tag"], 2)
        score += pts
        reasons.append(f"mood tag '{song['mood_tag']}' (+{pts:.2f})")

    # 8. [NEW] Instrumental preference
    if user_prefs.get("likes_instrumental") and song.get("instrumentalness", 0) > 0.5:
        pts = round(1.0 * w["instrumental"], 2)
        score += pts
        reasons.append(f"instrumental track (+{pts:.2f})")

    # 9. [NEW] Liveness penalty
    if song.get("liveness", 0) > 0.6:
        score -= 0.4
        reasons.append("live recording penalty (−0.40)")

    return round(score, 4), "; ".join(reasons)


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    strategy: ScoringStrategy = None,
    diversity: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """
    Ranks all songs by score and returns the top-k as (song, score, explanation) tuples.

    Challenge 2: pass a ScoringStrategy to switch scoring mode.
    Challenge 3: set diversity=True to apply artist/genre diversity penalty.
    """
    scored = [(song, *score_song(user_prefs, song, strategy)) for song in songs]
    scored.sort(key=lambda x: x[1], reverse=True)

    if not diversity:
        return scored[:k]

    # Challenge 3: greedy diversity re-ranking
    artist_count: Dict[str, int] = {}
    genre_count: Dict[str, int] = {}
    selected = []

    for song, base_score, explanation in scored:
        artist_penalty = artist_count.get(song["artist"], 0) * 0.8
        genre_penalty = max(0, genre_count.get(song["genre"], 0) - 1) * 0.5
        adjusted = round(base_score - artist_penalty - genre_penalty, 4)

        if adjusted > 0 or len(selected) < k:
            reasons_note = explanation
            if artist_penalty > 0:
                reasons_note += f"; artist diversity penalty (−{artist_penalty:.2f})"
            if genre_penalty > 0:
                reasons_note += f"; genre diversity penalty (−{genre_penalty:.2f})"
            selected.append((song, adjusted, reasons_note))
            artist_count[song["artist"]] = artist_count.get(song["artist"], 0) + 1
            genre_count[song["genre"]] = genre_count.get(song["genre"], 0) + 1

        if len(selected) >= k:
            break

    return selected
