import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

ENERGY_WINDOW = 0.3

# Importance weights: Energy > Mood > Genre > Acoustic
WEIGHT_ENERGY   = 0.50
WEIGHT_MOOD     = 0.25
WEIGHT_GENRE    = 0.15
WEIGHT_ACOUSTIC = 0.10

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

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = []
        for song in self.songs:
            energy_diff = abs(song.energy - user.target_energy)
            # Energy score: 0 outside the ±ENERGY_WINDOW, graded inside it
            energy_score   = max(0.0, 1.0 - (energy_diff / ENERGY_WINDOW))
            mood_score     = 1.0 if song.mood  == user.favorite_mood  else 0.0
            genre_score    = 1.0 if song.genre == user.favorite_genre else 0.0
            acoustic_score = song.acousticness if user.likes_acoustic else (1.0 - song.acousticness)

            total = (
                energy_score   * WEIGHT_ENERGY +
                mood_score     * WEIGHT_MOOD +
                genre_score    * WEIGHT_GENRE +
                acoustic_score * WEIGHT_ACOUSTIC
            )
            scored.append((total, song))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [song for _, song in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons = []

        energy_diff = abs(song.energy - user.target_energy)
        reasons.append(
            f"energy {song.energy:.2f} is {'close to' if energy_diff < 0.1 else 'within range of'} "
            f"your target {user.target_energy:.2f}"
        )

        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches your favorite ({song.mood})")
        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches your favorite ({song.genre})")
        if user.likes_acoustic and song.acousticness > 0.5:
            reasons.append(f"has an acoustic feel ({song.acousticness:.2f})")

        return "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    user_prefs keys: genre, mood, energy, likes_acoustic (optional, default False)
    Returns (score, reasons). Score is 0.0 if song is outside the energy window.
    """
    energy_diff = abs(song["energy"] - user_prefs["energy"])
    # Energy score: 0 outside the ±ENERGY_WINDOW, graded inside it
    energy_score = max(0.0, 1.0 - (energy_diff / ENERGY_WINDOW))

    reasons = []

    if energy_diff <= ENERGY_WINDOW:
        reasons.append(
            f"energy {song['energy']:.2f} within ±{ENERGY_WINDOW} of target {user_prefs['energy']:.2f}"
        )

    mood_score = 1.0 if song["mood"] == user_prefs.get("mood", "") else 0.0
    if mood_score:
        reasons.append(f"mood matches ({song['mood']})")

    genre_score = 1.0 if song["genre"] == user_prefs.get("genre", "") else 0.0
    if genre_score:
        reasons.append(f"genre matches ({song['genre']})")

    likes_acoustic = user_prefs.get("likes_acoustic", False)
    acoustic_score = song["acousticness"] if likes_acoustic else (1.0 - song["acousticness"])
    if likes_acoustic and song["acousticness"] > 0.5:
        reasons.append(f"acoustic feel ({song['acousticness']:.2f})")

    score = (
        energy_score   * WEIGHT_ENERGY +
        mood_score     * WEIGHT_MOOD +
        genre_score    * WEIGHT_GENRE +
        acoustic_score * WEIGHT_ACOUSTIC
    )
    return (score, reasons)


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons) if reasons else "outside energy range"))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
