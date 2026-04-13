import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

ENERGY_WINDOW      = 0.3
VALENCE_WINDOW     = 0.3
DANCEABILITY_WINDOW = 0.3

# Importance weights: Energy > Mood > Genre > Artist > Valence > Acoustic > Danceability
WEIGHT_ENERGY      = 0.35
WEIGHT_MOOD        = 0.20
WEIGHT_GENRE       = 0.15
WEIGHT_ARTIST      = 0.10
WEIGHT_VALENCE     = 0.10
WEIGHT_ACOUSTIC    = 0.05
WEIGHT_DANCEABILITY = 0.05

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
    target_valence: float = 0.5
    target_danceability: float = 0.5
    preferred_artists: List[str] = field(default_factory=list)

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
            energy_score = max(0.0, 1.0 - (energy_diff / ENERGY_WINDOW))

            valence_diff = abs(song.valence - user.target_valence)
            valence_score = max(0.0, 1.0 - (valence_diff / VALENCE_WINDOW))

            dance_diff = abs(song.danceability - user.target_danceability)
            danceability_score = max(0.0, 1.0 - (dance_diff / DANCEABILITY_WINDOW))

            mood_score   = 1.0 if song.mood  == user.favorite_mood  else 0.0
            mood_score     = 0.5  # mood feature disabled
            genre_score    = 1.0 if song.genre == user.favorite_genre else 0.0
            acoustic_score = song.acousticness if user.likes_acoustic else (1.0 - song.acousticness)

            if user.preferred_artists:
                artist_score = 1.0 if song.artist in user.preferred_artists else 0.0
            else:
                artist_score = 0.5  # neutral when no preference set

            total = (
                energy_score      * WEIGHT_ENERGY +
                mood_score        * WEIGHT_MOOD +
                genre_score       * WEIGHT_GENRE +
                artist_score      * WEIGHT_ARTIST +
                valence_score     * WEIGHT_VALENCE +
                acoustic_score    * WEIGHT_ACOUSTIC +
                danceability_score * WEIGHT_DANCEABILITY
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
        if user.preferred_artists and song.artist in user.preferred_artists:
            reasons.append(f"by a preferred artist ({song.artist})")

        valence_diff = abs(song.valence - user.target_valence)
        reasons.append(
            f"valence {song.valence:.2f} is {'close to' if valence_diff < 0.1 else 'within range of'} "
            f"your target {user.target_valence:.2f}"
        )

        dance_diff = abs(song.danceability - user.target_danceability)
        reasons.append(
            f"danceability {song.danceability:.2f} is {'close to' if dance_diff < 0.1 else 'within range of'} "
            f"your target {user.target_danceability:.2f}"
        )

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
    energy_score = max(0.0, 1.0 - (energy_diff / ENERGY_WINDOW))

    valence_diff = abs(song["valence"] - user_prefs.get("target_valence", 0.5))
    valence_score = max(0.0, 1.0 - (valence_diff / VALENCE_WINDOW))

    dance_diff = abs(song["danceability"] - user_prefs.get("target_danceability", 0.5))
    danceability_score = max(0.0, 1.0 - (dance_diff / DANCEABILITY_WINDOW))

    preferred_artists = user_prefs.get("preferred_artists", [])
    if preferred_artists:
        artist_score = 1.0 if song["artist"] in preferred_artists else 0.0
    else:
        artist_score = 0.5  # neutral when no preference set

    reasons = []

    if energy_diff <= ENERGY_WINDOW:
        reasons.append(
            f"energy {song['energy']:.2f} within ±{ENERGY_WINDOW} of target {user_prefs['energy']:.2f}"
        )

    mood_score = 1.0 if song["mood"] == user_prefs.get("mood", "") else 0.0
    mood_score = 0.5  # mood feature disabled
    if mood_score:
        reasons.append(f"mood matches ({song['mood']})")

    genre_score = 1.0 if song["genre"] == user_prefs.get("genre", "") else 0.0
    if genre_score:
        reasons.append(f"genre matches ({song['genre']})")

    if preferred_artists and song["artist"] in preferred_artists:
        reasons.append(f"preferred artist ({song['artist']})")

    if valence_diff <= VALENCE_WINDOW:
        reasons.append(f"valence {song['valence']:.2f} within range of target {user_prefs.get('target_valence', 0.5):.2f}")

    if dance_diff <= DANCEABILITY_WINDOW:
        reasons.append(f"danceability {song['danceability']:.2f} within range of target {user_prefs.get('target_danceability', 0.5):.2f}")

    likes_acoustic = user_prefs.get("likes_acoustic", False)
    acoustic_score = song["acousticness"] if likes_acoustic else (1.0 - song["acousticness"])
    if likes_acoustic and song["acousticness"] > 0.5:
        reasons.append(f"acoustic feel ({song['acousticness']:.2f})")

    score = (
        energy_score       * WEIGHT_ENERGY +
        mood_score         * WEIGHT_MOOD +
        genre_score        * WEIGHT_GENRE +
        artist_score       * WEIGHT_ARTIST +
        valence_score      * WEIGHT_VALENCE +
        acoustic_score     * WEIGHT_ACOUSTIC +
        danceability_score * WEIGHT_DANCEABILITY
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
