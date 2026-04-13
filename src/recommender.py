import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
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

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Computes a numeric score and reasons for a Song against a UserProfile.

        Experiment – Weight Shift applied:
          - Genre match: +1.0  (halved from original +2.0)
          - Mood  match: +2.0  (unchanged)
          - Energy proximity: up to +2.0  (doubled from original +1.0 max)
          - Acoustic bonus: +1.0 (unchanged)
        """
        score = 0.0
        reasons = []

        if song.genre == user.favorite_genre:
            score += 1.0
            reasons.append("genre match (+1.0)")

        if song.mood == user.favorite_mood:
            score += 2.0
            reasons.append("mood match (+2.0)")

        energy_diff = abs(song.energy - user.target_energy)
        energy_points = round(2.0 * (1.0 - energy_diff), 2)
        score += energy_points
        reasons.append(f"energy proximity ({energy_points:+.2f})")

        if user.likes_acoustic and song.acousticness > 0.5:
            score += 1.0
            reasons.append("acoustic preference match (+1.0)")

        return score, reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top-k songs sorted by descending score for the given user."""
        scored = [(song, self._score(user, song)[0]) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable explanation of why a song was recommended."""
        _, reasons = self._score(user, song)
        return "; ".join(reasons) if reasons else "No specific match factors."


def load_songs(csv_path: str) -> List[Dict]:
    """Reads songs.csv and returns a list of dicts with numeric fields cast to float/int."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
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
            })
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, str]:
    """Scores a single song dict against user preference dict; returns (score, reasons_string).

    Experiment – Weight Shift applied:
      - Genre match: +1.0  (halved from original +2.0)
      - Mood  match: +2.0  (unchanged)
      - Energy proximity: up to +2.0  (doubled from original +1.0 max)
    """
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs.get("genre", ""):
        score += 1.0
        reasons.append("genre match (+1.0)")

    if song["mood"] == user_prefs.get("mood", ""):
        score += 2.0
        reasons.append("mood match (+2.0)")

    target_energy = user_prefs.get("energy", 0.5)
    energy_diff = abs(song["energy"] - target_energy)
    energy_points = round(2.0 * (1.0 - energy_diff), 2)
    score += energy_points
    reasons.append(f"energy proximity ({energy_points:+.2f})")

    return score, "; ".join(reasons)


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Ranks all songs by score and returns the top-k as (song, score, explanation) tuples."""
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
